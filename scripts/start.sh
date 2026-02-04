#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "未检测到 python3，请先安装 Python 3.9+。"
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "创建虚拟环境..."
  python3 -m venv .venv
fi

source ".venv/bin/activate"

echo "安装依赖..."
pip install -r requirements.txt

cd cad_agent

if [ ! -f "config.env.local" ]; then
  echo "未发现 config.env.local，正在创建模板..."
  cat > config.env.local <<'EOF'
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=glm-4-plus
EOF
  echo "请编辑 cad_agent/config.env.local，填入你的 API Key。"
  exit 1
fi

if grep -q "your_api_key_here" "config.env.local"; then
  echo "请先在 cad_agent/config.env.local 中填写 OPENAI_API_KEY。"
  exit 1
fi

echo "启动服务: http://localhost:8000"
python3 app.py
