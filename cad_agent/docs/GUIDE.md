# CAD Agent - 完整使用指南

> AI 驱动的智能机械设计系统使用手册

## 目录

1. [系统概述](#系统概述)
2. [命令行工具](#命令行工具)
3. [支持的零件类型](#支持的零件类型)
4. [高级功能](#高级功能)
5. [配置选项](#配置选项)
6. [故障排除](#故障排除)

## 系统概述

CAD Agent 是一个基于大语言模型（LLM）的智能设计系统，能够：

- 🗣️ **自然语言交互**：像与工程师对话一样描述需求
- 🧠 **智能理解**：AI 自动识别零件类型、参数、标准件规格
- 🎯 **自动生成**：一键生成 DXF 工程图或 STL 3D 模型
- ✅ **工程验证**：内置工程知识，自动进行合理性校验

## 命令行工具

### 基础用法

```bash
python3 cli.py [prompt] [options]
```

### 常用参数

| 参数 | 说明 |
|------|------|
| `prompt` | 零件描述（自然语言） |
| `--output, -o` | 输出文件名 |
| `--quiet, -q` | 静默模式 |
| `--3d` | 生成 3D STL 文件 |
| `--standard` | 显示标准件库 |
| `--assembly FILE` | 生成装配体 |
| `--direct` | 直接模式（跳过 LLM） |

### API 配置参数

| 参数 | 说明 |
|------|------|
| `--api-key` | API 密钥 |
| `--base-url` | API 基础 URL |
| `--model` | 模型名称 |

## 使用示例

### 基础零件

```bash
# 底板
python3 cli.py "500x300的底板，厚度10mm，四角M8螺丝孔"

# 齿轮
python3 cli.py "模数2齿数24的直齿轮，压力角20度"

# 轴承
python3 cli.py "6208轴承"

# 螺栓
python3 cli.py "M10螺栓，长度50mm"
```

### 复杂零件

```bash
# 带多种特征的底板
python3 cli.py "600x400安装板，厚15mm，四角M10沉孔深度8mm，中间有50x20腰形孔，四周倒角5mm"

# 阶梯轴
python3 cli.py "传动轴总长200mm，三段：直径30-25-20，长度50-100-50"

# 法兰
python3 cli.py "法兰盘DN100，PN16，8个M16螺栓孔"
```

### 3D 打印

```bash
# 生成 3D 齿轮
python3 cli.py "模数2齿数20的齿轮" --3d

# 生成 3D 螺栓
python3 cli.py "M10螺栓长度50mm" --3d --output bolt.stl

# 直接模式生成（无需 API）
python3 cli.py --direct --type gear --params '{"module":2,"teeth":20}' --3d
```

### 装配体

创建装配配置文件 `assembly.json`：

```json
{
  "parts": [
    {
      "type": "gear",
      "parameters": {"module": 2, "teeth": 20},
      "position": [0, 0]
    },
    {
      "type": "bearing",
      "parameters": {"inner_diameter": 20},
      "position": [100, 0]
    }
  ],
  "output": "assembly.dxf"
}
```

生成装配体：

```bash
python3 cli.py --assembly assembly.json
```

## 支持的零件类型

### 基础零件

| 类型 | 说明 | 支持特征 |
|------|------|----------|
| `plate` | 底板 | 倒角、倒圆、腰形孔、螺纹孔、沉孔、键槽 |
| `bolt` | 螺栓 | 标准螺纹 |
| `nut` | 螺母 | 标准螺纹 |
| `washer` | 垫圈 | 标准规格 |
| `screw` | 螺丝 | 标准螺纹 |

### 传动零件

| 类型 | 说明 |
|------|------|
| `gear` | 直齿圆柱齿轮 |
| `sprocket` | 滚子链链轮 |
| `pulley` | V 带轮 |
| `shaft` | 传动轴 |
| `stepped_shaft` | 阶梯轴 |
| `coupling` | 联轴器 |

### 支撑零件

| 类型 | 说明 |
|------|------|
| `bearing` | 深沟球轴承 |
| `flange` | 圆盘法兰 |
| `bracket` | L 型支架 |

### 其他零件

| 类型 | 说明 |
|------|------|
| `spring` | 压缩弹簧 |
| `snap_ring` | 卡簧 |
| `retainer` | 挡圈 |
| `chassis_frame` | 梯形车架 |

### 自定义

- `custom_code` - 使用 TurtleCAD 绘制任意形状

## 高级功能

### 标准件查询

```bash
python3 cli.py --standard
```

显示：
- 轴承规格表
- 紧固件规格表
- 齿轮模数标准系列

### 直接模式

跳过 LLM 解析，直接用参数生成：

```bash
python3 cli.py --direct --type gear --params '{"module":2,"teeth":20}' --3d
```

支持类型：所有零件类型

参数格式：JSON 字符串

### 工程验证

系统自动进行：
- 🦷 齿轮传动验证（模数匹配、中心距、传动比）
- 🔄 轴承配合验证（轴/孔公差）
- 💪 强度校验（简化）
- 🧱 材料推荐（Q235、45号钢、40Cr等）
- 📏 公差分析

### 静默模式

```bash
python3 cli.py "设计一个齿轮" --quiet
```

减少输出信息，适用于脚本调用。

## 配置选项

### 环境变量

```bash
export OPENAI_API_KEY="<API 密钥>"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODEL="gpt-4"
```

### 配置文件

创建 `config.env.local`：

```bash
OPENAI_API_KEY=<API 密钥>
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

### 命令行参数覆盖

```bash
python3 cli.py \
  --api-key <API 密钥> \
  --base-url https://api.openai.com/v1 \
  --model gpt-4 \
  --output output.dxf \
  "设计需求"
```

## 故障排除

### API 调用失败

**症状**：`API调用失败` 或 `401 Unauthorized`

**解决方案**：
1. 检查 API Key 是否正确
2. 检查网络连接
3. 检查 API 额度是否用完
4. 尝试其他 API 提供商

### 参数解析失败

**症状**：`参数解析失败` 或 `无法识别的零件类型`

**解决方案**：
1. 尝试更具体地描述需求
2. 明确指出尺寸、材质等参数
3. 使用 `--standard` 查看支持的零件类型
4. 使用 `--direct` 模式直接指定参数

### 生成失败

**症状**：`设计失败` 或 `ValueError`

**解决方案**：
1. 查看错误信息
2. 检查参数是否合理（如模数是否为标准值）
3. 检查尺寸是否在合理范围内
4. 尝试使用 `--direct` 模式

### 依赖问题

**症状**：`ModuleNotFoundError` 或 `ImportError`

**解决方案**：

```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 单独安装缺失的包
pip install ezdxf numpy-stl trimesh
```

## 输出文件说明

### 2D DXF 文件

- 用途：工程图纸、激光切割
- 查看软件：AutoCAD、SolidWorks、LibreCAD
- 格式：DXF R2010

### 3D STL 文件

- 用途：3D 打印、CNC 加工
- 查看软件：Blender、Ultimaker Cura、FreeCAD
- 格式：ASCII STL

文件自动复制到桌面，方便快速访问。

## 更多资源

- [快速开始](QUICKSTART.md)
- [3D 打印指南](3D.md)
- [Web 界面指南](WEB.md)
- [技术规范](cad_agent.md)
