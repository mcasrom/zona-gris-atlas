# Arquitectura

## Principios

- Estático primero: la web no necesita backend ni base de datos en producción.
- SQLite para la revisión local; el JSON es el contrato de publicación.
- Sin APIs de pago, sin modelos descargados automáticamente y sin servicios externos en la página.
- El pipeline se ejecuta por lotes, con caché y sin cargar el corpus entero en memoria.

## Componentes

```text
GDELT / RSS autorizados
        │
        ▼
ingest (caché + ritmo) ──► raw_items ──► dedupe ──► incidents
                                                   │
                                                   ▼
                                      classify (propone, no publica)
                                                   │
                                                   ▼
                                         revisión humana
                                                   │
                                                   ▼
                                  export JSON + Atom ──► web estática
```

## Presupuesto de memoria en el VPS de 4 GB

El servidor comparte RAM con otros servicios. La unidad de `zonagris` lleva `MemoryMax=1200M`; no se asume que pueda usar 4 GB.

| Componente | Presupuesto orientativo |
|---|---:|
| Sistema base y agentes | 700 MB |
| Otros servicios del VPS | 1.500 MB |
| `zonagris` (lote, máximo) | 1.200 MB |
| SQLite, caché y ficheros | 200 MB |
| Margen de seguridad | 400 MB |
| **Total** | **4.000 MB** |

El proceso por lotes debe trabajar por trozos y cerrar conexiones. La web es estática y no compite por RAM con el pipeline.

## Producción

La v0.1 **no se despliega** en esta sesión. `deploy/zonagris.service` y `deploy/zonagris.timer` quedan preparados para una fase posterior, con `MemoryMax=1200M` y `Nice=10`.
