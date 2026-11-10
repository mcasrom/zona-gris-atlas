# Revisión correctiva del baseline de aeropuertos · 10-nov-2026

## Motivo

Al verificar las fuentes para la fase de corroboración aparecieron tres
inconsistencias entre la fecha del registro y la fecha real de la pieza:

1. **R13 (Jersey, 25-jun-2025)** no era un incidente nuevo: la pieza de BBC del
   25-jun-2025 informa de una amenaza de marzo y de que Ports of Jersey tardó
   horas en evacuar. Es un **seguimiento de R08 (6-mar-2025)**.
2. **R37 (Ben Gurión, 11-may-2026)** estaba fechado el 11-may, pero la pieza de
   ynet se publicó el **5-nov-2026**.
3. **R38 (Bruselas, 11-may-2026)** estaba fechado el 11-may, pero la URL y la
   publicación de Israel Hayom son del **5-nov-2026**.

## Corrección aplicada

- **R13** sale del baseline y pasa a `airports-followups.csv` como seguimiento de
  R08.
- **R37 y R38** se fechan el **2026-11-05**.
- Se reconstruye el baseline: **65 eventos / 24 meses**; N1 sigue `ready`.
- Se crea **v1.5** y se conservan **v1** (69), **v1.1** (68), **v1.2** (66), **v1.3** (65) y **v1.4** (65) como versiones anteriores.
- N2 queda en **57 eventos / 23 meses completos** (sin 2025-06), p90 5.

## Consecuencias documentales

- Corroborados: **55**.
- Documentados: **10**.
- El mes de **2025-06** queda sin eventos; no se rellena con una pieza de otro
  episodio.
- **2026-11** queda en 8 eventos, pero sigue siendo parcial y no se compara.

## Límite

Esta revisión corrige lo detectado, no acredita que no queden más errores de
fecha o seguimiento. Antes de abrir N3 hay que auditar una muestra mayor y
revisar las fuentes primarias de los eventos con fecha dudosa.
