# Metodología

La unidad de trabajo es la **ficha de incidente**, no el titular. Un incidente puede tener varias piezas asociadas; una pieza puede no llegar a ser incidente.

## Pipeline

1. **Fuente registrada.** Toda consulta debe estar en `config/sources.yaml` con condiciones de uso, formato y frecuencia. Bing News RSS está registrado como **agregador de descubrimiento activo**; no es una fuente primaria ni una autorización para publicar. Las fuentes institucionales siguen desactivadas hasta su revisión.
2. **Ingesta.** `src/zonagris/ingest/` descarga con caché local, User-Agent propio y límite de ritmo. No se guarda una copia masiva de textos que no necesitemos.
3. **Deduplicado.** `dedupe.py` compara primero el hash de la URL canónica y después la similitud de texto. Una URL repetida no crea una segunda pieza.
4. **Clasificación.** `classify/baseline.py` propone dominio, gravedad y realidad con TF-IDF + regresión logística. La propuesta se guarda en `classifications`; no cambia el estado de publicación. El clasificador es **experimental**: no hay puerta de publicación ni lote obligatorio de etiquetado; la revisión es por ficha.
5. **Revisión humana.** Verifico la fecha del hecho, el lugar, la fuente, la tabla de atribución y si el incidente resiste la etiqueta `probable`, `dudoso` o `descartado`.
6. **Publicación.** Solo una ficha `published` y revisada llega al JSON y a la web. **Los candidatos automáticos nunca superan `PENDIENTE`**: dos dominios pueden ser el mismo cable o la misma nota de prensa, así que no cuentan como confirmación independiente. La exportación de demo nunca se mezcla con incidentes reales.

## Estados

- `draft`: existe una propuesta, no está revisada.
- `reviewed`: una persona la ha revisado; aún no es pública.
- `published`: aparece en la web y en los datos abiertos.
- `rejected`: no se publica; se conserva el motivo en el flujo de trabajo.

## Comandos

```bash
.venv/bin/python -m zonagris.cli initdb
.venv/bin/python -m zonagris.cli ingest --source gdelt --query "drones europa"
.venv/bin/python -m zonagris.cli dedupe
.venv/bin/python -m zonagris.cli classify
.venv/bin/python -m zonagris.cli export
.venv/bin/python -m zonagris.cli stats
```

La web se construye sin backend:

```bash
make web
make serve
```

## Fuentes

`config/sources.yaml` es un registro, no una autorización. Una fuente con `enabled: false` no se consulta. Bing News RSS está activo solo para **descubrir enlaces**; sus condiciones de uso siguen pendientes de revisión legal. GDELT está implementado, pero no activado por defecto; la primera ejecución debe revisar su documentación vigente y sus condiciones. La dieta actual de fuentes institucionales es occidental y no se presenta como neutral; la ampliación a otras perspectivas es un pendiente explícito (ver `LIMITES.md`).

## Qué no hace el pipeline

No decide autoría, no puntúa personas, no publica una clasificación automática y no convierte una reivindicación en prueba. Esas decisiones están en `docs/LIMITES.md` y `docs/ATRIBUCION.md`.
