#!/usr/bin/env bash
# Recogida automática + build local. No publica salvo que ZG_AUTO_DEPLOY=1.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
.venv/bin/python scripts/ingest_events.py
.venv/bin/python scripts/ingest_primary.py
.venv/bin/python scripts/build_web.py
.venv/bin/python scripts/make_og.py
if [ "${ZG_AUTO_DEPLOY:-0}" = "1" ]; then
  : "${SERVER:?define SERVER para desplegar}"
  : "${ZG_DOMAIN:?define ZG_DOMAIN para desplegar}"
  SERVER="$SERVER" ZG_DOMAIN="$ZG_DOMAIN" ./scripts/deploy_web.sh --apply
fi
