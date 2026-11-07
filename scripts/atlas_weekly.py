#!/usr/bin/env python3
"""Resumen semanal de Zona Gris. Por defecto SOLO genera el HTML (dry-run)."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("ATLAS_SUBS_DB", "/home/deploy/atlas-subs/data/subs.db"))
EVENTS = Path(os.environ.get("ATLAS_EVENTS", ROOT / "web" / "assets" / "data" / "events.json"))
ENV_PATH = Path(os.environ.get("ATLAS_SUBS_ENV", "/home/deploy/newsletter/.env"))
BASE_URL = os.environ.get("ATLAS_SUBS_BASE_URL", "https://zonagris.pruebapublica.com").rstrip("/")
FROM = os.environ.get("ATLAS_SUBS_FROM", "Zona Gris <newsletter@viajeinteligencia.com>")
REPLY_TO = os.environ.get("ATLAS_SUBS_REPLY_TO", "info.zonagris@pruebapublica.com")


def load_env() -> dict[str, str]:
    out = {}
    try:
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                out[key.strip()] = value.strip().strip('"').strip("'")
    except OSError:
        pass
    return out


def confirmed() -> list[sqlite3.Row]:
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id,email,last_sent_at FROM subscribers WHERE status='confirmed' ORDER BY created_at").fetchall()
    conn.close()
    return rows


def build() -> tuple[str, str, int]:
    data = json.loads(EVENTS.read_text(encoding="utf-8"))
    cutoff = datetime.now(timezone.utc).date() - timedelta(days=7)
    rows = []
    for item in data.get("events", []):
        try:
            day = datetime.fromisoformat(item.get("event_date") or item.get("published_at")).date()
        except (TypeError, ValueError):
            continue
        if day >= cutoff:
            rows.append(item)
    documented = [x for x in rows if x.get("verification_status") == "DOCUMENTADO"]
    pending = [x for x in rows if x.get("verification_status") == "PENDIENTE"]
    if not rows:
        return "", "", 0
    def line(item: dict) -> str:
        title = escape(item.get("title") or "Sin título")
        zone = escape(item.get("place") or item.get("country") or "zona no documentada")
        return f"<li><strong>{title}</strong><br><span style='color:#59636e'>{escape(item.get('event_date') or '')} · {zone}</span></li>"
    html = f"""<!doctype html><html lang="es"><body style="margin:0;background:#f4f1ea;color:#17202a;font-family:Georgia,serif">
<div style="max-width:620px;margin:0 auto;padding:30px 22px">
<p style="font-family:Arial,sans-serif;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#b4532a">Zona Gris · resumen semanal</p>
<h1 style="font-size:26px;line-height:1.2">Lo que el atlas incorporó esta semana</h1>
<p>{len(documented)} documentados y {len(pending)} candidatos pendientes en los últimos 7 días. Un pendiente no es un ataque confirmado.</p>
<h2 style="font-size:18px">Documentados</h2><ul>{''.join(line(x) for x in documented[:8]) or '<li>Ninguno.</li>'}</ul>
<h2 style="font-size:18px">Pendientes</h2><ul>{''.join(line(x) for x in pending[:8]) or '<li>Ninguno.</li>'}</ul>
<p><a href="{BASE_URL}/incidentes.html">Ver la matriz completa →</a></p>
<p style="font-size:12px;color:#59636e">No se atribuye autoría por inferencia. Las fuentes están enlazadas en cada ficha.</p>
</div></body></html>"""
    text = f"Zona Gris · resumen semanal\n{len(documented)} documentados · {len(pending)} pendientes\n{BASE_URL}/incidentes.html\n"
    return html, text, len(rows)


def send(email: str, token: str, html: str, text: str) -> bool:
    key = load_env().get("RESEND_API_KEY", "")
    if not key:
        print("atlas_weekly: falta RESEND_API_KEY", file=sys.stderr)
        return False
    unsub = f"{BASE_URL}/api/atlas/unsubscribe?id={quote(token)}"
    body = html.replace("</div></body></html>", f'<p style="font-size:12px;color:#59636e">Recibes esto porque te suscribiste. <a href="{unsub}">Darse de baja</a>.</p></div></body></html>')
    payload = json.dumps({"from": FROM, "to": [email], "reply_to": REPLY_TO,
                          "subject": "Zona Gris · resumen semanal", "html": body, "text": text + f"\nBaja: {unsub}\n"}).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=payload, method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "User-Agent": "Mozilla/5.0 (compatible; AtlasZonaGris/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return 200 <= response.status < 300
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        print(f"atlas_weekly: {email}: {exc}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true", help="envía de verdad; sin esto solo genera el HTML")
    args = parser.parse_args()
    html, text, count = build()
    if not count:
        print("atlas_weekly: sin acontecimientos en 7 días; no se envía")
        return 0
    rows = confirmed()
    print(f"atlas_weekly: {len(rows)} confirmados · {count} acontecimientos en 7 días")
    if not args.send:
        print("atlas_weekly: dry-run; no se envía nada")
        return 0
    sent = 0
    for row in rows:
        if send(row["email"], row["id"], html, text):
            sent += 1
    print(f"atlas_weekly: enviados {sent}/{len(rows)}")
    return 0 if sent == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
