from urllib.parse import parse_qs, urlparse

from zonagris.ingest.gdelt import build_url, parse_payload


def test_build_url_has_expected_parameters():
    url = build_url("drones AND europa", maxrecords=25, timespan="48h")
    query = parse_qs(urlparse(url).query)
    assert query["mode"] == ["artlist"]
    assert query["format"] == ["json"]
    assert query["maxrecords"] == ["25"]
    assert query["timespan"] == ["48h"]


def test_parse_payload_skips_empty_urls():
    payload = '{"articles":[{"title":"A","url":"https://example.org/a"},{"title":"B"}]}'
    assert len(parse_payload(payload)) == 1
