#!/usr/bin/env bash
# Despliegue estático con releases + current.
# Por defecto SOLO dry-run. Requiere --apply para tocar el servidor.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER="${SERVER:?define SERVER, por ejemplo: export SERVER=178.105.80.193}"
REMOTE_ROOT="${ZG_REMOTE_ROOT:-/var/www/atlas-zonagris}"
RELEASES="$REMOTE_ROOT/releases"
CURRENT="$REMOTE_ROOT/current"
APPLY=0
ROLLBACK=0

for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    --rollback) ROLLBACK=1 ;;
    --dry-run) APPLY=0 ;;
    *) echo "uso: $0 [--dry-run|--apply] [--rollback]" >&2; exit 2 ;;
  esac
done

if [ "$ROLLBACK" = "1" ]; then
  mapfile -t versions < <(ssh "deploy@$SERVER" "ls -1dt '$RELEASES'/* 2>/dev/null")
  if [ "${#versions[@]}" -lt 2 ]; then
    echo "No hay dos releases para hacer rollback." >&2
    exit 1
  fi
  target="${versions[1]}"
  echo "rollback -> $target"
  if [ "$APPLY" = "1" ]; then
    ssh "deploy@$SERVER" "ln -sfn '$target' '$CURRENT'"
    echo "current actualizado."
  else
    echo "dry-run: no se ha cambiado el enlace current."
  fi
  exit 0
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TARGET="$RELEASES/$STAMP"
echo "destino: deploy@$SERVER:$TARGET"

rsync -az --delete --dry-run -e ssh "$ROOT/web/" "deploy@$SERVER:$TARGET/"
if [ "$APPLY" != "1" ]; then
  echo "dry-run: no se ha creado el release ni cambiado current."
  exit 0
fi

ssh "deploy@$SERVER" "mkdir -p '$RELEASES'"
rsync -az --delete -e ssh "$ROOT/web/" "deploy@$SERVER:$TARGET/"
ssh "deploy@$SERVER" "ln -sfn '$TARGET' '$CURRENT'"
echo "desplegado: $TARGET"
echo "rollback: SERVER=$SERVER $0 --apply --rollback"
