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

El alojamiento registra peticiones HTTP como cualquier servidor. La aplicación no añade identificadores, píxeles ni almacenamiento local.

## Retención

- **Logs HTTP del servidor:** 14 días. Se usan para seguridad y diagnóstico, no para perfilado.
- **Candidatos y caché de captura:** 30 días como máximo; los registros publicados y sus fuentes se conservan.
- **Datos personales:** no se recogen formularios, cuentas, cookies ni analítica. No hay base de datos de usuarios.
- **Copias:** los bundles locales conservan 10 versiones; no se envían a terceros.

No se guardan direcciones IP en una base propia ni se cruzan con otros servicios.

## Resumen semanal

- **Dato:** email, fecha, página de origen y UTM. No se guarda la IP en la base.
- **Finalidad:** enviar el resumen semanal.
- **Base jurídica:** consentimiento; doble confirmación obligatoria.
- **Conservación:** mientras la suscripción esté activa. Las solicitudes pendientes se borran a los 30 días.
- **Baja:** enlace en cada correo; se marca como baja y no se vuelve a escribir.
- **Encargado:** Resend para el envío. No se cede a terceros.
- **Lista separada:** no se mezcla con FIMI, el blog ni el hub.
