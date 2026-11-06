# B19 · Auditoría SEO, Open Graph y CTR

**Fecha:** 2026-11-06  
**Release pública auditada:** `20261106T151553Z`  
**Estado:** **LISTO PARA PUBLICAR** (mejoras locales; sin despliegue ni push).

## 1. Diagnóstico

La base SEO de B16 era correcta: títulos y descripciones propios, canonical absoluto, `robots` explícito, `lang="es"`, un solo H1, sitemap válido y demo fuera del sitemap.

Faltaban cuatro piezas:

1. **Open Graph incompleto:** no había `og:site_name`, `og:locale`, `og:image:alt` ni Twitter Cards completas.
2. **Imagen social genérica:** todas las páginas usaban `og-preview.png`; `/registros.html` no tenía imagen propia.
3. **Datos estructurados:** no había JSON-LD.
4. **Coherencia de contenido:** `/fuentes.html` seguía diciendo que ninguna fuente estaba activa y `/metodologia.html` describía un modelo que no produjo la primera captura.

La versión pública actual mantiene esos huecos porque las mejoras son **locales**; no se ha desplegado.

## 2. Tabla SEO por página

| Página | Title | Description | Robots | Canonical | OG image | JSON-LD |
|---|---:|---:|---|---|---|---|
| `/` | 41 | 151 | `index,follow` | `/` | `og-atlas.png` | `WebSite` |
| `/registros.html` | 43 | 153 | `index,follow` | `/registros.html` | `og-registros.png` | `CollectionPage` |
| `/about.html` | 27 | 155 | `index,follow` | `/about.html` | `og-atlas.png` | `AboutPage` |
| `/avisos.html` | 24 | 159 | `index,follow` | `/avisos.html` | `og-atlas.png` | `WebPage` |
| `/metodologia.html` | 35 | 149 | `index,follow` | `/metodologia.html` | `og-atlas.png` | `WebPage` |
| `/fuentes.html` | 41 | 151 | `index,follow` | `/fuentes.html` | `og-atlas.png` | `WebPage` |
| `/privacidad.html` | 28 | 159 | `index,follow` | `/privacidad.html` | `og-atlas.png` | `WebPage` |
| `/limites.html` | 25 | 125 | `index,follow` | `/limites.html` | `og-atlas.png` | `WebPage` |
| `/demo.html` | 22 | 140 | `noindex, nofollow` | `/demo.html` | `og-atlas.png` | `WebPage` |

- Todos los títulos son únicos.
- Todas las descripciones están entre 120 y 160 caracteres.
- Todas las páginas declaran `lang="es"` y tienen un solo H1.
- `/registros.html` incluye un H2 oculto para cerrar la jerarquía H1 → H2 → H3.
- `/demo.html` queda fuera de la indexación.
- `/mapa.html` conserva `noindex` y meta refresh; no está en el sitemap.

## 3. Sitemap y robots.txt

- `sitemap.xml`: **8 URLs**, todas absolutas HTTPS, sin duplicados.
- Incluye portada, registros, método, límites, fuentes, privacidad, avisos y About.
- **No incluye** `/demo.html` ni `/mapa.html`.
- `lastmod` es `2026-11-06`, fecha de la captura y de la release B16; no se han inventado fechas.
- `robots.txt` permite el rastreo y declara el sitemap.
- No se añadió `Disallow: /demo.html`; se usa `noindex` para no impedir que el crawler vea la señal.

## 4. Open Graph y Twitter Cards

Implementado en todas las páginas:

- `og:title`, `og:description`, `og:type`, `og:url`
- `og:image`, `og:image:width`, `og:image:height`, `og:image:alt`
- `og:site_name` = **Atlas Zona Gris**
- `og:locale` = **es_ES**
- `twitter:card` = `summary_large_image`
- `twitter:title`, `twitter:description`, `twitter:image`, `twitter:image:alt`

### Imágenes OG

- `web/assets/img/og-atlas.png` — 1200 × 630, 44 KB.
- `web/assets/img/og-registros.png` — 1200 × 630, 46 KB.
- Diseño textual y sobrio, con la identidad visual de la web.
- La imagen principal incluye **«Atlas Zona Gris»** y el subtítulo **«Observación documental de riesgos e infraestructuras»**.
- La imagen de registros indica **«Ocho documentos institucionales»**, **«212 revisados · 8 incorporados · 204 descartados»**.
- Sin mapas, sin fotografías de cables, sin incidentes ficticios y sin imágenes externas.

## 5. Datos estructurados

Decisiones:

- **WebSite** en la portada.
- **WebPage** en About, Avisos, Método, Fuentes, Privacidad, Límites y Demo.
- **CollectionPage** en Registros.
- **AboutPage** en About.
- Todas incluyen `name`, `description`, `url`, `inLanguage: es` y `isPartOf` al WebSite.

No se añadieron:

- **Organization:** el proyecto es personal, no una organización.
- **Dataset:** no hay una licencia y distribución formal del conjunto completo.
- **Article:** las páginas no son artículos.
- **Premios, financiación, avales o instituciones:** no existen y no se inventan.

Los 9 bloques JSON-LD se parsearon correctamente con `json.loads`.

## 6. CTA y navegación

La portada ofrece tres acciones:

1. **Ver los 8 registros** → `/registros.html`.
2. **Leer el método** → `/metodologia.html`.
3. **Fuentes y condiciones** → `/fuentes.html`.

En `/registros.html` cada ficha enlaza a la **fuente original** y declara la condición de reutilización.

En About se explica la independencia y el contacto es **info.zonagris@pruebapublica.com**. No se añadieron formularios, suscripciones, donaciones ni servicios inexistentes.

## 7. CTR y medición

No hay acceso a Google Search Console ni Bing Webmaster Tools en esta sesión. **No se ha medido CTR, impresiones, clics, posición media ni consultas.** No hay Google Analytics, píxeles ni cookies.

Pasos necesarios para el propietario:

### Google Search Console

1. Crear la propiedad de dominio `zonagris.pruebapublica.com`.
2. Verificarla por DNS TXT en Cloudflare.
3. Enviar `https://zonagris.pruebapublica.com/sitemap.xml`.
4. Consultar **Rendimiento** para impresiones, clics, CTR, posición media, páginas de entrada y consultas.
5. Usar **Inspección de URL** para las páginas nuevas.

### Bing Webmaster Tools

1. Añadir el sitio o importarlo desde Search Console.
2. Verificar por DNS o metaetiqueta.
3. Enviar el sitemap.
4. Consultar **Search Performance**.

No se crean cuentas ni se instala seguimiento desde el servidor.

## 8. Rendimiento y accesibilidad

- Web total: **668 KB**.
- Portada: **12 KB**; registros: **16 KB**; CSS: **20 KB**; JS: **4 KB**.
- Imágenes OG: **44 KB** y **46 KB**.
- Sin frameworks, sin analítica, sin cookies, sin terceros.
- CSS responsive y `viewport` en todas las páginas.
- Enlaces internos comprobados: 10 rutas locales, todas 200.
- 404 local comprobado.
- `skip-link`, navegación con `aria-label`, `aria-current` y botón de menú.
- Única imagen del sitio: mapa decorativo de la demo con `alt`.
- No se ejecutó Lighthouse, PageSpeed ni una auditoría automática de contraste: no hay herramienta instalada y no se autorizó instalar dependencias.
- Core Web Vitals no medidos por falta de datos de campo.

## 9. Auditoría de contenidos

Se corrigieron afirmaciones que no correspondían a la primera captura:

- `/fuentes.html` ahora refleja **5 fuentes**, **212 revisados**, **8 incorporados**, **204 descartados**, con CERT-EU/BOE/Comisión en positivo y EASA/EUROCONTROL sin incorporaciones.
- `/metodologia.html` describe revisión documental y humana, no un modelo que publicaba.
- `/about.html` habla de **documentos y señales**, no de incidentes confirmados.
- `/limites.html` añade que no se afirma detectar sabotajes, interferencias GNSS o incidentes de cables submarinos sin registro real.
- La portada mantiene: **no mide incidentes confirmados, no atribuye autoría y no convierte una alerta en campaña**.
- No se añadieron palabras clave artificiales ni cifras de incidentes.

## 10. Mejoras realizadas

- Metadatos OG/Twitter completos en 9 páginas.
- Imagen `og-atlas.png` y `og-registros.png`.
- JSON-LD justificado en 9 páginas.
- H2 oculto para la jerarquía de registros.
- CTA de fuentes en portada.
- Corrección de contenido de Fuentes, Método, About y Límites.
- Descripciones ajustadas a 120–160 caracteres.
- `robots` explícito y `404` con `noindex`.
- `sr-only` para etiquetas accesibles.

## 11. Mejoras pendientes

- **Desplegar** estas mejoras; la versión pública aún usa `og-preview.png` y carece de Twitter Cards y JSON-LD.
- Verificar las URLs en Google Search Console y Bing Webmaster Tools.
- Revisar las previsualizaciones con los depuradores de Open Graph de las plataformas.
- Ejecutar PageSpeed/Lighthouse cuando el propietario lo autorice.
- Verificar externamente la disponibilidad de las 8 fuentes originales; el DNS local falló en esta sesión y no se debe afirmar que están caídas.
- Valorar `Dataset` solo si se publica una distribución estable con licencia explícita.

## 12. Validación y Git

- `make lint`: **OK**.
- `make test`: **19 passed**.
- Páginas locales: **200**; `/no-existe`: **404**.
- `/mapa.html`: meta refresh y `noindex`.
- `/demo.html`: `noindex, nofollow`; 10 casos demo.
- Sitemap: XML válido, 8 URLs, sin demo/mapa.
- **15 commits locales** conservados.
- Cambios B19 sin commit y **sin push**.
- No se desplegó, no se tocó Nginx/DNS/TLS, no se modificaron B11/B13/B14 ni se ejecutaron ingestas.

## 13. Veredicto

**LISTO PARA PUBLICAR** localmente. La publicación de estas mejoras requiere autorización posterior.
