from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_coverage_matrix_declares_regions_and_gaps() -> None:
    page = (ROOT / "web" / "cobertura.html").read_text(encoding="utf-8")
    config = json.loads((ROOT / "config" / "queries.json").read_text(encoding="utf-8"))
    ids = {region["id"] for region in config["regions"]}
    assert {"europe", "americas", "asia", "china", "africa", "middle_east"} <= ids
    assert "Matriz de consultas" in page
    assert "ámbito de la consulta" in page
    assert "cobertura.html" in (ROOT / "web" / "sitemap.xml").read_text(encoding="utf-8")


def test_english_entry_point_and_language_link() -> None:
    page = (ROOT / "web" / "en.html").read_text(encoding="utf-8")
    home = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    assert '<html lang="en">' in page
    assert 'hreflang="en"' in page
    assert 'href="en.html"' in home
    assert 'en.html' in (ROOT / "web" / "sitemap.xml").read_text(encoding="utf-8")
