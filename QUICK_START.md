# 🚀 CAD Agent 快速使用指南

## ✅ 已完成的改造

### 1. 新增 6 种机械零件类型

| 零件 | 命令示例 |
|-----|---------|
| **齿轮** | `python3 advanced_cli.py "模数2齿数20的齿轮"` |
| **轴承** | `python3 advanced_cli.py "6204轴承"` |
| **法兰** | `python3 advanced_cli.py "法兰DN100，8个孔"` |
| **螺栓** | `python3 advanced_cli.py "M10螺栓长度50"` |
| **弹簧** | `python3 advanced_cli.py "压缩弹簧线径2圈径8"` |
| **车架** | `python3 advanced_cli.py "车架长2.5米宽0.8米"` |
| **支架** | `python3 advanced_cli.py "L型支架100x80"` |

### 2. 标准件库

内置轴承和螺栓标准参数，自动识别：

```bash
# 直接使用标准件型号
python3 advanced_cli.py "6204轴承"  # 自动填充: 内径20, 外径47, 宽14
python3 advanced_cli.py "M10螺栓"   # 自动填充: 直径10, 头宽17
```

### 3. 装配体功能

```bash
# 查看示例
python3 advanced_cli.py --assembly ../assembly_example.json
```

### 4. 增强 TurtleCAD

新增绘图方法：
- `t.rectangle(width, height)` - 矩形
- `t.polygon(sides, radius)` - 正多边形
- `t.slot(length, width)` - 腰形孔
- `t.threaded_hole(dia, length)` - 螺纹孔

---

## 📝 常用命令

### 查看帮助
```bash
cd cad_agent
python3 advanced_cli.py
```

### 查看标准件库
```bash
python3 advanced_cli.py --standard
```

### 测试所有零件类型
```bash
cd ..
python3 test_advanced_agent.py
```

---

## 💡 使用场景示例

### 场景 1: 设计汽车零件

```bash
# 设计车架
python3 advanced_cli.py "微型电动车车架，长2.5米宽0.8米，5根横梁"

# 设计支架
python3 advanced_cli.py "发动机支架，L型，长150高100厚10"

# 设计法兰盘
python3 advanced_cli.py "连接法兰，外径150内径80，8个M10螺栓"
```

### 场景 2: 设计传动系统

```bash
# 大齿轮
python3 advanced_cli.py "大齿轮，模数3齿数60，中心孔30"

# 小齿轮
python3 advanced_cli.py "小齿轮，模数3齿数20，中心孔20"

# 轴承
python3 advanced_cli.py "6308轴承"
```

### 场景 3: 设计充电桩零件

```bash
# 安装底板
python3 advanced_cli.py "底板600x400，厚5mm，四角M8螺栓孔"

# 外壳支架
python3 advanced_cli.py "L型支架200x150，厚8mm"

# 法兰连接件
python3 advanced_cli.py "圆形法兰，外径120内孔50，4个安装孔"
```

---

## 📦 项目文件说明

| 文件 | 说明 |
|-----|------|
| `advanced_agent_core.py` | 高级 Agent 核心，支持标准件查询和装配体 |
| `advanced_cli.py` | 新的命令行接口 |
| `gen_parts.py` | 10种零件生成器 |
| `turtle_cad.py` | 增强的绘图引擎 |
| `test_advanced_agent.py` | 测试所有零件类型 |
| `assembly_example.json` | 装配体示例 |

---

## 🎯 下一步可以做什么？

1. **添加更多零件类型**
   - 在 `gen_parts.py` 中添加新的 `validate` 和 `draw` 函数
   - 在 `GENERATORS` 字典中注册

2. **扩展标准件库**
   - 在 `advanced_agent_core.py` 的 `STANDARD_PARTS_LIBRARY` 中添加

3. **改进 LLM Prompt**
   - 编辑 `nl_to_spec_llm.py` 中的 `SYSTEM_PROMPT`
   - 添加更多工程知识和示例

4. **创建自定义装配体**
   - 复制 `assembly_example.json` 作为模板
   - 修改零件类型、参数和位置

---

## 🔍 测试结果

```
✅ 底板 (plate)
✅ 齿轮 (gear)
✅ 轴承 (bearing)
✅ 法兰 (flange)
✅ 螺栓 (bolt)
✅ 弹簧 (spring)
✅ 车架 (chassis_frame)
✅ 支架 (bracket)

8/8 测试通过
```

---

**开始使用：**
```bash
cd /Users/chu/vibe_coding/cad_agent
python3 advanced_cli.py "你的需求描述"
```
