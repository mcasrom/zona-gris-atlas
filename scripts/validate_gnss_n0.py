#!/usr/bin/env python3
"""Valida el inventario GNSS N0. No es una puerta N1."""
from __future__ import annotations
import csv
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "baseline" / "gnss-n0.csv"
FIELDS = ("inventory_id", "event_date", "region", "country", "place", "event_type",
          "record_type", "source_url", "source_type", "evidence_type", "status", "notes")
VALID_TYPES = {"jamming", "spoofing", "interference"}
VALID_STATUS = {"PENDIENTE", "DOCUMENTADO", "DESCARTADO"}
VALID_RECORD = {"episode", "aggregate", "alert"}


def main() -> int:
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    if rows and tuple(rows[0]) != FIELDS:
        print("ERROR: columnas inesperadas", tuple(rows[0]), file=sys.stderr)
        return 2
    ids = set()
    months = set()
    status = Counter()
    record = Counter()
    errors = []
    for n, row in enumerate(rows, 2):
        rid = row["inventory_id"].strip()
        if not rid or rid in ids:
            errors.append(f"línea {n}: id vacío o duplicado")
        ids.add(rid)
        try:
            months.add(date.fromisoformat(row["event_date"]).strftime("%Y-%m"))
        except ValueError:
            errors.append(f"línea {n}: fecha inválida")
        if row["event_type"] not in VALID_TYPES:
            errors.append(f"línea {n}: tipo inválido")
        if row["status"] not in VALID_STATUS:
            errors.append(f"línea {n}: estado inválido")
        if row["record_type"] not in VALID_RECORD:
            errors.append(f"línea {n}: record_type inválido")
        record[row["record_type"]] += 1
        if not row["source_url"].startswith("https://"):
            errors.append(f"línea {n}: URL no https")
        status[row["status"]] += 1
    episodes = sum(1 for r in rows if r["record_type"] == "episode" and r["status"] == "DOCUMENTADO")
    print(f"N0 · {len(rows)} registros · {episodes} episodios documentados · {dict(record)} · {len(months)} meses")
    if errors:
        print("\n".join("ERROR " + e for e in errors), file=sys.stderr)
        return 2
    print(f"N1: cerrado ({episodes}/50 episodios; {len(months)}/24 meses)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
