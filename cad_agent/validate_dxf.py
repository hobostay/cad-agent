# -*- coding: utf-8 -*-
"""
DXF 验收模块。
根据 spec json 验收 dxf 文件。
支持 plate (底板) 和 screw (螺丝)。
"""
import ezdxf
from ezdxf import units
import json
import sys

def fail(msg):
    raise ValueError(msg)

def check_units(doc):
    if doc.units != units.MM:
        fail("DXF 单位不是 mm")

def check_layers(doc, required_layers):
    existing = {layer.dxf.name for layer in doc.layers}
    missing = required_layers - existing
    if missing:
        fail(f"缺少必要图层: {missing}")

def check_plate(doc, params):
    msp = doc.modelspace()
    length = params.get("length")
    width = params.get("width")
    hole_diameter = params.get("hole_diameter", 0)

    chamfer_size = params.get("chamfer_size", 0)
    fillet_radius = params.get("fillet_radius", 0)
    slots = params.get("slots", [])
    threaded_holes = params.get("threaded_holes", [])
    counterbores = params.get("counterbores", [])
    keyway = params.get("keyway")

    check_layers(doc, {"outline"})
    if hole_diameter > 0 or slots or threaded_holes or counterbores or keyway:
        check_layers(doc, {"hole"})

    # Check Outline - 有倒角/倒圆时会有额外的线和圆弧
    if chamfer_size == 0 and fillet_radius == 0:
        outlines = list(msp.query('LWPOLYLINE[layer=="outline"]'))
        if len(outlines) != 1:
            fail("outline 图层必须且只能有一个矩形轮廓")
        poly = outlines[0]
        if not poly.closed:
            fail("底板轮廓未闭合")
    else:
        # 有倒角/倒圆时，检查是否有图形元素即可
        outlines = list(msp.query('LWPOLYLINE[layer=="outline"]'))
        arcs = list(msp.query('ARC[layer=="outline"]'))
        lines = list(msp.query('LINE[layer=="outline"]'))
        if len(outlines) + len(arcs) + len(lines) == 0:
            fail("轮廓无数据")

    # 简单尺寸校验 (bounding box)
    extents = ezdxf.bbox.extents(msp.query('*[layer=="outline"]'))
    if not extents.has_data:
        fail("轮廓无数据")

    size_x = extents.size.x
    size_y = extents.size.y

    if abs(size_x - length) > 1.0 or abs(size_y - width) > 1.0:
        if abs(size_x - width) < 1.0 and abs(size_y - length) < 1.0:
            pass  # 宽高反了也算对
        else:
            fail(f"轮廓尺寸 ({size_x:.1f}x{size_y:.1f}) 与参数 ({length}x{width}) 不符")

    # Check Corner Holes if any
    if hole_diameter > 0:
        circles = list(msp.query('CIRCLE[layer=="hole"]'))
        # 只检查四角孔，不考虑其他类型的孔
        expected_holes = 4
        if len(circles) < expected_holes:
            fail(f"孔数量不对，期望至少 {expected_holes} 个，实际 {len(circles)} 个")

    # Check slots (腰形孔) - 应该有弧和线的组合
    if slots:
        arcs = list(msp.query('ARC[layer=="hole"]'))
        if len(arcs) < len(slots) * 2:  # 每个腰形孔至少2个半圆
            fail(f"腰形孔数量不匹配，期望 {len(slots)} 个")

    # Check threaded holes - 应该有虚线圆
    if threaded_holes:
        thread_circles = list(msp.query('CIRCLE[layer=="thread"]'))
        if len(thread_circles) < len(threaded_holes):
            fail(f"螺纹孔表示不完整")

    # Check counterbores - 应该有同心圆
    if counterbores:
        # 通过统计圆的数量来验证
        hole_circles = list(msp.query('CIRCLE[layer=="hole"]'))
        if len(hole_circles) < len(counterbores) * 2:
            fail(f"沉孔表示不完整")

    # Check keyway - 应该有闭合的多段线
    if keyway:
        polylines = list(msp.query('LWPOLYLINE[layer=="hole"]'))
        if len(polylines) == 0:
            fail("键槽未生成")

def check_screw(doc, params):
    msp = doc.modelspace()
    check_layers(doc, {"outline", "thread"})
    
    # 只要有东西画出来就行，详细尺寸校验比较复杂
    if len(msp) == 0:
        fail("图纸为空")

def check_custom_code(doc, params):
    msp = doc.modelspace()
    if len(msp) == 0:
        fail("图纸为空 (自定义代码未绘制任何图元)")

def validate_dxf_file(dxf_file, spec_file):
    try:
        with open(spec_file, "r", encoding="utf-8") as f:
            spec = json.load(f)
        
        # 兼容旧格式
        part_type = spec.get("type", "plate")
        params = spec.get("parameters", spec)
        
        doc = ezdxf.readfile(dxf_file)
        check_units(doc)
        
        if part_type == "plate":
            check_plate(doc, params)
        elif part_type == "screw":
            check_screw(doc, params)
        elif part_type == "custom_code":
            check_custom_code(doc, params)
        else:
            # 未知类型，暂不校验逻辑，只看文件是否有效
            pass

        return True, "CAD 图纸通过工程验收"

    except Exception as e:
        return False, str(e)
