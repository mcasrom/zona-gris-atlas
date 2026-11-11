#!/usr/bin/env python3
"""Genera la página pública del inventario GNSS N0 v0.1."""
from __future__ import annotations

import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "baseline" / "gnss-n0-v0.1.csv"
BASE = ROOT / "web" / "alcance.html"
OUT = ROOT / "web" / "gnss-n0.html"

rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
eps = sorted([r for r in rows if r["record_type"] == "episode"], key=lambda r: r["event_date"], reverse=True)
aggs = [r for r in rows if r["record_type"] == "aggregate"]
inside = [r for r in eps if r["event_date"] >= "2024-11-11"]
months = sorted({r["event_date"][:7] for r in eps})
missing = [m for m in ["2025-02","2025-08","2026-01","2026-02","2026-04","2026-07"] if m not in months]

def e(x): return html.escape(str(x or ""))
def src(r):
    u = e(r["source_url"])
    return f'<a href="{u}" rel="noopener" target="_blank">Fuente</a>'

ep_rows = "\n".join(
    f'<tr><td>{e(r["event_date"])}</td><td>{e(r["region"])}</td><td>{e(r["place"])}</td><td>{e(r["event_type"])}</td><td>{src(r)}</td></tr>'
    for r in eps
)
agg_rows = "\n".join(
    f'<tr><td>{e(r["event_date"])}</td><td>{e(r["region"])}</td><td>{e(r["place"])}</td><td>{e(r["event_type"])}</td><td>{src(r)}</td></tr>'
    for r in aggs
)
base = BASE.read_text(encoding="utf-8")
header = base.split("<main id=\"contenido\">", 1)[0]
footer = base.split("</main>", 1)[1]
page = f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="alternate icon" href="favicon.ico" type="image/x-icon">
  <title>GNSS N0 · inventario documentado · Atlas Zona Gris</title>
  <meta name="description" content="Inventario GNSS N0: 30 episodios documentados, 24 en ventana de 24 meses y 4 agregados. Sin N1 ni tendencia.">
  <link rel="canonical" href="https://zonagris.pruebapublica.com/gnss-n0.html">
  <meta name="theme-color" content="#12171d">
  <link rel="preload" href="assets/fonts/archivo-latin-wdth.woff2" as="font" type="font/woff2" crossorigin>
  <meta name="robots" content="index,follow">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Atlas Zona Gris">
  <meta property="og:locale" content="es_ES">
  <meta property="og:title" content="GNSS N0 · inventario documentado">
  <meta property="og:description" content="30 episodios documentados; 24 en ventana de 24 meses. Sin N1 ni tendencia.">
  <meta property="og:url" content="https://zonagris.pruebapublica.com/gnss-n0.html">
  <meta property="og:image" content="https://zonagris.pruebapublica.com/assets/img/og-atlas.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="GNSS N0 · inventario documentado">
  <meta name="twitter:description" content="30 episodios documentados; 24 en ventana de 24 meses. Sin N1 ni tendencia.">
  <meta name="twitter:image" content="https://zonagris.pruebapublica.com/assets/img/og-atlas.png">
  <link rel="stylesheet" href="assets/css/styles.css?v=20261108f">
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"GNSS N0 · inventario documentado","description":"Inventario GNSS N0: 30 episodios documentados, 24 en ventana de 24 meses y 4 agregados. Sin N1 ni tendencia.","url":"https://zonagris.pruebapublica.com/gnss-n0.html","inLanguage":"es"}}</script>
</head>
<body>
{header}
<main id="contenido">
  <section class="hero"><div class="container">
    <p class="eyebrow">GNSS · N0 · v0.1</p>
    <h1>Inventario GNSS: 30 episodios, sin línea base.</h1>
    <p class="lead">Registro documental de interferencia, suplantación y perturbación GNSS. <strong>No hay N1</strong>: todavía no se publica frecuencia, tendencia ni atribución.</p>
  </div></section>

  <section class="section"><div class="container">
    <div class="state-grid">
      <div class="state-card"><span class="code-label">episodios</span><strong>{len(eps)}</strong><p>Con fecha, región/lugar y fuente directa.</p></div>
      <div class="state-card"><span class="code-label">en ventana</span><strong>{len(inside)}</strong><p>Últimos 24 meses; el resto es contexto histórico.</p></div>
      <div class="state-card"><span class="code-label">agregados</span><strong>{len(aggs)}</strong><p>Contexto; no cuentan para N1.</p></div>
      <div class="state-card"><span class="code-label">N1</span><strong>cerrado</strong><p>Faltan 26 episodios en ventana y 6 meses.</p></div>
    </div>
    <div class="notice warn" style="margin-top:18px"><strong>Qué no es:</strong> una serie de frecuencia, un nivel de amenaza ni una atribución. Un agregado no es un episodio y una alerta no es un incidente.</div>
  </div></section>

  <section class="paper section"><div class="container">
    <div class="section-head"><div><p class="eyebrow">Inventario</p><h2>Episodios documentados.</h2></div><p>Ordenados del más reciente al más antiguo.</p></div>
    <div class="tablewrap"><table><thead><tr><th>Fecha</th><th>Región</th><th>Lugar</th><th>Tipo</th><th>Fuente</th></tr></thead><tbody>
    {ep_rows}
    </tbody></table></div>
    <p class="muted small">30 episodios; 24 dentro de la ventana de 24 meses. Los episodios de 2024 fuera de ventana no cuentan para N1.</p>
  </div></section>

  <section class="section"><div class="container">
    <div class="section-head"><div><p class="eyebrow">Contexto</p><h2>Agregados, no episodios.</h2></div><p>Se conservan, pero no suman.</p></div>
    <div class="tablewrap"><table><thead><tr><th>Fecha</th><th>Región</th><th>Ámbito</th><th>Tipo</th><th>Fuente</th></tr></thead><tbody>
    {agg_rows}
    </tbody></table></div>
  </div></section>

  <section class="section"><div class="container split">
    <div><p class="eyebrow">Límites</p><h2>Lo que falta.</h2><p>La fuente que falta no es una noticia: es un registro de ocurrencias de aerolíneas/ATC. Sin acceso a él, ASRS, NTSB y Aviation Herald solo producen indicios, no episodios.</p><p class="muted small">Meses sin episodio: {", ".join(missing)}.</p></div>
    <div class="notice"><strong>Regla:</strong> un indicio no pasa a N0 sin fecha, lugar, fuente directa y revisión humana. No se rellena la serie con agregados para llegar a 50.</div>
  </div></section>

  <section class="section"><div class="container">
    <p class="muted small"><a href="alcance.html">Volver a alcance</a> · <a href="fuentes.html">Fuentes</a> · <a href="metodologia.html">Método</a> · <a href="https://github.com/mcasrom/zona-gris-atlas/blob/main/data/baseline/gnss-n0-v0.1.csv">CSV N0 v0.1</a></p>
  </div></section>
</main>
{footer}'''
OUT.write_text(page, encoding="utf-8")
print("ok", OUT, len(eps), len(inside), len(aggs))
