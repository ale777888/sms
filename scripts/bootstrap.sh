#!/usr/bin/env bash
# Bootstrap environment for tg-sms-suite on Debian/Ubuntu-like hosts.
set -euo pipefail

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$PROJECT_ROOT"

SUDO=""
if command -v sudo >/dev/null 2>&1 && [ "${EUID:-$(id -u)}" -ne 0 ]; then
  SUDO="sudo"
fi

echo "[tg-sms] Starting bootstrap in $PROJECT_ROOT"

APT_PACKAGES=(python3 python3-venv python3-pip sqlite3 unzip)
if command -v apt-get >/dev/null 2>&1; then
  if [ "${SKIP_APT_UPDATE:-0}" -ne 1 ]; then
    echo "[tg-sms] Updating apt package index..."
    $SUDO apt-get update -y
  fi
  echo "[tg-sms] Installing system packages: ${APT_PACKAGES[*]}"
  $SUDO apt-get install -y "${APT_PACKAGES[@]}"
else
  echo "[tg-sms] apt-get not found, ensure ${APT_PACKAGES[*]} are available" >&2
fi

PYTHON_BIN=${PYTHON_BIN:-python3}
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[tg-sms] Python interpreter '$PYTHON_BIN' not found" >&2
  exit 1
fi

VENV_DIR=${VENV_DIR:-$PROJECT_ROOT/.venv}
if [ ! -d "$VENV_DIR" ]; then
  echo "[tg-sms] Creating virtualenv at $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

PIP_BIN="$VENV_DIR/bin/pip"
if [ ! -x "$PIP_BIN" ]; then
  echo "[tg-sms] pip executable not found in $VENV_DIR" >&2
  exit 1
fi

echo "[tg-sms] Installing Python dependencies..."
"$PIP_BIN" install --upgrade pip
"$PIP_BIN" install -r requirements.txt

if [ ! -f .env ]; then
  echo "[tg-sms] Seeding .env from .env.example (edit required!)"
  cp .env.example .env
fi

mkdir -p data
if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "[tg-sms] sqlite3 command not available; install it before continuing" >&2
  exit 1
fi

DB_PATH=${DB_PATH:-$PROJECT_ROOT/data/tg_sms.db}
if [ ! -f "$DB_PATH" ]; then
  echo "[tg-sms] Initialising SQLite database at $DB_PATH"
  sqlite3 "$DB_PATH" < migrations/versions/0001_init.sql
else
  echo "[tg-sms] Database already exists at $DB_PATH"
fi

LOG_DIR=$(grep -E '^LOG_DIR=' .env | head -n1 | cut -d'=' -f2- | tr -d '\r')
LOG_DIR=${LOG_DIR//[[:space:]]/}
if [ -n "$LOG_DIR" ]; then
  if [ ! -d "$LOG_DIR" ]; then
    echo "[tg-sms] Creating log directory $LOG_DIR"
    $SUDO mkdir -p "$LOG_DIR"
    if [ -n "$SUDO" ]; then
      $SUDO chown "${USER:-$(id -un)}":"${USER:-$(id -un)}" "$LOG_DIR"
    fi
  fi
else
  echo "[tg-sms] LOG_DIR not set in .env; update the file before going live" >&2
fi

cat <<'SUMMARY'

[tg-sms] Bootstrap complete.
Next steps:
  1. Edit .env with real TELEGRAM_BOT_TOKEN, SMS_TOKEN, JWT_SECRET, etc.
  2. Activate the venv: source .venv/bin/activate
  3. Run services:
       - Bot:      python -m bot.app
       - Admin UI: uvicorn admin.main:app --host 0.0.0.0 --port 8080
SUMMARY
