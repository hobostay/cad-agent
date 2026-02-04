#!/usr/bin/env bash
# 从项目根目录运行 CAD 命令行入口（生成 + 验收）
# 用法:
#   ./scripts/run_cli.sh <length> <width> <hole_diameter> <corner_offset>
#   ./scripts/run_cli.sh --nl "500×300底板，四角孔直径12mm，孔距边25mm"
#   ./scripts/run_cli.sh --nl "一句描述" --api
# 示例: ./scripts/run_cli.sh 500 300 12 25

set -e
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-.venv/bin/python3}"
if [ ! -x "$PYTHON" ]; then
  PYTHON="python3"
fi
exec "$PYTHON" cad_agent/cad_cli.py "$@"
