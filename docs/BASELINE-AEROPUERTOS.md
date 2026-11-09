# Línea base de aeropuertos

**Estado:** esquema y validador listos; backfill pendiente.  
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

El comando devuelve `status: insufficient` hasta que se alcancen los mínimos.

## Regla

**N1 no es “hay muchos registros”. Es “hay serie histórica suficiente para comparar”.**
