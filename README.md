# 🤖 CAD Agent - 智能机械零件设计系统

一个强大的 AI 驱动 CAD 系统，可以自动生成各种机械零件的 DXF 图纸。

---

## ✨ 特性

### 🎯 核心功能
- **自然语言输入** - 用简单的中文描述即可生成复杂零件
- **10+ 零件类型** - 支持齿轮、轴承、车架、法兰等常见机械零件
- **标准件库** - 内置轴承、螺栓等标准件参数
- **工程验收** - 自动验证图纸的工程合理性
- **装配体支持** - 支持多个零件组合成装配图
- **TurtleCAD** - 可编程绘图引擎，支持任意复杂形状

### 🔧 支持的零件类型

| 零件类型 | 说明 | 主要参数 |
|---------|------|----------|
| `plate` | 底板 | length, width, hole_diameter, corner_offset |
| `gear` | 齿轮 | module, teeth, pressure_angle, bore_diameter |
| `bearing` | 轴承 | inner_diameter, outer_diameter, width |
| `flange` | 法兰 | outer_diameter, inner_diameter, bolt_count |
| `bolt` | 螺栓 | diameter, length |
| `spring` | 弹簧 | wire_diameter, coil_diameter, free_length |
| `chassis_frame` | 车架 | length, width, rail_height |
| `bracket` | 支架 | length, height, thickness |
| `screw` | 螺丝 | head_diameter, body_diameter, body_length |
| `custom_code` | 自定义 | Python TurtleCAD 代码 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd vibe_coding
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置 API Key（可选）

如需使用 AI 解析自然语言，设置 OpenAI 兼容 API：

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选
export OPENAI_MODEL="gpt-4"  # 可选
```

支持任意 OpenAI 兼容接口（ChatGPT、DeepSeek、智谱、千问等）。

### 一键启动（推荐）

#### macOS / Linux
```bash
bash scripts/start.sh
```

#### Windows
```bat
scripts\start.bat
```

首次运行会自动创建 `cad_agent/config.env.local`，请填写：
```
OPENAI_API_KEY=你的API密钥
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=glm-4-plus
```

启动后访问：
`http://localhost:8000`

### 3. 生成零件

**方式一：使用高级 CLI（推荐）**

```bash
cd cad_agent
python3 advanced_cli.py "设计一个模数2、齿数20的齿轮"
python3 advanced_cli.py "6204轴承"
python3 advanced_cli.py "M10螺栓长度50mm"
python3 advanced_cli.py "汽车车架，长2.5米宽0.8米"
```

**方式二：使用装配体**

```bash
python3 advanced_cli.py --assembly ../assembly_example.json
```

**方式三：查看标准件库**

```bash
python3 advanced_cli.py --standard
```

**方式四：使用原始 CLI**

```bash
cd cad_agent
python3 cad_cli.py --nl "500×300底板，四角孔12mm，距边25mm"
```

### 4. 测试所有零件类型

```bash
python3 ../test_advanced_agent.py
```

---

## 🌐 API 半自动流程（推荐）

这个流程适合「用户不知道参数 → 让大模型设计参数 → 用户确认 → 再生成」。

### 1. 启动服务

```bash
cd cad_agent
python3 app.py
```

默认访问地址：
`http://localhost:8000`

### 2. 设计参数（/api/design）

请求：
```json
{"text": "设计一个微型电动车底盘，长2.5米宽0.8米，5根横梁"}
```

返回（示例）：
```json
{
  "success": true,
  "data": {
    "type": "chassis_frame",
    "parameters": {
      "length": 2500,
      "width": 800,
      "rail_height": 120,
      "rail_thickness": 8,
      "cross_members": 5
    }
  }
}
```

### 3. 确认参数后生成（/api/generate）

请求：
```json
{
  "part_type": "chassis_frame",
  "parameters": {
    "length": 2500,
    "width": 800,
    "rail_height": 120,
    "rail_thickness": 8,
    "cross_members": 5
  },
  "output_format": "dxf"
}
```

返回：
```json
{
  "success": true,
  "filename": "chassis_frame_output.dxf",
  "size": 12345,
  "format": "dxf"
}
```

### 4. 下载文件

`GET /api/download/{filename}`

---

## 📖 使用示例

### 示例 1: 生成齿轮

```bash
python3 advanced_cli.py "设计一个模数2.5、齿数24的直齿轮，中心孔20mm"
```

输出：
```
🤖 Advanced CAD Agent - 高级机械设计 AI

📝 需求描述: 设计一个模数2.5、齿数24的直齿轮，中心孔20mm

🚀 开始设计...

🔍 步骤 1: 分析用户需求...
📖 步骤 2: 查询标准件库...
🧠 调用 AI 进行设计推理...
✏️  生成 CAD 图纸...
✅ DXF 文件已生成
🔍 进行工程验收...
✅ 验收通过
💾 保存成功案例到记忆库...

============================================================
✅ 设计完成！
📄 输出文件: agent_output.dxf
============================================================
```

### 示例 2: 生成车架

```bash
python3 advanced_cli.py "微型电动车车架，长2米宽0.7米，5根横梁"
```

### 示例 3: 生成装配体

创建 `my_assembly.json`:

```json
{
  "name": "齿轮变速箱",
  "output": "transmission.dxf",
  "parts": [
    {
      "type": "gear",
      "parameters": {"module": 2, "teeth": 40, "bore_diameter": 20},
      "position": [0, 0]
    },
    {
      "type": "gear",
      "parameters": {"module": 2, "teeth": 20, "bore_diameter": 15},
      "position": [60, 0]
    },
    {
      "type": "plate",
      "parameters": {"length": 150, "width": 120, "hole_diameter": 8},
      "position": [-30, -60]
    }
  ]
}
```

然后运行：

```bash
python3 advanced_cli.py --assembly my_assembly.json
```

### 示例 4: 自定义复杂形状

使用 TurtleCAD 编程绘制：

```bash
python3 advanced_cli.py "画一个S型吊钩，上钩半径10mm，下钩半径10mm，中间连接20mm"
```

Agent 会自动生成类似这样的代码：

```python
t.set_heading(90)  # 面向上
t.circle(10, 180)  # 上钩(左转180度)
t.forward(20)      # 主体
t.circle(-10, 180) # 下钩(右转180度)
```

---

## 📚 标准件库

系统内置以下标准件参数：

### 轴承系列 (62xx/63xx)

- 6200: 10×30×9mm
- 6204: 20×47×14mm
- 6208: 40×80×18mm
- 6300: 10×35×11mm
- 6308: 40×90×23mm

### 螺栓系列 (Mx)

- M3: 直径3mm, 头宽5.5mm
- M6: 直径6mm, 头宽10mm
- M10: 直径10mm, 头宽17mm
- M20: 直径20mm, 头宽30mm

查看完整标准件库：

```bash
python3 advanced_cli.py --standard
```

---

## 🏗️ 项目结构

```
vibe_coding/
├── cad_agent/
│   ├── advanced_agent_core.py    # 高级 Agent 核心
│   ├── advanced_cli.py           # 高级命令行接口
│   ├── agent_core.py             # 原始 Agent 核心
│   ├── cad_cli.py                # 原始命令行接口
│   ├── gen_parts.py              # 零件生成器（10+类型）
│   ├── turtle_cad.py             # TurtleCAD 绘图引擎
│   ├── nl_to_spec_llm.py         # 自然语言解析器
│   ├── validate_dxf.py           # DXF 验收器
│   ├── memory.py                 # 记忆系统
│   └── cad_agent.md              # 规范文档
├── assembly_example.json         # 装配体示例
├── test_advanced_agent.py        # 测试脚本
└── README.md
```

---

## 🎓 工程知识库

Agent 内置工程知识，包括：

- **齿轮**: 标准模数系列 (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10)
- **轴承**: 标准系列 (618, 619, 60, 62, 63)
- **螺栓**: 公称直径与头高关系
- **法兰**: PN10, PN16, PN25 标准
- **汽车车架**: 常见尺寸范围

---

## 🔧 高级功能

### 1. 记忆系统

Agent 会自动保存成功案例，下次生成类似零件时会参考历史经验。

### 2. 多轮迭代

如果生成失败，Agent 会自动分析错误并修正参数，最多重试 3 次。

### 3. 工程验收

自动检查：
- 单位是否正确（毫米）
- 图层是否完整
- 轮廓是否闭合
- 孔位是否合理
- 是否越界

### 4. 装配体生成

支持将多个零件组装成一个装配图，每个零件可指定位置偏移。

---

## 📝 TODO

- [ ] 添加 3D 导出（STEP/IGES）
- [ ] 添加更多零件类型（链轮、皮带轮等）
- [ ] 支持参数化约束
- [ ] 添加图纸标注功能
- [ ] Web UI 界面
- [ ] 批量生成功能

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 🌟 致谢

- [ezdxf](https://github.com/mozman/ezdxf) - DXF 文件生成库
- OpenAI & 各大模型厂商 - AI 能力支持
