# -*- coding: utf-8 -*-
"""
CAD 底板参数 → 生成 DXF → 验收。仅使用 Tkinter，无第三方 GUI。
"""
import json
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_FILE = os.path.join(SCRIPT_DIR, "plate_spec.json")


def run_generate_and_validate(length, width, hole_diameter, corner_offset, status_callback):
    """写入 plate_spec.json，执行 gen_plate_from_json.py 与 validate_dxf.py，回调状态。"""
    try:
        spec = {
            "length": length,
            "width": width,
            "hole_diameter": hole_diameter,
            "corner_offset": corner_offset,
        }
        with open(SPEC_FILE, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)

        python = sys.executable
        gen_script = os.path.join(SCRIPT_DIR, "gen_plate_from_json.py")
        val_script = os.path.join(SCRIPT_DIR, "validate_dxf.py")

        r1 = subprocess.run(
            [python, gen_script],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r1.returncode != 0:
            status_callback(
                "生成 DXF 失败：" + (r1.stderr or r1.stdout or str(r1.returncode)).strip()
            )
            return

        r2 = subprocess.run(
            [python, val_script],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=10,
        )
        out = (r2.stdout or "").strip()
        err = (r2.stderr or "").strip()
        if r2.returncode == 0:
            status_callback("CAD 图纸通过工程验收，可直接使用")
        else:
            status_callback(out or err or "验收失败")
    except subprocess.TimeoutExpired:
        status_callback("执行超时")
    except Exception as e:
        status_callback("错误：" + str(e))


def main():
    root = tk.Tk()
    root.title("底板 CAD 生成与验收")
    root.resizable(True, False)

    frm = ttk.Frame(root, padding=10)
    frm.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    ttk.Label(frm, text="length (mm):").grid(row=0, column=0, sticky=tk.W, pady=2)
    ttk.Label(frm, text="width (mm):").grid(row=1, column=0, sticky=tk.W, pady=2)
    ttk.Label(frm, text="hole_diameter (mm):").grid(row=2, column=0, sticky=tk.W, pady=2)
    ttk.Label(frm, text="corner_offset (mm):").grid(row=3, column=0, sticky=tk.W, pady=2)

    var_length = tk.StringVar(value="500")
    var_width = tk.StringVar(value="300")
    var_hole_diameter = tk.StringVar(value="12")
    var_corner_offset = tk.StringVar(value="25")

    e_length = ttk.Entry(frm, textvariable=var_length, width=12)
    e_width = ttk.Entry(frm, textvariable=var_width, width=12)
    e_hole_diameter = ttk.Entry(frm, textvariable=var_hole_diameter, width=12)
    e_corner_offset = ttk.Entry(frm, textvariable=var_corner_offset, width=12)

    e_length.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(8, 0))
    e_width.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(8, 0))
    e_hole_diameter.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(8, 0))
    e_corner_offset.grid(row=3, column=1, sticky=tk.W, pady=2, padx=(8, 0))

    status_var = tk.StringVar(value="输入参数后点击按钮生成并验收。")

    def on_click():
        try:
            length = float(var_length.get().strip())
            width = float(var_width.get().strip())
            hole_diameter = float(var_hole_diameter.get().strip())
            corner_offset = float(var_corner_offset.get().strip())
        except ValueError:
            status_var.set("请输入有效数字。")
            return

        status_var.set("正在生成并验收…")

        def update_status(msg):
            root.after(0, lambda: status_var.set(msg))

        def run():
            try:
                run_generate_and_validate(
                    length, width, hole_diameter, corner_offset, update_status
                )
            except Exception as e:
                update_status("错误：" + str(e))

        threading.Thread(target=run, daemon=True).start()

    btn = ttk.Button(frm, text="生成 CAD 并自动验收", command=on_click)
    btn.grid(row=4, column=0, columnspan=2, pady=12)

    status_label = ttk.Label(
        frm, textvariable=status_var, wraplength=320, justify=tk.LEFT
    )
    status_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=8)

    root.mainloop()


if __name__ == "__main__":
    main()
