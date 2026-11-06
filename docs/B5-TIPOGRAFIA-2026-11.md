# B5 · Corrección tipográfica de la portada

**Fecha:** 2026-11-06  
**Estado:** **desplegada** en producción. Sin push.

## Problema

El `h1` de la portada usaba:

```css
font-size: clamp(2.8rem, 6.7vw, 6.7rem);
line-height: .94;
```

A 1366 px el titular llegaba a ~91 px y ocupaba cinco líneas. El bloque completo no cabía en la primera pantalla.

## Cambio aplicado

`web/assets/css/styles.css`:

```diff
-h1 { font-stretch: 125%; font-size: clamp(2.8rem, 6.7vw, 6.7rem); line-height: .94; margin: 0 0 24px; }
+h1 { font-stretch: 125%; font-size: clamp(2rem, 4.2vw, 4.25rem); line-height: .98; letter-spacing: -0.03em; max-width: 14ch; margin: 0 0 20px; }

-.hero { padding: 76px 0 72px; }
+.hero { padding: 48px 0 52px; }

-.hero-grid { grid-template-columns: minmax(0, .9fr) minmax(380px, 1.1fr); gap: 52px; }
+.hero-grid { grid-template-columns: minmax(0, .95fr) minmax(380px, 1.05fr); gap: 40px; }

-  h1 { font-size: clamp(2.5rem, 13vw, 4rem); }
+  h1 { font-size: clamp(2rem, 8.2vw, 3rem); max-width: 15ch; }
```

También se retiró la regla de tamaño antigua del CSS crítico inline de las páginas, que sobreescribía la hoja externa. No se cambió el texto, el mapa, las fuentes ni los datos.

## Capturas

En `docs/capturas/`:

- `b5-before-1366x768.png` / `b5-after-1366x768.png`
- `b5-before-1280x720.png` / `b5-after-1280x720.png`
- `b5-before-390x844.png` / `b5-after-390x844.png`
- `b5-before-360x800.png` / `b5-after-360x800.png`

## Resultado visual

| Tamaño | Antes | Después |
|---|---|---|
| 1366×768 | titular ~91 px, 5 líneas, no cabe completo | titular ~57 px, 4 líneas, visible completo |
| 1280×720 | titular desbordado verticalmente | completo y proporcionado |
| 390×844 | titular de 5 líneas muy alto | 5 líneas, legible, sin desbordes |
| 360×800 | titular al límite | 4–5 líneas, sin scroll horizontal |

El mapa sigue visible en escritorio; en móvil queda bajo el bloque editorial, como antes. No se ha añadido JavaScript.

## Validación

- `make lint`: **OK**.
- `make test`: **19 passed**.
- Sin cambios en incidentes, datos, mapa, Nginx, TLS, DNS ni despliegue.
- Web pública sin cambios: la corrección está solo en local hasta autorización independiente.
- 15 commits locales conservados; sin push.


## Despliegue B5

**Fecha:** 2026-11-06 14:21 UTC.

Comando:

```bash
SERVER=178.105.80.193 ZG_DOMAIN=zonagris.pruebapublica.com \
  ./scripts/deploy_web.sh --apply
```

- Release: `/var/www/atlas-zonagris/releases/20261106T142116Z`
- `current`: apunta a la release nueva.
- Release anterior conservada: `20261106T141308Z`.
- `styles.css` local y remoto: mismo SHA-256 (`17ed6e2d...`).
- CSS público servido con la regla nueva `clamp(2rem, 4.2vw, 4.25rem)`.
- Cabecera del CSS: sin caché (`no-cache`); sin versión antigua visible.

## Verificación pública

| Recurso | Resultado |
|---|---|
| HTTP | 301 → HTTPS |
| HTTPS portada | 200 |
| CSS actualizado | 200, regla nueva |
| Mapa y recursos | 200 |
| Canonical, OG, sitemap, robots, feed | correctos |
| Incidentes | 10/10 `demo: true` |
| Cabeceras | HSTS, `nosniff`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, CSP |
| `viajeinteligencia.com` | 0 |
| Contacto | 0 |
| `__DOMAIN__` | 0 |

Capturas públicas:

- `docs/capturas/b5-public-1366x768.png`
- `docs/capturas/b5-public-1280x720.png`
- `docs/capturas/b5-public-390x844.png`
- `docs/capturas/b5-public-360x800.png`

El titular se lee completo y no hay scroll horizontal en los cuatro tamaños.

## Estado final

- Web pública: **actualizada**.
- Rollback: disponible hacia `20261106T141308Z`; no ejecutado.
- Nginx, TLS, DNS, Docker, PM2 ni AdGuard: sin cambios.
- Push: **no realizado**.
- 15 commits locales conservados.
