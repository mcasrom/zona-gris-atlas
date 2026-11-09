#!/usr/bin/env python3
"""Actualiza el timestamp estático de la portada desde events.json."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.events.read_text(encoding="utf-8"))
    captured = data.get("generated_at")
    if not captured:
        return 1
    stamp = datetime.fromisoformat(captured.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Madrid"))
    months = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")
    label = f"{stamp.day} {months[stamp.month - 1]} {stamp.year}, {stamp:%H:%M}"
    text = args.html.read_text(encoding="utf-8")
    text = re.sub(r'<time[^>]*data-last-capture[^>]*>[^<]*</time>', f'<time id="last-capture" data-last-capture datetime="{captured}">{label}</time>', text)
    events = data.get("events", [])
    counts = {
        "total": len(events),
        "confirmed": sum(1 for e in events if e.get("verification_status") == "CONFIRMADO"),
        "documented": sum(1 for e in events if e.get("verification_status") == "DOCUMENTADO"),
        "pending": sum(1 for e in events if e.get("verification_status") == "PENDIENTE"),
        "coordinates": sum(1 for e in events if e.get("lat") is not None and e.get("lon") is not None),
        "unlocated": sum(1 for e in events if e.get("lat") is None or e.get("lon") is None),
        "sources": len({s.get("url") for e in events for s in (e.get("sources") or []) if s.get("url")}),
    }
    for key, value in counts.items():
        text = re.sub(rf'(data-stat="{key}"[^>]*>)[^<]*', lambda m, v=value: m.group(1) + str(v), text)
    coverage = f'{counts["coordinates"]} de {counts["total"]} registros tienen ubicación documentada; los demás quedan en la lista, no en el mapa.'
    text = re.sub(r'(id="preview-coverage"[^>]*>)[^<]*', lambda m: m.group(1) + coverage, text)
    args.html.write_text(text, encoding="utf-8")
    print(f"timestamp {label} · {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
