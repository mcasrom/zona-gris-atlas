from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_caso_moscu_es_publico_e_indexable() -> None:
    page = (ROOT / "web" / "caso-moscu-aeropuertos.html").read_text(encoding="utf-8")
    sitemap = (ROOT / "web" / "sitemap.xml").read_text(encoding="utf-8")
    llms = (ROOT / "web" / "llms.txt").read_text(encoding="utf-8")
    assert "Cuatro episodios, no una campaña" in page
    assert "canonical\" href=\"https://zonagris.pruebapublica.com/caso-moscu-aeropuertos.html\"" in page
    assert "og-caso-moscu.png" in page
    assert 'id="timeline-moscu"' in page
    assert "2025-05-06" in page and "2025-05-21" in page
    assert "2025-07-20" in page and "2026-10-30" in page
    assert "No se atribuye autoría" in page
    assert "caso-moscu-aeropuertos.html" in sitemap
    assert "caso-moscu-aeropuertos.html" in llms


def test_sitemap_incluye_paginas_publicas_de_analisis() -> None:
    sitemap = (ROOT / "web" / "sitemap.xml").read_text(encoding="utf-8")
    for page in ("baseline-aeropuertos.html", "gnss-n0.html", "grafo.html"):
        assert page in sitemap
