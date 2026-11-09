#!/usr/bin/env python3
"""Descubre candidatos históricos para la línea base de aeropuertos.

GDELT se usa solo para descubrimiento. Ningún candidato entra en la línea base
hasta revisión humana; el CSV queda con status=CANDIDATO.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parents[1]
GDELT = "https://api.gdeltproject.org/api/v2/doc/doc"
WINDOWS = [
    ("20241101000000", "20250501000000"),
    ("20250501000000", "20251101000000"),
    ("20251101000000", "20260501000000"),
    ("20260501000000", "20261101000000"),
]
QUERY = '"airport" ("bomb threat" OR "bomb scare" OR "drone" OR "evacuated")'

FIELDS = ("event_id", "event_date", "published_at", "airport", "country", "event_type",
          "source_url", "source_type", "independent_group", "status", "notes")


def _event_id(url: str) -> str:
    return "GDELT-" + hashlib.sha256(url.encode("utf-8")).hexdigest()[:12].upper()


def _date(seendate: str) -> str:
    return datetime.strptime(seendate[:8], "%Y%m%d").date().isoformat()


def fetch(window: tuple[str, str], query: str, kind: str, max_records: int) -> list[dict]:
    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": str(max_records),
        "format": "json",
        "startdatetime": window[0],
        "enddatetime": window[1],
        "sort": "hybridrel",
    }
    response = requests.get(GDELT, params=params, timeout=40,
                            headers={"User-Agent": "AtlasZonaGris/0.1 (baseline discovery)"})
    if response.status_code == 429:
        time.sleep(10)
        response = requests.get(GDELT, params=params, timeout=40,
                                headers={"User-Agent": "AtlasZonaGris/0.1 (baseline discovery)"})
    response.raise_for_status()
    try:
        payload = response.json()
    except ValueError:
        return []
    rows = []
    for item in payload.get("articles", []):
        url = item.get("url") or ""
        title = item.get("title") or ""
        seendate = item.get("seendate") or ""
        if not url or not seendate:
            continue
        rows.append({
            "event_id": _event_id(url),
            "event_date": _date(seendate),
            "published_at": _date(seendate),
            "airport": "",
            "country": "",
            "event_type": kind,
            "source_url": url,
            "source_type": "news",
            "independent_group": (url.split("/")[2].lower() if "://" in url else ""),
            "status": "CANDIDATO",
            "notes": f"GDELT · {title[:240]}",
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "baseline" / "airports-candidates.csv")
    parser.add_argument("--max-records", type=int, default=250)
    parser.add_argument("--sleep", type=float, default=6.0)
    args = parser.parse_args()
    rows: dict[str, dict] = {}
    for window in WINDOWS:
        try:
            for row in fetch(window, QUERY, "airport", args.max_records):
                rows.setdefault(row["event_id"], row)
        except Exception as exc:
            print(f"aviso {window}: {exc}")
        time.sleep(args.sleep)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sorted(rows.values(), key=lambda r: (r["event_date"], r["event_id"])))
    print(f"candidatos: {len(rows)} · {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
