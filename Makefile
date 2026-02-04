# CAD 底板项目 - 常用命令
# 用法: make help / make install / make run / make run-nl / make push

PYTHON := .venv/bin/python3
CAD_AGENT := cad_agent

.PHONY: install run run-nl run-gui validate push help

help:
	@echo "install   - 创建虚拟环境并安装依赖"
	@echo "run       - 数字参数生成并验收  例: make run ARGS='500 300 12 25'"
	@echo "run-nl    - 自然语言生成并验收  例: ./scripts/run_cli.sh --nl \"500×300底板，四角孔12mm，距边25mm\""
	@echo "run-gui   - 启动 GUI"
	@echo "validate  - 仅验收已生成的 DXF"
	@echo "push      - 推送到 GitHub        例: make push REPO=仓库名"

install:
	python3 -m venv .venv
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(CAD_AGENT)/cad_cli.py $(ARGS)

run-nl:
	$(PYTHON) $(CAD_AGENT)/cad_cli.py --nl $(ARGS)

run-gui:
	$(PYTHON) $(CAD_AGENT)/cad_gui.py

validate:
	$(PYTHON) $(CAD_AGENT)/validate_dxf.py

push:
	@chmod +x scripts/push_github.sh 2>/dev/null || true
	./scripts/push_github.sh $(REPO)
