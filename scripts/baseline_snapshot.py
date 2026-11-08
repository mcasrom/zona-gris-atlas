#!/usr/bin/env python3
"""Foto diaria interna para construir una línea base histórica real."""
from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = ROOT / "data" / "quality" / "reviewed" / "enriched_sources.jsonl"
DEFAULT_CANONICAL = ROOT / "data" / "quality" / "reviewed" / "canonical_events.json"
DEFAULT_OUT = ROOT / "data" / "quality" / "baseline"


def load_rows(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        payload = json.loads(text)
        return payload.get("events", payload) if isinstance(payload, dict) else payload
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--canonical", type=Path, default=DEFAULT_CANONICAL)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    rows = load_rows(args.events)
    try:
        canonical = json.loads(args.canonical.read_text(encoding="utf-8")) if args.canonical.exists() else None
    except (OSError, ValueError):
        canonical = None
    snapshot = {
        "snapshot_date": date.today().isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_window": {
            "first_event_date": min((x.get("event_date") or "") for x in rows),
            "last_event_date": max((x.get("event_date") or "") for x in rows),
        },
        "records": len(rows),
        "canonical_events": len(canonical) if canonical is not None else None,
        "by_status": dict(Counter(x.get("verification_status") for x in rows)),
        "by_category": dict(Counter((x.get("incident_type") or x.get("category")) for x in rows)),
        "by_event_date": dict(sorted(Counter(x.get("event_date") for x in rows).items())),
        "with_timestamp": sum(1 for x in rows if x.get("published_at_utc")),
        "with_country": sum(1 for x in rows if x.get("country_iso2")),
        "with_airport": sum(1 for x in rows if x.get("airport_iata")),
        "note": "una sola foto no es una línea base; se necesita acumulación diaria",
    }
    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / f"{snapshot['snapshot_date']}.json"
    target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    existing = set()
    history = args.out / "history.jsonl"
    if history.exists():
        for line in history.read_text(encoding="utf-8").splitlines():
            try:
                existing.add(json.loads(line).get("snapshot_date"))
            except ValueError:
                pass
    if snapshot["snapshot_date"] not in existing:
        with history.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(snapshot, ensure_ascii=False) + "\n")
    print(f"snapshot {target} · {snapshot['records']} registros · {snapshot['canonical_events']} canónicos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
