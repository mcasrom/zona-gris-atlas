# Taxonomía

## Dominios

- **CIB · Ciber.** Intrusiones, phishing, ransomware y operaciones contra sistemas.
- **INF · Infraestructura crítica.** Energía, agua, transporte, sanidad o telecomunicaciones.
- **AER · Espacio aéreo y drones.** Incursiones, cierres de espacio aéreo, drones hostiles y alertas aeronáuticas.
- **GNS · Interferencia GNSS.** Interferencia o suplantación de GPS, Galileo y otros sistemas de navegación.
- **SAB · Sabotaje físico.** Daños deliberados a instalaciones, cables, gasoductos o equipos.
- **DES · Desinformación.** Operaciones coordinadas para alterar la percepción pública.
- **ECO · Coerción económica.** Presión comercial, energética o financiera con fines políticos.
- **MIG · Instrumentalización migratoria.** Uso político de flujos migratorios para presionar a un Estado.

## Escala

1. `paz_estable`: cooperación ordinaria y ausencia de presión hostil.
2. `competencia`: rivalidad sin coerción directa.
3. `zona_gris`: coerción ambigua por debajo del umbral armado.
4. `hostilidad_hibrida`: acciones hostiles combinadas, negables y sostenidas.
5. `conflicto_abierto`: violencia armada declarada o confrontación directa.

El atlas solo admite las posiciones **2, 3 y 4**.

## Gravedad

`baja`, `media`, `alta`. La gravedad describe el impacto observado o declarado, no la identidad del actor.

## Realidad del incidente

`probable`, `dudoso`, `descartado`. Sirve para filtrar falsas alarmas, drones de aficionados y ransomware puramente criminal.

## Atribución

`none`, `official`, `claimed`; además `attributed_by`, `attributed_by_type`, `source_url`, `confidence` y una cita corta. La atribución nunca se deduce por el dominio ni por la gravedad.
