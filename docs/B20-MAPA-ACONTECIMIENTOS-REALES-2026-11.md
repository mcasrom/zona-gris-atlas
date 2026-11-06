# B20 · Mapa de acontecimientos reales

**Fecha:** 2026-11-06  
**Estado:** **PUBLICADO** a las 15:59:02 UTC. Release `20261106T155839Z`; sin push y sin cambios en Nginx, DNS o TLS.

## 1. Estado anterior del mapa

- El mapa original está en el commit `cfd7465` (`feat: add static atlas web, map and demo data`).
- Usaba un SVG propio (`world-dots.svg`), una proyección Natural Earth y un `map.js` sin Leaflet, sin claves y sin peticiones externas.
- B16 sustituyó `/mapa.html` por una redirección meta a `/demo.html`; el mapa real desapareció de la portada y del sitemap.
- El archivo de demo `incidents.json` contiene **10 casos**, no cuatro. No se han eliminado ni convertido en datos reales. Esta discrepancia queda documentada.

## 2. Cambios realizados

### Mapa

- `/mapa.html` vuelve a ser una página interactiva con el mapa SVG original y la proyección recuperada.
- Marcadores con estado `CONFIRMADO`, `DOCUMENTADO` o `PENDIENTE`.
- Filtros por fecha, categoría, país y estado de verificación.
- Lista de acontecimientos filtrada y panel de ficha con fuente original.
- Los registros sin ciudad/región documentada **no se dibujan**: aparecen solo en la lista.
- La portada incorpora un mapa de vista previa, CTA al mapa completo y últimos acontecimientos.
- `/mapa.html` vuelve al sitemap; `/demo.html` sigue fuera y con `noindex`.

### Datos

- `data/events/2026-11-06/events.jsonl`: **16 acontecimientos reales**, uno por línea, tras la revisión editorial.
- `web/assets/data/events.json`: misma colección para el mapa, generada desde el JSONL.
- `data/events/2026-11-06/sources.json`: pruebas de fuentes y limitaciones.
- `scripts/collect_events.py`: recolector RSS ligero, sin IA, sin artículos completos y con deduplicación.
- `scripts/build_web.py`: regenera `events.json`, mapa en sitemap y manifest.
- `tests/test_events.py` y `tests/test_collect_events.py`: validación de registros, coordenadas, demo, fuentes y deduplicación.

## 3. Fuentes probadas

Pruebas realizadas desde el servidor con HTTP directo y UA de navegador. Un `403` de protección anti-bot no significa que la fuente no exista; se limita la afirmación.

| Fuente | Método | HTTP | Auth | Resultado | Uso |
|---|---|---:|---|---|---|
| Bing News RSS | RSS 2.0 | 200 | No | 12 consultas; 120 candidatos normalizados | **Sí**: enlace original del medio |
| Google News RSS | RSS 2.0 | 200 | No | Hasta 100 elementos por consulta; 14 consultas | No: enlaces de agregador |
| Europa Press | RSS 2.0 | 200 | No | Feed de portada | No: sin los eventos concretos |
| EASA | RSS 2.0 | 200 | No | Feed institucional | No: sin incidentes concretos |
| EUROCONTROL | RSS 2.0 | 200 | No | Feed de 1,3 MB | No: sin eventos concretos |
| GDELT DOC API | JSON | **429** | No | 0 utilizables | No: rate limit; no se insistió |
| EODI (`eodidata.com`, `eodi.eu`) | HTML/API | DNS | — | 0 | No verificable |
| CERT-EU threat-intelligence | RSS | **404** | No | 0 | No |
| ENISA news | RSS | **404** | No | 0 | No |
| RTVE noticias | RSS/API | **404** | No | 0 | No |
| CIAIAC | HTML | **403** | No | 0 | No |
| CIAF | HTML | DNS | — | 0 | No verificable |
| Protección Civil | RSS | **404** | No | 0 | No |
| AP News | RSS | **403** | No | 0 | No |
| Reuters | RSS | DNS | — | 0 | No verificable |
| EFE | HTML | 200 | No | 0 | No: no es RSS |

- **Reutilización:** solo se conservan metadatos y resúmenes propios; no se guardan artículos completos. Cada ficha enlaza la fuente original.
- **Actualización:** el colector puede repetirse; deduplica por URL y no inventa fechas. Los registros incorporados se revisaron manualmente.
- **Muestra de enlaces:** Leipzig/Halle (Tagesspiegel, Zeit), Copenhague (London Loves Business, BBC), Praga (NL Times, Cyprus Mail), ciberataque al servicio de sangre francés (The Guardian, France 24).

## 4. Acontecimientos reales incorporados

**16 registros · 6 categorías · 12 con ciudad o región · 4 sin coordenada única.**  
Estados: **0 CONFIRMADO · 14 DOCUMENTADO · 2 PENDIENTE · 0 DESCARTADO**.

| ID | Fecha | País / lugar | Categoría | Estado | Fuentes |
|---|---|---|---|---|---:|
| EV-20261106-001 | 2026-11-05 | Alemania · Aeropuerto de Leipzig/Halle, Schkeuditz | Drones e incursiones en aeropuertos | DOCUMENTADO | 2 |
| EV-20261106-002 | 2026-11-01 | Jersey · Aeropuerto de Jersey | Drones e incursiones en aeropuertos | DOCUMENTADO | 2 |
| EV-20261106-004 | 2026-11-05 | Arabia Saudí · Aeropuerto Rey Fahd | Drones e incursiones en aeropuertos | DOCUMENTADO | 2 |
| EV-20261106-006 | 2026-11-06 | Dinamarca · Aeropuerto de Copenhague-Kastrup | Amenazas de bomba y evacuaciones aeroportuarias | DOCUMENTADO | 2 |
| EV-20261106-007 | 2026-11-06 | Chequia · Aeropuerto de Praga-Václav Havel | Amenazas de bomba y evacuaciones aeroportuarias | DOCUMENTADO | 2 |
| EV-20261106-008 | 2026-11-06 | Italia · Aeropuerto de Malpensa | Amenazas de bomba y evacuaciones aeroportuarias | DOCUMENTADO | 1 |
| EV-20261106-009 | 2026-11-06 | Francia · Espacio aéreo y aeropuertos de París | Amenazas de bomba y evacuaciones aeroportuarias | DOCUMENTADO | 2 |
| EV-20261106-010 | 2026-11-05 | Israel · Aeropuerto Ben Gurion | Alertas de seguridad civil y protección de infraestructuras | DOCUMENTADO | 1 |
| EV-20261106-011 | 2026-11-04 | Francia · Servicio Nacional de Sangre (Francia) | Ciberataques contra infraestructuras y servicios | DOCUMENTADO | 2 |
| EV-20261106-012 | 2026-11-04 | Rusia · Proveedor de alojamiento Beget (Rusia) | Ciberataques contra infraestructuras y servicios | DOCUMENTADO | 1 |
| EV-20261106-013 | 2026-11-02 | Unión Europea · Supermercados europeos | Ciberataques contra infraestructuras y servicios | PENDIENTE | 1 |
| EV-20261106-015 | 2026-11-03 | Francia · Red ferroviaria del sur de Francia | Incidentes ferroviarios y aeroportuarios | PENDIENTE | 1 |
| EV-20261106-016 | 2026-11-04 | Reino Unido · Manchester Piccadilly | Incidentes ferroviarios y aeroportuarios | DOCUMENTADO | 1 |
| EV-20261106-017 | 2026-11-05 | Reino Unido · Entre University y Five Ways | Incidentes ferroviarios y aeroportuarios | DOCUMENTADO | 1 |
| EV-20261106-018 | 2026-11-06 | Reino Unido · Tramo ferroviario de Wiltshire | Incidentes ferroviarios y aeroportuarios | DOCUMENTADO | 1 |
| EV-20261106-020 | 2026-11-04 | OTAN (flanco este) · Frontera este de la OTAN | Interferencias GNSS y navegación | DOCUMENTADO | 1 |

### Casos que no se presentan como ataques

- **EV-006 a EV-009** son **amenazas de bomba**; no se confirma explosivo ni ataque. Su estado es `DOCUMENTADO`, no `CONFIRMADO`.
- **EV-001 (Leipzig/Halle)** está documentado por una investigación policial; no se eleva a ataque confirmado.
- **EV-004 (Dammam)** conserva una **reivindicación** hutí y una interceptación comunicada por la coalición; no hay confirmación independiente.
- **EV-013 (supermercados europeos)** depende de una fuente secundaria y queda como `PENDIENTE`.
- **EV-015 (sur de Francia)** depende de una fuente secundaria y queda como `PENDIENTE`.
- **EV-020 (GNSS)** no asigna autoría; el evento es regional y no tiene una coordenada única.

### Registros excluidos en la revisión

| ID | Registro | Motivo |
|---|---|---|
| EV-20261106-003 | Alerta por drones en Cartagena | Es una **alerta de riesgo**, no un acontecimiento operativo documentado. |
| EV-20261106-005 | Restricciones en aeropuertos rusos | Fuente única no suficientemente contrastada y sin ciudad/región documentada. |
| EV-20261106-014 | Ciberataque a GitBook | Fuente secundaria, alcance posible y sin comunicación primaria localizada. |
| EV-20261106-019 | Retrasos de Eurostar | Noticia de interrupción sin causa ni acontecimiento de seguridad documentado. |

No se completaron huecos con noticias irrelevantes ni con casos ficticios. El número final es **16**.

Además, en la capa B13 se excluyó de la superficie pública la **Resolución 770/38447/2026 (Adenda del Mando de Apoyo Logístico)**: es un acto administrativo rutinario sin incidencia operativa y no aporta nada al objeto del Atlas. El dato histórico permanece en B13; solo se retiró su presentación pública.

## 5. Registros, mapa y portada

- La portada abre con el mapa de vista previa, CTA al mapa completo y tres accesos: registros, método y fuentes/condiciones.
- Los indicadores de portada son de **acontecimientos reales**: 16, 6 categorías, 0 confirmados, 14 documentados y 2 pendientes.
- B13 conserva su histórico de 8 documentos, pero la superficie pública muestra 5: se excluyeron las dos promociones militares y la adenda administrativa rutinaria del Mando de Apoyo Logístico. El feed público tampoco las incluye. B13 y B14 no se han reescrito.
- La demo sigue separada, con `noindex`, sin entrada en sitemap y sin datos en el mapa real.

## 6. Incidencias y limitaciones

- El DNS local del portátil falló para dominios externos; las pruebas de fuentes se hicieron desde el servidor, sin modificarlo.
- **GDELT** respondió **429**; no se repitieron peticiones.
- **EODI**, **CIAF** y **Reuters** no resolvieron por DNS; no se declaran operativos.
- Varias fuentes (NL Times, Die Zeit, France 24, Express & Star, Militarnyi, Operativ, Notizie, Rus Tourism News y Siasat) devolvieron **403** a clientes automatizados; siguen siendo enlaces periodísticos identificables y no se presentan como fuentes primarias oficiales.
- **16 de 23 URLs únicas de las 16 fichas respondieron 200; 7 respondieron 403; 0 dieron 404.** No se afirma que las 403 estén caídas.
- No hay una fuente primaria para todos los eventos; por eso la mayoría queda `DOCUMENTADO`, no `CONFIRMADO`.
- Cuatro registros no tienen coordenada única y no se dibujan en el mapa.
- Algunas fechas de acontecimiento proceden de la publicación o del título de la fuente; la fecha de captura es **2026-11-06T16:00Z**. No se inventan horas ni coordenadas.
- El mapa usa el SVG y la proyección locales recuperados; **no usa OSM, Leaflet, APIs comerciales ni claves**.
- El archivo demo contiene 10 casos, no cuatro. No se eliminó ni se usó como sustituto; sigue fuera del mapa, del sitemap y del feed.

## 7. Capturas

- `docs/capturas/b20-mapa-desktop.png` — mapa y filtros a 1440 px.
- `docs/capturas/b20-mapa-mobile.png` — mapa a 390 px.

## 8. Pruebas

- `make lint`: **OK**.
- `make test`: **26 passed**.
- 16 registros JSONL, IDs únicos, `demo: false`, estados válidos, fuente HTTPS y coordenadas dentro de rango.
- 16 entradas en `events.json`; 12 marcadores en el mapa; 16 filas en la lista.
- Pruebas de navegador con Chrome/CDP:
  - sin filtros: **16**;
  - categoría `ferroviario`: **4**;
  - estado `PENDIENTE`: **2**;
  - país `Francia`: **3**;
  - fecha 24 h: **5**.
- El detalle abre la ficha y muestra el enlace a la fuente.
- `/demo.html` conserva `noindex`; no aparece en el sitemap.
- `/mapa.html` está en el sitemap y ya no redirige a demo.

## 9. Estado de publicación

**PUBLICADO.** El mapa funciona, contiene 16 acontecimientos reales documentados y los filtros responden. Release activa: `20261106T155839Z`.

## 10. Git

- **15 commits locales conservados**.
- Cambios B20 sin commit.
- **Sin push**.
- Despliegue realizado con el procedimiento existente; sin cambios en otros servicios.


## 11. Publicación

- **Release activa:** `/var/www/atlas-zonagris/releases/20261106T155839Z` · `2026-11-06T15:59:02Z`.
- **Backup previo verificado:** `~/backups/zona-gris-atlas/zona-gris-atlas-20261106T155839Z.bundle`.
- **Release anterior conservada:** `20261106T155746Z`.
- **Rollback disponible:** `SERVER=178.105.80.193 ./scripts/deploy_web.sh --apply --rollback`; no ejecutado.
- **HTTP:** raíz `http://` → **301** a HTTPS; HTTPS **200**, verificación TLS **0**.
- **URLs públicas:** `/`, `/mapa.html`, `/registros.html`, `/demo.html`, `/about.html`, `/avisos.html`, `/metodologia.html`, `/fuentes.html`, `/privacidad.html`, `/limites.html`, `/feed.xml`, `/sitemap.xml` y `/assets/data/events.json`: **200**.
- **Mapa público:** **16 filas**, **12 marcadores** y contador **16**; filtros locales verificados.
- **Registros públicos:** **5 tarjetas**; sin promociones militares ni adenda administrativa.
- **Feed público:** **5 entradas**; sin promoción militar ni adenda administrativa.
- **Sitemap:** incluye `/mapa.html`; no incluye demo ni el antiguo mapa.
- **Demo:** `noindex, nofollow`; fuera del sitemap y del mapa.
- **Cabeceras:** HSTS, `nosniff`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` y CSP presentes.
- **Otros servicios:** no modificados.
- **Git:** sin commit y **sin push**.
