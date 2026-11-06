# Atribución

## Regla central

El sistema **no atribuye autoría por su cuenta**. Registra una atribución ajena, con su fuente, o deja el campo vacío.

«Sin atribuir» no es un fallo: es un resultado habitual y perfectamente publicable.

## Estados

| Estado | Significado | Ejemplo |
|---|---|---|
| `none` | No hay atribución pública verificable | Un corte de red sin reivindicación |
| `official` | Un gobierno, una agencia o una empresa técnica señala un actor | Un CERT atribuye una intrusión |
| `claimed` | Un grupo reivindica el hecho | Un colectivo se atribuye un sabotaje |

## Campos

- `attributed_by`: nombre de quien atribuye.
- `attributed_by_type`: `government`, `agency`, `vendor` u `other`.
- `source_url`: enlace a la atribución original.
- `confidence`: `low`, `medium` o `high`; es confianza en la fuente, no en la culpabilidad.
- `quote`: cita corta de máximo 15 palabras.

## Qué no se hace

- No se convierte una reivindicación en prueba independiente.
- No se atribuye por analogía, motivación o beneficio.
- No se rellena `attributed_by` con una deducción propia.
- No se publica un nombre de persona como autor sin una fuente pública y una revisión específica.
- No se oculta una atribución oficial solo porque resulte incómoda.

## Confianza

`confidence` describe la calidad de la fuente que atribuye, no la probabilidad de que el actor sea culpable. Una fuente oficial puede ser `high` y una reivindicación anónima `low`; ambas se conservan y se distinguen.

## Cita

La cita debe ser literal, breve y verificable. No se parafrasea una atribución como si fuera una cita textual. Si no hay una cita clara, se deja vacía.

## Cambios

Cualquier cambio de atribución se registra en `changelog` con el campo, el valor anterior, el nuevo, quién lo cambió y cuándo. La trazabilidad es parte del dato.
