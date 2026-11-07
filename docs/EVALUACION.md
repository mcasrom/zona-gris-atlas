# Evaluación opcional

## Sin puerta de publicación

El clasificador es **experimental y no publica fichas**. No hay un requisito de
etiquetar 200 eventos ni un lote de oro obligatorio. La revisión humana relevante
es **por ficha**: fuente, fecha, lugar, atribución y estado.

## Conjunto de muestra

Si alguien quiere medir una muestra concreta, cada línea de un JSONL opcional
puede contener:

- `id`
- `title`
- `text`
- `domain`
- `severity`
- `reality`
- `attribution.status`
- `attribution.attributed_by`
- `attribution.source_url`

`eval/gold/ejemplo.jsonl` solo documenta el formato. No es un conjunto de
evaluación ni una obligación de etiquetado.

## Métricas

`eval/metrics.py` calcula, si se le pasa una muestra:

- precisión, recall y F1 por clase;
- F1 macro y F1 ponderado;
- matriz de confusión.

## Regla de honestidad

Un F1 alto sobre un conjunto pequeño no es una validación. Se reporta siempre el
tamaño de la muestra, la distribución por clase y la matriz de confusión. Un
resultado malo se publica como malo. Ningún resultado automático autoriza una
publicación.
