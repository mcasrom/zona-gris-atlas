from __future__ import annotations

import sqlite3
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET  # nosec B405

from .. import config
from ..db import ensure_source, insert_raw_item
from ..dedupe import text_hash, url_hash


def allowed_by_robots(url: str) -> bool:
    parsed = urllib.parse.urlsplit(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except OSError:
        return True
    return parser.can_fetch(config.user_agent(), url)


def fetch(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("solo se permiten URLs http/https")
    request = urllib.request.Request(url, headers={"User-Agent": config.user_agent()})
    with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310
        return response.read().decode("utf-8", "replace")


def parse_feed(payload: str) -> list[dict]:
    try:
        root = ET.fromstring(payload.encode("utf-8"))  # nosec B314
    except ET.ParseError:
        return []
    items = []
    for item in root.findall(".//item"):
        items.append(
            {
                "title": item.findtext("title") or "",
                "url": item.findtext("link") or "",
                "published": item.findtext("pubDate"),
                "text": item.findtext("description") or "",
            }
        )
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall(".//atom:entry", ns):
        link = entry.find("atom:link", ns)
        items.append(
            {
                "title": entry.findtext("atom:title", default="", namespaces=ns),
                "url": link.get("href", "") if link is not None else "",
                "published": entry.findtext("atom:updated", default=None, namespaces=ns),
                "text": entry.findtext("atom:summary", default="", namespaces=ns),
            }
        )
    return items


def ingest(connection: sqlite3.Connection) -> int:
    inserted = 0
    for source in config.sources().get("sources", []):
        if not source.get("enabled") or source.get("type") != "rss":
            continue
        source_id = source["id"]
        url = source["url"]
        if not allowed_by_robots(url):
            print(f"rss: {source_id}: robots.txt no permite la lectura")
            continue
        ensure_source(
            connection,
            source_id,
            source["name"],
            url,
            "rss",
            licence=source.get("licencia"),
            enabled=True,
        )
        for item in parse_feed(fetch(url)):
            if not item["url"] or not item["title"]:
                continue
            before = connection.total_changes
            insert_raw_item(
                connection,
                source_id,
                item["url"],
                item["title"],
                item["text"],
                None,
                item["published"],
                url_hash(item["url"]),
                text_hash(item["text"] or item["title"]),
            )
            if connection.total_changes > before:
                inserted += 1
    return inserted
