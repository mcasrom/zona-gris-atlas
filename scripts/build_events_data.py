#!/usr/bin/env python3
"""Fusiona registros curados y automáticos en el JSON estático del mapa.

Sin dependencias externas: se ejecuta con python3 del sistema en el servidor.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "events" / "2026-11-06" / "events.jsonl"
AUTO = ROOT / "data" / "events" / "auto" / "events.jsonl"
OUT = ROOT / "web" / "assets" / "data" / "events.json"
RELATIONS = ROOT / "data" / "relations.json"


def load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def key(title: str) -> str:
    return " ".join("".join(c.lower() if c.isalnum() or c.isspace() else " " for c in title).split())


def tokens(title: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9áéíóúüñ]{4,}", title.casefold())}


def similar(left: str, right: str) -> bool:
    a, b = tokens(left), tokens(right)
    return bool(a and b and len(a & b) / len(a | b) >= 0.55)


def public_row(row: dict) -> dict:
    """Prepara una ficha pública: sin demo y sin promoción automática."""
    row = {key: value for key, value in row.items() if key != "demo"}
    if row.get("automated") and not row.get("reviewed_by_human"):
        row["verification_status"] = "PENDIENTE"
        row["status_reason"] = (
            "candidato automático; pendiente de revisión humana"
            + (f" · {row['status_reason']}" if row.get("status_reason") else "")
        )
    return row


def merge(curated: list[dict], automatic: list[dict]) -> list[dict]:
    rows = [public_row(row) for row in curated]
    titles = [row["title"] for row in rows]
    urls = {source["url"].split("#")[0].rstrip("/") for row in rows for source in row.get("sources", [])}
    for row in automatic:
        row = public_row(row)
        new_urls = {source["url"].split("#")[0].rstrip("/") for source in row.get("sources", [])}
        if new_urls & urls or key(row["title"]) in {key(title) for title in titles} or any(similar(row["title"], title) for title in titles):
            continue
        rows.append(row)
        titles.append(row["title"])
        urls |= new_urls
    return rows


def _date(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        return None


def valid_dates(row: dict) -> bool:
    """Una ficha pública no puede tener fechas futuras o incoherentes."""
    event = _date(row.get("event_date"))
    published = _date(row.get("published_at"))
    captured = _date(row.get("captured_at"))
    if not event or not published:
        return False
    if event > published:
        return False
    if captured and (event > captured or published > captured):
        return False
    return True


def apply_relations(rows: list[dict], relations: dict) -> list[dict]:
    """Convierte seguimientos en fuentes del hecho principal; no los cuenta como incidentes."""
    by_id = {row.get("id"): row for row in rows}
    out = []
    for row in rows:
        relation = relations.get(row.get("id"))
        if not relation:
            out.append(row)
            continue
        if str(relation.get("type") or "").lower() != "seguimiento":
            out.append(row)
            continue
        parent = by_id.get(relation.get("of"))
        if parent is None:
            print(f"relación sin padre: {row.get('id')} -> {relation.get('of')}", file=sys.stderr)
            out.append(row)
            continue
        follow = parent.setdefault("follow_up_sources", [])
        known = {item.get("url") for item in follow}
        for source in row.get("sources", []):
            if source.get("url") not in known:
                follow.append(source)
        note = relation.get("note") or "seguimiento editorial del mismo patrón"
        parent["observations"] = (parent.get("observations") or "").strip() + f" Seguimiento: {note}"
    return out


def apply_reviews(rows: list[dict], reviews: dict) -> list[dict]:
    out = []
    for row in rows:
        review = reviews.get(row.get("id"))
        if review:
            status = str(review.get("status") or "").upper()
            if status == "RECHAZADO":
                continue
            if status in {"DOCUMENTADO", "PENDIENTE", "CONFIRMADO"}:
                row["verification_status"] = status
                row["reviewed_by_human"] = True
                row["reviewed_at"] = review.get("reviewed_at")
                row["status_reason"] = review.get("note") or "decisión de revisión humana"
        out.append(row)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--curated", type=Path, default=CURATED)
    parser.add_argument("--auto", type=Path, default=AUTO)
    parser.add_argument("--reviews", type=Path, default=ROOT / "data" / "reviews.json")
    parser.add_argument("--relations", type=Path, default=RELATIONS)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    curated = load(args.curated)
    automatic = load(args.auto)
    reviews = json.loads(args.reviews.read_text(encoding="utf-8")) if args.reviews.exists() else {}
    relations = json.loads(args.relations.read_text(encoding="utf-8")) if args.relations.exists() else {}
    rows = apply_reviews(merge(curated, automatic), reviews)
    rows = apply_relations(rows, relations)
    clean = []
    for row in rows:
        if valid_dates(row):
            clean.append(row)
        else:
            print(f"fechas inválidas, cuarentena: {row.get('id')} {row.get('event_date')} / {row.get('published_at')}", file=sys.stderr)
    rows = clean
    if not rows:
        raise SystemExit("datos inválidos: faltan registros")
    generated = datetime.now(timezone.utc).isoformat()
    payload = {"generated_at": generated, "count": len(rows), "events": rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"eventos fusionados: {len(rows)} ({len(curated)} curados, {len(automatic)} automáticos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
