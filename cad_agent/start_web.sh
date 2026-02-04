#!/bin/bash
# CAD Agent Web 界面启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 激活虚拟环境（如果存在）
if [ -d ".venv" ]; then
    source .venv/bin/activate
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║         🤖 CAD Agent - Web 界面启动                      ║"
echo "║                                                            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 检查 streamlit
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit 未安装"
    echo "正在安装..."
    $PIP_CMD install streamlit -q
    echo "✅ Streamlit 安装完成"
fi

echo "🚀 启动 Web 服务..."
echo ""
echo "📱 访问地址: http://localhost:8501"
echo "📋 按 Ctrl+C 停止服务"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 启动 Streamlit Web 界面
streamlit run web_app.py --server.port 8501
