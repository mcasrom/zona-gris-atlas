#!/usr/bin/env bash
# Copia de seguridad local del repositorio en un git bundle fechado.
# Conserva los últimos 10. El remoto de GitHub es la copia principal.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${ZG_BACKUP_DIR:-$HOME/backups/zona-gris-atlas}"
KEEP="${ZG_BACKUP_KEEP:-10}"

mkdir -p "$DEST"
cd "$REPO_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BUNDLE="$DEST/zona-gris-atlas-$STAMP.bundle"
git bundle create "$BUNDLE" --all
git bundle verify "$BUNDLE" >/dev/null
ls -1t "$DEST"/zona-gris-atlas-*.bundle 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -f
printf 'backup: %s\n' "$BUNDLE"
