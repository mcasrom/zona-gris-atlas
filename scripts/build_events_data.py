#!/usr/bin/env python3
"""Fusiona registros curados y automáticos en el JSON estático del mapa.

Sin dependencias externas: se ejecuta con python3 del sistema en el servidor.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "events" / "2026-11-06" / "events.jsonl"
AUTO = ROOT / "data" / "events" / "auto" / "events.jsonl"
OUT = ROOT / "web" / "assets" / "data" / "events.json"


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--curated", type=Path, default=CURATED)
    parser.add_argument("--auto", type=Path, default=AUTO)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    curated = load(args.curated)
    automatic = load(args.auto)
    rows = merge(curated, automatic)
    if not rows:
        raise SystemExit("datos inválidos: faltan registros")
    generated = max((row.get("captured_at") or "" for row in rows), default="") or datetime.now(timezone.utc).isoformat()
    payload = {"generated_at": generated, "count": len(rows), "events": rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"eventos fusionados: {len(rows)} ({len(curated)} curados, {len(automatic)} automáticos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
