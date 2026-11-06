# B13 · Primera ingesta institucional

**Fecha:** 2026-11-06  
**Estado:** ingesta local completada. **No se ha publicado nada, no se ha desplegado y no se ha hecho push.**

## 1. Fuentes consultadas

| Fuente | URL | HTTP | Elementos | Incorporados |
|---|---|---:|---:|---:|
| CERT-EU | `https://cert.europa.eu/publications/threat-intelligence-rss` | 200 | 10 | **1** |
| BOE | `https://www.boe.es/rss/boe.php` | 200 | 192 | **3** |
| Comisión Europea | `https://ec.europa.eu/commission/presscorner/api/rss?language=en` | 200 | 10 | **4** |
| EASA CZIB | `https://www.easa.europa.eu/en/domains/air-operations/czibs` | 200 | 0 | **0** |
| EUROCONTROL | `https://www.eurocontrol.int/newsroom` | 200 | 0 | **0** |

No se consultaron GPSJam, Hybrid CoE, GDELT, CISA, CCN-CERT, INCIBE ni ENISA.

## 2. Condiciones de reutilización

- **CERT-EU:** aviso legal accesible; reutilización concreta **pendiente de verificación**.
- **Comisión Europea:** aviso legal accesible; reutilización concreta **pendiente de verificación**.
- **BOE:** no se localizó una página de condiciones operativa; **pendiente**.
- **EASA/EUROCONTROL:** no se incorporaron documentos; sus condiciones generales no se han validado.

Por precaución, **solo se guardan metadatos**: título, URL, fechas, tipo, ámbito y resumen descriptivo. No se almacenan textos completos ni PDFs.

## 3. Periodo efectivo

- Ventana objetivo: **2026-10-30 → 2026-11-06**.
- Sesión efectiva: **2026-11-06 15:55 UTC**.
- Cobertura temporal real muy concentrada: casi todos los documentos son de **2026-11-06**.
- No se simulan días no ejecutados.

## 4. Documentos incorporados

### CERT-EU (1)

- `DOC-20261106-0001` — *Cyber Brief 26-11 - October 2026* — alerta técnica.
- Fecha: 2026-11-06.

### BOE (3)

- `DOC-20261106-0002` — Real Decreto 963/2026, promoción militar.
- `DOC-20261106-0003` — Real Decreto 964/2026, promoción militar.
- `DOC-20261106-0004` — Resolución 770/38447/2026, Adenda del Mando de Apoyo Logístico.
- Tipo: disposición normativa/comunicación institucional; no incidentes.

### Comisión Europea (4)

- `DOC-20261106-0005` — lanzamiento del segundo ciclo de gestión migratoria.
- `DOC-20261106-0006` — preguntas y respuestas del ciclo migratorio.
- `DOC-20261106-0007` — intervención de la comisaria Brunner.
- `DOC-20261106-0008` — ayuda humanitaria para Myanmar y Rohingya.
- Tipo: comunicación institucional; no incidentes.

### EASA y EUROCONTROL (0)

No se incorporaron elementos: no había documentos dentro de la ventana y del ámbito que justificaran un registro.

## 5. Duplicados y descartes

- Duplicados: **0**.
- Descartados: **204**.
  - CERT-EU: 9 fuera de ventana.
  - BOE: 189 fuera del filtro temático (anuncios, nombramientos y disposiciones sin relación).
  - Comisión Europea: 6 fuera del filtro temático.
- Los descartes se registran agregados por fuente y motivo en `discarded.jsonl`.

## 6. Revisión manual

- Documentos incorporados revisados: **8/8 (100 %)**.
- Cada registro tiene `review_status: revisado_manualmente`.
- No se ha inferido coordinación, intención ni autoría.
- No se han generado HIGH/CRITICAL ni alertas públicas.

## 7. Problemas técnicos

- BOE usa ISO-8859-1; se parseó como bytes para evitar mojibake.
- CERT-EU solo tenía un elemento dentro de la ventana.
- EASA y EUROCONTROL no ofrecieron elementos concretos en la ventana.
- No hubo errores HTTP en las cinco fuentes.
- No se forzó ninguna fuente bloqueada.

## 8. Calidad y utilidad

**Útil como capa documental:** demuestra que el sistema puede registrar procedencia, fechas, tipos y URLs de documentos oficiales, con deduplicación y revisión.

**Limitado como observatorio de incidentes:** ninguno de los 8 documentos es un incidente confirmado. Son alertas, normas o comunicaciones. El conjunto no mide coordinación ni actividad hostil.

## 9. Distribución

- Por fuente: CERT-EU 1 · BOE 3 · Comisión Europea 4 · EASA 0 · EUROCONTROL 0.
- Por tipo: alerta técnica 1 · disposición normativa 2 · comunicación institucional 5.
- Geografía: UE, España, Myanmar/Bangladesh.
- Cobertura temporal: un solo día efectivo.

## 10. Recomendación

**Continuar B como capa documental, con condiciones**, pero no presentarlo como registro de incidentes.

Antes de una segunda pasada:

1. aclarar reutilización de CERT-EU, BOE y Comisión Europea;
2. ampliar la ventana o mantener la frecuencia diaria para obtener una serie temporal real;
3. no añadir medios ni fuentes bloqueadas;
4. mantener solo metadatos hasta que la reutilización esté verificada;
5. no publicar nada sin autorización independiente.

El conjunto está en `data/pilots/institucional-20261106/`. Los 10 incidentes demo siguen intactos.
