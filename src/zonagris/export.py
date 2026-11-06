from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from . import config

ATOM_NS = "http://www.w3.org/2005/Atom"


def _attributions(connection: sqlite3.Connection, incident_id: str) -> list[dict]:
    rows = connection.execute(
        """
        SELECT status, attributed_by, attributed_by_type, source_url, confidence, quote
        FROM attributions WHERE incident_id = ? ORDER BY id
        """,
        (incident_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def _sources(connection: sqlite3.Connection, incident_id: str) -> list[dict]:
    rows = connection.execute(
        """
        SELECT r.title, r.url, r.published_at
        FROM incident_items i JOIN raw_items r ON r.id = i.raw_item_id
        WHERE i.incident_id = ? ORDER BY r.published_at DESC
        """,
        (incident_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def load_incidents(connection: sqlite3.Connection, published_only: bool = True) -> list[dict]:
    if published_only:
        query = """SELECT id, title, summary, domain, scale_position, severity, reality,
                   lat, lon, place, country_iso2, event_date, status, demo,
                   reviewed_by_human, reviewed_at
                   FROM incidents WHERE status = 'published'
                   ORDER BY event_date DESC, id DESC"""
    else:
        query = """SELECT id, title, summary, domain, scale_position, severity, reality,
                   lat, lon, place, country_iso2, event_date, status, demo,
                   reviewed_by_human, reviewed_at
                   FROM incidents
                   ORDER BY event_date DESC, id DESC"""
    rows = connection.execute(query).fetchall()
    incidents = []
    for row in rows:
        item = dict(row)
        item["demo"] = bool(item["demo"])
        item["reviewed_by_human"] = bool(item["reviewed_by_human"])
        item["attributions"] = _attributions(connection, item["id"])
        item["sources"] = _sources(connection, item["id"])
        incidents.append(item)
    return incidents


def write_json(connection: sqlite3.Connection, out_path: Path) -> list[dict]:
    incidents = load_incidents(connection)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "demo": all(item["demo"] for item in incidents) if incidents else False,
        "count": len(incidents),
        "incidents": incidents,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return incidents


def write_atom(connection: sqlite3.Connection, out_path: Path) -> None:
    incidents = load_incidents(connection)
    site = config.site()
    updated = datetime.now(timezone.utc).isoformat()
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<feed xmlns="{ATOM_NS}">',
        f"  <title>{escape(site.get('title', 'Zona Gris'))}</title>",
        f"  <link href=\"{escape(site.get('url', ''))}\"/>",
        f"  <updated>{updated}</updated>",
        f"  <id>{escape(site.get('url', '') + '/feed.xml')}</id>",
        "  <author><name>Miguel</name></author>",
    ]
    for incident in incidents:
        url = f"{site.get('url', '').rstrip('/')}/mapa.html#{incident['id']}"
        lines.extend(
            [
                "  <entry>",
                f"    <title>{escape(incident['title'])}</title>",
                f"    <id>{escape(url)}</id>",
                f"    <link href=\"{escape(url)}\"/>",
                f"    <updated>{escape(incident['event_date'])}T00:00:00Z</updated>",
                f"    <summary>{escape(incident['summary'])}</summary>",
                "  </entry>",
            ]
        )
    lines.append("</feed>")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
