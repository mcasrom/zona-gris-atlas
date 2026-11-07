#!/usr/bin/env bash
# Actualización automática en el servidor: captura, merge, nueva release y current.
# No toca Nginx, DNS ni TLS. Conserva releases anteriores para rollback.
set -euo pipefail
BASE="/home/deploy/atlas-zonagris-auto"
CURRENT="/var/www/atlas-zonagris/current"
RELEASES="/var/www/atlas-zonagris/releases"
LOCK="/tmp/atlas-zonagris-auto.lock"
mkdir -p "$BASE/logs"
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "$(date -u +%FT%TZ) otra actualización en curso" >&2
  exit 1
fi
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TARGET="$RELEASES/$STAMP"
cd "$BASE"
/usr/bin/python3 scripts/ingest_events.py \
  --places data/event_places.json \
  --out data/events/auto/events.jsonl \
  --sources data/events/auto/sources.json \
  --limit 120
/usr/bin/python3 scripts/ingest_primary.py || echo "CERT-EU no disponible; se conserva la capa anterior" >&2
/usr/bin/python3 scripts/build_events_data.py \
  --curated data/events/2026-11-06/events.jsonl \
  --auto data/events/auto/events.jsonl \
  --out "$BASE/build/events.json"
test -s "$BASE/build/events.json"
test -f "$CURRENT/assets/data/events.json"
mkdir -p "$TARGET"
cp -a "$CURRENT"/. "$TARGET/"
cp "$BASE/build/events.json" "$TARGET/assets/data/events.json"
if [ -s "$BASE/data/events/primary/documents.json" ]; then
  cp "$BASE/data/events/primary/documents.json" "$TARGET/assets/data/primary.json"
fi
/usr/bin/python3 - "$TARGET/assets/data/events.json" <<'PY2'
import json, sys
p=sys.argv[1]
d=json.load(open(p, encoding='utf-8'))
assert int(d.get('count',0)) >= 16, 'pocos registros'
assert all(e.get('verification_status') != 'CONFIRMADO' for e in d['events'] if e.get('automated')), 'automático confirmado'
print('eventos', d['count'])
PY2
if [ -n "${PREVIOUS_TARGET:-}" ]; then :; fi
ln -sfn "$TARGET" "$CURRENT"
echo "$(date -u +%FT%TZ) release $TARGET · $(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["count"])' "$TARGET/assets/data/events.json") eventos"
