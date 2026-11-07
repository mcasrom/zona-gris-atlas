from zonagris import config


def test_taxonomy_has_all_domains():
    data = config.taxonomy()
    assert set(data["domains"]) == {"CIB", "INF", "AER", "GNS", "SAB", "DES", "ECO", "MIG"}


def test_atlas_covers_only_central_scale():
    data = config.taxonomy()
    assert data["atlas_scale"] == ["competencia", "zona_gris", "hostilidad_hibrida"]


def test_source_registry_records_active_discovery_aggregator():
    data = config.sources()
    assert data["sources"]
    by_id = {source["id"]: source for source in data["sources"]}
    assert by_id["bing-news-rss"]["enabled"] is True
    assert by_id["bing-news-rss"]["type"] == "aggregator"
    assert by_id["bing-news-rss"]["fecha_revision"] == "2026-11-07"
    assert all(source["licencia"] for source in data["sources"])
