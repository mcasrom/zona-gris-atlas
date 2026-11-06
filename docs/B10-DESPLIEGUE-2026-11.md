# B10 · Despliegue de About y Avisos

**Fecha:** 2026-11-06 14:42 UTC  
**Estado:** **PUBLICADO**. Sin push, sin correo y sin ingestas.

## Release

- Activa: `/var/www/atlas-zonagris/releases/20261106T144246Z`
- `current` apunta a esa release.
- Anterior conservada: `20261106T142116Z`.
- También se conserva `20261106T141308Z`.
- Rollback disponible; no ejecutado.

## Backup

- Bundle local: `~/backups/zona-gris-atlas/zona-gris-atlas-20261106T144236Z.bundle`
- Verificado por `git bundle verify`.
- Se conservan los backups y releases anteriores.

## Archivos publicados

- `about.html` y `avisos.html`.
- Navegación actualizada en `index`, `mapa`, `metodologia`, `limites`, `fuentes` y `privacidad`.
- `assets/css/styles.css`.
- `sitemap.xml`.
- `feed.xml` regenerado.
- Sin cambios en los datos de incidentes.

## Verificación pública

| URL | HTTP |
|---|---:|
| `/` | 200 |
| `/about.html` | 200 |
| `/avisos.html` | 200 |
| `/metodologia.html` | 200 |
| `/mapa.html` | 200 |
| `/fuentes.html` | 200 |
| `/privacidad.html` | 200 |
| `/limites.html` | 200 |
| `/sitemap.xml` | 200 |
| `/feed.xml` | 200 |
| `/assets/css/styles.css` | 200 |
| `/assets/data/incidents.json` | 200 |

- HTTP raíz: **301 → HTTPS**.
- Canonical y OG de About/Avisos: dominio correcto.
- About: `mailto:info.zonagris@pruebapublica.com` y texto exacto.
- Sitemap público incluye `about.html` y `avisos.html`.
- About y Avisos enlazados en todas las páginas con navegación completa.
- **10/10 incidentes `demo: true`**.
- Sin `info.atlaszonagris` ni `viajeinteligencia.com` en las páginas revisadas.
- Cabeceras: HSTS, `nosniff`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` y CSP.
- `/metodo.html` sigue sin existir; no se creó alias.

## Capturas

- `docs/capturas/b10-about-1366x768.png`
- `docs/capturas/b10-about-390x844.png`
- `docs/capturas/b10-avisos-1366x768.png`
- `docs/capturas/b10-avisos-390x844.png`

## Comprobaciones locales

- `make lint`: OK.
- `make test`: **19 passed**.
- No se envió correo.
- No se verificó la recepción del buzón.
- No se activaron fuentes ni se ejecutaron consultas de datos.

## Estado

- Web pública: actualizada.
- Nginx, TLS, DNS, Docker, PM2 y AdGuard: sin cambios.
- Push: **no realizado**.
- 15 commits locales conservados.
