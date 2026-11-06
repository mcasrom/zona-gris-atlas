# Privacidad

## Web

- Sin cookies.
- Sin rastreadores.
- Sin analítica activa por defecto.
- Sin formularios ni boletín en la v0.1.
- Sin recursos remotos: fuentes, CSS, JS, mapa y datos se sirven desde el mismo dominio.

## Datos del atlas

Se publican hechos y fuentes públicas. No se publican datos personales innecesarios ni perfiles de individuos. Las organizaciones solo se citan cuando una fuente pública las nombra y la ficha pasa revisión humana.

## Ingesta

La caché local de GDELT y RSS se guarda en `data/` (ignorada por git). No se envían textos a servicios de terceros. Los modelos de embeddings no se descargan automáticamente.

## Registros del servidor

El alojamiento puede registrar peticiones HTTP como cualquier servidor. La aplicación no añade identificadores, píxeles ni almacenamiento local. La política de retención de logs del servidor queda pendiente de revisión.
