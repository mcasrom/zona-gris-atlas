# Changelog

## 2026-11-11 — caso de Moscú y baseline v1.7

- Publicado `/caso-moscu-aeropuertos.html`: cuatro episodios documentados, sin atribución ni campaña.
- Añadida OG propia y enlace desde portada, alcance y baseline.
- Sitemap corregido para incluir baseline de aeropuertos, GNSS N0, grafo y el caso.
- París (6-nov-2026) pasa a `CORROBORADO` con CBS News; Auckland y Great Falls se corroboran y se corrige la fecha de Auckland. Baseline **v1.7**: 65 eventos, 63 corroborados y 2 documentados.

## 0.1.1 — 2026-11-07

- Sin demo, sin gold set obligatorio, autoría/contacto público y versión en el pie.

## 0.1.0 — 2026-11-06

- Esqueleto del proyecto y repositorio.
- Esquema SQLite para fuentes, piezas, incidentes, atribuciones y clasificaciones.
- Ingesta GDELT y lector RSS apagado por defecto.
- Deduplicado por URL y similitud.
- Clasificador TF-IDF + regresión logística con puerta de evaluación.
- Exportación JSON y Atom.
- Web estática con mapa de puntos, landing, método, fuentes y límites.
- 10 incidentes de demostración, todos con `demo: true`.
- Workflow de CI, plantillas de issues y respaldo en git bundle.

## 2026-11-07 — coherencia de fuentes y publicación

- Bing News RSS queda registrado como agregador de descubrimiento activo, no como fuente primaria.
- Los candidatos automáticos nunca pasan a `DOCUMENTADO`; el constructor los degrada a `PENDIENTE` si detecta un registro sin revisión humana.
- El clasificador se declara experimental; se elimina el conjunto de validación obligatorio y no hay puerta de publicación.
- Licencia de datos CC BY 4.0 para estructura y metadatos propios; los titulares de terceros conservan sus derechos.
- Criterios de inclusión MIG y límites de sesgo de fuentes documentados.
- Rutas personales sustituidas por rutas genéricas y fichero de continuidad añadido.
