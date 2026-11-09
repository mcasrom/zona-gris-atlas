# Zona Gris · Open atlas of hybrid incidents

[![CI](https://github.com/mcasrom/zona-gris-atlas/actions/workflows/ci.yml/badge.svg)](https://github.com/mcasrom/zona-gris-atlas/actions/workflows/ci.yml)
[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-ffb020)](LICENSE)

> **Visible warning:** the public map contains reviewed records and automatic candidates. Candidates remain `PENDIENTE` and are never presented as confirmed incidents. There is no demonstration data.

An open atlas of gray-zone and hybrid-threat incidents. It records the event, its source and **who attributes it**. The system does not attribute authorship on its own.

## What it is, and what it is not

**It is** a dated record across ten domains: cyber, critical infrastructure, airspace and drones, GNSS interference, physical sabotage, disinformation, economic coercion, migration instrumentalisation, submarine cables and AI-enabled attacks.

**It is not** an automatic attribution engine, an attack predictor, a people profiler or a real-time intelligence base.

## Attribution principle

Attribution is a datum, not the system's conclusion. Each record keeps one of three states: `none`, `official` or `claimed`. It also stores who attributes, the source type, the source URL, a confidence level and a quote of at most 15 words. “Unattributed” is a valid and frequent result.

## Scale and taxonomy

The full scale runs from `paz_estable` to `conflicto_abierto`. This atlas covers only the middle: `competencia`, `zona_gris` and `hostilidad_hibrida`.

Domains: `CIB`, `INF`, `AER`, `GNS`, `SAB`, `DES`, `ECO`, `MIG`, `CAB`, `IAA`.

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

The home page combines a **compact map**, the latest records and an
**events-per-day strip** (last 8 days). The strip counts event dates, **not
ingestion runs**. Map lists use two independently scrolling columns on desktop
and one on mobile; markers only appear when a city or region is documented.

## Current state

- **Live:** <https://zonagris.pruebapublica.com>.
- **State (9 Nov):** 17 events · **16 documented** · **1 pending** · **12 located**. Map, matrix/API and no-JS fallback share the same total. `llms.txt` is published.
- **Automatic capture:** every 6 hours from Bing News RSS as discovery, plus a regional query matrix.
- **Primary layer:** `/primarias.html` — CERT-EU, JPCERT/CC, CERT.br and NCSC-UK documents; not incidents.
- **Coverage:** `/cobertura.html` — query scope, candidates and documented locations are separate.
- **Publication rule:** automatic candidates always remain `PENDIENTE`; only human review can promote a record to `DOCUMENTADO`.
- **Classifier:** experimental and never publishes. There is no release gate and no bulk-labelling requirement; human review is per record.
- **Geolocation:** `--geo-shadow` suggests countries without publishing them; not active in production.

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

`eval/metrics.py` is available for optional sample checks, but there is **no publication gate and no bulk-labelling requirement**. Human review is per record. The classifier is experimental and never publishes.

## Internal data quality

The internal layer lives in `data/quality/` and is **not published**:

- `quality_report.py`: normalization, TF-IDF dedupe, canonical events and correction proposals.
- `review.json`: 13 accepted and 17 rejected/pending corrections out of 30.
- `graph_report.py` and `graph_temporal.py`: co-occurrence and temporal graphs.
- `campaign_report.py`: candidate campaigns/waves with shared entities.
- `baseline_snapshot.py`: daily snapshot for a historical baseline.

Current state: **59 records → 45 canonical events**, 42 with a source timestamp, 19 with ISO country and 13 with an airport. The two reviewed campaigns are **internal hypotheses**, not attribution.

The `45 8 * * *` cron stores the daily snapshot on the server; the comparator stays `insufficient` until the minimum window is reached.

## Sources and licences

See `config/sources.yaml`. Bing News RSS is **discovery**. CERT-EU, JPCERT/CC, CERT.br and NCSC-UK feed the separate primary-document layer. CISA, CCN-CERT and other sources remain pending review. No paid APIs, cookies, trackers or remote Google Fonts.

## Limits

Read [`docs/LIMITES.md`](docs/LIMITES.md): no self-attribution, no prediction and no judging people. Submarine cables and AI-enabled attacks have explicit categories and strict criteria. It also documents source-diet bias and the strict **MIG** inclusion criteria: a migration flow is not, by itself, instrumentalisation.

Coverage lesson: [`docs/LECCION-AMERICA-ASIA.md`](docs/LECCION-AMERICA-ASIA.md). The Americas and Asia are not empty; they are outside the current source matrix. The note separates external hypotheses from verified records and states what is missing.

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md). Open an issue with the relevant template. Do not include personal data or secrets.

## License

Code under **AGPL-3.0** (see [`LICENSE`](LICENSE)). Original data (structure, metadata and editorial notes) is under **CC BY 4.0**; third-party headlines and articles keep their own rights and are only linked. See [`DATA-LICENSE.md`](DATA-LICENSE.md).

## Relationship with FIMI Radar

FIMI Radar measures network diffusion. Zona Gris measures **real-world events**. They do not share code.

## Geolocation shadow mode

`scripts/ingest_events.py --geo-shadow` proposes a country but does not publish it. The 7-Nov test produced false positives (hypothetical countries and actor mentions), so the flag stays off. See `docs/GEO-SOMBRA.md`.

## Continuity

See `docs/CONTINUIDAD.md` for maintainer and recovery. GitHub and the server are the copies; a local bundle is optional.
