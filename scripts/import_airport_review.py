#!/usr/bin/env python3
"""Fusiona respuestas manuales de aeropuertos con la semilla, sin duplicar."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("event_id", "event_date", "published_at", "airport", "country", "event_type",
          "source_url", "source_type", "independent_group", "status", "notes")


def domain(url: str) -> str:
    return (urlsplit(url).hostname or "").lower().removeprefix("www.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviews", type=Path, default=ROOT / "docs" / "airports-review_answer.csv")
    parser.add_argument("--seed", type=Path, default=ROOT / "data" / "baseline" / "airports.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "baseline" / "airports-reviewed.csv")
    args = parser.parse_args()
    rows = list(csv.DictReader(args.seed.open(encoding="utf-8"))) if args.seed.exists() else []
    seen = {(r["event_date"], r["airport"], r["event_type"]) for r in rows}
    accepted = duplicates = rejected = missing_piece = 0
    for review in csv.DictReader(args.reviews.open(encoding="utf-8")):
        decision = review["decision"].strip().upper()
        if decision == "DUPLICADO":
            duplicates += 1
            continue
        if decision != "ACEPTAR":
            rejected += 1
            continue
        accepted += 1
        url = review["source_url_final"].strip()
        if urlsplit(url).path in ("", "/"):
            missing_piece += 1
        row = {
            "event_id": f"REV-{review['review_id']}",
            "event_date": (review["date_final"] or review["event_date"]).strip(),
            "published_at": (review["date_final"] or review["event_date"]).strip(),
            "airport": review["airport_final"].strip(),
            "country": "",
            "event_type": review["event_type"].strip(),
            "source_url": url,
            "source_type": "news",
            "independent_group": domain(url),
            "status": "DOCUMENTADO",
            "notes": "revisión manual" + ("; fuente=dominio, falta URL de pieza" if urlsplit(url).path in ("", "/") else ""),
        }
        key = (row["event_date"], row["airport"], row["event_type"])
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        rows.append(row)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (r["event_date"], r["event_id"])))
    print(f"aceptados={accepted} duplicados={duplicates} rechazados={rejected} sin_pieza={missing_piece} total={len(rows)} → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
