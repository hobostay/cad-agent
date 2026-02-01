# -*- coding: utf-8 -*-
"""
命令行：根据参数生成 plate_spec.json，执行生成 DXF 与验收，打印结果。
用法：python cad_cli.py <length> <width> <hole_diameter> <corner_offset>
单位：mm。
"""
import argparse
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_FILE = os.path.join(SCRIPT_DIR, "plate_spec.json")


def main():
    parser = argparse.ArgumentParser(description="底板 CAD：生成 DXF 并验收")
    parser.add_argument("length", type=float, help="底板长度 (mm)")
    parser.add_argument("width", type=float, help="底板宽度 (mm)")
    parser.add_argument("hole_diameter", type=float, help="圆孔直径 (mm)")
    parser.add_argument("corner_offset", type=float, help="孔距边 (mm)")
    args = parser.parse_args()

    length = args.length
    width = args.width
    hole_diameter = args.hole_diameter
    corner_offset = args.corner_offset

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
            msg = (r1.stderr or r1.stdout or str(r1.returncode)).strip()
            print("❌ 生成 DXF 失败：" + msg)
            sys.exit(1)

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
            print("✅ CAD 图纸通过工程验收，可直接使用")
            sys.exit(0)
        else:
            print(out or err or "验收失败")
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print("❌ 执行超时")
        sys.exit(1)
    except Exception as e:
        print("❌ 错误：" + str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
