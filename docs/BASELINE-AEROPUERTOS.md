# Línea base de aeropuertos

**Estado:** **N1 inicial**: 52 eventos / 25 meses; mediana 1 evento/mes.  
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

La semilla + revisión manual suma **52 eventos en 25 meses**; el validador devuelve `ready`. La mediana es **1 evento/mes**, así que la línea base es fina y descriptiva: no autoriza a hablar de tendencia consolidada ni de atribución.

## Descubrimiento de candidatos

`scripts/discover_airports_baseline.py` consulta GDELT por ventanas y escribe
`data/baseline/airports-candidates.csv` con `status=CANDIDATO`. **No entra en la
línea base**: solo sirve para localizar piezas que luego se revisan a mano.

GDELT limita peticiones (HTTP 429); si falla, no se inventan candidatos.

`scripts/discover_airports_google.py` usa Google News RSS como vía alternativa
para descubrir piezas históricas por ventanas. Escribe
`data/baseline/airports-candidates-google.csv`; tampoco entra en la línea base
y no sustituye la revisión de la fuente original.

`scripts/filter_airport_candidates.py` cruza los candidatos con el gazetteer y
descarta falsos positivos evidentes. La última pasada dejó 94 candidatos en 21
meses; siguen siendo candidatos, no eventos aceptados.

## Regla

**N1 no es “hay muchos registros”. Es “hay serie histórica suficiente para comparar”.**
