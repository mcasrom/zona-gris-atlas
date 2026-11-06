# Seguridad

## Alcance

La v0.1 es un pipeline local y una web estática. No hay autenticación, base de datos pública ni formularios.

## Cómo reportar

Abre una issue privada de seguridad en el repositorio si está disponible. Si no, escribe al contacto editorial cuando exista. No publiques una prueba de concepto con datos personales o secretos.

## Reglas

- No se aceptan credenciales en el repositorio.
- `.env` nunca se versiona.
- Las dependencias se revisan con `pip-audit` en CI (no bloqueante).
- No se ejecutan modelos descargados automáticamente.
- Las fuentes externas se tratan como no confiables.
