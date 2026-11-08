#!/usr/bin/env python3
"""Extrae solo metadatos públicos de la fuente: fecha y lugar declarados.

No guarda el artículo completo. No infiere si la página no lo declara.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = ROOT / "data" / "quality" / "reviewed" / "enriched.jsonl"
DEFAULT_OUT = ROOT / "data" / "quality" / "source_metadata.json"
UA = "Mozilla/5.0 (compatible; AtlasZonaGris/0.5; +https://zonagris.pruebapublica.com/metodologia.html)"
MAX_BYTES = 1_500_000
PATTERNS = (
    re.compile(r'<meta[^>]+(?:property|name)=["\'](?:article:published_time|datePublished|date|pubdate|publish-date|dc\.date)["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:article:published_time|datePublished|date|pubdate|publish-date|dc\.date)["\']', re.I),
    re.compile(r'"datePublished"\s*:\s*"([^"]+)"', re.I),
    re.compile(r'<time[^>]+datetime=["\']([^"\']+)', re.I),
)


def fetch(url: str) -> tuple[int | None, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:  # nosec B310
            return response.status, response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as exc:
        return exc.code, b""
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None, b""


def parse_timestamp(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return None


def extract(html: bytes) -> dict:
    text = html.decode("utf-8", "replace")
    published = None
    for pattern in PATTERNS:
        match = pattern.search(text)
        if match:
            published = parse_timestamp(match.group(1))
            if published:
                break
    location = None
    for pattern in (
        re.compile(r'<meta[^>]+(?:property|name)=["\'](?:og:locality|geo\.placename|article:location)["\'][^>]+content=["\']([^"\']+)', re.I),
        re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:locality|geo\.placename|article:location)["\']', re.I),
    ):
        match = pattern.search(text)
        if match:
            location = " ".join(match.group(1).split())[:120]
            break
    return {"published_at": published, "time_precision": "timestamp" if published and "T" in published else ("day" if published else None), "location_hint": location}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="source", type=Path, default=DEFAULT_IN)
    parser.add_argument("--out", dest="out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.source.read_text(encoding="utf-8").splitlines() if line.strip()]
    tasks = []
    for row in rows:
        sources = row.get("sources") or []
        if sources:
            tasks.append((row.get("event_id"), sources[0].get("url")))
    result = {}
    def work(item: tuple[str, str]) -> tuple[str, str, dict]:
        event_id, url = item
        status, body = fetch(url)
        meta = extract(body) if body else {"published_at": None, "time_precision": None, "location_hint": None}
        return event_id, url, {"http": status, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **meta}
    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 10))) as pool:
        futures = [pool.submit(work, task) for task in tasks]
        for future in as_completed(futures):
            event_id, url, meta = future.result()
            result[event_id] = {"url": url, **meta}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with_ts = sum(1 for x in result.values() if x.get("published_at"))
    with_loc = sum(1 for x in result.values() if x.get("location_hint"))
    print(f"fuentes {len(result)} · con timestamp {with_ts} · con lugar {with_loc} → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
