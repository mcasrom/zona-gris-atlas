#!/usr/bin/env python3
"""Filtra candidatos de aeropuerto para revisión humana.

No los convierte en eventos: elimina falsos positivos evidentes y propone
aeropuerto/país cuando el titular contiene un alias del gazetteer.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACES = ROOT / "data" / "event_places.json"
EVENT_TERMS = re.compile(r"\b(bomb|threat|drone|evacuat|security scare|suspicious package)\b", re.I)
FALSE_TERMS = re.compile(
    r"(like an airport|airport tax|airport lounge|airport hotel|airport expansion|"
    r"airport travel|airport parking|airport transfer|airport code|airport name|airport song)",
    re.I,
)


def load_places() -> list[dict]:
    return json.loads(PLACES.read_text(encoding="utf-8"))["places"]


def match_place(text: str, places: list[dict]) -> dict | None:
    low = text.casefold()
    hits = []
    for place in places:
        names = [place["name"], *place.get("aliases", [])]
        for name in names:
            if re.search(r"(?<!\w)" + re.escape(name.casefold()) + r"(?!\w)", low):
                hits.append(place)
                break
    return max(hits, key=lambda p: len(p["name"])) if hits else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "baseline" / "airports-candidates-google.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "baseline" / "airports-candidates-filtered.csv")
    args = parser.parse_args()
    places = load_places()
    rows = []
    with args.input.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            text = f'{row.get("notes", "")} {row.get("source_url", "")}'
            if not EVENT_TERMS.search(text) or FALSE_TERMS.search(text):
                continue
            place = match_place(text, places)
            if place is None:
                continue
            row["airport"] = place.get("name") or place.get("place")
            row["country"] = place.get("country") or ""
            row["notes"] = f'{row.get("notes", "")} · sugerido por gazetteer'
            rows.append(row)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys() if rows else ["event_id"])
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (r["event_date"], r["event_id"])))
    print(f"filtrados: {len(rows)} · {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
