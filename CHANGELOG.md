# Changelog

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
- El clasificador se declara experimental; se elimina el gold set de 200 eventos como requisito y no hay puerta de publicación.
- Licencia de datos CC BY 4.0 para estructura y metadatos propios; los titulares de terceros conservan sus derechos.
- Criterios de inclusión MIG y límites de sesgo de fuentes documentados.
- Rutas personales sustituidas por rutas genéricas y fichero de continuidad añadido.
