#!/usr/bin/env python3
"""Lista propia de Zona Gris: doble opt-in y baja en un clic.

Escucha en 127.0.0.1:3033. Sin dependencias externas.
"""
from __future__ import annotations

import base64
import csv
import io
import json
import os
import re
import secrets
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("ATLAS_SUBS_DB", ROOT / "data" / "subs.db"))
ENV_PATH = Path(os.environ.get("ATLAS_SUBS_ENV", "/home/deploy/newsletter/.env"))
BASE_URL = os.environ.get("ATLAS_SUBS_BASE_URL", "https://zonagris.pruebapublica.com").rstrip("/")
REPLY_TO = os.environ.get("ATLAS_SUBS_REPLY_TO", "info.zonagris@pruebapublica.com")
HOST = os.environ.get("ATLAS_SUBS_HOST", "127.0.0.1")
PORT = int(os.environ.get("ATLAS_SUBS_PORT", "3033"))
INCIDENTS_PATH = Path(os.environ.get("ATLAS_INCIDENTS_PATH", "/var/www/atlas-zonagris/current/assets/data/incidentes.json"))
DRY_RUN = os.environ.get("ATLAS_SUBS_DRY_RUN", "0") == "1"
API = "/api/atlas"
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
MAX_BODY = 16_384
PENDING_DAYS = 30
RESEND_WINDOW = 600
CONSENT_VERSION = "2026-11-07-v1"
SOURCE = "zonagris"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_env(path: Path = ENV_PATH) -> dict[str, str]:
    data: dict[str, str] = {}
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    except OSError as exc:
        print(f"atlas_subs: no se pudo leer {path}: {exc}", file=sys.stderr)
    return data


def db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 15000")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db() -> None:
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS subscribers (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL CHECK (status IN ('pending','confirmed','unsubscribed')),
                source TEXT NOT NULL DEFAULT 'zonagris',
                page TEXT,
                utm_source TEXT,
                utm_medium TEXT,
                referrer_host TEXT,
                created_at TEXT NOT NULL,
                confirmed_at TEXT,
                unsubscribed_at TEXT,
                last_sent_at TEXT,
                consent_version TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_atlas_subs_status ON subscribers(status);
            CREATE INDEX IF NOT EXISTS idx_atlas_subs_created ON subscribers(created_at);
            """
        )


def clean(value: object, limit: int) -> str:
    return " ".join(str(value or "").split())[:limit]


def norm_email(value: object) -> str:
    email = clean(value, 254).lower()
    return email if EMAIL_RE.match(email) else ""


def ref_host(value: object) -> str:
    raw = clean(value, 500)
    if not raw:
        return ""
    if "://" not in raw and not raw.startswith("//"):
        raw = "https://" + raw
    try:
        return (urlsplit(raw).hostname or "").lower().removeprefix("www.")[:120]
    except ValueError:
        return ""


def prune_pending() -> int:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=PENDING_DAYS)).isoformat(timespec="seconds")
    with db() as conn:
        cur = conn.execute(
            "DELETE FROM subscribers WHERE status='pending' AND COALESCE(last_sent_at, created_at) < ?",
            (cutoff,),
        )
        return cur.rowcount


def subscribe(email: str, page: str = "", utm_source: str = "", utm_medium: str = "", referrer: str = "") -> tuple[str, bool]:
    email = norm_email(email)
    if not email:
        raise ValueError("email inválido")
    stamp = now_iso()
    token = secrets.token_urlsafe(32)
    with db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT * FROM subscribers WHERE email = ?", (email,)).fetchone()
        if row and row["status"] == "confirmed":
            conn.commit()
            return row["id"], False
        if row:
            token = row["id"]
            if row["status"] == "pending" and row["last_sent_at"]:
                try:
                    age = (datetime.now(timezone.utc) - datetime.fromisoformat(row["last_sent_at"])).total_seconds()
                except ValueError:
                    age = RESEND_WINDOW
                if age < RESEND_WINDOW:
                    conn.commit()
                    return token, False
            conn.execute(
                """UPDATE subscribers SET status='pending', page=?, utm_source=?, utm_medium=?,
                   referrer_host=?, last_sent_at=?, confirmed_at=NULL, unsubscribed_at=NULL,
                   consent_version=? WHERE id=?""",
                (clean(page, 200), clean(utm_source, 80), clean(utm_medium, 80), ref_host(referrer),
                 stamp, CONSENT_VERSION, token),
            )
        else:
            conn.execute(
                """INSERT INTO subscribers
                   (id,email,status,source,page,utm_source,utm_medium,referrer_host,created_at,last_sent_at,consent_version)
                   VALUES(?,?,'pending',?,?,?,?,?,?,?,?)""",
                (token, email, SOURCE, clean(page, 200), clean(utm_source, 80), clean(utm_medium, 80),
                 ref_host(referrer), stamp, stamp, CONSENT_VERSION),
            )
        conn.commit()
        return token, True


def mark(token: str, status: str) -> str:
    with db() as conn:
        row = conn.execute("SELECT status FROM subscribers WHERE id = ?", (token,)).fetchone()
        if not row:
            return "missing"
        if status == "confirmed":
            if row["status"] == "unsubscribed":
                return "missing"
            if row["status"] == "confirmed":
                return "already"
            conn.execute("UPDATE subscribers SET status='confirmed', confirmed_at=?, unsubscribed_at=NULL WHERE id=?", (now_iso(), token))
            return "ok"
        if row["status"] == "unsubscribed":
            return "already-unsubscribed"
        conn.execute("UPDATE subscribers SET status='unsubscribed', unsubscribed_at=? WHERE id=?", (now_iso(), token))
        return "ok"


def send_confirmation(email: str, token: str) -> bool:
    env = load_env()
    if DRY_RUN:
        print(f"atlas_subs: dry-run confirmation for {email} ({token})", file=sys.stderr)
        return True
    key = env.get("RESEND_API_KEY", "")
    if not key:
        raise RuntimeError("RESEND_API_KEY no configurada")
    sender = env.get("RESEND_FROM", "newsletter@viajeinteligencia.com")
    if "<" not in sender:
        sender = f"Zona Gris <{sender}>"
    confirm_url = f"{BASE_URL}{API}/confirm?id={quote(token)}"
    unsub_url = f"{BASE_URL}{API}/unsubscribe?id={quote(token)}"
    text = f"Confirma tu suscripción al resumen semanal de Zona Gris:\n{confirm_url}\n\nBaja: {unsub_url}\n"
    html = f"""<!doctype html><html lang="es"><body style="margin:0;background:#f4f1ea;color:#17202a;font-family:Georgia,serif">
<div style="max-width:560px;margin:0 auto;padding:30px 22px">
<p style="font-family:Arial,sans-serif;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#b4532a">Zona Gris</p>
<h1 style="font-size:26px;line-height:1.2">Confirma tu suscripción</h1>
<p>Recibirás un resumen semanal con los acontecimientos documentados y los candidatos pendientes. Sin ruido diario.</p>
<p style="margin:26px 0"><a href="{confirm_url}" style="background:#17202a;color:#fff;padding:13px 20px;text-decoration:none;border-radius:4px">Confirmar suscripción</a></p>
<p style="font-size:13px;color:#59636e">Si no lo has pedido, ignora este mensaje.</p>
<p style="font-size:13px"><a href="{unsub_url}" style="color:#59636e">Darse de baja</a></p>
</div></body></html>"""
    payload = json.dumps({"from": sender, "to": [email], "reply_to": REPLY_TO,
                          "subject": "Confirma tu suscripción al resumen semanal de Zona Gris",
                          "text": text, "html": html}).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=payload, method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "User-Agent": "Mozilla/5.0 (compatible; AtlasZonaGris/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return 200 <= response.status < 300
    except urllib.error.HTTPError as exc:
        print(f"atlas_subs: Resend HTTP {exc.code}: {exc.read(300).decode('utf-8', 'replace')}", file=sys.stderr)
        return False
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"atlas_subs: Resend error: {exc}", file=sys.stderr)
        return False


LIMITER = {}
LOCK = threading.Lock()


def rate_ok(ip: str) -> bool:
    now = time.monotonic()
    with LOCK:
        hits = [t for t in LIMITER.get(ip, []) if now - t < 3600]
        if len(hits) >= 10:
            LIMITER[ip] = hits
            return False
        hits.append(now)
        LIMITER[ip] = hits
        return True


def _incidents() -> list[dict]:
    try:
        payload = json.loads(INCIDENTS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return payload.get("events", []) if isinstance(payload, dict) else payload


def _cursor(item: dict) -> str:
    raw = f"{item.get('event_date') or ''}|{item.get('id') or ''}".encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _decode_cursor(value: str) -> tuple[str, str] | None:
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)).decode()
        date, ident = raw.split("|", 1)
        return date, ident
    except (ValueError, UnicodeDecodeError):
        return None


def _incident_query(query: str) -> tuple[list[dict], dict]:
    params = parse_qs(query)
    domain = (params.get("domain") or ["all"])[0]
    status = (params.get("status") or ["all"])[0]
    attribution = (params.get("attribution") or ["all"])[0]
    search = (params.get("q") or [""])[0].strip().casefold()
    cursor = (params.get("cursor") or [""])[0]
    try:
        days = int((params.get("days") or ["0"])[0])
    except ValueError:
        days = 0
    cutoff = (date.today() - timedelta(days=days)).isoformat() if days > 0 else None
    try:
        limit = max(1, min(100, int((params.get("limit") or ["50"])[0])))
    except ValueError:
        limit = 50
    rows = _incidents()
    filtered = []
    for item in rows:
        if cutoff and (item.get("event_date") or "") < cutoff:
            continue
        if domain != "all" and item.get("category") != domain:
            continue
        if status != "all" and item.get("verification_status") != status:
            continue
        attr = (item.get("attribution") or {}).get("status") or "none"
        if attribution != "all" and attr != attribution:
            continue
        if search:
            text = " ".join(str(item.get(k) or "") for k in ("id", "title", "description", "place", "country", "category_label")).casefold()
            if search not in text:
                continue
        filtered.append(item)
    filtered.sort(key=lambda x: (x.get("event_date") or "", x.get("id") or ""), reverse=True)
    total = len(filtered)
    if cursor:
        decoded = _decode_cursor(cursor)
        if decoded:
            filtered = [x for x in filtered if (x.get("event_date") or "", x.get("id") or "") < decoded]
    page = filtered[:limit]
    domains = {}
    for item in rows:
        if item.get("category"):
            domains[item["category"]] = item.get("category_label") or item["category"]
    counts = {
        "documented": sum(1 for x in filtered if x.get("verification_status") == "DOCUMENTADO"),
        "pending": sum(1 for x in filtered if x.get("verification_status") == "PENDIENTE"),
        "confirmed": sum(1 for x in filtered if x.get("verification_status") == "CONFIRMADO"),
        "attributed": sum(1 for x in filtered if ((x.get("attribution") or {}).get("status") or "none") != "none"),
    }
    return page, {
        "total": total,
        "limit": limit,
        "next_cursor": _cursor(filtered[limit - 1]) if len(filtered) > limit else None,
        "counts": counts,
        "domains": [{"id": k, "label": v} for k, v in sorted(domains.items())],
    }


def _incidents_csv(query: str) -> str:
    # Descarga con los mismos filtros, sin cursor ni límite de página.
    params = parse_qs(query)
    params.pop("limit", None)
    params.pop("cursor", None)
    all_rows = _incidents()
    out = []
    for item in all_rows:
        try:
            days = int((params.get("days") or ["0"])[0])
        except ValueError:
            days = 0
        if days > 0 and (item.get("event_date") or "") < (date.today() - timedelta(days=days)).isoformat():
            continue
        if params.get("domain") and params["domain"][0] != "all" and item.get("category") != params["domain"][0]:
            continue
        if params.get("status") and params["status"][0] != "all" and item.get("verification_status") != params["status"][0]:
            continue
        attr = (item.get("attribution") or {}).get("status") or "none"
        if params.get("attribution") and params["attribution"][0] != "all" and attr != params["attribution"][0]:
            continue
        q = (params.get("q") or [""])[0].casefold()
        if q and q not in " ".join(str(item.get(k) or "") for k in ("id", "title", "description", "place", "country", "category_label")).casefold():
            continue
        out.append(item)
    out.sort(key=lambda x: (x.get("event_date") or "", x.get("id") or ""), reverse=True)
    handle = io.StringIO()
    writer = csv.writer(handle)
    writer.writerow(["id", "event_date", "title", "category", "category_label", "place", "country", "verification_status", "attribution", "sources"])
    for item in out:
        writer.writerow([
            item.get("id"), item.get("event_date"), item.get("title"), item.get("category"),
            item.get("category_label"), item.get("place"), item.get("country"),
            item.get("verification_status"), (item.get("attribution") or {}).get("status") or "none",
            " | ".join(s.get("url", "") for s in item.get("sources", [])),
        ])
    return handle.getvalue()


def action_page(kind: str, token: str) -> str:
    confirm = kind == "confirm"
    title = "Confirma tu suscripción" if confirm else "Darse de baja"
    body = ("Pulsa el botón para confirmar que quieres recibir el resumen semanal de Zona Gris."
            if confirm else "Pulsa el botón para dejar de recibir el resumen semanal. La baja es inmediata.")
    endpoint = f"{API}/confirm" if confirm else f"{API}/unsubscribe"
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>{title} · Zona Gris</title>
<style>body{{margin:0;background:#12171d;color:#e9ecef;font-family:Georgia,serif}}main{{max-width:620px;margin:0 auto;padding:48px 22px}}p{{line-height:1.65;font-size:17px}}a{{color:#ffb020}}.eyebrow{{font-family:Arial,sans-serif;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#ffb020}}h1{{font-size:30px;line-height:1.2}}button{{font:inherit;font-weight:700;background:#ffb020;color:#12171d;border:0;border-radius:4px;padding:13px 20px;cursor:pointer}}</style></head>
<body><main><p class="eyebrow">Zona Gris</p><h1>{title}</h1><p>{body}</p>
<form method="post" action="{endpoint}"><input type="hidden" name="id" value="{escape(token)}"><button type="submit">{title}</button></form>
<p><a href="/">Volver al atlas</a></p></main></body></html>"""


def result_page(status: str) -> str:
    messages = {
        "ok": ("Suscripción confirmada", "Te he añadido a la lista. Recibirás el resumen semanal cuando haya algo que merezca la pena."),
        "already": ("Ya estabas suscrito", "No hace falta hacer nada más."),
        "unsubscribed": ("Baja completada", "No volverás a recibir el resumen semanal."),
        "already-unsubscribed": ("Ya estabas de baja", "No hace falta hacer nada más."),
    }
    title, body = messages.get(status, ("Enlace no válido", "El enlace ha caducado o no existe."))
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>{title} · Zona Gris</title>
<style>body{{margin:0;background:#12171d;color:#e9ecef;font-family:Georgia,serif}}main{{max-width:620px;margin:0 auto;padding:48px 22px}}p{{line-height:1.65;font-size:17px}}a{{color:#ffb020}}.eyebrow{{font-family:Arial,sans-serif;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#ffb020}}</style></head>
<body><main><p class="eyebrow">Zona Gris</p><h1>{title}</h1><p>{body}</p><p><a href="/">Volver al atlas</a></p></main></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def send_html(self, code: int, body: str) -> None:
        raw = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def send_json(self, code: int, obj: dict) -> None:
        raw = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self) -> dict:
        try:
            size = int(self.headers.get("Content-Length", 0) or 0)
            if size > MAX_BODY:
                return {}
            return json.loads(self.rfile.read(size).decode("utf-8")) if size else {}
        except (ValueError, json.JSONDecodeError):
            return {}

    def read_form(self) -> dict:
        size = min(int(self.headers.get("Content-Length", 0) or 0), MAX_BODY)
        return {k: v[0] for k, v in parse_qs(self.rfile.read(size).decode("utf-8")).items()}

    def do_GET(self):
        parts = urlsplit(self.path)
        path = parts.path.rstrip("/")
        if path == f"{API}/health":
            return self.send_json(200, {"ok": True, "dry_run": DRY_RUN})
        if path == f"{API}/incidentes":
            page, meta = _incident_query(parts.query)
            return self.send_json(200, {"items": page, **meta})
        if path == f"{API}/incidentes.csv":
            body = _incidents_csv(parts.query).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="incidentes-zonagris.csv"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path in {f"{API}/confirm", f"{API}/unsubscribe"}:
            token = (parse_qs(parts.query).get("id") or [""])[0]
            if not token:
                return self.send_html(400, result_page("missing"))
            return self.send_html(200, action_page("confirm" if path.endswith("confirm") else "unsubscribe", token))
        return self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if not rate_ok(self.client_address[0]):
            return self.send_json(429, {"error": "demasiadas peticiones"})
        path = urlsplit(self.path).path.rstrip("/")
        if path == f"{API}/subscribe":
            data = self.read_json()
            email = data.get("email")
            try:
                token, _ = subscribe(email, data.get("page", ""), data.get("utm_source", ""), data.get("utm_medium", ""), data.get("referrer", ""))
            except ValueError:
                return self.send_json(400, {"error": "email inválido"})
            try:
                if not send_confirmation(norm_email(email), token):
                    return self.send_json(502, {"error": "no se pudo enviar la confirmación"})
            except Exception as exc:  # noqa: BLE001
                print(f"atlas_subs: confirmación fallida: {exc}", file=sys.stderr)
                return self.send_json(502, {"error": "no se pudo enviar la confirmación"})
            return self.send_json(200, {"ok": True, "message": "revisa tu correo"})
        if path in {f"{API}/confirm", f"{API}/unsubscribe"}:
            token = self.read_form().get("id", "")
            status = mark(token, "confirmed" if path.endswith("confirm") else "unsubscribed")
            return self.send_html(200, result_page(status))
        return self.send_json(404, {"error": "not found"})


def main() -> int:
    init_db()
    prune_pending()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"atlas_subs: {HOST}:{PORT} db={DB_PATH} dry_run={DRY_RUN}", file=sys.stderr)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
