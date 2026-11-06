from __future__ import annotations

import difflib
import hashlib
import re
import sqlite3
from typing import Iterable


def normalize_text(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"https?://\S+", " ", value)
    value = re.sub(r"[^\wáéíóúüñ]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def url_hash(url: str) -> str:
    canonical = url.strip().split("#", 1)[0].rstrip("/")
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def text_hash(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def similarity(left: str, right: str) -> float:
    return difflib.SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio()


def find_duplicate(
    connection: sqlite3.Connection,
    url: str,
    text: str,
    threshold: float = 0.92,
) -> int | None:
    row = connection.execute(
        "SELECT id FROM raw_items WHERE url_hash = ? LIMIT 1",
        (url_hash(url),),
    ).fetchone()
    if row:
        return int(row["id"])

    needle = normalize_text(text)
    if not needle:
        return None
    for candidate in connection.execute("SELECT id, text FROM raw_items WHERE text IS NOT NULL"):
        if candidate["text"] and similarity(needle, candidate["text"]) >= threshold:
            return int(candidate["id"])
    return None


def dedupe_rows(rows: Iterable[dict], threshold: float = 0.92) -> list[dict]:
    kept: list[dict] = []
    for row in rows:
        title = row.get("title") or row.get("text") or ""
        if any(similarity(title, other.get("title") or other.get("text") or "") >= threshold for other in kept):
            continue
        kept.append(row)
    return kept
