# Zona Gris · Open atlas of hybrid incidents

[![CI](https://github.com/mcasrom/zona-gris-atlas/actions/workflows/ci.yml/badge.svg)](https://github.com/mcasrom/zona-gris-atlas/actions/workflows/ci.yml)
[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-ffb020)](LICENSE)

> **Visible warning:** the public map contains curated records and automatic candidates. Candidates remain `PENDIENTE` and are never presented as confirmed incidents. There is no demonstration data.

An open atlas of gray-zone and hybrid-threat incidents. It records the event, its source and **who attributes it**. The system does not attribute authorship on its own.

## What it is, and what it is not

**It is** a dated record across eight domains: cyber, critical infrastructure, airspace and drones, GNSS interference, physical sabotage, disinformation, economic coercion and migration instrumentalisation.

**It is not** an automatic attribution engine, an attack predictor, a people profiler or a real-time intelligence base. Submarine cables are outside v0.1.

## Attribution principle

Attribution is a datum, not the system's conclusion. Each record keeps one of three states: `none`, `official` or `claimed`. It also stores who attributes, the source type, the source URL, a confidence level and a quote of at most 15 words. “Unattributed” is a valid and frequent result.

## Scale and taxonomy

The full scale runs from `paz_estable` to `conflicto_abierto`. This atlas covers only the middle: `competencia`, `zona_gris` and `hostilidad_hibrida`.

Domains: `CIB`, `INF`, `AER`, `GNS`, `SAB`, `DES`, `ECO`, `MIG`.

## Pipeline

```mermaid
flowchart LR
  A[Registered sources] --> B[Ingestion with cache]
  B --> C[URL and text dedupe]
  C --> D[Classifier suggests]
  D --> E[Human review]
  E --> F[Published record]
  F --> G[Static web + JSON + Atom]
  E --> X[Rejected or draft]
```

## Current state

- **Live:** <https://zonagris.pruebapublica.com>.
- **Automatic capture:** every 6 hours from Bing News RSS, registered as a discovery aggregator, not as a primary source.
- **Publication rule:** automatic candidates always remain `PENDIENTE`; only human review can promote a record to `DOCUMENTADO`.
- **Classifier:** experimental and never publishes. There is no release gate and no requirement to label 200 events; human review is per record.

## Quick start

```bash
make setup
make lint
make test
make web
make serve
# http://localhost:8080
```

Commands: `setup`, `lint`, `test`, `ingest`, `classify`, `export`, `web`, `serve`, `backup`.

## Backup

GitHub is the primary copy. The local bundle is the second:

```bash
make backup
# ~/backups/zona-gris-atlas/zona-gris-atlas-<timestamp>.bundle
```

Daily cron example:

```cron
15 3 * * * cd "$HOME/zona-gris-atlas" && ./scripts/backup.sh >> "$HOME/backups/zona-gris-atlas/backup.log" 2>&1
```

The last **10** bundles are kept.

## Evaluation

`eval/metrics.py` is available for optional sample checks, but there is **no publication gate and no 200-event labelling requirement**. Human review is per record. The classifier is experimental and never publishes.

## Sources and licences

See `config/sources.yaml`. Bing News RSS is an **active discovery aggregator**; institutional sources remain disabled pending review. No paid APIs, cookies, trackers or remote Google Fonts.

## Limits

Read [`docs/LIMITES.md`](docs/LIMITES.md): no self-attribution, no prediction, no judging people and no submarine cables in v0.1. It also documents source-diet bias and the strict **MIG** inclusion criteria: a migration flow is not, by itself, instrumentalisation.

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md). Open an issue with the relevant template. Do not include personal data or secrets.

## License

Code under **AGPL-3.0** (see [`LICENSE`](LICENSE)). Original data (structure, metadata and editorial notes) is under **CC BY 4.0**; third-party headlines and articles keep their own rights and are only linked. See [`DATA-LICENSE.md`](DATA-LICENSE.md).

## Relationship with FIMI Radar

FIMI Radar measures network diffusion. Zona Gris measures **real-world events**. They do not share code.

## Continuity

See `docs/CONTINUIDAD.md` for maintainer, recovery and off-site backup status. A verified off-site copy is still pending.
