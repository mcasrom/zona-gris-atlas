#!/usr/bin/env python3
"""Distribución temporal de la capa interna; no publica."""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "quality" / "reviewed" / "enriched_sources.jsonl"
OUT = ROOT / "data" / "quality" / "reviewed"


def main() -> int:
    rows = [json.loads(line) for line in IN.read_text(encoding="utf-8").splitlines() if line.strip()]
    zones = ZoneInfo("Europe/Madrid")
    by_day, by_hour, by_cat = Counter(), Counter(), Counter()
    for row in rows:
        value = row.get("published_at_utc")
        if not value:
            continue
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(zones)
        except ValueError:
            continue
        by_day[dt.date().isoformat()] += 1
        by_hour[f"{dt.hour:02d}:00"] += 1
        by_cat[row.get("incident_type")] += 1
    report = {
        "records_with_timestamp": sum(by_day.values()),
        "by_day": dict(sorted(by_day.items())),
        "by_hour_madrid": dict(sorted(by_hour.items())),
        "by_category": dict(by_cat),
        "note": "hora de publicación de la fuente; no hora del hecho",
    }
    (OUT / "time_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Distribución temporal", "", f"Registros con timestamp: **{report['records_with_timestamp']}**", "", "## Por día", ""]
    lines += [f"- {k}: {v}" for k, v in report["by_day"].items()]
    lines += ["", "## Por hora (Madrid)", ""]
    lines += [f"- {k}: {v}" for k, v in report["by_hour_madrid"].items()]
    lines += ["", "> Es hora de publicación de la fuente, no hora del hecho.", ""]
    (OUT / "time_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(report["records_with_timestamp"], report["by_day"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
