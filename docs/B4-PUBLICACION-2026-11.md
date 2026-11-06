# B4 · Preparación de publicación

**Fecha:** 2026-11-06  
**Estado:** preparado para revisión. **No se ha ejecutado `--apply`, no se ha publicado la web y no se ha hecho push.**

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

- 11 commits locales previos conservados.
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
