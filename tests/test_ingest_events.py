from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ingest_events", ROOT / "scripts" / "ingest_events.py")
ingest = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(ingest)

XML = b"""<?xml version="1.0"?><rss><channel>
<item><title>Bomb threat at Copenhagen Airport</title><link>https://www.bing.com/news/apiclick.aspx?url=https%3A%2F%2Fexample.com%2Fa</link><description>Airport evacuated after a threat; police investigate.</description><pubDate>Fri, 06 Nov 2026 10:00:00 GMT</pubDate></item>
<item><title>Bomb threat at Copenhagen Airport</title><link>https://www.bing.com/news/apiclick.aspx?url=https%3A%2F%2Fexample.net%2Fb</link><description>Flights delayed after a bomb threat at the airport.</description><pubDate>Fri, 06 Nov 2026 11:00:00 GMT</pubDate></item>
<item><title>Opinion: what the airport threat means</title><link>https://example.org/opinion</link><description>Analysis.</description><pubDate>Fri, 06 Nov 2026 12:00:00 GMT</pubDate></item>
</channel></rss>"""


def test_feed_is_parsed_and_opinion_is_filtered() -> None:
    rows = ingest.parse_feed(XML, "amenazas_bomba")
    assert len(rows) == 2
    assert rows[0]["url"] == "https://example.com/a"
    assert rows[0]["category"] == "amenazas_bomba"


def test_similar_headlines_are_grouped_but_remain_pending() -> None:
    rows = ingest.parse_feed(XML, "amenazas_bomba")
    groups = ingest.group_rows(rows)
    assert len(groups) == 1
    status, reason = ingest.assess(groups[0])
    assert status == "PENDIENTE"
    assert "revisión humana" in reason
    assert "sindicación" in reason


def test_single_source_stays_pending() -> None:
    row = ingest.parse_feed(XML, "amenazas_bomba")[0]
    status, reason = ingest.assess([row])
    assert status == "PENDIENTE"
    assert "una sola" in reason


def test_place_is_optional_and_never_invented() -> None:
    places = json.loads((ROOT / "data" / "event_places.json").read_text(encoding="utf-8"))
    assert ingest.place_for("Bomb threat at Copenhagen Airport", places)["city"] == "Copenhagen"
    assert ingest.place_for("A threat without a city", places) is None


def test_automatic_events_are_never_documented_without_human_review() -> None:
    rows = ingest.parse_feed(XML, "amenazas_bomba")
    events = ingest.build_events(ingest.group_rows(rows), json.loads((ROOT / "data" / "event_places.json").read_text(encoding="utf-8")), "2026-11-07T00:00:00Z")
    assert events
    assert all(event["automated"] is True for event in events)
    assert all(event["verification_status"] == "PENDIENTE" for event in events)
    assert all(event["reviewed_by_human"] is False for event in events)
    assert events[0]["source_sha256"]


def test_query_matrix_declares_all_regions() -> None:
    rows = ingest.query_matrix()
    regions = {row[0] for row in rows}
    assert {"europe", "americas", "asia", "china", "africa", "middle_east"} <= regions
    assert all(len(row) == 3 for row in rows)


def test_cable_market_noise_is_filtered() -> None:
    xml = b"""<?xml version="1.0"?><rss><channel>
    <item><title>Global Submarine Cables Market Size Report</title><link>https://example.org/market</link><description>Forecast and share.</description><pubDate>Fri, 06 Nov 2026 10:00:00 GMT</pubDate></item>
    <item><title>Submarine cable cut disrupts internet</title><link>https://example.org/cut</link><description>Damage to a subsea cable.</description><pubDate>Fri, 06 Nov 2026 11:00:00 GMT</pubDate></item>
    </channel></rss>"""
    rows = ingest.parse_feed(xml, "cables_submarinos")
    assert len(rows) == 1
    assert "cut" in rows[0]["title"].lower()


def test_explicit_country_is_accepted_but_actor_mention_is_not() -> None:
    assert ingest.country_for("Attack in France disrupts rail")["iso2"] == "FR"
    assert ingest.country_for("China-linked hackers hit 200 targets") is None
    assert ingest.country_for("French blood banks hit by cyberattack") is None


def test_geo_shadow_suggests_without_assigning_country() -> None:
    row = ingest.parse_feed(XML, "amenazas_bomba")[0]
    row["title"] = "Bomb threat in France"
    events = ingest.build_events([[row]], {"places": []}, "2026-11-07T00:00:00Z", geo_shadow=True)
    assert events[0]["country"] is None
    assert events[0]["geo_suggestion"]["country_iso2"] == "FR"


def test_generic_migration_is_not_instrumentalisation() -> None:
    assert ingest.query_relevant("migracion_instrumentalizada", "Migrants arrive at the border") is False
    assert ingest.query_relevant("migracion_instrumentalizada", "Belarus weaponised migration at the border") is True
