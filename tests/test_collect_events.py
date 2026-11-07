from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("collect_events", ROOT / "scripts" / "collect_events.py")
collect_events = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(collect_events)

XML = b"""<?xml version=\"1.0\"?><rss><channel>
<item><title>Aeropuerto: amenaza de bomba</title><link>https://www.bing.com/news/apiclick.aspx?url=https%3A%2F%2Fexample.com%2Fnoticia</link><pubDate>Fri, 06 Nov 2026 10:00:00 GMT</pubDate></item>
<item><title>Aeropuerto: amenaza de bomba</title><link>https://www.bing.com/news/apiclick.aspx?url=https%3A%2F%2Fexample.com%2Fnoticia</link><pubDate>Fri, 06 Nov 2026 10:00:00 GMT</pubDate></item>
</channel></rss>"""


def test_bing_link_is_decoded_and_duplicates_are_removed() -> None:
    rows = collect_events.parse_feed(XML, "Bing News RSS", "amenazas_bomba")
    assert len(rows) == 2
    assert rows[0]["url"] == "https://example.com/noticia"
    deduped = collect_events.dedupe(rows, 7)
    assert len(deduped) == 1
    assert deduped[0]["published_at"] == "2026-11-06"
    assert deduped[0]["reviewed_by_human"] is False


def test_category_guess_and_invalid_feed() -> None:
    assert collect_events.classify("Dron cerca del aeropuerto") == "drones_aeropuertos"
    assert collect_events.classify("GPS jamming") == "gnss"
    try:
        collect_events.parse_feed(b"<html>no rss</html>", "x", "y")
    except Exception as exc:
        assert exc
    else:
        raise AssertionError("un feed inválido debe fallar")
