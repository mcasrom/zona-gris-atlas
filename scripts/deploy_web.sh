#!/usr/bin/env bash
# Despliegue estático con releases + current.
# Sin --apply no conecta al servidor: solo imprime el plan.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER="${SERVER:?define SERVER, por ejemplo: export SERVER=178.105.80.193}"
DOMAIN="${ZG_DOMAIN:-}"
REMOTE_ROOT="${ZG_REMOTE_ROOT:-/var/www/atlas-zonagris}"
PROJECT_REMOTE_ROOT="/var/www/atlas-zonagris"
ALLOW_CUSTOM_ROOT="${ZG_ALLOW_CUSTOM_REMOTE_ROOT:-0}"
RELEASES="$REMOTE_ROOT/releases"
CURRENT="$REMOTE_ROOT/current"
APPLY=0
ROLLBACK=0
LOCK_FILE="${TMPDIR:-/tmp}/atlas-zonagris-deploy.lock"

case "$REMOTE_ROOT" in
  /|""|*..*) echo "ZG_REMOTE_ROOT no puede ser /, vacío ni contener .." >&2; exit 2 ;;
  /*) ;;
  *) echo "ZG_REMOTE_ROOT debe ser una ruta absoluta" >&2; exit 2 ;;
esac
if [ "$REMOTE_ROOT" != "$PROJECT_REMOTE_ROOT" ] && [ "$ALLOW_CUSTOM_ROOT" != "1" ]; then
  echo "ZG_REMOTE_ROOT debe ser $PROJECT_REMOTE_ROOT (o ZG_ALLOW_CUSTOM_REMOTE_ROOT=1 solo para pruebas locales)." >&2
  exit 2
fi

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "hay otro despliegue en curso" >&2
  exit 1
fi

for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    --rollback) ROLLBACK=1 ;;
    --dry-run) APPLY=0 ;;
    *) echo "uso: $0 [--dry-run|--apply] [--rollback]" >&2; exit 2 ;;
  esac
done

remote() {
  ssh -o BatchMode=yes -o ConnectTimeout=10 "deploy@$SERVER" "$1"
}

if [ "$ROLLBACK" = "1" ]; then
  if [ "$APPLY" != "1" ]; then
    echo "rollback: requiere --apply para leer el estado remoto y cambiar current."
    echo "plan: elegir el release inmediatamente anterior al actual y apuntar $CURRENT."
    exit 0
  fi
  versions="$(remote "ls -1d '$RELEASES'/* 2>/dev/null | sort -r" || true)"
  current_target="$(remote "readlink -f '$CURRENT' 2>/dev/null" || true)"
  mapfile -t all < <(printf '%s\n' "$versions" | sed '/^$/d')
  if [ "${#all[@]}" -eq 0 ]; then
    echo "estado inicial: no hay releases; nada que hacer."
    exit 0
  fi
  if [ -z "$current_target" ]; then
    echo "estado inicial: no hay current activo; nada que hacer."
    exit 0
  fi
  current_index=-1
  for i in "${!all[@]}"; do
    if [ "${all[$i]}" = "$current_target" ]; then
      current_index="$i"
      break
    fi
  done
  if [ "$current_index" -lt 0 ]; then
    echo "current no apunta a ningún release; no se hace rollback." >&2
    exit 1
  fi
  if [ "${#all[@]}" -eq 1 ]; then
    echo "rollback inicial -> sin release activa"
    remote "rm -f '$CURRENT'"
    remote "readlink -f '$CURRENT' 2>/dev/null || true"
    exit 0
  fi
  if [ $((current_index + 1)) -ge "${#all[@]}" ]; then
    echo "El release actual es el más antiguo; no hay versión anterior." >&2
    exit 1
  fi
  previous="${all[$((current_index + 1))]}"
  echo "rollback -> $previous"
  remote "ln -sfn '$previous' '$CURRENT'"
  remote "readlink -f '$CURRENT'"
  exit 0
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TARGET="$RELEASES/$STAMP"
echo "destino: deploy@$SERVER:$TARGET"
if [ "$APPLY" != "1" ]; then
  echo "dry-run: se ejecutará (sin conexión):"
  echo "  ssh deploy@$SERVER \"mkdir -p '$RELEASES'\""
  echo "  rsync -az --delete -e ssh '$ROOT/web/' 'deploy@$SERVER:$TARGET/'"
  echo "  ssh deploy@$SERVER \"ln -sfn '$TARGET' '$CURRENT'\""
  exit 0
fi

if [ -z "$DOMAIN" ]; then
  echo "define ZG_DOMAIN con el dominio definitivo antes de --apply" >&2
  exit 1
fi
if grep -Rq --exclude-dir=.git -F "__DOMAIN__" "$ROOT/web"; then
  echo "La web contiene el placeholder __DOMAIN__; reconstruye con el dominio definitivo." >&2
  exit 1
fi
if ! grep -Rq --exclude-dir=.git -F "https://$DOMAIN" "$ROOT/web"; then
  echo "La web no contiene el dominio confirmado https://$DOMAIN; reconstruye antes de desplegar." >&2
  exit 1
fi
previous_target="$(remote "readlink -f '$CURRENT' 2>/dev/null" || true)"
if remote "test -e '$TARGET'"; then
  echo "El release ya existe; abortando para no borrar una versión." >&2
  exit 1
fi
remote "mkdir -p '$RELEASES'"
rsync -az --delete -e ssh "$ROOT/web/" "deploy@$SERVER:$TARGET/"
for required in index.html mapa.html incidentes.html cobertura.html suscribirse.html en.html primarias.html 404.html assets/css/styles.css assets/js/map.js; do
  if ! remote "test -f '$TARGET/$required'"; then
    echo "release incompleto: falta $required; no se cambia current." >&2
    exit 1
  fi
done
remote "ln -sfn '$TARGET' '$CURRENT'"
if ! remote "test -f '$TARGET/index.html'" || [ "$(remote "readlink -f '$CURRENT'")" != "$TARGET" ]; then
  echo "validación posterior al enlace falló; restaurando estado anterior." >&2
  if [ -n "$previous_target" ]; then
    remote "ln -sfn '$previous_target' '$CURRENT'"
  else
    remote "rm -f '$CURRENT'"
  fi
  exit 1
fi
remote "readlink -f '$CURRENT'"
echo "desplegado: $TARGET"
echo "rollback: SERVER=$SERVER $0 --apply --rollback"
