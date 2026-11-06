# B2 · Auditoría de despliegue

**Fecha:** 2026-11-06  
**Alcance:** local. **No se conectó al servidor, no se ejecutó `--apply` real, no se hizo push.**  
**Commit de partida:** `a3d7d06`.

## 1. Resultado ejecutivo

El script queda más seguro, pero **no está listo para B3** por dos motivos:

1. La web publicada localmente todavía contiene el dominio candidato `zonagris.viajeinteligencia.com` en canonical, OG, sitemap, robots y feed. Debe reconstruirse con el dominio definitivo.
2. El dominio, el autor público y el TLS del dominio nuevo siguen pendientes. El vhost y Certbot no se pueden cerrar sin ellos.

**Estado:** B3 bloqueado hasta resolver esos puntos.

## 2. Auditoría del script

| Comprobación | Resultado |
|---|---|
| Dry-run por defecto | **OK**: no conecta; imprime el plan completo |
| `--apply` obligatorio | **OK**: sin `--apply` no hay SSH, rsync ni symlink |
| Borrados peligrosos | **OK**: `--delete` solo dentro de un release nuevo; se aborta si el release ya existe |
| Rutas | **OK**: `ZG_REMOTE_ROOT` debe ser absoluto, no `/` y no contener `..` |
| Releases | **OK**: `AAAAMMDDTHHMMSS` bajo `releases/` |
| `current` seguro | **OK**: se actualiza solo después de verificar ficheros requeridos |
| Errores de rsync | **OK**: `set -e`; la prueba con rsync rc=23 dejó `current` intacto |
| Despliegue incompleto | **OK**: comprueba `index.html`, `mapa.html`, `404.html`, CSS y JS antes del symlink |
| Versiones anteriores | **OK**: no se borran releases antiguos |
| Rollback | **Corregido**: ordenaba por mtime y elegía mal; ahora ordena por nombre de release y va al inmediatamente anterior |
| Rollback en el más antiguo | **OK**: aborta sin cambiar `current` |
| Concurrencia | **Añadido** `flock` local para impedir dos despliegues simultáneos |
| Dominio | **Añadida** puerta: `--apply` exige `ZG_DOMAIN` y que la web contenga ese dominio; rechaza `__DOMAIN__` |

### Correcciones aplicadas

- `flock` en `/tmp/atlas-zonagris-deploy.lock`.
- Validación de `ZG_REMOTE_ROOT`.
- Rollback por orden de release, no por mtime.
- Aborto si `current` no existe o es el release más antiguo.
- Verificación de ficheros requeridos antes de mover `current`.
- Aborto si el release destino ya existe.
- Puerto de dominio: `ZG_DOMAIN` obligatorio para `--apply`.
- Dry-run sin conexión: no ejecuta `rsync -n` remoto, imprime el plan.

### Pruebas locales realizadas

Con `PATH` falso para `ssh`/`rsync`, `SERVER=dummy` y un `ZG_REMOTE_ROOT` en `/tmp`:

- dry-run: **rc=0**, sin release.
- dos `--apply`: dos releases, `current` apunta al segundo.
- `--rollback`: `current` pasa al primero.
- segundo rollback: **rc=1**, `current` no cambia.
- rsync simulado con error 23: **rc=23**, `current` intacto.
- `--apply` con web que contiene el dominio viejo: **rc=1**, sin release.
- `--apply` con `ZG_DOMAIN=test.example` sobre una copia temporal saneada: **OK**.

## 3. Auditoría de Nginx

| Comprobación | Resultado |
|---|---|
| `__DOMAIN__` sustituible | **OK**: 2 apariciones, solo en la plantilla |
| Compatibilidad con 30 vhosts | **No verificable en servidor**; el `server_name` será único cuando se sustituya |
| Cabeceras | **OK**: HSTS, `nosniff`, `Referrer-Policy`, `Permissions-Policy`, CSP |
| TLS 1.2/1.3 | **OK** en el vhost nuevo |
| Cambios globales | **Ninguno**; `nginx.conf` global no se toca |
| Certbot | **Pendiente**: requiere dominio, DNS y certificado; no se emite nada |
| Cloudflare/mTLS | **Pendiente**: si el dominio va proxied, hay que añadir el snippet de origen que use el servidor |

**Observaciones:** la CSP permite `style-src 'unsafe-inline'` porque hay CSS crítico y atributos `style` en el HTML. Es una concesión necesaria para el diseño actual; no se elimina sin refactorizar estilos. No se ha ejecutado `nginx -t` contra el servidor ni se ha aplicado la plantilla.

## 4. Auditoría de publicación

| Comprobación | Resultado |
|---|---|
| Solo 10 incidentes demo | **OK** |
| Todos `demo: true` | **OK** (10/10) |
| Datos reales | **No hay** |
| Secretos | **No encontrados** en `web`, `config`, `deploy`, `scripts`, `docs` |
| Contacto en web | **No aparece** |
| `__DOMAIN__` en web | **0 apariciones** |
| Dominio candidato viejo | **Fallo**: 9 archivos (`index`, `mapa`, `metodologia`, `limites`, `fuentes`, `privacidad`, `feed`, `sitemap`, `robots`) contienen `zonagris.viajeinteligencia.com` |
| Recursos externos | **OK**: solo enlaces, canonical, OG y JSON-LD; no hay scripts, CSS ni imágenes remotas |
| Coherencia de marca | **Pendiente**: la web aún dice «Zona Gris»; el nombre decidido es «Atlas Zona Gris» |

La web **no debe desplegarse** hasta reconstruirla con el dominio y el nombre definitivos.

## 5. Tests

- `make lint`: **OK**.
- `make test`: **13 passed**.
- `git diff --check`: **OK**.
- Sin peticiones de red en los tests.

## 6. Riesgos pendientes

1. Dominio sin decidir; sin DNS ni TLS.
2. Web con dominio candidato antiguo; reconstrucción obligatoria.
3. Vhost no probado contra Nginx real; no se toca el servidor.
4. Certbot nuevo pendiente; no se solicita nada.
5. TLS global con TLS 1.0/1.1; solo hay propuesta, no cambio.
6. CSP con `style-src 'unsafe-inline'`; documentado como concesión.
7. Memoria: 2.230 MB disponibles y swap usado; el lote de 1.200 MB debe medirse.

## 7. Condiciones para B3

1. `[DECIDIR: dominio definitivo]`.
2. `[DECIDIR: autor público]`.
3. Verificar el buzón antes de publicar el contacto.
4. Actualizar `config/site.yaml` con el dominio y reconstruir `web`.
5. Comprobar que `web` no contiene el dominio viejo ni `__DOMAIN__`.
6. Copiar el vhost actual y presentar el diff del vhost nuevo.
7. Emitir certificado por el flujo Certbot/DNS existente.
8. Backup, `nginx -t`, `--dry-run`, autorización y solo después `--apply`.
9. Verificar 200, cabeceras, CSP y rollback.

## 8. Archivos afectados

- `scripts/deploy_web.sh` — correcciones de seguridad y rollback.
- `docs/B2-AUDITORIA-2026-11.md` — este informe.
- No se modificó ningún archivo del servidor.
