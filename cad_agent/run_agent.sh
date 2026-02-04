#!/bin/bash
# CAD Agent 启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 激活虚拟环境（如果存在）
if [ -d ".venv" ]; then
    source .venv/bin/activate
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# 设置 API Key（从环境变量或配置文件）
export OPENAI_API_KEY="${OPENAI_API_KEY:-}"
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://api.openai.com/v1}"

echo "=== CAD Agent - LLM 智能设计 ==="
echo "API: $OPENAI_BASE_URL"
echo "模型: ${OPENAI_MODEL:-gpt-4}"
echo ""

# 运行 Agent
$PYTHON_CMD cli.py "$@"
