#!/usr/bin/env python3
"""Descubre candidatos históricos en Google News RSS.

No son eventos: quedan como CANDIDATO y exigen revisión humana. Google News se
usa para localizar piezas; el enlace de la fuente se conserva cuando existe.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("event_id", "event_date", "published_at", "airport", "country", "event_type",
          "source_url", "source_type", "independent_group", "status", "notes")
QUERIES = {
    "bomb": 'airport bomb threat',
    "drone": 'airport drone',
    "evacuation": 'airport evacuation',
}
WINDOWS = [
    ("2024-11-01", "2025-02-01"), ("2025-02-01", "2025-05-01"),
    ("2025-05-01", "2025-08-01"), ("2025-08-01", "2025-11-01"),
    ("2025-11-01", "2026-02-01"), ("2026-02-01", "2026-05-01"),
    ("2026-05-01", "2026-08-01"), ("2026-08-01", "2026-11-01"),
]


def _id(url: str) -> str:
    return "GNEWS-" + hashlib.sha256(url.encode()).hexdigest()[:12].upper()


def fetch(query: str, start: str, end: str) -> list[dict]:
    q = f'{query} after:{start} before:{end}'
    url = "https://news.google.com/rss/search"
    response = requests.get(url, params={"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"},
                            headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    rows = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        source_node = item.find("source")
        source_url = source_node.get("url") if source_node is not None else ""
        try:
            published = parsedate_to_datetime(pub).date().isoformat()
        except (TypeError, ValueError):
            continue
        if not title or not link:
            continue
        url_source = source_url or link
        rows.append({
            "event_id": _id(url_source + "|" + title),
            "event_date": published,
            "published_at": published,
            "airport": "",
            "country": "",
            "event_type": "airport",
            "source_url": url_source,
            "source_type": "news",
            "independent_group": (url_source.split("/")[2].lower() if "://" in url_source else ""),
            "status": "CANDIDATO",
            "notes": f"Google News · {title[:240]}",
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "baseline" / "airports-candidates-google.csv")
    parser.add_argument("--sleep", type=float, default=1.5)
    args = parser.parse_args()
    rows: dict[str, dict] = {}
    for start, end in WINDOWS:
        for kind, query in QUERIES.items():
            try:
                for row in fetch(query, start, end):
                    row["event_type"] = kind
                    rows.setdefault(row["event_id"], row)
            except Exception as exc:
                print(f"aviso {start}/{kind}: {exc}")
            time.sleep(args.sleep)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sorted(rows.values(), key=lambda row: (row["event_date"], row["event_id"])))
    print(f"candidatos: {len(rows)} · {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
