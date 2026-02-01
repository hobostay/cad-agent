# CAD 底板参数化出图与验收

参数化机械 CAD 工作流：从 JSON 规格生成 DXF 工程图，并自动验收单位、图层与几何约束。支持命令行与 Tkinter GUI，适合作为参数化出图与工程校验的示例项目。

---

## 目录

- [技术栈](#技术栈)
- [功能概览](#功能概览)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [简历用描述](#简历用描述)
- [推送到 GitHub](#推送到-github)
- [许可证](#许可证)

---

## 技术栈

| 类别     | 技术              |
| -------- | ----------------- |
| 语言     | Python 3          |
| DXF 生成 | ezdxf             |
| 规格格式 | JSON              |
| 界面     | Tkinter（可选）、CLI |

- **单位**：毫米（mm）
- **图层**：`outline`（外轮廓）、`hole`（圆孔）

---

## 功能概览

- **参数化出图**：通过 `plate_spec.json`（length / width / hole_diameter / corner_offset）驱动生成底板矩形与四角圆孔 DXF
- **参数校验**：生成前校验尺寸与孔位（正数、孔不越界、孔距边 > 孔径/2）
- **自动验收**：对生成的 DXF 检查单位（mm）、必要图层、轮廓闭合与尺寸、孔数量与半径及越界
- **多入口**：命令行一键生成并验收；可选 GUI（Tkinter）输入参数后生成并验收
- **规范文档**：`cad_agent.md` 定义机械描述 → JSON 的解析规范与 Schema，便于扩展为「自然语言 → JSON → DXF」流程

---

## 项目结构

```
vibe_coding/
├── README.md
├── .gitignore
├── requirements.txt           # 依赖：ezdxf
├── Makefile                   # 常用命令：make run / make push
├── .venv/                     # 虚拟环境（不提交）
├── cad_agent/
│   ├── cad_agent.md           # 机械 CAD 参数解析规范与 Schema
│   ├── plate_spec.json        # 底板参数（示例）
│   ├── gen_plate_from_json.py # 从 JSON 生成 DXF（核心）
│   ├── validate_dxf.py        # DXF 工程验收
│   ├── cad_cli.py             # 命令行：生成 + 验收
│   ├── cad_gui.py             # GUI：输入参数 → 生成 + 验收
│   └── gen_test_plate.py      # 固定尺寸测试用出图
└── scripts/
    ├── push_github.sh         # 一键推送到 GitHub（可自动建仓）
    └── run_cli.sh             # 从根目录运行 CLI
```

生成结果：`cad_agent/plate_from_json.dxf`（由脚本生成，已加入 .gitignore）。

---

## 快速开始

### 1. 克隆与依赖

```bash
git clone https://github.com/<你的用户名>/<仓库名>.git
cd <仓库名>
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 命令行生成并验收（推荐）

**方式 A：Make（从项目根目录）**

```bash
make run ARGS="500 300 12 25"
```

**方式 B：脚本（从项目根目录）**

```bash
chmod +x scripts/run_cli.sh
./scripts/run_cli.sh 500 300 12 25
```

参数依次：长度(mm)、宽度(mm)、孔直径(mm)、孔距边(mm)。

**方式 C：进入 cad_agent 目录**

```bash
cd cad_agent
../.venv/bin/python3 cad_cli.py 500 300 12 25
```

成功时输出：`CAD 图纸通过工程验收，可直接使用`。

### 3. 修改 JSON 后生成

编辑 `cad_agent/plate_spec.json`，然后：

```bash
cd cad_agent
../.venv/bin/python3 gen_plate_from_json.py
../.venv/bin/python3 validate_dxf.py
```

### 4. GUI（需本机图形环境）

```bash
cd cad_agent
../.venv/bin/python3 cad_gui.py
```

在界面输入四个参数，点击「生成 CAD 并自动验收」，底部会显示验收结果。

---

## 简历用描述

- **项目名**：CAD 底板参数化出图与验收
- **一句话**：基于 Python + ezdxf 实现由 JSON 参数驱动生成 DXF 底板图，并实现单位、图层、轮廓与孔位的自动验收；提供 CLI 与 Tkinter GUI，配套机械 CAD 参数解析规范文档。
- **关键词**：Python、ezdxf、DXF、参数化 CAD、JSON 驱动、工程验收、Tkinter、CLI

---

## 推送到 GitHub

本地已初始化 Git 并完成首次提交（分支 `main`）。

### 方式一：一键脚本或 Make（推荐）

在项目根目录执行：

```bash
chmod +x scripts/push_github.sh
./scripts/push_github.sh <仓库名>              # 需已安装 GitHub CLI (gh)，自动建仓并推送
# 或
./scripts/push_github.sh https://github.com/<用户名>/<仓库名>.git   # 添加 origin 并推送
# 若已配置 origin，直接执行：
./scripts/push_github.sh                       # 仅执行 git push
```

或使用 Make（传仓库名或 URL）：`make push REPO=<仓库名或完整 URL>`。

### 方式二：手动

1. 在 [GitHub New Repository](https://github.com/new) 新建仓库，不勾选「Initialize with README」。
2. 在项目根目录执行（将 `<用户名>`、`<仓库名>` 替换为实际值）：

   ```bash
   git remote add origin https://github.com/<用户名>/<仓库名>.git
   git push -u origin main
   ```

   SSH 方式：

   ```bash
   git remote add origin git@github.com:<用户名>/<仓库名>.git
   git push -u origin main
   ```

3. 推送完成后，将 README 中「克隆与依赖」的克隆地址改为你的仓库地址即可。

---

## 许可证

MIT 或按需自定。
