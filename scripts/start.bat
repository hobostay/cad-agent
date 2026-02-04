@echo off
setlocal

set ROOT_DIR=%~dp0..
cd /d "%ROOT_DIR%"

where python >nul 2>nul
if errorlevel 1 (
  echo 未检测到 Python，请先安装 Python 3.9+。
  exit /b 1
)

if not exist ".venv" (
  echo 创建虚拟环境...
  python -m venv .venv
)

call .venv\Scripts\activate.bat

echo 安装依赖...
pip install -r requirements.txt

cd cad_agent

if not exist "config.env.local" (
  echo 未发现 config.env.local，正在创建模板...
  > config.env.local echo OPENAI_API_KEY=your_api_key_here
  >> config.env.local echo OPENAI_BASE_URL=https://api.openai.com/v1
  >> config.env.local echo OPENAI_MODEL=glm-4-plus
  echo 请编辑 cad_agent\config.env.local，填入你的 API Key。
  exit /b 1
)

findstr /C:"your_api_key_here" config.env.local >nul
if %errorlevel%==0 (
  echo 请先在 cad_agent\config.env.local 中填写 OPENAI_API_KEY。
  exit /b 1
)

echo 启动服务: http://localhost:8000
python app.py
