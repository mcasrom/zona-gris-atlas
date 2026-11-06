from pathlib import Path

from zonagris import db


def test_schema_and_stats(tmp_path: Path):
    connection = db.connect(tmp_path / "test.db")
    db.init_db(connection)
    db.ensure_source(connection, "demo", "Demo", "https://example.org", "web")
    item_id = db.insert_raw_item(
        connection,
        "demo",
        "https://example.org/a",
        "Titular",
        "Texto",
        "es",
        "2026-11-01",
        "hash",
        "text-hash",
    )
    assert item_id > 0
    connection.execute(
        """
        INSERT INTO incidents
        (id, title, summary, domain, scale_position, severity, reality, event_date, status, demo)
        VALUES ('ZG-2026-0001', 'Caso', 'Resumen', 'CIB', 'zona_gris', 'media', 'probable',
                '2026-11-01', 'published', 1)
        """
    )
    connection.commit()
    assert db.stats(connection)["incidents"] == 1
