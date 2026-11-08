from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_incident_matrix_is_public_and_indexable() -> None:
    page = (ROOT / "web" / "incidentes.html").read_text(encoding="utf-8")
    script = (ROOT / "web" / "assets" / "js" / "incidentes.js").read_text(encoding="utf-8")
    sitemap = (ROOT / "web" / "sitemap.xml").read_text(encoding="utf-8")
    assert 'Incidentes de zona gris en curso' in page
    assert 'canonical" href="https://zonagris.pruebapublica.com/incidentes.html"' in page
    assert 'assets/data/incidentes.json' in script
    assert 'Por definir' in script
    assert 'incidentes.html' in sitemap
    assert 'assets/js/incidentes.js' in page
