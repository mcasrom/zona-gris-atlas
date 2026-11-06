# B3 · Preparación de despliegue

**Fecha:** 2026-11-06  
**Dominio oficial:** `https://zonagris.pruebapublica.com`
**Servidor:** `178.105.80.193`  
**Estado:** preparación local y revisión remota en solo lectura. **No se ha desplegado, ni modificado Nginx, ni emitido certificado, ni hecho push.**

## 1. B3.1 · Reconstrucción local

- `config/site.yaml` usa el dominio oficial.
- `make web` reconstruyó todas las páginas, canonical, Open Graph, sitemap, robots y feed.
- La web ya no contiene `__DOMAIN__`.
- El contacto **no aparece** en la web.
- No hay datos reales: **10 incidentes, 10/10 `demo: true`**.
- No hay secretos visibles.
- No hay recursos externos cargados: solo enlaces, canonical, OG y JSON-LD.
- Las páginas locales responden **200**; `404.html` responde 200 como fichero estático y el vhost la usará para 404.
- `make lint`: OK.
- `make test`: **13 passed**.

La marca visible de la web sigue usando el nombre corto «ZONA GRIS»; el nombre de proyecto es «Atlas Zona Gris». No se ha rediseñado la marca en este paso.

## 2. B3.2 · DNS y certificados

Comprobación en el servidor:

```text
getent ahostsv4 zonagris.pruebapublica.com  -> vacío
dig +short @1.1.1.1 zonagris... A                -> vacío
/etc/letsencrypt/live/zonagris...                -> no existe
```

**El dominio no resuelve.** No hay registro A, por tanto:

- no se puede validar HTTP-01;
- no se puede emitir certificado;
- no se puede instalar el vhost TLS;
- **B3.2 queda bloqueado**.

Certbot sigue activo para los certificados existentes; no se ha solicitado ni modificado nada.

## 3. B3.3 · Nginx preparado, no instalado

Archivo: `deploy/zonagris.pruebapublica.com.conf`.

Incluye:

- HTTP 80 con `/.well-known/acme-challenge/` y redirección a HTTPS;
- HTTPS 443 con certificado de `zonagris.pruebapublica.com`;
- `cf-origin.conf`, `block-attacks.conf`, `indexnow.conf`;
- TLS 1.2/1.3;
- HSTS, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` y CSP;
- raíz `/var/www/atlas-zonagris/current` (coincide con `ZG_REMOTE_ROOT`);
- `try_files` y `error_page 404 /404.html`.

No se ha copiado a `sites-available`, no se ha enlazado, no se ha validado con `nginx -t` remoto y no se ha recargado Nginx. No se ha tocado la configuración TLS global.

## 4. B3.4 · Script de despliegue

`scripts/deploy_web.sh` queda preparado:

- dry-run por defecto, sin conexión;
- `--apply` obligatorio;
- `ZG_DOMAIN` obligatorio y comprobación de que la web contiene el dominio;
- releases fechados y `current`;
- `flock`, validación de rutas, comprobación de ficheros y rollback;
- `--rollback` elige el release inmediatamente anterior;
- no borra versiones antiguas.

Comando previsto, **no ejecutado**:

```bash
SERVER=178.105.80.193 ZG_DOMAIN=zonagris.pruebapublica.com \
  ./scripts/deploy_web.sh --apply
```

## 5. Condiciones exactas para autorizar B3

1. Crear el registro A `zonagris.pruebapublica.com -> 178.105.80.193` (gris para HTTP-01; naranja después si se decide).
2. Confirmar resolución pública y desde el servidor.
3. Emitir certificado sin tocar los existentes.
4. Backup de `sites-enabled` a `/etc/nginx/backups/2026-11-06/`.
5. Instalar el vhost, `nginx -t` y `reload` (nunca restart).
6. Ejecutar el despliegue en dry-run y revisar el plan.
7. Autorizar `--apply`.
8. Verificar 200, TLS, cabeceras, canonical, OG, sitemap, robots, feed, mapa y demo.

No se ha ejecutado ninguno de estos pasos.

## 6. Riesgos pendientes

- **DNS ausente:** bloqueo principal.
- **Certificado ausente:** el vhost no puede activarse.
- **`cf-origin.conf`:** presupone el patrón Cloudflare/mTLS del servidor; confirmar si el registro será proxied.
- **CSP:** mantiene `style-src 'unsafe-inline'` por el CSS crítico y atributos de estilo.
- **TLS global:** sigue con TLS 1.0/1.1; no se toca.
- **Marca:** la web usa «ZONA GRIS» como nombre corto; el proyecto es «Atlas Zona Gris».
- **B3.4:** no ejecutado; no hay releases en el servidor.

## 7. Decisiones abiertas

- `[DECIDIR: autor público]`
- Verificar `info.atlaszonagris@pruebapublica.com` antes de publicarlo.
- `[DECIDIR: Cloudflare proxied o DNS-only para el nuevo dominio]`
- `[DECIDIR: KOFI_URL]`
- `[DECIDIR: licencia de datos]`
- `[DECIDIR: condiciones y activación de cada fuente]`
- `[DECIDIR: ventana y retención del lote]`
