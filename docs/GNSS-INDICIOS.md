# GNSS · indicios y fuentes de ocurrencia

**Estado:** capa separada de N0. **No cuenta para N1.**

## Qué es un indicio

Un indicio es una señal de que puede haber un episodio GNSS, pero **no tiene fecha exacta, lugar verificable y fuente directa suficiente** para entrar en `gnss-n0.csv`.

No se presenta como incidente. No se atribuye autoría. No se suma a la serie.

## Fuentes

- **NASA ASRS:** informes voluntarios de pilotos, deidentificados. Son útiles para detectar patrones y tipos de fallo, pero no permiten reconstruir un episodio con fecha y lugar.
- **NTSB CAROL:** accidentes e incidentes de EE. UU. Oficial, pero no cubre todos los eventos GNSS.
- **The Aviation Herald:** ocurrencias concretas y fechadas; sirve como pista, no como registro oficial completo.
- **EASA / EUROCONTROL / ICAO / IATA:** guías, SIB y formularios de reporte; no publican un listado completo de ocurrencias.

## Regla de promoción

Un indicio solo pasa a N0 si se consigue:

1. fecha del hecho;
2. lugar o región documentada;
3. fuente directa del episodio;
4. revisión humana.

Si falta uno de esos cuatro, se queda en `data/gnss/indicios.csv`.

## Por qué existe esta capa

Porque la fuente que falta no es una noticia: es un **registro de ocurrencias**. Las aerolíneas y los ATC tienen esos datos, pero no son públicos. Sin acceso a ellos, ASRS/NTSB/AvHerald solo permiten indicios.

## Estado actual

- **N0:** 30 episodios documentados; 24 en ventana.
- **Indicios:** 3 informes ASRS sin fecha exacta.
- **N1:** cerrado (24/50; 18/24 meses).
