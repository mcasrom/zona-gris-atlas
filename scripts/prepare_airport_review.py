#!/usr/bin/env python3
"""Agrupa candidatos para revisión manual de la línea base de aeropuertos."""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FALSE_TERMS = re.compile(
    r"(like an airport|airport tax|airport lounge|airport hotel|airport expansion|"
    r"airport travel|airport parking|airport transfer|airport code|airport name|airport song|"
    r"detection system|new strategy|documents show|investigates increase|security council|"
    r"search for dog|passenger names bluetooth|threat before bomb scare)",
    re.I,
)
FIELDS = (
    "review_id", "event_date", "airport_suggested", "event_type", "titles", "sources",
    "decision", "airport_final", "date_final", "source_url_final", "duplicate_of", "notes",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "baseline" / "airports-candidates-filtered.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "baseline" / "airports-review.csv")
    args = parser.parse_args()
    groups: dict[tuple, list[dict]] = defaultdict(list)
    with args.input.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            text = f'{row.get("notes", "")} {row.get("source_url", "")}'
            if FALSE_TERMS.search(text):
                continue
            groups[(row["event_date"], row["airport"], row["event_type"])].append(row)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for i, key in enumerate(sorted(groups), 1):
            rows = groups[key]
            writer.writerow({
                "review_id": f"R{i:02d}",
                "event_date": key[0],
                "airport_suggested": key[1],
                "event_type": key[2],
                "titles": " | ".join(dict.fromkeys(r.get("notes", "") for r in rows)),
                "sources": " | ".join(dict.fromkeys(r.get("source_url", "") for r in rows)),
                "decision": "",
                "airport_final": "",
                "date_final": "",
                "source_url_final": "",
                "duplicate_of": "",
                "notes": "",
            })
    print(f"revisión: {len(groups)} grupos → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
