from zonagris import config


def test_taxonomy_has_all_domains():
    data = config.taxonomy()
    assert set(data["domains"]) == {"CIB", "INF", "AER", "GNS", "SAB", "DES", "ECO", "MIG"}


def test_atlas_covers_only_central_scale():
    data = config.taxonomy()
    assert data["atlas_scale"] == ["competencia", "zona_gris", "hostilidad_hibrida"]


def test_all_sources_disabled_and_pending_licence():
    data = config.sources()
    assert data["sources"]
    assert all(not source["enabled"] for source in data["sources"])
    assert all("DECIDIR" in source["licencia"] for source in data["sources"])
