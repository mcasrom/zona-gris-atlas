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
          "source_url", "source_type", "evidence_type", "status", "notes")
VALID_TYPES = {"jamming", "spoofing", "interference"}
VALID_STATUS = {"PENDIENTE", "DOCUMENTADO", "DESCARTADO"}


def main() -> int:
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    if rows and tuple(rows[0]) != FIELDS:
        print("ERROR: columnas inesperadas", tuple(rows[0]), file=sys.stderr)
        return 2
    ids = set()
    months = set()
    status = Counter()
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
        if not row["source_url"].startswith("https://"):
            errors.append(f"línea {n}: URL no https")
        status[row["status"]] += 1
    print(f"N0 · {len(rows)} episodios · {len(months)} meses · {dict(status)}")
    if errors:
        print("\n".join("ERROR " + e for e in errors), file=sys.stderr)
        return 2
    print("N1: cerrado (faltan 50 episodios y 24 meses)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
