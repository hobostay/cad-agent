# -*- coding: utf-8 -*-
import ezdxf
from ezdxf import units
import json
import sys

DXF_FILE = "plate_from_json.dxf"
SPEC_FILE = "plate_spec.json"


def fail(msg):
    print(f"❌ 验收失败：{msg}")
    sys.exit(1)


def pass_ok():
    print("✅ CAD 图纸通过全部工程验收，可直接用于制造")
    sys.exit(0)


def load_spec():
    with open(SPEC_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def check_units(doc):
    if doc.units != units.MM:
        fail("DXF 单位不是 mm")


def check_layers(doc):
    required = {"outline", "hole"}
    existing = {layer.dxf.name for layer in doc.layers}
    missing = required - existing
    if missing:
        fail(f"缺少必要图层: {missing}")


def check_outline(msp, length, width):
    outlines = list(msp.query('LWPOLYLINE[layer=="outline"]'))
    if len(outlines) != 1:
        fail("outline 图层必须且只能有一个矩形轮廓")

    poly = outlines[0]
    if not poly.closed:
        fail("底板轮廓未闭合")

    points = [(round(p[0], 3), round(p[1], 3)) for p in poly.get_points()]
    expected = {(0, 0), (length, 0), (length, width), (0, width)}

    if set(points[:-1]) != expected:
        fail("底板轮廓尺寸或位置不正确")


def check_holes(msp, length, width, hole_diameter):
    circles = list(msp.query('CIRCLE[layer=="hole"]'))
    if len(circles) != 4:
        fail("孔数量不是 4 个")

    radius = hole_diameter / 2

    for c in circles:
        x, y = c.dxf.center[0], c.dxf.center[1]
        r = c.dxf.radius

        if abs(r - radius) > 0.001:
            fail("孔半径不符合参数")

        if x - r < 0 or x + r > length or y - r < 0 or y + r > width:
            fail(f"孔越界：center=({x},{y})")


def main():
    try:
        spec = load_spec()
        length = spec["length"]
        width = spec["width"]
        hole_diameter = spec["hole_diameter"]

        doc = ezdxf.readfile(DXF_FILE)
        msp = doc.modelspace()

        check_units(doc)
        check_layers(doc)
        check_outline(msp, length, width)
        check_holes(msp, length, width, hole_diameter)

        pass_ok()

    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()
