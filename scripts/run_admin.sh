#!/usr/bin/env bash
# 启动 FastAPI 后台服务。
set -euo pipefail

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$PROJECT_ROOT"

VENV_DIR=${VENV_DIR:-$PROJECT_ROOT/.venv}
UVICORN_BIN="$VENV_DIR/bin/uvicorn"

if [ ! -x "$UVICORN_BIN" ]; then
  echo "[tg-sms] 未找到虚拟环境 $VENV_DIR，请先运行 bash scripts/bootstrap.sh" >&2
  exit 1
fi

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8080}
WORKERS=${WORKERS:-1}

exec "$UVICORN_BIN" admin.main:app --host "$HOST" --port "$PORT" --workers "$WORKERS" "$@"
