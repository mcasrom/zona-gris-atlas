from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "data" / "events" / "2026-11-06" / "events.jsonl"
WEB = ROOT / "web" / "assets" / "data" / "events.json"
STATUSES = {"CONFIRMADO", "DOCUMENTADO", "PENDIENTE", "DESCARTADO"}
CATEGORIES = {
    "drones_aeropuertos",
    "amenazas_bomba",
    "ciberataque",
    "ferroviario",
    "gnss",
    "proteccion_civil",
}


def load() -> list[dict]:
    return [json.loads(line) for line in EVENTS.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_real_events_are_complete_and_deduplicated() -> None:
    rows = load()
    assert len(rows) == 16
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids))
    assert {row["category"] for row in rows} >= {"drones_aeropuertos", "amenazas_bomba", "ciberataque", "ferroviario", "gnss"}
    assert all(row["demo"] is False for row in rows)
    assert all(row["verification_status"] in STATUSES for row in rows)
    assert all(row["category"] in CATEGORIES for row in rows)
    assert {row["verification_status"] for row in rows} == {"DOCUMENTADO", "PENDIENTE"}


def test_each_record_has_a_source_and_defensible_location() -> None:
    for row in load():
        assert row["sources"], row["id"]
        assert row["title"] and row["description"] and row["event_date"], row["id"]
        assert all(source["url"].startswith("https://") for source in row["sources"])
        assert "example.org" not in json.dumps(row)
        if row["lat"] is None:
            assert row["lon"] is None
            assert row["geo_precision"] is None
        else:
            assert -90 <= row["lat"] <= 90
            assert -180 <= row["lon"] <= 180
            assert row["geo_precision"] in {"city", "region"}


def test_map_data_is_generated_from_real_records_only() -> None:
    payload = json.loads(WEB.read_text(encoding="utf-8"))
    assert payload["demo"] is False
    assert payload["count"] == 16
    assert len(payload["events"]) == 16
    assert all(event["demo"] is False for event in payload["events"])
    assert not any("EJ-" in event["id"] for event in payload["events"])


def test_map_page_uses_real_events_and_keeps_demo_out() -> None:
    page = (ROOT / "web" / "mapa.html").read_text(encoding="utf-8")
    assert 'assets/data/events.json' not in page  # la carga la hace map.js
    script = (ROOT / "web" / "assets" / "js" / "map.js").read_text(encoding="utf-8")
    assert "assets/data/events.json" in script
    assert "incidents.json" not in script
    assert 'id="filter-date"' in page
    assert 'id="filter-category"' in page
    assert 'id="filter-country"' in page
    assert 'id="filter-status"' in page
    assert 'noindex' not in page
    demo = (ROOT / "web" / "demo.html").read_text(encoding="utf-8")
    assert 'noindex' in demo


def test_public_surfaces_do_not_present_military_promotions() -> None:
    for name in ("index.html", "mapa.html", "feed.xml"):
        text = (ROOT / "web" / name).read_text(encoding="utf-8").lower()
        assert "general de división" not in text
        assert "promoción al empleo" not in text
        assert "ascenso" not in text
        assert "adenda del mando de apoyo logístico" not in text
    registros = (ROOT / "web" / "registros.html").read_text(encoding="utf-8").lower()
    assert "general de división" not in registros
    assert "promoción al empleo" not in registros
    assert "adenda del mando de apoyo logístico" not in registros
