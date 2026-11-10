# Revisión manual de aeropuertos

**Archivo:** `data/baseline/airports-review.csv`  
**Objetivo:** decidir qué candidatos pasan a la línea base.  
**Regla:** nada entra automáticamente.

## Qué tienes que hacer

Por cada fila:

1. **`decision`**: `ACEPTAR`, `RECHAZAR`, `DUPLICADO` o `DUDOSO`.
2. Si aceptas:
   - corrige **`airport_final`** (el gazetteer puede fallar);
   - corrige **`date_final`** si la fecha publicada no es la del hecho;
   - pon la **URL de la pieza** en `source_url_final`, no solo el dominio.
3. Si es duplicado:
   - rellena `duplicate_of` con el `review_id` del episodio principal.
4. Si rechazas o dudas, deja una nota breve en `notes`.

No hace falta rellenar filas que rechaces.

## Criterio rápido

- **ACEPTAR:** aeropuerto identificable, fecha del hecho plausible y una pieza concreta.
- **RECHAZAR:** es análisis, agregado, noticia genérica, otro tipo de incidente o no hay aeropuerto.
- **DUPLICADO:** es seguimiento o segunda pieza del mismo episodio.
- **DUDOSO:** falta la fuente, la fecha no cuadra o el aeropuerto no está claro.

## Tiempo estimado

**59 grupos × 1–2 minutos ≈ 1–2 horas.**  
No hay que revisar 59 si rechazas rápido los agregados.

## Qué hago yo después

- Importar tus decisiones.
- Cruzar los aceptados con la semilla actual.
- Mantener la relación de seguimientos.
- Ejecutar el validador: **50 eventos / 24 meses / 2 grupos de fuente**.
- Publicar N1 solo si pasa.

## Qué falta además de los 59

La revisión puede dar menos de 50 eventos. En ese caso faltan:

- meses sin candidatos;
- acontecimientos históricos que no aparecen en Google News;
- fuentes oficiales o hemeroteca.

No se rellena con noticias inventadas ni con seguimientos.

## Resultado de la revisión (10-nov-2026)

- **39 aceptados**
- **17 duplicados**
- **3 rechazados**
- Total con la semilla: **47 eventos**
- Cobertura: **20 meses**
- Faltan: **3 eventos y 5 meses**
- **39/39 aceptados** tienen URL directa de la pieza tras resolver los enlaces de Google News

El baseline pasa a **`ready`**: 65 eventos / 24 meses, mediana 2/mes, tras la ampliación y la retirada de 6 seguimientos/duplicados (R27, R58, R13, EV-20261106-002, EV-20261106-010 y EV-20261106-001). N1 es inicial y descriptivo; no se afirma tendencia ni atribución.
