# B11 · Primera ingesta GNSS/Báltico

**Fecha:** 2026-11-06 15:40 UTC  
**Estado:** consulta real limitada completada. **No hay observaciones que publicar, no se ha desplegado y no se ha hecho push.**

## 1. Periodo efectivo

- Ventana objetivo: **2026-10-30 → 2026-11-06** (7 días).
- Sesión efectiva: **2026-11-06 15:40 UTC**.
- No se simulan días no ejecutados ni se rellenan resultados.

## 2. Fuentes consultadas

| Fuente | URL | HTTP | Resultado |
|---|---|---:|---|
| EASA CZIB | `https://www.easa.europa.eu/en/domains/air-operations/czibs` | 200 | 0 coincidencias GNSS/Báltico |
| EUROCONTROL | `https://www.eurocontrol.int/newsroom` | 200 | 1 candidato, fuera de ventana/ámbito |
| GDELT DOC | `https://api.gdeltproject.org/api/v2/doc/doc?...` | 0 | **SSL timeout**, dos intentos |

No se consultaron GPSJam ni Hybrid CoE. No se añadieron fuentes.

## 3. Registros creados

Directorio independiente:

`data/pilots/gnss-baltic-20261106/`

- `source_runs.jsonl`: 3 consultas con estado y errores.
- `discarded.jsonl`: 1 candidato y motivo.
- `summary.json`: recuento real.
- `README.md`: alcance y ausencia de datos.
- **No existe `observations.jsonl`**: no hubo observaciones que cumplan los criterios.

## 4. Resultados

| Métrica | Valor |
|---|---:|
| Fuentes consultadas | 3 |
| Fuentes con respuesta | 2 |
| Fuentes con error | 1 |
| Candidatos | 1 |
| Observaciones reales | **0** |
| Descartes | 1 |
| Duplicados | 0 |
| Revisión manual | 1/1 (100 %) |

### Candidato descartado

- **EUROCONTROL**
- Título: «Protecting the backbone of aviation: EASA and EUROCONTROL host workshop on Europe’s GNSS interference Action Plan»
- Fecha: 2026-07-09
- URL: `https://www.eurocontrol.int/news/protecting-backbone-aviation-easa-and-eurocontrol-host-workshop-europes-gnss-interference`
- Clasificación: comunicación institucional.
- Motivo: fuera de la ventana de 7 días y sin ámbito Báltico; no es un registro técnico de interferencia.

## 5. Deduplicación

No hubo duplicados que resolver. No se ha fusionado ningún documento.

## 6. Separación hechos/contexto

- EASA no aportó coincidencias GNSS/Báltico.
- EUROCONTROL solo aportó un comunicado institucional fuera de plazo.
- GDELT no respondió; no se usó un endpoint alternativo.
- No se ha convertido ninguna noticia en incidente confirmado.
- No se ha atribuido autoría, intención ni coordinación.

## 7. Limitaciones

- EASA CZIB es un listado de avisos, no una serie dedicada a GNSS; no se encontraron coincidencias.
- EUROCONTROL Newsroom no es un registro técnico.
- GDELT no fue accesible desde el servidor (SSL timeout).
- La ventana de 7 días fue consultada en una sola sesión; no se observó continuidad diaria.
- Sin observaciones, no se puede evaluar precisión ni utilidad empírica.

## 8. Recursos

- Sin modelos, sin bases de datos nuevas, sin dependencias instaladas.
- Sin ingestas concurrentes.
- Sin texto completo almacenado.
- Sin cambios en el servidor, Nginx, TLS, DNS, Docker, PM2 ni AdGuard.

## 9. Recomendación

**No continuar el piloto en esta configuración.** La mezcla actual no produce datos GNSS/Báltico verificables:

1. EASA no ofrece aquí una serie GNSS utilizable.
2. EUROCONTROL solo aporta contexto institucional.
3. GDELT no responde desde el servidor.
4. GPSJam sigue bloqueado por licencia.

Antes de reanudar hace falta una fuente primaria verificable, acceso estable a GDELT o una ampliación de fuentes autorizada. No se debe rellenar el vacío con noticias secundarias ni con datos de demostración.

## 10. Confirmaciones

- No se publicaron observaciones reales.
- No se modificaron los 10 incidentes demo.
- No se ejecutó `deploy_web.sh --apply`.
- No se hizo push.
- No se enviaron correos.
- No se activaron fuentes en el pipeline ni se creó cron.
- 15 commits locales conservados.
