#!/usr/bin/env python3
"""Construye una línea base mensual a partir de eventos auditados.

No publica nada: escribe un JSON interno y se niega a declarar baseline si no
hay meses/eventos suficientes.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "event_id", "event_date", "published_at", "airport", "country",
    "event_type", "source_url", "source_type", "independent_group", "status", "notes",
)


def _date(value: str) -> date:
    return date.fromisoformat(value.strip())


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [field for field in FIELDS if field not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"faltan columnas: {', '.join(missing)}")
        return [row for row in reader if row.get("event_id")]


def build(rows: list[dict], *, domain: str, min_months: int, min_events: int) -> dict:
    seen: set[str] = set()
    events: list[dict] = []
    for row in rows:
        event_id = row["event_id"].strip()
        if not event_id or event_id in seen:
            continue
        if row.get("status", "").strip().upper() not in {"DOCUMENTADO", "CORROBORADO", "CONFIRMADO"}:
            continue
        event_date = _date(row["event_date"])
        published = _date(row["published_at"]) if row.get("published_at") else event_date
        if event_date > published:
            continue
        seen.add(event_id)
        events.append({**row, "event_date": event_date.isoformat(), "_month": event_date.strftime("%Y-%m")})

    monthly = Counter(event["_month"] for event in events)
    months = sorted(monthly)
    groups = {event.get("independent_group", "").strip() for event in events if event.get("independent_group", "").strip()}
    n = len(events)
    values = list(monthly.values())
    median = round(statistics.median(values), 2) if values else None
    iqr = round(statistics.quantiles(values, n=4)[2] - statistics.quantiles(values, n=4)[0], 2) if len(values) >= 4 else 0.0
    ready = n >= min_events and len(months) >= min_months and len(groups) >= 2
    reason = "ok" if ready else (
        f"insuficiente: {n}/{min_events} eventos, {len(months)}/{min_months} meses, "
        f"{len(groups)} grupos de fuente"
    )
    return {
        "domain": domain,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready" if ready else "insufficient",
        "reason": reason,
        "criteria": {"min_events": min_events, "min_months": min_months, "min_independent_groups": 2},
        "n_events": n,
        "months_covered": len(months),
        "first_month": months[0] if months else None,
        "last_month": months[-1] if months else None,
        "monthly_counts": dict(sorted(monthly.items())),
        "median_monthly": median,
        "iqr_monthly": iqr,
        "independent_groups": sorted(groups),
        "note": "Una línea base no es una predicción; los seguimientos y agregados no cuentan como eventos.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--domain", default="airports")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "baseline" / "airports-baseline.json")
    parser.add_argument("--min-months", type=int, default=24)
    parser.add_argument("--min-events", type=int, default=50)
    args = parser.parse_args()
    rows = load(args.input)
    result = build(rows, domain=args.domain, min_months=args.min_months, min_events=args.min_events)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']} · {result['reason']} · {args.out}")
    return 0 if result["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
