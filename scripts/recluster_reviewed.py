#!/usr/bin/env python3
"""Recalcula canónicos y grafo usando solo correcciones revisadas."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from quality_report import cluster

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "quality" / "events_reviewed.jsonl"
OUT = ROOT / "data" / "quality" / "reviewed"


def main() -> int:
    rows = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
    items = []
    for row in rows:
        item = dict(row)
        item["category"] = row.get("incident_type")
        item["event_date"] = row.get("event_date")
        item["country"] = row.get("country")
        item["title"] = row.get("title")
        item["description"] = row.get("description")
        item["sources"] = row.get("sources") or []
        items.append(item)
    groups = cluster(items, 0.40)
    canonical_by_index = {}
    canonical_rows = []
    for group in groups:
        seed = min(items[i].get("event_id") or "" for i in group)
        canonical = "CAN-" + hashlib.sha256(seed.encode()).hexdigest()[:10].upper()
        for i in group:
            canonical_by_index[i] = canonical
        canonical_rows.append({
            "canonical_event_id": canonical,
            "event_ids": [items[i].get("event_id") for i in group],
            "titles": [items[i].get("title") for i in group],
            "category": items[group[0]].get("incident_type"),
            "first_date": min(items[i].get("event_date") or "" for i in group),
            "last_date": max(items[i].get("event_date") or "" for i in group),
            "records": len(group),
        })
    for i, item in enumerate(items):
        item["canonical_event_id"] = canonical_by_index[i]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "events.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in items) + "\n", encoding="utf-8"
    )
    (OUT / "canonical_events.json").write_text(
        json.dumps(canonical_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "records": len(items),
        "canonical_events": len(groups),
        "duplicates_collapsed": len(items) - len(groups),
        "accepted_corrections": sum(1 for x in rows if x.get("reviewed_fields")),
        "groups_with_multiple_records": sum(1 for g in groups if len(g) > 1),
    }
    (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"revisado: {report['records']} registros · {report['canonical_events']} canónicos · {report['accepted_corrections']} corregidos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
