# B18 · Publicación de B16

**Fecha:** 2026-11-06 15:15 UTC  
**Estado:** **PUBLICACIÓN CORRECTA**. Sin push.

## Release

- Activa: `/var/www/atlas-zonagris/releases/20261106T151553Z`
- `current` apunta a esa release.
- Anterior conservada: `20261106T144246Z`.
- También se conservan `20261106T142116Z` y `20261106T141308Z`.
- Rollback disponible; no se ha ejecutado.

## Backup

- Bundle local: `~/backups/zona-gris-atlas/zona-gris-atlas-20261106T151544Z.bundle`
- Verificado con `git bundle verify`.
- Release anterior intacta.

## Archivos publicados

- Portada con indicadores reales de B13.
- `registros.html` con 8 documentos reales.
- `demo.html` con 10 casos ficticios, `demo: true`, aviso y `noindex`.
- `mapa.html` con meta refresh a `demo.html`.
- Navegación separada Registros/Demo.
- `feed.xml` con 8 entradas reales.
- `sitemap.xml` con `registros.html`, sin demo ni mapa.
- About y Avisos actualizados.
- CSS y JSON de registros.

## Verificación pública

| URL | HTTP |
|---|---:|
| `/` | 200 |
| `/registros.html` | 200 |
| `/demo.html` | 200 |
| `/mapa.html` | 200 |
| `/about.html` | 200 |
| `/avisos.html` | 200 |
| `/metodologia.html` | 200 |
| `/fuentes.html` | 200 |
| `/privacidad.html` | 200 |
| `/limites.html` | 200 |
| `/feed.xml` | 200 |
| `/sitemap.xml` | 200 |
| `/assets/data/registros.json` | 200 |

- HTTP raíz: **301 → HTTPS**.
- HTTPS: **200**, `ssl_verify_result=0`.
- Portada: KPIs **5/212/8/204/100 %/1** y **13-nov-2026**.
- Registros: 8 IDs y URLs de B13; atribución; sin texto completo.
- Demo: 10 casos; `noindex`; aviso visible.
- Feed: **8 entradas**, sin demo.
- Sitemap: sin `demo.html` ni `mapa.html`.
- Sin `viajeinteligencia.com`, contacto antiguo ni texto completo en registros.
- Cabeceras de seguridad: HSTS, `nosniff`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, CSP.

## Otros servicios

Comprobados desde el servidor: `fimi`, `analisis`, `vivienda` y `municipal` responden **200**. Nginx sigue **active**. No se tocaron Docker, PM2, AdGuard, DNS ni TLS.

## Integridad

- B11, B13 y B14 no se han modificado.
- Los 10 incidentes demo siguen `demo: true`.
- No se ejecutaron ingestas ni se añadieron fuentes.
- `make lint`: OK.
- `make test`: **19 passed**.

## Git

- **15 commits locales** conservados.
- Cambios B16 y este informe pendientes de commit.
- No hay push.
- No se ha ejecutado ninguna operación adicional de despliegue.

## Incidencias

- `/mapa.html` usa **meta refresh**, no HTTP 301. Es la limitación aceptada en B17.
- El `curl` local del servidor sin `-k` puede fallar por la cadena CA local; `ssl_verify_result=0` y los clientes públicos funcionan.
