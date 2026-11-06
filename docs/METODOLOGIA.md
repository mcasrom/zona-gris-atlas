# Metodología

La unidad de trabajo es la **ficha de incidente**, no el titular. Un incidente puede tener varias piezas asociadas; una pieza puede no llegar a ser incidente.

## Pipeline

1. **Fuente autorizada.** La fuente debe estar revisada en `config/sources.yaml`: condiciones de uso, licencia, formato y frecuencia. Todas empiezan con `enabled: false`.
2. **Ingesta.** `src/zonagris/ingest/` descarga con caché local, User-Agent propio y límite de ritmo. No se guarda una copia masiva de textos que no necesitemos.
3. **Deduplicado.** `dedupe.py` compara primero el hash de la URL canónica y después la similitud de texto. Una URL repetida no crea una segunda pieza.
4. **Clasificación.** `classify/baseline.py` propone dominio, gravedad y realidad con TF-IDF + regresión logística. La propuesta se guarda en `classifications`; no cambia el estado de publicación.
5. **Revisión humana.** Verifico la fecha del hecho, el lugar, la fuente, la tabla de atribución y si el incidente resiste la etiqueta `probable`, `dudoso` o `descartado`.
6. **Publicación.** Solo una ficha `published` y revisada llega al JSON y a la web. La exportación de demo nunca se mezcla con incidentes reales.

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

`config/sources.yaml` es un registro, no una autorización. Una fuente con `enabled: false` no se consulta. GDELT está implementado, pero no activado por defecto; la primera ejecución debe revisar su documentación vigente y sus condiciones.

## Qué no hace el pipeline

No decide autoría, no puntúa personas, no publica una clasificación automática y no convierte una reivindicación en prueba. Esas decisiones están en `docs/LIMITES.md` y `docs/ATRIBUCION.md`.
