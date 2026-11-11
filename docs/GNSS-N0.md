# GNSS · N0

**Estado:** inventario en curso. **No hay N1.**

## Alcance

Registro de **episodios documentados** de interferencia, suplantación o perturbación
GNSS que afecten a navegación civil, aviación o infraestructura crítica.

No incluye:

- una alerta genérica sin episodio identificable;
- un comunicado institucional sin fecha y lugar;
- un hueco de recepción ADS-B;
- una atribución de autoría por inferencia;
- ejercicios militares sin afectación civil documentada.

## Unidad de inventario

Un **episodio** (`record_type: episode`) por combinación de:

- fecha del hecho (no de publicación);
- región o lugar documentado;
- tipo: `jamming`, `spoofing` o `interference`;
- fuente directa.

Dos piezas del mismo episodio no crean dos inventarios. Una nueva fecha o una
zona distinta sí pueden ser episodios separados, pero deben justificarse.

Los **agregados** (`record_type: aggregate`) y las **alertas** (`alert`) se guardan
como contexto y **no cuentan** para la puerta N1.

## Evidencia

| Nivel | Qué es | Uso |
|---|---|---|
| `medicion` | Datos técnicos agregados (p. ej. mapas de interferencia) | Contexto; no es un incidente por sí solo |
| `oficial` | Aviso o comunicación de autoridad | Documenta el marco o la alerta |
| `prensa` | Pieza periodística con fecha y lugar | Candidato a episodio |
| `operador` | Aerolínea, aeropuerto o proveedor afectado | Refuerza el episodio si es directo |

Una alerta no se convierte en incidente. Una medición agregada no se convierte en
una ficha sin un episodio concreto.

## Campos

`inventory_id,event_date,region,country,place,event_type,record_type,source_url,source_type,evidence_type,status,notes`

## Estados

- `PENDIENTE`: candidato, sin revisión suficiente.
- `DOCUMENTADO`: episodio con fuente directa y fecha/lugar comprobados.
- `DESCARTADO`: no cumple alcance; se conserva el motivo.

## Puerta para GNSS N1

No se abre N1 hasta cumplir:

- **50 episodios** únicos (`record_type: episode`, `DOCUMENTADO`);
- **24 meses** con datos;
- al menos **2 grupos de fuente independientes**;
- revisión manual de fechas, lugares y duplicados.

Con el inventario actual no se publica tendencia, frecuencia ni nivel de amenaza.
