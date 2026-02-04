# CAD Agent - 快速开始指南

> 5分钟上手 AI 驱动的智能机械设计系统

## 环境准备

### 1. 安装依赖

```bash
# 使用虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

创建 `config.env.local` 文件：

```bash
OPENAI_API_KEY=<API 密钥>
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

**推荐 API 提供商：**
- 智谱 GLM: https://open.bigmodel.cn（有免费额度）
- DeepSeek: https://www.deepseek.com
- 通义千问: https://dashscope.aliyuncs.com

## 快速使用

### 命令行模式

```bash
# 基础零件设计
python3 cli.py "设计一个模数2、齿数20的齿轮"

# 3D 打印模型
python3 cli.py "M10螺栓长度50mm" --3d

# 查看标准件库
python3 cli.py --standard

# 静默模式
python3 cli.py "6204轴承" --quiet
```

### Web 界面模式

```bash
# 启动 Web 服务
./start_web.sh

# 或直接运行
streamlit run web_app.py
```

访问 http://localhost:8501

### API 服务模式

```bash
# 启动 API 服务
python3 app.py
```

访问 http://localhost:8000/docs 查看 API 文档

## 输出文件

- **2D DXF**: 工程图纸，可用 AutoCAD、SolidWorks 打开
- **3D STL**: 3D 打印模型，可用 Blender、Cura 打开

文件自动保存到当前目录，并复制到桌面。

## 常见问题

### API 调用失败
- 检查 API Key 是否正确
- 检查网络连接
- 尝试其他 API 提供商

### 依赖安装失败
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Web 界面无法访问
```bash
# 检查端口占用
lsof -i :8501

# 更换端口
streamlit run web_app.py --server.port 8502
```

## 下一步

- 阅读 [完整使用指南](GUIDE.md)
- 了解 [3D 打印功能](3D.md)
- 查看 [Web 界面文档](WEB.md)
- 了解 [技术规范](cad_agent.md)
