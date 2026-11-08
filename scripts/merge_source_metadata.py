#!/usr/bin/env python3
"""Une metadatos de fuente al registro enriquecido. No cambia el mapa público."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "quality" / "reviewed" / "enriched.jsonl"
META = ROOT / "data" / "quality" / "source_metadata.json"
OUT = ROOT / "data" / "quality" / "reviewed" / "enriched_sources.jsonl"
REPORT = ROOT / "data" / "quality" / "reviewed" / "source_report.json"


def main() -> int:
    rows = [json.loads(line) for line in IN.read_text(encoding="utf-8").splitlines() if line.strip()]
    meta = json.loads(META.read_text(encoding="utf-8"))
    for row in rows:
        item = meta.get(row.get("event_id"), {})
        row["source_url"] = item.get("url")
        row["source_http"] = item.get("http")
        row["source_published_at"] = item.get("published_at")
        row["source_time_precision"] = item.get("time_precision")
        row["source_location_hint"] = item.get("location_hint")
        if item.get("published_at"):
            row["published_at_utc"] = item["published_at"]
            row["time_precision"] = item["time_precision"]
        row["analysis_ready"] = bool(row.get("published_at_utc") and row.get("country_iso2"))
    OUT.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n", encoding="utf-8")
    report = {
        "records": len(rows),
        "with_source_timestamp": sum(1 for x in rows if x.get("source_published_at")),
        "with_source_location": sum(1 for x in rows if x.get("source_location_hint")),
        "with_country_iso2": sum(1 for x in rows if x.get("country_iso2")),
        "with_airport_iata": sum(1 for x in rows if x.get("airport_iata")),
        "with_timestamp": sum(1 for x in rows if x.get("published_at_utc")),
        "time_precision": dict(Counter(x.get("time_precision") for x in rows)),
        "analysis_ready": sum(1 for x in rows if x.get("analysis_ready")),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
