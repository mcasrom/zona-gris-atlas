# Reconocimiento del servidor · 2026-11

**Fecha:** 2026-11-06 13:17–13:20 UTC  
**Host:** `ubuntu-4gb-nbg1-1` (`deploy@178.105.80.193`, WireGuard)  
**Modo:** solo lectura. No se reinició, paró ni modificó ningún servicio.

## 1. Recursos

| Recurso | Medición |
|---|---:|
| RAM total | 3.819 MB |
| RAM usada | 1.589 MB |
| RAM libre | 335 MB |
| RAM disponible | 2.230 MB |
| Swap total | 2.047 MB |
| Swap usado | 1.108 MB |
| Swap libre | 939 MB |
| Disco raíz | 38 GB · 22 GB usados · **15 GB libres (60 %)** |
| CPU | 2 vCPU |
| Carga media | 0,42 / 0,43 / 0,47 |
| Uptime | 21 días |

Muestras de 30 s: disponible entre **2.217 y 2.235 MB**. No hay serie histórica suficiente para afirmar un pico real; la cifra es una foto de ventana corta.

## 2. Servicios existentes

- **Docker:** `myip-server` (65,8 MB), `wg-easy` (12,1 MB), `uptime-kuma` (120,2 MB).
- **PM2:** 22 procesos; **21 online**, `radar-email-api` **stopped** (API antigua de FIMI, retirada por Nginx).
- **systemd:** 25 servicios running; entre ellos `nginx`, `postgresql@16-main`, `docker`, `AdGuardHome`, `fail2ban`, `pm2-deploy`, `pm2-root`, `cron`, `ssh`.
- **No existe** ningún proceso, unidad ni vhost de `zonagris`/`zona-gris-atlas`.

Consumo PM2 observado: ~442 MB sumando RSS; Docker ~198 MB. El resto es sistema, caché, PostgreSQL y servicios de fondo.

## 3. Web y puertos

- **Servidor web:** Nginx **1.24.0** (Ubuntu), activo.
- **TLS:** Let's Encrypt gestionado por **Certbot**; `certbot.timer` activo, última ejecución 07:27 UTC, próxima 18:58 UTC. **28 certificados** vivos. No hay `cloudflared` local.
- **Proxy/CDN:** Cloudflare en las zonas que ya lo usan; no se toca.
- **Puertos públicos:** 22/2222 (SSH), 80/443 (Nginx), 53/8081 (AdGuardHome, limitado a WireGuard).
- **Puertos internos:** 3010, 3015, 3017–3032, 3310/3320, 3420, 51821, 5432, 8080, 8100, 8201, 8600, 8700/8710, 8801, 9099.
- **Vhosts existentes:** 30 nombres, incluidos `viajeinteligencia.com`, `pruebapublica.com`, `fimi`, `municipal`, `nearme`, `radar`, `elecciones29n`, `vivienda`, `gcmotors-workshop`. No hay conflicto con un dominio nuevo si se elige uno libre.

## 4. Historial de memoria

`journalctl -k --since "14 days ago"` no muestra ningún evento `oom` ni `killed process` en los últimos 14 días. Histórico anterior del servidor: hubo incidentes OOM en octubre; no se repiten en esta ventana. El swap usado (**1.108 MB**) indica presión de memoria, así que la ausencia de OOM no equivale a holgura.

## 5. Riesgos detectados

1. **Swap alto:** 1,1 GB usados; un lote nuevo de 1.200 MB cabe ahora, pero deja poco margen si coincide con picos de otros servicios.
2. **Ventana nocturna ocupada:** hay tareas diarias a las 03:00, 03:05, 03:12, 03:30 y 03:35 (país, retención, backups, comisiones, SEO). **No conviene usar 03:30.**
3. **TLS del dominio nuevo:** no existe certificado para `[DECIDIR: dominio]`; habrá que emitirlo siguiendo el flujo Certbot/Cloudflare existente, sin tocar los certificados actuales.
4. **Nginx:** la configuración global mantiene `TLSv1` y `TLSv1.1`; no es un cambio de esta fase, pero es una deuda de seguridad existente.
5. **Riesgo de vhost:** cualquier nuevo `server_name` debe convivir con los 30 actuales y no capturar tráfico por defecto.
6. **El lote no debe entrenar ni cargar modelos:** el servidor solo debe ingerir, deduplicar y escribir en sombra.

## 6. Viabilidad de un lote de 1.200 MB

**Sí, con condiciones.** Con 2.217–2.235 MB disponibles, un proceso limitado por `MemoryMax=1200M` cabe, pero consume más de la mitad del margen actual. Antes de activarlo hay que:

- ejecutarlo fuera de la ventana 03:00–03:40;
- mantener `MemoryMax=1200M`, `Nice=10` e `IOSchedulingClass=idle`;
- medir el RSS real de la primera pasada y no asumir que 1.200 MB es el uso normal;
- vigilar swap y `oom_watch`; si el pico se acerca al límite, parar y replantear.

Recomendación: **no** programarlo a las 03:30. La franja con menos tareas diarias observadas es **04:45–05:20 Europe/Madrid** (03:45–04:20 UTC), evitando las tareas de las 03:00–03:40 y las de las 04:15–04:40. No hay serie histórica de carga suficiente; la elección se basa en el calendario de cron, no en una medición de 14 días.

## 7. Decisiones pendientes antes del Paso B

- `[DECIDIR: dominio]`
- `[DECIDIR: nombre público del autor]`
- `[DECIDIR: contacto]`
- `[DECIDIR: KOFI_URL]`
- `[DECIDIR: licencia de datos]`
- `[DECIDIR: condiciones y activación de cada fuente]`
- `[DECIDIR: ventana definitiva del lote, propuesta 04:45 Europe/Madrid]`
- `[DECIDIR: retención de textos crudos, propuesta 30 días]`
