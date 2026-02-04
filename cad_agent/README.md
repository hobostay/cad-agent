# CAD Agent

> AI 驱动的智能机械设计系统

CAD Agent 是一个基于大语言模型（LLM）的智能 CAD 设计系统，能够通过自然语言生成 2D DXF 工程图和 3D STL 模型。

## 特性

- 🗣️ **自然语言交互** - 用对话方式描述设计需求
- 🎯 **智能生成** - 自动识别零件类型和参数
- 📄 **双格式输出** - 2D DXF 工程图 + 3D STL 模型
- 🔧 **19+ 零件类型** - 齿轮、轴承、螺栓、底板等
- ✅ **工程验证** - 内置工程知识库
- 🌐 **Web 界面** - 可视化设计平台

## 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd cad_agent

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 配置 API Key

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

### 使用

```bash
# 命令行模式
python3 cli.py "设计一个模数2、齿数20的齿轮"

# 3D 打印模式
python3 cli.py "M10螺栓长度50mm" --3d

# Web 界面
./start_web.sh

# API 服务
python3 app.py
# 访问 http://localhost:8000/docs 查看 API 文档
```

## 文档

- [快速开始](docs/QUICKSTART.md) - 5 分钟上手指南
- [使用指南](docs/GUIDE.md) - 完整功能说明
- [Web 界面](docs/WEB.md) - Web 平台使用
- [3D 打印](docs/3D.md) - 3D 建模与打印
- [技术规范](cad_agent.md) - 系统架构

## 支持的零件类型

### 基础零件
- 底板、螺栓、螺母、垫圈、螺丝

### 传动零件
- 齿轮、链轮、皮带轮、传动轴、阶梯轴、联轴器

### 支撑零件
- 轴承、法兰、支架、弹簧、车架

### 自定义
- 使用 TurtleCAD 绘制任意形状

## 使用示例

```bash
# 基础零件
python3 cli.py "500x300的底板，厚度10mm，四角M8螺丝孔"
python3 cli.py "模数2齿数24的直齿轮，压力角20度"
python3 cli.py "6208轴承"

# 复杂零件
python3 cli.py "600x400安装板，厚15mm，四角M10沉孔深度8mm"
python3 cli.py "传动轴总长200mm，三段：直径30-25-20"

# 3D 打印
python3 cli.py "齿轮" --3d --output gear.stl

# 直接模式（无需 API）
python3 cli.py --direct --type gear --params '{"module":2,"teeth":20}' --3d

# 标准件查询
python3 cli.py --standard
```

## 项目结构

```
cad_agent/
├── cli.py              # 统一命令行工具
├── web_app.py          # Web 界面
├── app.py              # API 服务
├── core/               # 核心模块
│   ├── config.py       # 配置管理
│   ├── agent.py        # Agent 编排
│   └── api_client.py   # API 客户端
├── gen_parts.py        # 2D 生成器
├── gen_parts_3d.py     # 3D 生成器
├── standard_parts/     # 标准件库
├── docs/               # 文档
└── requirements.txt    # 依赖列表
```

## 技术栈

- **LLM**: OpenAI GPT / 智谱 GLM / DeepSeek / 通义千问
- **CAD**: ezdxf (DXF 生成)
- **3D**: numpy-stl (STL 生成)
- **Web**: Streamlit

## 开发

```bash
# 运行测试
python3 -m pytest

# 代码检查
black . --check
flake8 .
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系

如有问题或建议，请提交 Issue。
