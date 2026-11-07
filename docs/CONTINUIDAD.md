# Continuidad del proyecto

## Responsable

El proyecto lo mantiene **Miguel Castillo** como mantenedor único. No hay una
organización detrás ni un equipo de guardia. Esta nota existe para que la
continuidad no dependa de conocimiento tácito.

## Qué debe sobrevivir

1. **Código y datos**: repositorio de GitHub y bundles de `scripts/backup.sh`.
2. **Web**: release estática en el servidor; las releases anteriores se
   conservan para rollback.
3. **Dominio y TLS**: `zonagris.pruebapublica.com`.
4. **Fuentes**: registro en `config/sources.yaml` y condiciones de uso.
5. **Decisiones**: `CHANGELOG.md`, `docs/` y los informes de auditoría.

## Si el proyecto se detiene

- El repositorio y los datos publicados siguen disponibles con su licencia.
- La web puede quedar congelada; se debe indicar la fecha del último registro y
  no presentar la captura automática como si siguiera viva.
- No se debe transferir el dominio sin conservar el archivo y la atribución.
- Cualquier persona que retome el proyecto debe revisar primero las condiciones
  de las fuentes y no reactivar capturas sin comprobarlas.

## Copia de seguridad

`scripts/backup.sh` crea un `git bundle` local y conserva 10 copias. GitHub es la
copia principal. **Falta una copia off-site verificada**: debe añadirse un destino
externo (otra máquina u object storage) y probar una restauración completa. Hasta
que exista, la continuidad depende de GitHub y del disco local.

## Restauración mínima

```bash
git clone https://github.com/mcasrom/zona-gris-atlas.git
cd zona-gris-atlas
git bundle verify "$HOME/backups/zona-gris-atlas/<bundle>"  # si se usa el bundle
make setup
make test
make web
```

La web se sirve desde `web/`; el despliegue del servidor está en
`deploy/server_update.sh` y `scripts/deploy_web.sh`.
