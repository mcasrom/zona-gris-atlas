import json
from pathlib import Path

from zonagris import db
from zonagris.export import write_atom, write_json


def _seed(tmp_path: Path):
    connection = db.connect(tmp_path / "test.db")
    db.init_db(connection)
    connection.execute(
        """
        INSERT INTO incidents
        (id, title, summary, domain, scale_position, severity, reality,
         lat, lon, place, country_iso2, event_date, status, demo)
        VALUES ('EJ-0001', 'Ejemplo', 'Resumen', 'AER', 'competencia',
                'baja', 'probable', 40.0, -3.0, 'Lugar', 'ES', '2026-11-01',
                'published', 1)
        """
    )
    connection.execute(
        """
        INSERT INTO attributions
        (incident_id, status, attributed_by, attributed_by_type, source_url, confidence)
        VALUES ('EJ-0001', 'none', NULL, NULL, NULL, 'low')
        """
    )
    connection.commit()
    return connection


def test_json_export_marks_demo(tmp_path: Path):
    connection = _seed(tmp_path)
    incidents = write_json(connection, tmp_path / "incidents.json")
    payload = json.loads((tmp_path / "incidents.json").read_text(encoding="utf-8"))
    assert incidents[0]["demo"] is True
    assert payload["demo"] is True
    assert payload["incidents"][0]["id"] == "EJ-0001"


def test_atom_export(tmp_path: Path):
    connection = _seed(tmp_path)
    write_atom(connection, tmp_path / "feed.xml")
    assert "<feed" in (tmp_path / "feed.xml").read_text(encoding="utf-8")
