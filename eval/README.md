# Evaluación opcional

El clasificador es **experimental y no publica fichas**. No existe una puerta
de publicación ni un requisito de etiquetar 200 eventos.

`metrics.py` está disponible para quien quiera medir una muestra concreta, pero
sus resultados no bloquean releases ni convierten una propuesta en un hecho
publicado. La revisión humana relevante es **por ficha**: fuente, fecha, lugar,
atribución y estado.

`gold/ejemplo.jsonl` documenta únicamente el formato de una posible muestra
opcional. No es un conjunto de evaluación ni una obligación de etiquetado.

Campos de cada línea, si se usa una muestra:

- `id`
- `title`
- `text`
- `domain` (`CIB`, `INF`, `AER`, `GNS`, `SAB`, `DES`, `ECO`, `MIG`)
- `severity` (`baja`, `media`, `alta`)
- `reality` (`probable`, `dudoso`, `descartado`)
- `attribution`: `status`, `attributed_by`, `source_url`
