#!/usr/bin/env bash
# 启动 Telegram Bot 服务。
set -euo pipefail

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$PROJECT_ROOT"

VENV_DIR=${VENV_DIR:-$PROJECT_ROOT/.venv}
PYTHON_BIN="$VENV_DIR/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "[tg-sms] 未找到虚拟环境 $VENV_DIR，请先运行 bash scripts/bootstrap.sh" >&2
  exit 1
fi

source "$VENV_DIR/bin/activate"
exec python -m bot.app "$@"
