# A2 · Revisión de riesgos y preparación

**Fecha:** 2026-11-06  
**Servidor:** `178.105.80.193` (solo lectura)  
**Estado:** no se ha aplicado ningún cambio en el servidor.

## 1. Resumen del reconocimiento

- RAM total: **3.819 MB**; disponible: **2.230 MB**; swap usado: **1.108 MB**.
- Disco: **15 GB libres (60 %)**.
- CPU: **2 vCPU**; carga actual: **0,42 / 0,43 / 0,47**.
- Servicios: 3 contenedores Docker, 21/22 procesos PM2 online y 25 servicios systemd.
- Nginx **1.24.0** con Certbot y 28 certificados; **no hay `cloudflared` local**.
- `journalctl -k` de 14 días: **sin OOM**. El swap alto sigue siendo un riesgo.

## 2. TLS global: propuesta, no aplicada

La configuración global mantiene protocolos antiguos:

```diff
--- /etc/nginx/nginx.conf (propuesta)
+++ /etc/nginx/nginx.conf (propuesta)
@@
-ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
+ssl_protocols TLSv1.2 TLSv1.3;
```

**Efectos:** los clientes modernos no cambian; pueden fallar clientes muy antiguos o integraciones heredadas. No afecta a certificados ni a vhosts. Antes de aplicarlo habría que:

1. copiar el fichero a `/etc/nginx/backups/<fecha>/`;
2. ejecutar `sudo nginx -t`;
3. recargar con `systemctl reload nginx` —nunca reiniciar—;
4. vigilar logs y errores TLS.

**No se aplica en esta fase.** La plantilla nueva ya fuerza TLS 1.2/1.3 en el vhost de Atlas, pero no cambia la configuración global.

## 3. Vhosts, TLS y DNS

- 30 `server_name` existentes; no hay conflicto con un dominio nuevo libre.
- Certbot gestiona los certificados y su renovación; no hay que instalar nada.
- El dominio sigue pendiente: **`[DECIDIR: dominio público definitivo]`**.
- Sin dominio no se puede emitir certificado, crear DNS ni escribir un vhost real.
- El correo `info.atlaszonagris@pruebapublica.com` **no se publica** hasta verificar que el buzón existe y recibe.

## 4. Memoria y ventana del lote

- 2.230 MB disponibles permiten un proceso con `MemoryMax=1200M`, pero dejan ~1 GB de margen y el swap ya está al 54 %.
- El lote debe ser **secuencial**, con `Nice=10`, `IOSchedulingClass=idle`, `TimeoutStartSec` y RSS medido.
- **No usar 03:30**: hay tareas a las 03:00, 03:05, 03:12, 03:30 y 03:35.
- Franja propuesta: **04:45–05:20 Europe/Madrid**, antes de la tarea de las 05:50. No hay histórico suficiente; es una decisión por calendario de cron.

## 5. Fuentes candidatas (todas desactivadas)

`config/sources.yaml` contiene el registro ampliado con `licencia`, `licencia_url`, `fecha_revision`, `limite_ritmo` y `justificacion`.

| Fuente | Tipo | Estado | Licencia/revisión |
|---|---|---|---|
| GDELT DOC API | API | desactivada | `[DECIDIR]` |
| EuRepoC | Web | desactivada | `[DECIDIR]` |
| CERT-EU | RSS | desactivada | `[DECIDIR]` |
| CCN-CERT | RSS | desactivada | `[DECIDIR]` |
| ENISA | RSS | desactivada | `[DECIDIR]` |
| CISA | RSS | desactivada | `[DECIDIR]` |
| ransomware.live | Web | desactivada | `[DECIDIR]` |
| GPSJam | Web | desactivada | `[DECIDIR]` |
| Eurocontrol | RSS | desactivada | `[DECIDIR]` |
| Hybrid CoE | RSS | desactivada | `[DECIDIR]` |
| EUvsDisinfo | RSS | desactivada | `[DECIDIR]` |
| EEAS | RSS | desactivada | `[DECIDIR]` |

No se ha consultado ninguna URL ni se ha ejecutado ingesta.

## 6. Política de retención propuesta

- Texto completo: **7 días**; después se borra y solo quedan URL, título, hash, idioma, fecha, fuente, identificador y una cita de hasta 15 palabras.
- Metadatos y agregados: se conservan mientras sean necesarios.
- Almacenamiento total del proyecto: objetivo **< 2 GB**; alerta **1,2 GB**; bloqueo de ingesta **1,8 GB**.
- `zonagris purge` y su prueba quedan para el bloque D, tras autorización independiente.
- No se borran datos de otros servicios para liberar espacio.

## 7. Archivos locales preparados en B1

- `scripts/deploy_web.sh`: rsync, releases fechados, `current`, dry-run por defecto, `--apply` y `--rollback`.
- `deploy/nginx.conf.example`: plantilla con `__DOMAIN__`, `__TLS_CERT__` y `__TLS_KEY__`; no contiene un dominio real.
- `config/sources.yaml`: 12 fuentes candidatas, todas `enabled: false`.
- `config/site.yaml`: nombre público «Atlas Zona Gris»; contacto pendiente de verificación; dominio pendiente.

## 8. Decisiones abiertas

- `[DECIDIR: dominio público definitivo]`
- `[DECIDIR: nombre o identificación pública del autor]`
- Verificar `info.atlaszonagris@pruebapublica.com` antes de publicarlo.
- `[DECIDIR: KOFI_URL]`
- Revisar y aprobar la licencia de datos (propuesta CC BY 4.0) y las condiciones de cada fuente.
- `[DECIDIR: ventana definitiva del lote]`
- `[DECIDIR: retención definitiva de textos]`
