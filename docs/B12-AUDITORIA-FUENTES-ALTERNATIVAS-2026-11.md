# B12 · Auditoría de fuentes alternativas

**Fecha:** 2026-11-06  
**Estado:** investigación documental y comprobaciones HTTP mínimas. **No se ha iniciado ninguna ingesta, no se han almacenado datos reales, no se ha desplegado y no se ha hecho push.**

## 1. Resumen ejecutivo

La mezcla GNSS/Báltico de B11 no produjo observaciones porque EASA no tenía coincidencias, EUROCONTROL solo aportó un comunicado fuera de ventana y GDELT no respondió.

Tras revisar tres alternativas:

- **Infraestructuras y transporte:** técnicamente débil. No se han encontrado feeds oficiales utilizables.
- **Actividad institucional y alertas:** la mejor opción para empezar. CERT-EU, BOE, Comisión Europea, EASA y EUROCONTROL responden, aunque no todos son feeds ni registros de incidentes.
- **Narrativas informativas:** accesible, pero dominada por fuentes secundarias y republicaciones; alta duplicación.

**Recomendación:** empezar por **actividad institucional y alertas**, como capa documental. No presenta todavía un registro de incidentes del mundo real; no debe etiquetarse como tal.

## 2. Diagnóstico de B11

- EASA CZIB: página accesible, **0 coincidencias GNSS/Báltico**.
- EUROCONTROL: un comunicado GNSS de julio, **fuera de la ventana de 7 días y sin ámbito Báltico**.
- GDELT: **SSL timeout** en dos intentos; no se usó un endpoint alternativo.
- GPSJam y Hybrid CoE: excluidos; GPSJam sin licencia verificada.
- Resultado: **0 observaciones**, 1 descarte. No se modifican los registros B11.

## 3. Temáticas estudiadas

### A. Infraestructuras críticas y transporte

Ferrocarril, puertos, aeropuertos, comunicaciones y energía.

Problema: los operadores publican incidencias en páginas de estado o notas de prensa, no en feeds estructurados estables. Las rutas RSS probadas no existen o están bloqueadas.

### B. Actividad institucional y alertas de seguridad

Comunicados oficiales, alertas de CERT, cambios normativos y avisos de seguridad.

Ventaja: fechas, identificadores y URLs estables; volumen bajo; varias fuentes oficiales accesibles. Límite: una alerta oficial no es un incidente confirmado.

### C. Narrativas informativas y campañas públicas

Comunicaciones institucionales, declaraciones, cobertura y repetición.

Ventaja: muchos feeds accesibles. Límite: predominio de fuentes secundarias, duplicación y circularidad; no sirve como registro factual primario.

## 4. Auditoría de fuentes

### A. Infraestructuras y transporte

| Fuente | Organismo | URL | HTTP / formato | Resultado |
|---|---|---|---|---|
| ADIF | ADIF | `https://www.adif.es/rss` | 403 HTML | Sin feed utilizable |
| Renfe | Renfe | `https://www.renfe.com/es/es/prensa/rss` | 404 HTML | Sin feed |
| Puertos del Estado | Puertos del Estado | `https://www.puertos.es/es-es/Paginas/RSS.aspx` | 404 HTML | Sin feed |
| AENA | AENA | `https://www.aena.es/es/rss` | 404 HTML | Sin feed |
| CNMC | CNMC | `https://www.cnmc.es/rss` | 404 HTML | Sin feed |
| Red Eléctrica | REE | `https://www.ree.es/es/rss` | 200 HTML | Página, no feed |

**Estado:** ninguna fuente primaria estructurada aprobada. No se propone este tema.

### B. Actividad institucional y alertas

| Fuente | Organismo | URL | HTTP / formato | Tipo | Estado |
|---|---|---|---|---|---|
| CERT-EU Threat Intelligence | CERT-EU | `https://cert.europa.eu/publications/threat-intelligence-rss` | 200 XML/RSS | Primaria institucional | **Aprobada con condiciones** |
| BOE | BOE | `https://www.boe.es/rss/boe.php` | 206 XML/RSS | Primaria normativa | **Aprobada con condiciones** |
| Comisión Europea · Press Corner | Comisión Europea | `https://ec.europa.eu/commission/presscorner/api/rss?language=en` | 200 RSS | Primaria institucional | **Aprobada con condiciones** |
| EASA CZIB | EASA | `https://www.easa.europa.eu/en/domains/air-operations/czibs` | 200 HTML | Primaria oficial | **Aprobada como contexto** |
| EUROCONTROL Newsroom | EUROCONTROL | `https://www.eurocontrol.int/newsroom` | 200 HTML | Institucional contextual | **Aprobada como contexto** |
| CISA advisories | CISA | `https://www.cisa.gov/cybersecurity-advisories/all.xml` | 403 HTML | Primaria bloqueada | Pendiente |
| CISA KEV | CISA | `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json` | 403 HTML | Primaria bloqueada | Pendiente |
| CCN-CERT | CCN-CERT | `https://www.ccn-cert.cni.es/seguridad-al-dia/avisos-ccn-cert.feed?type=rss` | 403 HTML | Primaria bloqueada | Pendiente |
| INCIBE-CERT | INCIBE | `https://www.incibe.es/incibe-cert/alerta-temprana/avisos/rss` | 200 HTML | No es RSS | Pendiente/corregir URL |
| ENISA | ENISA | `https://www.enisa.europa.eu/news/enisa-news/rss` | 404 HTML | Feed no disponible | Descartada esta ruta |

### C. Narrativas informativas

| Fuente | Organismo | URL | HTTP / formato | Tipo |
|---|---|---|---|---|
| EUvsDisinfo | EUvsDisinfo | `https://euvsdisinfo.eu/feed/` | 206 RSS | Secundaria analítica |
| Comisión Europea · Press Corner | Comisión Europea | `https://ec.europa.eu/commission/presscorner/api/rss?language=en` | 200 RSS | Primaria institucional |
| EEAS Press | EEAS | `https://www.eeas.europa.eu/eeas/press-material_en?rss=1` | 206 HTML | Página, no feed |
| El País | El País | `https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada` | 206 XML | Medio |
| El Mundo | El Mundo | `https://www.elmundo.es/rss/portada.xml` | 206 XML | Medio |
| La Vanguardia | La Vanguardia | `https://www.lavanguardia.com/rss/home.xml` | 200 XML | Medio |
| elDiario.es | elDiario.es | `https://www.eldiario.es/rss/` | 206 XML | Medio |
| 20minutos | 20minutos | `https://www.20minutos.es/rss/` | 206 XML | Medio |
| Consejo de la UE | Consejo UE | `https://www.consilium.europa.eu/en/rss/` | 403 HTML | Bloqueada |
| Parlamento Europeo | PE | `https://www.europarl.europa.eu/rss/plenary/en.xml` | 403 HTML | Bloqueada |

## 5. Evidencias de accesibilidad

Comprobaciones realizadas con `curl` desde el servidor, User-Agent de navegador y rango mínimo. No se interpreta un 200 como garantía de contenido útil.

- CERT-EU RSS: XML con `<channel>` y `<item>`.
- BOE RSS: XML con canal y edición del día.
- Comisión Europea Press Corner: RSS XML.
- EUvsDisinfo: RSS XML.
- Medios españoles: RSS XML.
- EASA/EUROCONTROL: HTML; no feed estructurado confirmado.
- CISA/CCN/Consejo/PE: 403 desde la IP del servidor; no se fuerza el acceso.
- ADIF/Renfe/AENA/Puertos/CNMC: rutas RSS 404 o 403.
- ENISA: 404 en la ruta probada.

## 6. Comparación

Escala 1–5; 5 es mejor. La puntuación es una valoración documental, no una predicción.

| Criterio | A. Infraestructuras | B. Institucional | C. Narrativas |
|---|---:|---:|---:|
| Fuentes primarias disponibles | 1 | 5 | 2 |
| Accesibilidad técnica | 1 | 4 | 5 |
| Frecuencia de actualización | 1 | 4 | 5 |
| Calidad documental | 2 | 4 | 2 |
| Trazabilidad e identificadores | 2 | 5 | 3 |
| Deduplicación | 2 | 4 | 2 |
| Cobertura temporal | 2 | 3 | 5 |
| Condiciones de reutilización | 1 | 3 | 3 |
| Coste operativo | 2 | 2 | 4 |
| Riesgo de falsos positivos | 2 | 3 | 1 |
| Adecuación al atlas | 2 | 4 | 3 |
| **Media** | **1,6** | **3,7** | **3,1** |

## 7. Riesgos

- **B:** una alerta institucional no es un incidente; el atlas registraría comunicaciones, no hechos verificados. Hay que etiquetar el tipo documental.
- **B:** CISA, CCN-CERT, Consejo y PE bloquean la IP del servidor; no se fuerza el acceso.
- **B:** BOE y Comisión Europea no son fuentes de incidentes; son normativa y comunicación.
- **C:** los medios son secundarios; la repetición no es corroboración.
- **C:** EUvsDisinfo es análisis, no registro de incidentes.
- **A:** no hay feed primario fiable; no se puede sostener un piloto con páginas no estructuradas.
- **General:** una fuente puede cambiar formato o bloquear la IP; hay que conservar errores y no rellenar huecos.

## 8. Temática recomendada

**B. Actividad institucional y alertas**, como **capa documental inicial**, no como registro de incidentes.

Por qué:

- cinco fuentes oficiales responden o son accesibles (CERT-EU, BOE, Comisión Europea, EASA, EUROCONTROL);
- fechas y URLs estables;
- volumen bajo y revisable;
- permite probar deduplicación, procedencia y separación entre alerta, norma y comunicación;
- no exige modelos ni bases pesadas.

Lo que **no** se podrá obtener:

- confirmación de que una alerta corresponda a un incidente real;
- autoría o intención;
- cobertura completa de zona gris;
- medición de coordinación.

## 9. Diseño propuesto para una futura ingesta

- Duración: 7 días.
- Límite: 300 elementos (más conservador que 500).
- Fuentes: CERT-EU, BOE, Comisión Europea, EASA y EUROCONTROL.
- Frecuencia: 1 consulta/día por feed; EASA/EUROCONTROL manual; sin paralelismo.
- Clasificación: `hecho_documentado`, `comunicacion_institucional`, `noticia_secundaria`, `afirmacion_pendiente`, `repeticion_republicacion`, `descartado`.
- Cada elemento: URL, organismo, fecha, consulta, tipo, ámbito y resumen; sin texto completo.
- Deduplicación por URL, identificador y título; las republicaciones se enlazan, no se suman.
- Revisión manual del 100 %.
- Sin alertas HIGH/CRITICAL; sin atribución.
- Retención: texto 7 días; metadatos mínimos 30 días.
- Memoria: ≤1200 MB; ventana 04:45–05:20 Europe/Madrid.

## 10. Fuentes que requieren autorización o aclaración

- **CISA y CCN-CERT:** 403 desde el servidor; no se insiste. Requieren revisión de acceso.
- **INCIBE:** la URL probada devuelve HTML, no RSS; requiere localizar el feed correcto.
- **ENISA:** ruta 404; requiere endpoint oficial verificado.
- **EASA/EUROCONTROL:** condiciones de reutilización no verificadas.
- **BOE/Comisión/CERT-EU:** revisar condiciones de reutilización antes de publicar.
- **Medios:** solo contexto; no usar como registro de incidentes.

## 11. Recomendación final

**B viable con condiciones**, y solo como capa de comunicaciones institucionales. Si el requisito es “incidentes reales” en sentido estricto, **ninguna de las tres temáticas ofrece hoy una base suficiente**. No se debe iniciar la ingesta sin autorización y sin cerrar las condiciones de reutilización.
