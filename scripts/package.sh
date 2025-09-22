#!/usr/bin/env bash
# Package the entire project into tg-sms.zip archive.
set -euo pipefail

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$PROJECT_ROOT"

ARCHIVE_NAME=${1:-tg-sms.zip}

if ! command -v zip >/dev/null 2>&1; then
  echo "[tg-sms] Installing zip utility..."
  if command -v apt-get >/dev/null 2>&1; then
    SUDO=""
    if command -v sudo >/dev/null 2>&1 && [ "${EUID:-$(id -u)}" -ne 0 ]; then
      SUDO="sudo"
    fi
    $SUDO apt-get update -y
    $SUDO apt-get install -y zip
  else
    echo "[tg-sms] zip command missing and automatic install unavailable" >&2
    exit 1
  fi
fi

EXCLUDES=(
  ".venv/*"
  "*.pyc"
  "__pycache__/*"
  ".pytest_cache/*"
  "logs/*"
  "*.log"
  "*.sqlite-journal"
)
EXCLUDES+=("$ARCHIVE_NAME")

echo "[tg-sms] Creating archive $ARCHIVE_NAME"
zip -r "$ARCHIVE_NAME" . -x "${EXCLUDES[@]}"

printf '\n[tg-sms] Archive ready at %s/%s\n' "$PROJECT_ROOT" "$ARCHIVE_NAME"
