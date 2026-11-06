# B8 · Piloto de datos reales (plan, sin ejecutar)

**Estado:** documentación únicamente. No se activan fuentes, no se ejecuta ingesta, no se consultan APIs y no se publican datos reales.

## 1. Temática inicial

**Interferencia GNSS y aviación civil en el Báltico.** Es un dominio acotado (`GNS`), con señales públicas recurrentes, bajo volumen y fuentes institucionales verificables. No incluye cables submarinos ni atribución de autoría.

## 2. Fuentes candidatas

| Fuente | URL | Uso previsto | Acceso / reutilización | Límite propuesto |
|---|---|---|---|---|
| GPSJam | https://gpsjam.org/ | Agregados diarios de interferencia | `[VERIFICAR]` términos y licencia | 1 consulta/día, sin descarga masiva |
| Eurocontrol | https://www.eurocontrol.int/news | Avisos y contexto aeronáutico | `[VERIFICAR]` | 1 consulta/día |
| EASA Conflict Zones | https://www.easa.europa.eu/en/domains/airworthiness/conflict-zones | Boletines oficiales | `[VERIFICAR]` | 1 consulta/semana |
| GDELT DOC API | https://api.gdeltproject.org/api/v2/doc/doc | Titulares públicos de contexto | `[VERIFICAR]` condiciones y cuota | máx. 4 consultas/día, 50 resultados |
| Hybrid CoE | https://www.hybridcoe.fi/ | Contexto de amenazas híbridas | `[VERIFICAR]` | 1 consulta/día |

Ninguna fuente se activa. Todas requieren revisión de robots.txt, condiciones y licencia antes de la primera consulta.

## 3. Condiciones y límites

- Solo páginas y APIs públicas; sin login, sin cuentas privadas, sin APIs de pago.
- Respetar `robots.txt`, términos y límites de frecuencia.
- Sin descargas masivas ni scraping de documentos completos.
- User-Agent identificable: `zona-gris-atlas/0.1`.
- Si una fuente devuelve 403/429/503, no se insiste; se registra y se detiene esa fuente.
- Sin X/TikTok mediante API de pago.

## 4. Volumen y duración

- **Duración:** 7 días consecutivos, en modo sombra.
- **Máximo:** 500 elementos crudos, 4 consultas/día como techo global, 1 proceso secuencial.
- **Texto:** retención máxima de 7 días; después solo metadatos y cita de hasta 15 palabras.
- **Disco:** objetivo < 50 MB para el piloto; alerta si el proyecto supera 1,2 GB.
- **Memoria:** `MemoryMax=1200M`; medir RSS por ejecución; si se acerca al límite, parar.
- **Ventana:** 04:45–05:20 Europe/Madrid, sin concurrencia.

## 5. Deduplicación y minimización

- Clave primaria: hash de URL canónica.
- Segunda pasada: similitud de título/texto; umbral conservador.
- No almacenar HTML completo si bastan título, URL, fecha, idioma y extracto.
- Conservar procedencia, fecha de captura, fecha del hecho si existe y fuente.
- No guardar datos personales innecesarios.

## 6. Registro de procedencia

Cada observación debe conservar:

- `source_id`
- URL original
- título
- fecha de publicación
- fecha de captura
- idioma
- hash de URL y texto
- extracto de hasta 15 palabras
- estado de revisión
- motivo de descarte, si aplica

## 7. Criterios de clasificación

- **Actividad normal:** patrón estable, sin concentración anómala ni coincidencia temporal.
- **Anomalía:** desviación medible respecto a una referencia declarada; no implica coordinación.
- **Posible coordinación:** varias señales independientes comparten tiempo, contenido o infraestructura en una ventana definida. Requiere revisión humana.
- **No es campaña ni autoría:** no se etiqueta como campaña sin evidencia convergente; nunca se atribuye a un Estado, grupo o persona sin fuente independiente.

## 8. Revisión manual

- Revisión del 100 % de los candidatos del piloto.
- Registrar cada falso positivo con motivo y fuente.
- Segunda lectura de una muestra del 20 % para medir consistencia.
- No se publica nada durante el piloto.

## 9. Métricas

- fuentes consultadas / fuentes con respuesta;
- elementos nuevos y duplicados;
- anomalías propuestas y aceptadas;
- falsos positivos documentados;
- tiempo de revisión por elemento;
- RSS máximo y duración;
- tamaño de BD y logs;
- utilidad: ¿la señal aporta contexto verificable o solo ruido?

## 10. Criterios para publicar

El piloto no publica. Una fase posterior solo podría publicar si:

1. la fuente y su licencia están verificadas;
2. hay revisión humana y trazabilidad completa;
3. no hay atribución sin evidencia independiente;
4. no se publican datos personales;
5. el resultado aporta contexto verificable y no solo una anomalía;
6. se ha medido el coste en memoria y disco.

## 11. No se hará

- Entrenar modelos en el servidor.
- Usar Ollama o modelos pesados.
- Ejecutar ingestas concurrentes.
- Activar fuentes automáticamente.
- Publicar datos reales durante el piloto.

## 12. Corrección de auditoría B8.1 (2026-11-06)

La auditoría documental corrige el plan original sin borrar el historial:

- **Eurocontrol:** la URL `/news` devuelve 404; la válida es `https://www.eurocontrol.int/newsroom`. Es comunicación institucional, no un feed estructurado.
- **EASA:** la URL `/airworthiness/conflict-zones` devuelve 404; la válida es `https://www.easa.europa.eu/en/domains/air-operations/czibs` (y la página informativa de conflict zones). Son CZIB/HTML-PDF, no una API.
- **GPSJam:** la página About no muestra una licencia de reutilización y sus datos derivan de airplanes.live/ADS-B Exchange. Queda **pendiente/no aprobada para publicar** hasta verificar términos.
- **GDELT:** sus términos permiten uso amplio sin fee, pero es un índice de noticias; se aprueba solo como **contexto secundario**, nunca como hecho primario.
- **Hybrid CoE:** es análisis editorial; se rechaza para la tabla factual y solo puede usarse como contexto.
- **Distribución:** EASA 100, Eurocontrol 100, GDELT 150, Hybrid CoE 20, GPSJam 0 y reserva 130. Ninguna fuente puede superar el 30 %.
- **Recomendación:** piloto **viable con condiciones**, solo documental y manual; sin GPSJam hasta aclarar licencia, sin HIGH/CRITICAL y sin publicación.

El diseño completo, la auditoría y los criterios están en `docs/B8.1-AUDITORIA-PILOTO-2026-11.md`.
