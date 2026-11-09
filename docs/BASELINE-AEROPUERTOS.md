# Línea base de aeropuertos

**Estado:** esquema y validador listos; semilla de 8 eventos en 1 mes. Backfill pendiente.  
**Objetivo:** pasar de N0 (registro) a N1 (línea base) sin inventar tendencia.

## Qué cuenta

- Amenaza de bomba, evacuación o actividad de drones en un aeropuerto.
- **Un evento por episodio**, con fecha del hecho, no de publicación.
- Un seguimiento no cuenta como evento nuevo: se enlaza al episodio original.
- Un agregado de prensa no es un evento.

## Campos

`event_id,event_date,published_at,airport,country,event_type,source_url,source_type,independent_group,status,notes`

## Criterios mínimos

Para publicar N1:

- **24 meses** distintos con datos.
- **50 eventos** únicos.
- Una fuente identificable por evento.
- Al menos dos grupos de fuente independientes en el conjunto.
- Sin duplicados por `event_id` ni por `(event_date, airport, event_type)` sin revisión.

Si no se cumple, el resultado es `insufficient` y no se publica tendencia.

## Fuentes previstas

- Autoridades aeroportuarias y policiales.
- EASA / EUROCONTROL cuando documenten el episodio.
- Agencias y prensa local/regional, siempre como fuente secundaria.
- Histórico de noticias para descubrimiento, nunca como confirmación automática.

## Uso

```bash
python scripts/build_baseline.py \
  --input data/baseline/airports.csv \
  --domain airports \
  --out data/baseline/airports-baseline.json
```

La semilla actual son 8 eventos documentados de noviembre de 2026 en 8 dominios; el validador devuelve `insufficient` (8/50 eventos, 1/24 meses). No es una línea base.

## Descubrimiento de candidatos

`scripts/discover_airports_baseline.py` consulta GDELT por ventanas y escribe
`data/baseline/airports-candidates.csv` con `status=CANDIDATO`. **No entra en la
línea base**: solo sirve para localizar piezas que luego se revisan a mano.

GDELT limita peticiones (HTTP 429); si falla, no se inventan candidatos. La
siguiente vía es el archivo de fuentes oficiales y hemerotecas, no insistir en
el mismo endpoint.

## Regla

**N1 no es “hay muchos registros”. Es “hay serie histórica suficiente para comparar”.**
