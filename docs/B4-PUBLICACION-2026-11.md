# B4 · Preparación de publicación

**Fecha:** 2026-11-06  
**Estado:** la primera ejecución de `--apply` falló antes de crear la release. **No hay web publicada, no hay `current` y no se ha hecho push.**

## 1. Corrección del pie

Se ha eliminado la referencia textual a `viajeinteligencia.com` del pie de `web/index.html`.

Sustitución aplicada:

> Parte del ecosistema de Prueba Pública. Complementa a FIMI Radar.

Búsqueda posterior en `web/`: **0 referencias** a `viajeinteligencia.com`.

## 2. Web

- Dominio: `https://zonagris.pruebapublica.com`.
- **10 incidentes**, todos con `demo: true`.
- Contacto `info.atlaszonagris@pruebapublica.com`: no aparece en la web.
- Sin `__DOMAIN__` en la web.
- Canonical, Open Graph, sitemap, robots y feed apuntan al dominio correcto.
- Sin secretos ni recursos externos cargados.
- `make lint`: **OK**.
- `make test`: **19 passed** (13 anteriores + 6 de despliegue).

## 3. Script de despliegue

Cambios realizados en `scripts/deploy_web.sh`:

1. **Raíz de proyecto:** solo se acepta `/var/www/atlas-zonagris`. Cualquier otra ruta se rechaza salvo `ZG_ALLOW_CUSTOM_REMOTE_ROOT=1` en pruebas locales.
2. **Rollback inicial:** si solo existe una release y `current` apunta a ella, `--rollback --apply` elimina `current` y deja el sitio sin release activa. No borra la release, para permitir recuperación.
3. **Fallo posterior al enlace:** si la validación después de crear `current` falla, restaura el `current` anterior o lo elimina si era la primera publicación.
4. Se mantiene:
   - dry-run por defecto sin conexión;
   - `--apply` obligatorio;
   - `ZG_DOMAIN` obligatorio y dominio presente en la web;
   - releases fechados, `flock`, comprobación de ficheros y rsync con `set -e`;
   - no se borran releases anteriores.

### Criterio de recuperación de la primera publicación

- Si falla la copia: no se crea `current`.
- Si falta un fichero requerido: no se crea `current`.
- Si falla la comprobación posterior al symlink: se restaura el estado anterior; si no había, se elimina `current`.
- Si se ejecuta rollback tras la primera release: se elimina `current`; la release queda en disco para diagnóstico y recuperación.
- Nginx y HTTPS no se tocan desde el script.

## 4. Pruebas del script

Nuevo `tests/test_deploy_web.py` con 6 casos:

1. Primer despliegue correcto.
2. Fallo de copia en el primer despliegue.
3. Fallo de validación por falta de fichero.
4. Rollback inicial sin release anterior: elimina `current`, conserva la release.
5. Rollback normal con dos releases: vuelve a la anterior.
6. Rechazo de una raíz remota ajena al proyecto.

Resultado: **19 passed**; sin red, con `ssh` y `rsync` simulados en directorio temporal.

## 5. Dry-run

Ejecutado:

```bash
SERVER=178.105.80.193 \
ZG_DOMAIN=zonagris.pruebapublica.com \
./scripts/deploy_web.sh
```

Resultado: plan correcto, **sin conexión**, sin crear releases, sin tocar `/var/www` ni Nginx.

## 6. Estado del servidor

- `/var/www/atlas-zonagris`: **no existe todavía**.
- `current`: no existe.
- HTTPS: **404** esperado, sin web.
- Nginx, TLS, DNS, Docker, PM2 y AdGuard: **sin cambios en esta fase**.
- `--apply`: **no ejecutado**.

## 7. Git

- 15 commits locales previos conservados.
- Nuevos cambios locales: pie, script, tests y este informe.
- Sin push.
- Sin reescritura de historial.
- Informe anterior conservado y actualizado.

## 8. Condición para B4 definitivo

1. Revisar el diff de `scripts/deploy_web.sh`.
2. Autorizar `--apply` de forma independiente.
3. Ejecutar el primer despliegue.
4. Verificar 200, canonical, OG, sitemap, robots, feed, mapa, cabeceras y demo.
5. Si falla, ejecutar el rollback inicial y comprobar que `current` desaparece y HTTPS vuelve a 404.

No se ha publicado nada.


## 9. Intento de publicación B4

Comando ejecutado:

```bash
SERVER=178.105.80.193 ZG_DOMAIN=zonagris.pruebapublica.com \
  ./scripts/deploy_web.sh --apply
```

Error literal:

```text
mkdir: cannot create directory '/var/www/atlas-zonagris': Permission denied
RC=1
```

Consecuencias:

- No se creó `/var/www/atlas-zonagris`.
- No se creó ninguna release.
- No se creó `current`.
- No se copió contenido.
- Nginx, TLS, DNS, Docker, PM2 y AdGuard quedaron intactos.
- HTTPS sigue devolviendo **404**.
- `--apply` no se reintentó.

Causa: el usuario `deploy` no tiene permiso para crear el directorio raíz bajo `/var/www`. Es un problema de provisión del destino, no del script ni de rsync.

Operación necesaria, **no ejecutada**, pendiente de autorización:

```bash
sudo install -d -o deploy -g deploy -m 0755 /var/www/atlas-zonagris
sudo install -d -o deploy -g deploy -m 0755 /var/www/atlas-zonagris/releases
```

Después habría que repetir el dry-run y autorizar un nuevo `--apply`.


## 10. Preparación del directorio de publicación

Inspección previa:

- Usuario conectado: `deploy` (`uid=1000`, `gid=1000`).
- Usuario/grupo `deploy` existen.
- `/var/www`: `root:root 755`, sin cambios.
- `/var/www/atlas-zonagris`: **no existía**.

Operaciones ejecutadas, solo las autorizadas:

```bash
sudo install -d -o deploy -g deploy -m 0755 /var/www/atlas-zonagris
sudo install -d -o deploy -g deploy -m 0755 /var/www/atlas-zonagris/releases
```

Estado posterior:

```text
deploy:deploy 755 /var/www/atlas-zonagris
deploy:deploy 755 /var/www/atlas-zonagris/releases
root:root     755 /var/www
```

- `deploy` puede escribir en ambos directorios.
- `releases/`: **vacío**.
- `current`: **no existe**.
- No se crearon ficheros de prueba.
- Nginx, TLS, DNS, Docker, PM2 y AdGuard: **sin cambios**.

Dry-run posterior:

```bash
SERVER=178.105.80.193 ZG_DOMAIN=zonagris.pruebapublica.com \
  ./scripts/deploy_web.sh
```

Resultado: destino correcto, **sin conexión, sin releases, sin `current`**, sin modificar `/var/www`.

**No se ha ejecutado `--apply`.** La publicación sigue pendiente de nueva autorización.


## 11. Publicación efectiva

**Fecha:** 2026-11-06 14:13 UTC.

Comando:

```bash
SERVER=178.105.80.193 ZG_DOMAIN=zonagris.pruebapublica.com \
  ./scripts/deploy_web.sh --apply
```

Resultado: **RC=0**.

- Release: `/var/www/atlas-zonagris/releases/20261106T141308Z`
- `current` → esa release.
- `index.html` local y remoto: mismo SHA-256 (`b808e052...`).
- Release anterior: no existía; se trata de la primera release.
- Rollback disponible: elimina `current` y deja el sitio sin contenido si se autoriza; el release se conserva.

## 12. Verificación pública

| Recurso | Resultado |
|---|---|
| HTTP | **301 → HTTPS** |
| HTTPS | **200** |
| Certificado | **CN zonagris.pruebapublica.com**, Let's Encrypt, válido hasta 2027-02-04 |
| Verificación TLS | `ssl_verify_result=0` |
| `/` | 200 |
| `/mapa.html` | 200 |
| `/metodologia.html` | 200 |
| `/limites.html` | 200 |
| `/fuentes.html` | 200 |
| `/privacidad.html` | 200 |
| `/404.html` | 200 |
| `/no-existe` | **404** |
| JSON de incidentes | 200 |
| Mapa SVG | 200 |
| CSS y JS | 200 |
| `sitemap.xml` | 200 |
| `robots.txt` | 200 |
| `feed.xml` | 200 |
| `site.webmanifest` | 200 |
| Demo | **10/10 `demo: true`** |
| `viajeinteligencia.com` en web | **0** |
| Contacto en web | **0** |
| `__DOMAIN__` en web | **0** |

Cabeceras comprobadas: HSTS, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` y CSP.

## 13. Incidencia pendiente

No existe una página `/avisos.html` en la v0.1. B4 pedía comprobar «método, fuentes, privacidad y avisos». Las tres primeras están publicadas; la página de avisos no forma parte del árbol actual y no se ha añadido sin autorización. Queda como decisión de producto.

## 14. Estado final

- Web demo: **publicada**.
- `current`: release `20261106T141308Z`.
- Nginx/TLS: sin cambios adicionales.
- Docker/PM2/AdGuard: sin cambios.
- Push: **no realizado**.
- Commits locales: **15**, conservados.
- Incidencias: página de avisos ausente.
