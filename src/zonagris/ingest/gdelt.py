from __future__ import annotations

import hashlib
import json
import sqlite3
import time
import urllib.parse
import urllib.request
from pathlib import Path

from .. import config
from ..db import ensure_source, insert_raw_item
from ..dedupe import text_hash, url_hash

DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
SOURCE_ID = "gdelt"


def build_url(query: str, maxrecords: int = 50, timespan: str = "24h") -> str:
    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "maxrecords": str(max(1, min(maxrecords, 250))),
        "timespan": timespan,
        "sort": "datedesc",
    }
    return f"{DOC_API}?{urllib.parse.urlencode(params)}"


def fetch(url: str, cache_dir: Path | None = None) -> str:
    target_dir = cache_dir or config.cache_dir() / "gdelt"
    target_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]
    cached = target_dir / f"{key}.json"
    if cached.exists():
        return cached.read_text(encoding="utf-8")
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("solo se permiten URLs http/https")
    request = urllib.request.Request(url, headers={"User-Agent": config.user_agent()})
    with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310
        payload = response.read().decode("utf-8", "replace")
    cached.write_text(payload, encoding="utf-8")
    return payload


def parse_payload(payload: str) -> list[dict]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return []
    articles = data.get("articles") or []
    return [a for a in articles if a.get("url") and a.get("title")]


def ingest(
    connection: sqlite3.Connection,
    query: str,
    maxrecords: int = 50,
    timespan: str = "24h",
    rate_limit: float = 2.0,
) -> int:
    ensure_source(
        connection,
        SOURCE_ID,
        "GDELT DOC API",
        DOC_API,
        "api",
        licence="[DECIDIR]",
        enabled=False,
    )
    url = build_url(query, maxrecords, timespan)
    payload = fetch(url)
    inserted = 0
    for article in parse_payload(payload):
        title = (article.get("title") or "").strip()
        link = (article.get("url") or "").strip()
        if not title or not link:
            continue
        published = article.get("seendate") or None
        language = article.get("language") or None
        before = connection.total_changes
        insert_raw_item(
            connection,
            SOURCE_ID,
            link,
            title,
            title,
            language,
            published,
            url_hash(link),
            text_hash(title),
        )
        if connection.total_changes > before:
            inserted += 1
    time.sleep(max(0.0, rate_limit))
    return inserted
