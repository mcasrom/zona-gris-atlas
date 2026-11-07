# Modo sombra de geolocalización

`scripts/ingest_events.py --geo-shadow` calcula una sugerencia de país pero **no la
asigna** al acontecimiento. No se publica, no cuenta como localización y no cambia
la cobertura.

## Prueba del 7-nov-2026

- 44 candidatos automáticos.
- 8 sugerencias de país.
- Sugerencias: Francia 3, Estados Unidos 2, Nigeria 1, España 1, Australia 1.

## Veredicto

No se activa. Hay falsos positivos claros:

- “Japan banking crisis… could hit banks in Spain” → **España**, pero es un escenario hipotético.
- “US AI firms” → **Estados Unidos**, pero es el actor, no el lugar.
- “after an identical attack in France” → **Francia**, pero es un ataque anterior.
- “Europe & US supermarkets” → país parcial en un hecho multi-país.

Casos defendibles: Sydney/Australia y Nigeria, y algunos de Francia; aun así no
justifican activar el modo automático.

## Regla

El modo sombra se queda como herramienta de revisión. Para activar geolocalización
hace falta metadata de fuente o reglas que ignoren condicionales, actores y
referencias a hechos anteriores.
