# Evaluación

## Conjunto de oro

Cada línea de `eval/gold/*.jsonl` contiene:

- `id`
- `title`
- `text`
- `domain`
- `severity`
- `reality`
- `attribution.status`
- `attribution.attributed_by`
- `attribution.source_url`

`eval/gold/ejemplo.jsonl` solo documenta el formato. No es un conjunto de evaluación válido para publicar.

## Métricas

`eval/metrics.py` calcula:

- precisión, recall y F1 por clase;
- F1 macro y F1 ponderado;
- matriz de confusión.

## Puerta de salida

No se publica nada generado por el clasificador mientras no se cumpla:

- **F1 macro ≥ 0,75** (`[DECIDIR]`);
- **≥ 200 eventos** etiquetados en el conjunto de oro.

El umbral vive en `eval/threshold.yaml`. Si falla, el clasificador puede seguir proponiendo, pero la ficha no se publica.

## Regla de honestidad

Un F1 alto sobre un conjunto pequeño no es una validación. Se reporta siempre el tamaño del conjunto, la distribución por clase y la matriz de confusión. Un resultado malo se publica como malo.
