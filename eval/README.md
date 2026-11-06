# Evaluación

El clasificador no publica nada hasta superar `min_macro_f1` sobre un conjunto de
oro de al menos 200 eventos etiquetados. El ejemplo de `gold/ejemplo.jsonl`
documenta el formato; no es un conjunto de evaluación real.

Campos de cada línea:

- `id`
- `title`
- `text`
- `domain` (`CIB`, `INF`, `AER`, `GNS`, `SAB`, `DES`, `ECO`, `MIG`)
- `severity` (`baja`, `media`, `alta`)
- `reality` (`probable`, `dudoso`, `descartado`)
- `attribution`: `status`, `attributed_by`, `source_url`

`metrics.py` calcula precisión, recall, F1 por clase, F1 macro y matriz de
confusión. La puerta de publicación está en `threshold.yaml` y sigue pendiente
de calibración con datos reales.
