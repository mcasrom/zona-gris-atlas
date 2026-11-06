# B9 · Revisión de About y Avisos antes de publicar

**Fecha:** 2026-11-06  
**Estado:** revisión local y pública. **No se ha desplegado, no se ha enviado correo y no se ha hecho push.**

## 1. Estado local

- `web/about.html`: **200** local.
- `web/avisos.html`: **200** local.
- `web/metodologia.html`: **200** local.
- `web/metodo.html`: **404** local (la ruta real es `metodologia.html`).
- `about.html` y `avisos.html` tienen canonical propio y Open Graph con el dominio correcto.
- About incluye naturaleza independiente, mantenimiento, relación con Prueba Pública/FIMI Radar, método, fuentes, límites, transparencia y contacto.
- Avisos mantiene demo, interpretación, limitaciones, correcciones y reutilización.
- Navegación: About y Avisos enlazados en todas las páginas con cabecera completa.
- Sitemap local incluye ambas páginas.
- 10/10 incidentes siguen `demo: true`.

## 2. Estado público actual

Comprobado con `curl --resolve` contra la release activa:

| URL | Código |
|---|---:|
| `/` | 200 |
| `/about.html` | **404** |
| `/avisos.html` | **404** |
| `/mapa.html` | 200 |
| `/metodologia.html` | 200 |
| `/metodo.html` | **404** |
| `/fuentes.html` | 200 |
| `/privacidad.html` | 200 |
| `/limites.html` | 200 |
| `/sitemap.xml` | 200 |

La release pública actual aún no contiene About ni Avisos. El sitemap público tampoco los incluye.

## 3. Correo

- Dirección en About: `info.zonagris@pruebapublica.com`.
- Enlace: `mailto:info.zonagris@pruebapublica.com`.
- Aparece dos veces: texto y `mailto:`.
- No aparece `info.atlaszonagris@...`.
- No se ha enviado ningún mensaje ni se ha verificado la recepción del buzón.
- No se afirma que el buzón esté operativo.

## 4. Diferencias local/público

`rsync --dry-run --checksum` contra la release activa muestra:

- Nuevos: `about.html`, `avisos.html`.
- Modificados por navegación/Sitemap: `index.html`, `mapa.html`, `metodologia.html`, `limites.html`, `fuentes.html`, `privacidad.html`, `sitemap.xml`.
- Modificados por estilos de avisos: `assets/css/styles.css`.
- `feed.xml` cambia por regeneración de fecha.
- `404.html`, `robots.txt`, `site.webmanifest` y `assets/data/incidents.json` solo muestran diferencias de metadatos/tiempo; el contenido de incidentes no cambia.
- Se conserva la release anterior y el rollback.

## 5. Archivos que entrarían en el despliegue

- `web/about.html` (nuevo)
- `web/avisos.html` (nuevo)
- `web/index.html`, `web/mapa.html`, `web/metodologia.html`, `web/limites.html`, `web/fuentes.html`, `web/privacidad.html` (enlaces de navegación)
- `web/assets/css/styles.css` (estilos `.notice`)
- `web/sitemap.xml`
- `web/feed.xml` (regeneración)
- `web/404.html`, `web/robots.txt`, `web/site.webmanifest`, `web/assets/data/incidents.json` solo por metadatos/tiempo

No se publican documentos B5–B9 ni capturas: están fuera de `web/`.

## 6. Lint y tests

- `make lint`: **OK**.
- `make test`: **19 passed**.

## 7. Procedimiento de publicación previsto

```bash
SERVER=178.105.80.193 ZG_DOMAIN=zonagris.pruebapublica.com \
  ./scripts/deploy_web.sh
# revisar el plan
SERVER=178.105.80.193 ZG_DOMAIN=zonagris.pruebapublica.com \
  ./scripts/deploy_web.sh --apply
```

El segundo comando **no se ha ejecutado**. Después habría que verificar `/about.html` y `/avisos.html` en público, sitemap, enlaces, cabeceras y que el correo aparece exactamente.

## 8. Incidencia de ruta

`/metodo.html` no existe ni local ni públicamente. La página real es `/metodologia.html`. No se ha creado un alias sin autorización; es una decisión de producto pendiente.

## 9. Confirmaciones

- **No** se ha ejecutado `deploy_web.sh --apply`.
- **No** se ha hecho push.
- **No** se ha enviado correo.
- **No** se han activado fuentes ni iniciado ingestas.
- **No** se han recogido datos reales.
- **No** se ha modificado Nginx, TLS, DNS, Docker, PM2 ni AdGuard.
- 15 commits locales conservados.

## 10. Recomendación

About y Avisos están listos localmente. Antes de publicar hay que decidir si se crea un alias `/metodo.html` o se mantiene únicamente `/metodologia.html`, y autorizar expresamente el `--apply`.
