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
    args.html.write_text(text, encoding="utf-8")
    print(f"timestamp {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
