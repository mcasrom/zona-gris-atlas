# Contribuir

Gracias por querer mejorar el atlas. La prioridad es la trazabilidad, no el volumen.

## Antes de abrir una issue

- Busca si ya existe una issue similar.
- Para una fuente, usa la plantilla `proponer-fuente` e indica la licencia y las condiciones de uso.
- Para una ficha, usa `corregir-ficha` e incluye el id y la fuente que sostiene la corrección.
- Para un incidente nuevo, usa `reportar-incidente`; no publiques datos personales.

## Pull requests

- Un cambio, un motivo y un enlace a la fuente.
- Código e identificadores en inglés; documentación e interfaz en español.
- Sin secretos, `.env`, bases de datos, modelos `.onnx` ni datos crudos.
- Los datos de demostración llevan `demo: true`.
- Ejecuta `make lint` y `make test` antes de enviar.
- No cambies el umbral de evaluación sin una discusión explícita.

## Atribución

No se aceptan cambios que atribuyan autoría por inferencia. Una atribución debe venir con `attributed_by`, `attributed_by_type`, `source_url` y `confidence`.

## Conducta

Sé concreto, cita fuentes y discute el dato, no a la persona. No se aceptan acusaciones sin evidencia ni datos personales.
