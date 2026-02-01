# -*- coding: utf-8 -*-
"""
从 plate_spec.json 读取参数，生成底板 DXF。
单位：mm。图层：outline / hole。
"""
import json
import ezdxf
from ezdxf import units

OUTPUT_FILE = "plate_from_json.dxf"
SPEC_FILE = "plate_spec.json"


def validate_params(spec):
    """
    校验 plate_spec 参数，不合格则抛出 ValueError。
    """
    length = spec["length"]
    width = spec["width"]
    hole_diameter = spec["hole_diameter"]
    corner_offset = spec["corner_offset"]
    radius = hole_diameter / 2.0

    if length <= 0:
        raise ValueError("length 必须大于 0")
    if width <= 0:
        raise ValueError("width 必须大于 0")
    if hole_diameter <= 0:
        raise ValueError("hole_diameter 必须大于 0")
    if corner_offset <= radius:
        raise ValueError("corner_offset 必须大于 hole_diameter / 2")
    # 四角孔必须完全在板内：孔心距边 corner_offset，孔缘距边 corner_offset - radius >= 0 已由上式保证；
    # 孔缘不超出对边：corner_offset + radius 不得超过 length / width
    if corner_offset + radius > length:
        raise ValueError("四角孔在 X 方向越界：corner_offset + hole_diameter/2 不得超过 length")
    if corner_offset + radius > width:
        raise ValueError("四角孔在 Y 方向越界：corner_offset + hole_diameter/2 不得超过 width")


def draw_plate(doc, length, width):
    """在模型空间绘制底板矩形外轮廓，图层 outline。"""
    msp = doc.modelspace()
    msp.add_lwpolyline(
        [(0, 0), (length, 0), (length, width), (0, width), (0, 0)],
        close=True,
        dxfattribs={"layer": "outline"},
    )


def draw_holes(doc, length, width, hole_diameter, corner_offset):
    """在模型空间绘制四角圆孔，图层 hole。孔位由参数推导，原点在板左下角。"""
    radius = hole_diameter / 2.0
    centers = [
        (corner_offset, corner_offset),
        (length - corner_offset, corner_offset),
        (length - corner_offset, width - corner_offset),
        (corner_offset, width - corner_offset),
    ]
    msp = doc.modelspace()
    for cx, cy in centers:
        msp.add_circle(
            center=(cx, cy),
            radius=radius,
            dxfattribs={"layer": "hole"},
        )


def main():
    with open(SPEC_FILE, "r", encoding="utf-8") as f:
        spec = json.load(f)

    validate_params(spec)

    doc = ezdxf.new("R2010", setup=True)
    doc.units = units.MM
    doc.layers.add("outline", color=1)
    doc.layers.add("hole", color=2)

    length = spec["length"]
    width = spec["width"]
    hole_diameter = spec["hole_diameter"]
    corner_offset = spec["corner_offset"]

    draw_plate(doc, length, width)
    draw_holes(doc, length, width, hole_diameter, corner_offset)

    doc.saveas(OUTPUT_FILE)


if __name__ == "__main__":
    main()
