# Ingesta automática de acontecimientos

`scripts/ingest_events.py` consulta Bing News RSS sin claves, normaliza titulares,
agrupa noticias parecidas, extrae una ubicación solo si aparece en el gazetteer
editorial (`data/event_places.json`) y escribe `data/events/auto/events.jsonl`.

La evaluación es deliberadamente conservadora:

- **todos** los candidatos automáticos quedan en `PENDIENTE`, incluso si varios
  dominios publican el mismo hecho: pueden compartir cable o nota de prensa;
- `DOCUMENTADO` exige revisión humana; el constructor degrada a `PENDIENTE`
  cualquier registro automático sin revisión;
- `CONFIRMADO` nunca se asigna automáticamente;
- `reviewed_by_human` queda en `false`;
- cada evento conserva URL, fecha de publicación, fecha de captura y `source_sha256`;
- no se descarga el artículo completo ni se inventan coordenadas.

`scripts/build_web.py` y `scripts/build_events_data.py` comparten la misma función
de fusión: los revisados tienen prioridad, se descartan los automáticos que repiten
URL o titular similar y **nunca se publica un automático como `DOCUMENTADO`**.
Bing News RSS está registrado en `config/sources.yaml` como agregador de
descubrimiento, no como fuente primaria; sus condiciones de uso siguen pendientes
de revisión legal.

## Ejecución

```bash
make events       # solo captura
make web          # reconstruye feed, sitemap, eventos y OG
scripts/auto_update.sh
```

Para que no dependa de una revisión diaria, programar `scripts/auto_update.sh` en el
servidor o en el equipo que tenga el repositorio. Ejemplo de cron (horario a ajustar):

```cron
17 */6 * * * cd /ruta/a/zona-gris-atlas && ./scripts/auto_update.sh >> logs/auto-update.log 2>&1
```

Si se quiere publicar desde el mismo proceso, añadir `ZG_AUTO_DEPLOY=1`, `SERVER` y
`ZG_DOMAIN` al entorno. Sin esas variables, el script solo deja los cambios locales.

## Servidor Hetzner

La automatización está instalada en:

```text
<ruta-de-despliegue>/atlas-zonagris-auto/server_update.sh
```

El cron de `deploy` la ejecuta cada 6 horas:

```cron
17 */6 * * * <ruta-de-despliegue>/atlas-zonagris-auto/server_update.sh >> <ruta-de-despliegue>/atlas-zonagris-auto/logs/update.log 2>&1
```

Cada ejecución captura, fusiona, crea una release fechada a partir de `current`,
valida el JSON y mueve el symlink `current`. No modifica Nginx, DNS ni TLS. Las
releases anteriores se conservan para rollback; el log está en
`<ruta-de-despliegue>/atlas-zonagris-auto/logs/update.log`.
