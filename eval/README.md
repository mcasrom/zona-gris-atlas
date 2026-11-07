# Evaluación opcional

El clasificador es **experimental y no publica fichas**. No existe una puerta
de publicación ni un requisito de etiquetado masivo.

`metrics.py` está disponible para quien quiera medir una muestra concreta, pero
sus resultados no bloquean releases ni convierten una propuesta en un hecho
publicado. La revisión humana relevante es **por ficha**: fuente, fecha, lugar,
atribución y estado.


Campos de una muestra opcional, si alguien la construye:

- `id`
- `title`
- `text`
- `domain` (`CIB`, `INF`, `AER`, `GNS`, `SAB`, `DES`, `ECO`, `MIG`)
- `severity` (`baja`, `media`, `alta`)
- `reality` (`probable`, `dudoso`, `descartado`)
- `attribution`: `status`, `attributed_by`, `source_url`
