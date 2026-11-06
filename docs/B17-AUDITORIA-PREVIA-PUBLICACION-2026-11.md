# B17 · Auditoría previa a la publicación de B16

**Fecha:** 2026-11-06  
**Estado:** auditoría local completada. **Web pública sin cambios; no se ha desplegado ni hecho push.**

## 1. Resultado

| Componente | Resultado | Observaciones |
|---|---|---|
| Portada | **OK** | Sin mapa demo; KPIs reales 5/212/8/204/100 %/1; B15 prevista 13-nov |
| Registros B13 | **OK** | 8 IDs y URLs coinciden con B13; resúmenes propios; atribución y enlaces |
| Demo | **OK** | 10 casos; `demo: true`; aviso visible; `noindex` |
| Feed | **OK** | 8 entradas reales; ninguna demo; título corregido a «Observatorio documental» |
| Sitemap | **OK** | Incluye `registros.html`; no incluye `demo.html` ni `mapa.html` |
| Navegación | **OK** | Registros en todas las páginas; Demo identificada y separada |
| About y Avisos | **OK** | Distinguen 8 documentos reales y 10 casos ficticios |
| Seguridad | **OK** | Sin datos personales innecesarios; sin atribuciones; sin texto completo |
| Tests | **OK** | `make lint` OK; `make test` **19 passed** |

## 2. Portada

- **5 fuentes consultadas**.
- **212 documentos revisados**.
- **8 incorporados**.
- **204 descartados**.
- **100 % de revisión manual**.
- **1 captura completada**.
- **0 contadores de incidentes, campañas o atribuciones**.
- La segunda captura aparece como **prevista 13-nov-2026**, no como dato existente.
- El mapa demo ya no está en la portada.

## 3. Registros

- `web/assets/data/registros.json`: 8 documentos.
- IDs y URLs: **coinciden exactamente** con `data/pilots/institucional-20261106/documents.jsonl`.
- Sin campos de texto completo.
- Cada ficha incluye fuente, organismo, título, fecha, tipo, categoría, ámbito, resumen propio, URL, atribución y estado de reutilización.
- Estado de reutilización:
  - CERT-EU: `open_cc_by_4`.
  - BOE: `public_sector_reuse`.
  - Comisión Europea: `open_cc_by_4`.
- Sin imágenes ni material de terceros.
- Sin afirmaciones de autoría, coordinación o intención.

## 4. Demo

- Los 10 casos originales siguen en `web/assets/data/incidents.json`.
- Todos mantienen `demo: true`.
- `/demo.html` tiene aviso visible y `noindex, nofollow`.
- No aparece ningún dato demo en la portada, registros, feed ni sitemap.
- `/mapa.html` redirige mediante `meta refresh` a `/demo.html`; es una redirección de cliente, no un 301 de Nginx.

## 5. Feed y sitemap

- `feed.xml`: **8 entradas reales**, sin demo.
- Título corregido de «Incidentes híbridos» a **«Atlas Zona Gris · Observatorio documental»**.
- Cada entrada conserva URL, fecha y fuente.
- `sitemap.xml`: incluye `/registros.html`; no incluye `demo.html` ni `mapa.html`.

## 6. Navegación y páginas

- Rutas locales comprobadas: **200** en portada, registros, demo, mapa, método, fuentes, privacidad, límites, avisos, About, feed y sitemap.
- About y Avisos han sido actualizados para separar los 8 documentos reales de los 10 ficticios.
- No quedan referencias a `viajeinteligencia.com` en la web.
- El contacto `info.zonagris@pruebapublica.com` solo aparece en About, con `mailto:`.

## 7. Integridad

Hashes comprobados: B11 y B13 conservan los valores de B14.

- B13: `summary.json`, `documents.jsonl`, `discarded.jsonl` y `source_runs.jsonl` sin cambios.
- B11: intacto.
- B14: intacto.
- Los 10 incidentes demo no se han convertido ni eliminado.
- No se han ejecutado ingestas ni consultas nuevas.

## 8. Incidencias corregidas

1. El feed conservaba el título antiguo «Incidentes híbridos»; corregido a «Observatorio documental» y regenerado.
2. La página `/mapa.html` es una redirección HTML de cliente; no se ha cambiado Nginx. Si se exige un 301 real, requiere una regla de servidor y autorización separada.

## 9. Git

- 15 commits locales conservados.
- Cambios B16 pendientes de commit: portada, registros, demo, mapa, navegación, CSS, feed, sitemap, `registros.json` y `build_web.py`.
- No se ha hecho push.
- No se ha desplegado.

## 10. Veredicto

**B16 LISTO PARA PUBLICAR**, con una salvedad: `/mapa.html` redirige por cliente, no por HTTP 301. La web pública sigue intacta hasta autorización expresa.
