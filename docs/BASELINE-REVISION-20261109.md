# Revisión de candidatos de aeropuertos · 9-nov-2026

## Resultado

- Candidatos Google News: **94**.
- Agrupados por fecha + aeropuerto sugerido + tipo: **65**.
- Tras descartar falsos evidentes: **53 grupos**.
- Meses cubiertos dentro de la ventana de 24: **20/24**.
- Faltan: **2025-04, 2025-08, 2025-10, 2025-12, 2026-01**.
- Baseline aceptado: **8 eventos / 1 mes**. Sigue `insufficient`.

## Problemas encontrados

1. **El gazetteer no identifica el aeropuerto**, solo una ciudad mencionada en el titular.
   - Fort Lauderdale aparece como “New York”.
   - Denver aparece como “New York”.
   - El Paso aparece como “New York”.
   - Dubai aparece como “Washington”.
   - Moldavia aparece como “Kyiv”.

2. **Hay duplicados por seguimiento**, no por URL:
   - Amenaza en Reagan/DCA: varias piezas y dos fechas.
   - Bruselas: cierre del 4-nov y nuevas alertas del 6-nov.
   - Leipzig: hallazgo, tercera pieza y atribución posterior.
   - Ben Gurión: cuatro piezas del mismo episodio.
   - Jersey: dos noches del mismo episodio.

3. **Faltan meses** y no se pueden rellenar con una foto de noviembre.

4. **La fuente del candidato es el dominio**, no siempre la pieza original.

## Decisión

No se acepta ningún candidato nuevo al baseline. Los 53 grupos son **candidatos**, no 53 incidentes.

## Siguiente paso

Revisión manual de los 53 grupos:

- confirmar aeropuerto real;
- confirmar fecha del hecho;
- enlazar seguimientos;
- obtener URL de la pieza;
- descartar agregados y análisis.

Sin esos cinco campos no se pasa a `DOCUMENTADO`.
