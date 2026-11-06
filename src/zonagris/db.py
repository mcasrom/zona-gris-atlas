from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from . import config

SCHEMA = config.ROOT / "db" / "schema.sql"


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    target = Path(path) if path else config.db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA.read_text(encoding="utf-8"))
    connection.commit()


def ensure_source(
    connection: sqlite3.Connection,
    source_id: str,
    name: str,
    url: str,
    source_type: str,
    licence: str | None = None,
    enabled: bool = False,
) -> None:
    connection.execute(
        """
        INSERT INTO sources (id, name, url, source_type, licence, enabled)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            url = excluded.url,
            source_type = excluded.source_type,
            licence = excluded.licence,
            enabled = excluded.enabled
        """,
        (source_id, name, url, source_type, licence, int(enabled)),
    )
    connection.commit()


def insert_raw_item(
    connection: sqlite3.Connection,
    source_id: str,
    url: str,
    title: str,
    text: str | None,
    language: str | None,
    published_at: str | None,
    url_hash: str,
    text_hash: str | None = None,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO raw_items
            (source_id, url, title, text, language, published_at, url_hash, text_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_id, url_hash) DO NOTHING
        """,
        (source_id, url, title, text, language, published_at, url_hash, text_hash),
    )
    connection.commit()
    if cursor.lastrowid:
        return int(cursor.lastrowid)
    row = connection.execute(
        "SELECT id FROM raw_items WHERE source_id = ? AND url_hash = ?",
        (source_id, url_hash),
    ).fetchone()
    return int(row["id"])


def stats(connection: sqlite3.Connection) -> dict[str, Any]:
    queries = {
        "sources": "SELECT COUNT(*) AS n FROM sources",
        "raw_items": "SELECT COUNT(*) AS n FROM raw_items",
        "incidents": "SELECT COUNT(*) AS n FROM incidents",
        "published": "SELECT COUNT(*) AS n FROM incidents WHERE status = 'published'",
        "demo": "SELECT COUNT(*) AS n FROM incidents WHERE demo = 1",
        "attributions": "SELECT COUNT(*) AS n FROM attributions",
    }
    return {name: connection.execute(sql).fetchone()["n"] for name, sql in queries.items()}
