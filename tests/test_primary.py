from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ingest_primary", ROOT / "scripts" / "ingest_primary.py")
primary = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(primary)

RSS = b"""<?xml version="1.0"?><rss><channel>
<item>
  <title>Cyber Brief 26-11 - October 2026</title>
  <link>https://cert.europa.eu/publications/threat-intelligence/cb26-11/</link>
  <description>Cyber Briefs are monthly reports. TLP:CLEAR.</description>
  <pubDate>Fri, 06 Nov 2026 15:00:00 CET</pubDate>
  <guid>threat-intelligence-10167</guid>
</item>
<item><title></title><link>https://cert.europa.eu/no-title/</link></item>
</channel></rss>"""


def test_cert_eu_document_is_primary_and_not_an_incident() -> None:
    documents = primary.parse_feed(RSS)
    assert len(documents) == 1
    doc = documents[0]
    assert doc["source"] == "CERT-EU"
    assert doc["tier"] == "primary"
    assert doc["kind"] == "primary_document"
    assert doc["is_incident"] is False
    assert doc["published_at"] == "2026-11-06"
    assert doc["license"] == "CC BY 4.0"
    assert doc["tlp"] == "CLEAR"
