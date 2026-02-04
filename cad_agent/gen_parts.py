# -*- coding: utf-8 -*-
"""
通用零件生成模块。
支持类型：

【基础零件类】
1. plate (底板)
2. screw (螺丝)
3. bolt (螺栓)
4. nut (螺母)
5. washer (垫圈)

【传动类】
6. gear (齿轮)
7. sprocket (链轮)
8. pulley (皮带轮)
9. shaft (传动轴)
10. stepped_shaft (阶梯轴)
11. key (键)
12. pin (销)
13. coupling (联轴器)

【支撑类】
14. bearing (轴承)
15. bearing_housing (轴承座)
16. flange (法兰)
17. bracket (支架)
18. base (底座)

【连接类】
19. spring (弹簧)
20. snap_ring (卡簧)
21. retainer (挡圈)

【结构件】
22. chassis_frame (车架)
23. beam (梁)
24. column (立柱)
25. panel (面板)

【冲压件】
26. blanking (落料件)
27. bending (折弯件)
28. deep_drawing (拉伸件)

【汽车零件】
29. wheel_hub (轮毂)
30. brake_disc (刹车盘)
31. control_arm (控制臂)
32. steering_knuckle (转向节)

【充电桩零件】
33. cabinet_body (柜体)
34. door_panel (门板)
35. heat_sink (散热器)
36. mounting_plate (安装板)

【模具零件】
37. die_base (模架)
38. core (型芯)
39. cavity (型腔)
40. guide_pin (导柱)

【自定义】
41. custom_code (自定义代码)
"""
import json
import math
import os
import sys

import ezdxf
from ezdxf import units

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from turtle_cad import TurtleCAD

def _validate_plate(params):
    length = params.get("length", 0)
    width = params.get("width", 0)
    hole_diameter = params.get("hole_diameter", 0)
    corner_offset = params.get("corner_offset", 0)

    # 倒角参数
    chamfer_size = params.get("chamfer_size", 0)
    fillet_radius = params.get("fillet_radius", 0)

    if length <= 0 or width <= 0:
        raise ValueError("length 和 width 必须大于 0")

    # 如果有孔，校验孔参数
    if hole_diameter > 0:
        radius = hole_diameter / 2.0
        if corner_offset > 0 and corner_offset + radius > length:
            raise ValueError("孔位置超出板材范围 (X方向)")
        if corner_offset > 0 and corner_offset + radius > width:
            raise ValueError("孔位置超出板材范围 (Y方向)")

    # 校验腰形孔参数
    slots = params.get("slots", [])
    for slot in slots:
        slot_length = slot.get("length", 0)
        slot_width = slot.get("width", 0)
        if slot_length <= 0 or slot_width <= 0:
            raise ValueError("腰形孔尺寸必须大于 0")
        if slot_width >= slot_length:
            raise ValueError("腰形孔宽度应小于长度")

        # 检查位置
        if "x" in slot and "y" in slot:
            x, y = slot["x"], slot["y"]
            if x < 0 or x > length or y < 0 or y > width:
                raise ValueError("腰形孔位置超出板材范围")

    # 校验螺纹孔参数
    threaded_holes = params.get("threaded_holes", [])
    for th in threaded_holes:
        th_dia = th.get("diameter", 0)
        if th_dia <= 0:
            raise ValueError("螺纹孔直径必须大于 0")

    # 校验沉孔参数
    counterbores = params.get("counterbores", [])
    for cb in counterbores:
        cb_dia = cb.get("diameter", 0)
        cb_depth = cb.get("depth", 0)
        if cb_dia <= 0:
            raise ValueError("沉孔直径必须大于 0")
        if cb_depth <= 0:
            raise ValueError("沉孔深度必须大于 0")

    # 校验键槽参数
    keyway = params.get("keyway")
    if keyway:
        kw_width = keyway.get("width", 0)
        kw_length = keyway.get("length", 0)
        if kw_width <= 0 or kw_length <= 0:
            raise ValueError("键槽尺寸必须大于 0")

    # 倒角和倒圆不能同时设置
    if chamfer_size > 0 and fillet_radius > 0:
        raise ValueError("倒角和倒圆不能同时设置")

def _draw_plate(doc, params):
    length = params.get("length", 100)
    width = params.get("width", 100)
    hole_diameter = params.get("hole_diameter", 0)
    corner_offset = params.get("corner_offset", 10)

    # 新参数
    chamfer_size = params.get("chamfer_size", 0)
    fillet_radius = params.get("fillet_radius", 0)
    slots = params.get("slots", [])
    threaded_holes = params.get("threaded_holes", [])
    counterbores = params.get("counterbores", [])
    keyway = params.get("keyway")

    msp = doc.modelspace()

    # ============== 1. 绘制外轮廓 ==============
    if chamfer_size > 0:
        # 带倒角的轮廓
        c = chamfer_size
        points = [
            (c, 0),  # 右下起点
            (length, 0),
            (length, width - c),
            (length - c, width),
            (0, width),
            (0, c),
            (c, 0),  # 闭合
        ]
        # 绘制倒角线
        msp.add_line((c, 0), (0, c), dxfattribs={"layer": "outline"})
        msp.add_line((length, width - c), (length - c, width), dxfattribs={"layer": "outline"})
        msp.add_line((length - c, 0), (length, c), dxfattribs={"layer": "outline"})
        msp.add_line((0, width - c), (c, width), dxfattribs={"layer": "outline"})
        msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "outline"})
    elif fillet_radius > 0:
        # 带倒圆的轮廓
        r = fillet_radius
        # 使用圆弧连接
        # 左下角
        msp.add_arc((r, r), r, 90, 180, dxfattribs={"layer": "outline"})
        msp.add_line((0, r), (0, width - r), dxfattribs={"layer": "outline"})
        # 左上角
        msp.add_arc((r, width - r), r, 180, 270, dxfattribs={"layer": "outline"})
        msp.add_line((r, width), (length - r, width), dxfattribs={"layer": "outline"})
        # 右上角
        msp.add_arc((length - r, width - r), r, 270, 360, dxfattribs={"layer": "outline"})
        msp.add_line((length, width - r), (length, r), dxfattribs={"layer": "outline"})
        # 右下角
        msp.add_arc((length - r, r), r, 0, 90, dxfattribs={"layer": "outline"})
        msp.add_line((length - r, 0), (r, 0), dxfattribs={"layer": "outline"})
    else:
        # 普通矩形轮廓
        msp.add_lwpolyline(
            [(0, 0), (length, 0), (length, width), (0, width), (0, 0)],
            close=True,
            dxfattribs={"layer": "outline"},
        )

    # ============== 2. 绘制四角孔 ==============
    if hole_diameter > 0:
        radius = hole_diameter / 2.0
        centers = [
            (corner_offset, corner_offset),
            (length - corner_offset, corner_offset),
            (length - corner_offset, width - corner_offset),
            (corner_offset, width - corner_offset),
        ]
        for cx, cy in centers:
            msp.add_circle(
                center=(cx, cy),
                radius=radius,
                dxfattribs={"layer": "hole"},
            )

    # ============== 3. 绘制腰形孔 ==============
    for slot in slots:
        slot_length = slot.get("length", 20)
        slot_width = slot.get("width", 10)
        slot_x = slot.get("x", length / 2)
        slot_y = slot.get("y", width / 2)
        slot_angle = slot.get("angle", 0)  # 旋转角度

        half_length = slot_length / 2
        half_width = slot_width / 2

        if slot_angle == 0:
            # 水平腰形孔
            left_center = (slot_x - half_length, slot_y)
            right_center = (slot_x + half_length, slot_y)

            # 左半圆
            msp.add_arc(left_center, half_width, 90, 270, dxfattribs={"layer": "hole"})
            # 右半圆
            msp.add_arc(right_center, half_width, 270, 90, dxfattribs={"layer": "hole"})
            # 连接线
            msp.add_line((slot_x - half_length, slot_y + half_width),
                        (slot_x + half_length, slot_y + half_width),
                        dxfattribs={"layer": "hole"})
            msp.add_line((slot_x - half_length, slot_y - half_width),
                        (slot_x + half_length, slot_y - half_width),
                        dxfattribs={"layer": "hole"})
        else:
            # 旋转的腰形孔 - 使用 TurtleCAD
            t = TurtleCAD(msp)
            t.jump_to(slot_x, slot_y)
            t.set_heading(slot_angle)
            # 使用 slot 方法
            t.slot(slot_length, slot_width)

    # ============== 4. 绘制螺纹孔 ==============
    for th in threaded_holes:
        th_dia = th.get("diameter", 6)
        th_x = th.get("x", length / 2)
        th_y = th.get("y", width / 2)
        th_pitch = th.get("pitch", 1.0)  # 螺距

        # 主圆
        msp.add_circle((th_x, th_y), th_dia / 2, dxfattribs={"layer": "hole"})

        # 螺纹示意（内螺纹用虚线圆表示）
        thread_radius = th_dia / 2 * 0.85  # 小径约为大径的85%
        msp.add_circle((th_x, th_y), thread_radius,
                      dxfattribs={"layer": "thread", "linetype": "DASHED"})

        # 中心线
        msp.add_line((th_x - th_dia, th_y), (th_x + th_dia, th_y),
                    dxfattribs={"layer": "center", "linetype": "CENTER"})
        msp.add_line((th_x, th_y - th_dia), (th_x, th_y + th_dia),
                    dxfattribs={"layer": "center", "linetype": "CENTER"})

    # ============== 5. 绘制沉孔 ==============
    for cb in counterbores:
        cb_dia = cb.get("diameter", 12)
        cb_depth = cb.get("depth", 5)
        cb_x = cb.get("x", length / 2)
        cb_y = cb.get("y", width / 2)
        cb_through_dia = cb.get("through_diameter", 6)  # 通孔直径

        # 绘制沉孔的截面视图（两个同心圆表示）
        # 外圆（沉孔）
        msp.add_circle((cb_x, cb_y), cb_dia / 2, dxfattribs={"layer": "hole"})
        # 内圆（通孔）
        msp.add_circle((cb_x, cb_y), cb_through_dia / 2, dxfattribs={"layer": "hole"})

        # 添加沉孔深度标注（用文字）
        if cb_depth > 0:
            text = msp.add_text(f"Depth:{cb_depth}", dxfattribs={"height": min(cb_dia, 3)})
            text.dxf.insert = (cb_x + cb_dia/2 + 2, cb_y)

    # ============== 6. 绘制键槽 ==============
    if keyway:
        kw_width = keyway.get("width", 6)
        kw_length = keyway.get("length", 20)
        kw_x = keyway.get("x", length / 2)
        kw_y = keyway.get("y", 0)  # 默认在底部边缘
        kw_orientation = keyway.get("orientation", "horizontal")  # horizontal 或 vertical

        half_length = kw_length / 2
        half_width = kw_width / 2

        if kw_orientation == "horizontal":
            # 水平键槽（在底部）
            points = [
                (kw_x - half_length, kw_y),
                (kw_x + half_length, kw_y),
                (kw_x + half_length, kw_y + kw_width),
                (kw_x - half_length, kw_y + kw_width),
                (kw_x - half_length, kw_y),
            ]
        else:
            # 垂直键槽（在侧边）
            points = [
                (kw_x, kw_y - half_length),
                (kw_x + kw_width, kw_y - half_length),
                (kw_x + kw_width, kw_y + half_length),
                (kw_x, kw_y + half_length),
                (kw_x, kw_y - half_length),
            ]

        msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "hole"})

def _validate_screw(params):
    head_diameter = params.get("head_diameter", 0)
    head_height = params.get("head_height", 0)
    body_diameter = params.get("body_diameter", 0)
    body_length = params.get("body_length", 0)
    
    if head_diameter <= 0 or head_height <= 0 or body_diameter <= 0 or body_length <= 0:
        raise ValueError("螺丝所有尺寸参数必须大于 0")
    if body_diameter >= head_diameter:
        raise ValueError("螺杆直径必须小于螺头直径")

def _draw_screw(doc, params):
    # 绘制螺丝侧视图
    # 原点 (0,0) 为螺杆底部中心
    
    hd = params.get("head_diameter", 10)
    hh = params.get("head_height", 5)
    bd = params.get("body_diameter", 5)
    bl = params.get("body_length", 20)
    
    msp = doc.modelspace()
    
    # 1. 螺杆 (Body) - 矩形
    # 左下 (-bd/2, 0), 右上 (bd/2, bl)
    msp.add_lwpolyline(
        [(-bd/2, 0), (bd/2, 0), (bd/2, bl), (-bd/2, bl), (-bd/2, 0)],
        close=True,
        dxfattribs={"layer": "outline"}
    )
    
    # 2. 螺头 (Head) - 矩形
    # 左下 (-hd/2, bl), 右上 (hd/2, bl+hh)
    msp.add_lwpolyline(
        [(-hd/2, bl), (hd/2, bl), (hd/2, bl+hh), (-hd/2, bl+hh), (-hd/2, bl)],
        close=True,
        dxfattribs={"layer": "outline"}
    )
    
    # 3. 螺纹示意线 (Thread lines) - 简化，画两条细线
    # 距离边缘 0.1 * bd
    margin = 0.1 * bd
    msp.add_line(
        (-bd/2 + margin, 0), (-bd/2 + margin, bl),
        dxfattribs={"layer": "thread", "color": 3} # 绿色
    )
    msp.add_line(
        (bd/2 - margin, 0), (bd/2 - margin, bl),
        dxfattribs={"layer": "thread", "color": 3}
    )
    
    # 4. 中心线
    msp.add_line(
        (0, -2), (0, bl + hh + 2),
        dxfattribs={"layer": "center", "color": 1, "linetype": "CENTER"} # 红色中心线
    )

def _validate_custom_code(params):
    code = params.get("code")
    if not code or not isinstance(code, str):
        raise ValueError("自定义代码类型必须包含非空 code 字符串")

def _draw_custom_code(doc, params):
    code = params.get("code")
    msp = doc.modelspace()

    # Create a TurtleCAD instance starting at (0,0)
    t = TurtleCAD(msp)

    # 准备执行环境
    # 限制环境，只提供必要的 ezdxf 绘图对象
    # 注意：exec 存在安全风险，但在此本地 Agent 场景下，视为用户授权执行 LLM 生成的代码

    local_env = {
        "msp": msp,
        "doc": doc,
        "math": math,
        "t": t,  # Inject turtle
        "TurtleCAD": TurtleCAD, # Allow creating new instances
        # 可以添加一些基础数学库，方便计算
        "abs": abs, "min": min, "max": max, "len": len, "range": range,
    }

    try:
        # 尝试执行代码
        exec(code, {}, local_env)
        print("Executed custom code with TurtleCAD support.")
    except Exception as e:
        print(f"Error executing custom code: {e}")
        # Add a text entity to show error in DXF
        msp.add_text(f"Error: {str(e)}", height=5).set_pos((0, 0))


# ============== 新增零件类型 ==============

def _validate_gear(params):
    """齿轮参数校验"""
    module = params.get("module", 0)
    teeth = params.get("teeth", 0)
    pressure_angle = params.get("pressure_angle", 20)

    if module <= 0:
        raise ValueError("齿轮模数必须大于 0")
    if teeth < 5:
        raise ValueError("齿轮齿数不能少于 5")
    if not (10 <= pressure_angle <= 30):
        raise ValueError("压力角应在 10-30 度之间")

def _draw_gear(doc, params):
    """绘制齿轮（简化渐开线齿轮）"""
    module = params.get("module", 2)
    teeth = params.get("teeth", 20)
    pressure_angle = params.get("pressure_angle", 20)
    bore_dia = params.get("bore_diameter", 10)  # 中心孔径
    hub_dia = params.get("hub_diameter", 20)    # 轮毂直径
    hub_width = params.get("hub_width", 5)      # 轮毂宽度

    msp = doc.modelspace()

    # 计算齿轮参数
    pitch_diameter = module * teeth
    addendum = module
    dedendum = 1.25 * module
    outer_radius = (pitch_diameter + 2 * addendum) / 2
    root_radius = (pitch_diameter - 2 * dedendum) / 2
    pitch_radius = pitch_diameter / 2

    # 绘制齿形（简化为梯形）
    tooth_angle = 360 / teeth
    tooth_width_angle = tooth_angle / 2  # 齿厚约占一半

    points = []
    for i in range(teeth):
        base_angle = i * tooth_angle

        # 齿根点
        angle1 = math.radians(base_angle)
        points.append((
            root_radius * math.cos(angle1),
            root_radius * math.sin(angle1)
        ))

        # 齿顶左点
        angle2 = math.radians(base_angle + tooth_width_angle * 0.3)
        points.append((
            outer_radius * math.cos(angle2),
            outer_radius * math.sin(angle2)
        ))

        # 齿顶右点
        angle3 = math.radians(base_angle + tooth_width_angle * 0.7)
        points.append((
            outer_radius * math.cos(angle3),
            outer_radius * math.sin(angle3)
        ))

        # 齿根点
        angle4 = math.radians(base_angle + tooth_width_angle)
        points.append((
            root_radius * math.cos(angle4),
            root_radius * math.sin(angle4)
        ))

    # 闭合齿轮外轮廓
    points.append(points[0])

    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "outline"})

    # 绘制中心孔
    bore_radius = bore_dia / 2
    msp.add_circle((0, 0), bore_radius, dxfattribs={"layer": "hole"})

    # 绘制轮毂
    if hub_dia > bore_dia:
        hub_radius = hub_dia / 2
        msp.add_circle((0, 0), hub_radius, dxfattribs={"layer": "outline"})

    # 绘制节圆（虚线）
    msp.add_circle((0, 0), pitch_radius, dxfattribs={"layer": "center", "linetype": "DASHED"})

def _validate_bearing(params):
    """轴承参数校验"""
    inner_dia = params.get("inner_diameter", 0)
    outer_dia = params.get("outer_diameter", 0)
    width = params.get("width", 0)

    if inner_dia <= 0 or outer_dia <= inner_dia or width <= 0:
        raise ValueError("轴承参数无效：内径、外径、宽度必须为正数且外径>内径")

def _draw_bearing(doc, params):
    """绘制轴承（深沟球轴承侧视图）"""
    inner_dia = params.get("inner_diameter", 20)
    outer_dia = params.get("outer_diameter", 47)
    width = params.get("width", 14)
    ball_count = params.get("ball_count", 8)

    msp = doc.modelspace()

    inner_r = inner_dia / 2
    outer_r = outer_dia / 2
    ball_r = (outer_r - inner_r) * 0.3  # 球径约为空间的一定比例

    # 内圈
    msp.add_lwpolyline(
        [(0, 0), (inner_r, 0), (inner_r, width), (0, width), (0, 0)],
        close=True,
        dxfattribs={"layer": "outline"}
    )

    # 外圈
    msp.add_lwpolyline(
        [(outer_r, 0), (outer_r, width), (inner_r + 2*ball_r, width), (inner_r + 2*ball_r, 0), (outer_r, 0)],
        close=True,
        dxfattribs={"layer": "outline"}
    )

    # 滚珠（简化为圆）
    ball_center_r = inner_r + ball_r + (outer_r - inner_r - 2*ball_r) / 2
    for i in range(ball_count):
        angle = 2 * math.pi * i / ball_count
        cx = ball_center_r * math.cos(angle)
        cy = width / 2
        msp.add_circle((cx, cy), ball_r, dxfattribs={"layer": "outline"})

    # 中心线
    msp.add_line(
        (0, -2), (0, width + 2),
        dxfattribs={"layer": "center", "linetype": "CENTER"}
    )

def _validate_flange(params):
    """法兰参数校验"""
    outer_dia = params.get("outer_diameter", 0)
    inner_dia = params.get("inner_diameter", 0)
    bolt_circle_dia = params.get("bolt_circle_diameter", 0)
    bolt_count = params.get("bolt_count", 0)
    bolt_size = params.get("bolt_size", 0)

    if outer_dia <= inner_dia:
        raise ValueError("法兰外径必须大于内径")
    if bolt_count < 3:
        raise ValueError("螺栓孔数不能少于 3")
    if bolt_circle_dia >= outer_dia or bolt_circle_dia <= inner_dia:
        raise ValueError("螺栓孔圆直径应在内径和外径之间")

def _draw_flange(doc, params):
    """绘制法兰"""
    outer_dia = params.get("outer_diameter", 150)
    inner_dia = params.get("inner_diameter", 80)
    bolt_circle_dia = params.get("bolt_circle_diameter", 120)
    bolt_count = params.get("bolt_count", 8)
    bolt_size = params.get("bolt_size", 16)
    thickness = params.get("thickness", 20)

    msp = doc.modelspace()

    outer_r = outer_dia / 2
    inner_r = inner_dia / 2
    bolt_circle_r = bolt_circle_dia / 2
    bolt_r = bolt_size / 2

    # 外圆
    msp.add_circle((0, 0), outer_r, dxfattribs={"layer": "outline"})

    # 内孔
    msp.add_circle((0, 0), inner_r, dxfattribs={"layer": "hole"})

    # 螺栓孔
    for i in range(bolt_count):
        angle = 2 * math.pi * i / bolt_count
        bx = bolt_circle_r * math.cos(angle)
        by = bolt_circle_r * math.sin(angle)
        msp.add_circle((bx, by), bolt_r, dxfattribs={"layer": "hole"})

    # 节圆（虚线）
    msp.add_circle((0, 0), bolt_circle_r, dxfattribs={"layer": "center", "linetype": "DASHED"})

    # 中心标记
    msp.add_line(
        (-outer_r * 1.1, 0), (outer_r * 1.1, 0),
        dxfattribs={"layer": "center", "linetype": "CENTER"}
    )
    msp.add_line(
        (0, -outer_r * 1.1), (0, outer_r * 1.1),
        dxfattribs={"layer": "center", "linetype": "CENTER"}
    )

def _validate_bolt(params):
    """螺栓参数校验"""
    diameter = params.get("diameter", 0)
    length = params.get("length", 0)

    if diameter <= 0 or length <= 0:
        raise ValueError("螺栓直径和长度必须大于 0")

def _draw_bolt(doc, params):
    """绘制六角头螺栓"""
    diameter = params.get("diameter", 10)
    length = params.get("length", 50)
    head_height = params.get("head_height", diameter * 0.7)

    msp = doc.modelspace()

    r = diameter / 2

    # 螺杆
    msp.add_lwpolyline(
        [(0, 0), (r, 0), (r, length), (-r, length), (-r, 0), (0, 0)],
        close=True,
        dxfattribs={"layer": "outline"}
    )

    # 六角头
    hex_width = diameter * 1.8
    msp.add_lwpolyline(
        [(-hex_width/2, length), (hex_width/2, length),
         (hex_width/2, length + head_height), (-hex_width/2, length + head_height),
         (-hex_width/2, length)],
        close=True,
        dxfattribs={"layer": "outline"}
    )

    # 螺纹示意
    thread_length = length * 0.7
    for y in range(int(thread_length)):
        msp.add_line(
            (-r * 0.9, y), (-r * 0.9, y + 1),
            dxfattribs={"layer": "thread", "color": 3}
        )
        msp.add_line(
            (r * 0.9, y), (r * 0.9, y + 1),
            dxfattribs={"layer": "thread", "color": 3}
        )

    # 中心线
    msp.add_line(
        (0, -2), (0, length + head_height + 2),
        dxfattribs={"layer": "center", "linetype": "CENTER"}
    )

def _validate_spring(params):
    """弹簧参数校验"""
    wire_dia = params.get("wire_diameter", 0)
    coil_dia = params.get("coil_diameter", 0)
    free_length = params.get("free_length", 0)

    if wire_dia <= 0 or coil_dia <= wire_dia or free_length <= 0:
        raise ValueError("弹簧参数无效")

def _draw_spring(doc, params):
    """绘制压缩弹簧侧视图"""
    wire_dia = params.get("wire_diameter", 2)
    coil_dia = params.get("coil_diameter", 20)
    free_length = params.get("free_length", 80)
    coils = params.get("coils", 8)

    msp = doc.modelspace()

    coil_r = coil_dia / 2
    wire_r = wire_dia / 2

    # 绘制弹簧波形
    points = []
    active_coils = coils - 2  # 减去两端支撑圈
    pitch = (free_length - 2 * wire_dia) / coils

    # 起始端
    points.append((0, 0))
    points.append((coil_r, wire_dia))

    # 主体螺旋
    y_start = wire_dia
    y_end = free_length - wire_dia
    for i in range(active_coils * 2):
        y = y_start + (i / 2) * pitch
        x = coil_r if i % 2 == 0 else -coil_r
        points.append((x, y))

    # 结束端
    points.append((0, free_length - wire_dia))
    points.append((0, free_length))

    msp.add_lwpolyline(points, dxfattribs={"layer": "outline"})

    # 中心线
    msp.add_line(
        (0, -2), (0, free_length + 2),
        dxfattribs={"layer": "center", "linetype": "CENTER"}
    )

def _validate_chassis_frame(params):
    """车架参数校验"""
    length = params.get("length", 0)
    width = params.get("width", 0)
    rail_height = params.get("rail_height", 0)

    if length <= 0 or width <= 0 or rail_height <= 0:
        raise ValueError("车架尺寸参数必须大于 0")

def _draw_chassis_frame(doc, params):
    """绘制车架（梯形车架）"""
    length = params.get("length", 2500)
    width = params.get("width", 800)
    rail_height = params.get("rail_height", 100)
    rail_thickness = params.get("rail_thickness", 5)
    cross_members = params.get("cross_members", 5)

    msp = doc.modelspace()

    # 左纵梁
    msp.add_lwpolyline(
        [(0, 0), (rail_thickness, 0), (rail_thickness, length), (0, length), (0, 0)],
        close=True,
        dxfattribs={"layer": "outline"}
    )

    # 右纵梁
    msp.add_lwpolyline(
        [(width - rail_thickness, 0), (width, 0), (width, length),
         (width - rail_thickness, length), (width - rail_thickness, 0)],
        close=True,
        dxfattribs={"layer": "outline"}
    )

    # 横梁
    for i in range(cross_members):
        y = (length / (cross_members + 1)) * (i + 1)
        msp.add_lwpolyline(
            [(rail_thickness, y), (width - rail_thickness, y),
             (width - rail_thickness, y + rail_thickness),
             (rail_thickness, y + rail_thickness), (rail_thickness, y)],
            close=True,
            dxfattribs={"layer": "outline"}
        )

def _validate_bracket(params):
    """支架参数校验"""
    length = params.get("length", 0)
    height = params.get("height", 0)
    thickness = params.get("thickness", 0)

    if length <= 0 or height <= 0 or thickness <= 0:
        raise ValueError("支架尺寸参数必须大于 0")

def _draw_bracket(doc, params):
    """绘制L型支架"""
    length = params.get("length", 100)
    height = params.get("height", 80)
    thickness = params.get("thickness", 10)
    hole_dia = params.get("hole_diameter", 10)
    hole_offset = params.get("hole_offset", 20)

    msp = doc.modelspace()

    # L型支架轮廓
    points = [
        (0, 0),
        (length, 0),
        (length, thickness),
        (thickness, thickness),
        (thickness, height),
        (0, height),
        (0, 0)
    ]
    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "outline"})

    # 水平安装孔
    if hole_dia > 0:
        hole_r = hole_dia / 2
        # 底部孔
        msp.add_circle((hole_offset, thickness/2), hole_r, dxfattribs={"layer": "hole"})
        msp.add_circle((length - hole_offset, thickness/2), hole_r, dxfattribs={"layer": "hole"})
        # 竖直孔
        msp.add_circle((thickness/2, height - hole_offset), hole_r, dxfattribs={"layer": "hole"})

# ============== 新增零件类型 ==============

def _validate_nut(params):
    """螺母参数校验"""
    diameter = params.get("diameter", 0)
    thickness = params.get("thickness", 0)

    if diameter <= 0:
        raise ValueError("螺母公称直径必须大于 0")
    if thickness <= 0:
        raise ValueError("螺母厚度必须大于 0")

def _draw_nut(doc, params):
    """绘制六角螺母（主视图）"""
    diameter = params.get("diameter", 10)  # 公称直径
    thickness = params.get("thickness", diameter * 0.9)  # 厚度

    msp = doc.modelspace()

    # 六角螺母的外轮廓（正六边形）
    # 对边距离约为 1.7-1.8 × d
    across_flats = diameter * 1.75
    radius = across_flats / 2

    points = []
    for i in range(6):
        angle = math.radians(30 + i * 60)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle) + thickness / 2
        points.append((x, y))

    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "outline"})

    # 内孔（螺纹孔）
    hole_radius = diameter / 2
    msp.add_circle((0, thickness / 2), hole_radius, dxfattribs={"layer": "hole"})

    # 螺纹示意
    thread_radius = hole_radius * 0.85
    msp.add_circle((0, thickness / 2), thread_radius,
                  dxfattribs={"layer": "thread", "linetype": "DASHED"})

    # 中心线
    msp.add_line((-radius * 1.2, thickness / 2), (radius * 1.2, thickness / 2),
                dxfattribs={"layer": "center", "linetype": "CENTER"})

def _validate_washer(params):
    """垫圈参数校验"""
    inner_dia = params.get("inner_diameter", 0)
    outer_dia = params.get("outer_diameter", 0)
    thickness = params.get("thickness", 0)

    if inner_dia <= 0 or outer_dia <= inner_dia:
        raise ValueError("垫圈尺寸参数无效：外径必须大于内径")
    if thickness <= 0:
        raise ValueError("垫圈厚度必须大于 0")

def _draw_washer(doc, params):
    """绘制平垫圈（截面图）"""
    inner_dia = params.get("inner_diameter", 11)  # M10 的内径约为 11mm
    outer_dia = params.get("outer_diameter", 20)
    thickness = params.get("thickness", 2)

    msp = doc.modelspace()

    inner_r = inner_dia / 2
    outer_r = outer_dia / 2

    # 截面图 - 矩形环
    # 内圆
    msp.add_lwpolyline(
        [(inner_r, 0), (inner_r, thickness), (-inner_r, thickness), (-inner_r, 0), (inner_r, 0)],
        close=True,
        dxfattribs={"layer": "outline"}
    )
    # 外圆
    msp.add_lwpolyline(
        [(outer_r, 0), (outer_r, thickness), (-outer_r, thickness), (-outer_r, 0), (outer_r, 0)],
        close=True,
        dxfattribs={"layer": "outline"}
    )

    # 中心线
    msp.add_line((0, -2), (0, thickness + 2),
                dxfattribs={"layer": "center", "linetype": "CENTER"})

def _validate_shaft(params):
    """传动轴参数校验"""
    diameter = params.get("diameter", 0)
    length = params.get("length", 0)

    if diameter <= 0 or length <= 0:
        raise ValueError("轴的直径和长度必须大于 0")

def _draw_shaft(doc, params):
    """绘制光轴（简化侧视图）"""
    diameter = params.get("diameter", 20)
    length = params.get("length", 100)

    msp = doc.modelspace()

    radius = diameter / 2

    # 轴主体 - 矩形
    msp.add_lwpolyline(
        [(-radius, 0), (radius, 0), (radius, length), (-radius, length), (-radius, 0)],
        close=True,
        dxfattribs={"layer": "outline"}
    )

    # 中心线
    msp.add_line((0, -5), (0, length + 5),
                dxfattribs={"layer": "center", "linetype": "CENTER"})

def _validate_stepped_shaft(params):
    """阶梯轴参数校验"""
    sections = params.get("sections", [])
    if len(sections) < 2:
        raise ValueError("阶梯轴至少需要 2 段")

    for i, sec in enumerate(sections):
        dia = sec.get("diameter", 0)
        length = sec.get("length", 0)
        if dia <= 0 or length <= 0:
            raise ValueError(f"第 {i+1} 段尺寸参数无效")

    # 检查直径是否递减
    for i in range(len(sections) - 1):
        if sections[i]["diameter"] < sections[i+1]["diameter"]:
            raise ValueError("阶梯轴直径应从一端向另一端递减")

def _draw_stepped_shaft(doc, params):
    """绘制阶梯轴（简化侧视图）"""
    sections = params.get("sections", [
        {"diameter": 30, "length": 40},
        {"diameter": 25, "length": 60},
        {"diameter": 20, "length": 30}
    ])

    msp = doc.modelspace()

    current_y = 0
    total_length = sum(sec["length"] for sec in sections)

    for sec in sections:
        dia = sec["diameter"]
        length = sec["length"]
        radius = dia / 2

        # 当前段的矩形
        msp.add_lwpolyline(
            [(-radius, current_y), (radius, current_y),
             (radius, current_y + length), (-radius, current_y + length),
             (-radius, current_y)],
            close=True,
            dxfattribs={"layer": "outline"}
        )

        current_y += length

    # 中心线
    msp.add_line((0, -5), (0, total_length + 5),
                dxfattribs={"layer": "center", "linetype": "CENTER"})

def _validate_coupling(params):
    """联轴器参数校验"""
    inner_dia = params.get("inner_diameter", 0)
    outer_dia = params.get("outer_diameter", 0)
    length = params.get("length", 0)

    if inner_dia <= 0 or outer_dia <= inner_dia:
        raise ValueError("联轴器尺寸参数无效")
    if length <= 0:
        raise ValueError("联轴器长度必须大于 0")

def _draw_coupling(doc, params):
    """绘制刚性联轴器（简化侧视图）"""
    inner_dia = params.get("inner_diameter", 20)
    outer_dia = params.get("outer_diameter", 50)
    length = params.get("length", 40)

    msp = doc.modelspace()

    inner_r = inner_dia / 2
    outer_r = outer_dia / 2

    # 外轮廓
    msp.add_lwpolyline(
        [(outer_r, 0), (outer_r, length), (-outer_r, length), (-outer_r, 0), (outer_r, 0)],
        close=True,
        dxfattribs={"layer": "outline"}
    )

    # 内孔
    msp.add_lwpolyline(
        [(inner_r, 0), (inner_r, length), (-inner_r, length), (-inner_r, 0), (inner_r, 0)],
        close=True,
        dxfattribs={"layer": "hole"}
    )

    # 中心线
    msp.add_line((0, -5), (0, length + 5),
                dxfattribs={"layer": "center", "linetype": "CENTER"})

def _validate_pulley(params):
    """皮带轮参数校验"""
    outer_dia = params.get("outer_diameter", 0)
    bore_dia = params.get("bore_diameter", 0)
    width = params.get("width", 0)

    if outer_dia <= bore_dia:
        raise ValueError("皮带轮外径必须大于内径")
    if width <= 0:
        raise ValueError("皮带轮宽度必须大于 0")

def _draw_pulley(doc, params):
    """绘制V带轮（侧视图）"""
    outer_dia = params.get("outer_diameter", 100)
    bore_dia = params.get("bore_diameter", 20)
    hub_dia = params.get("hub_diameter", 35)
    width = params.get("width", 30)
    grooves = params.get("grooves", 1)  # 槽数

    msp = doc.modelspace()

    outer_r = outer_dia / 2
    bore_r = bore_dia / 2
    hub_r = hub_dia / 2

    # 轮缘（带V型槽）
    groove_depth = 8
    groove_width = 10

    # 绘制轮缘轮廓（带槽）
    points = []
    points.append((-outer_r, 0))  # 左下

    # 左侧槽
    for i in range(grooves):
        base_y = (width - (grooves - 1) * groove_width) / 2 + i * groove_width
        points.append((-outer_r, base_y))
        points.append((-(outer_r - groove_depth/2), base_y + groove_width/3))
        points.append((-(outer_r - groove_depth), base_y + groove_width))
        points.append((-(outer_r - groove_depth/2), base_y + groove_width*2/3))
        points.append((-outer_r, base_y + groove_width))

    points.append((-outer_r, width))
    points.append((outer_r, width))

    # 右侧槽（镜像）
    for i in range(grooves - 1, -1, -1):
        base_y = (width - (grooves - 1) * groove_width) / 2 + i * groove_width
        points.append((outer_r, base_y + groove_width))
        points.append((outer_r - groove_depth/2, base_y + groove_width*2/3))
        points.append((outer_r - groove_depth, base_y + groove_width))
        points.append((outer_r - groove_depth/2, base_y + groove_width/3))
        points.append((outer_r, base_y))

    points.append((outer_r, 0))
    points.append((-outer_r, 0))

    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "outline"})

    # 中心孔
    msp.add_lwpolyline(
        [(-bore_r, 0), (bore_r, 0), (bore_r, width), (-bore_r, width), (-bore_r, 0)],
        close=True,
        dxfattribs={"layer": "hole"}
    )

    # 中心线
    msp.add_line((0, -5), (0, width + 5),
                dxfattribs={"layer": "center", "linetype": "CENTER"})

def _validate_sprocket(params):
    """链轮参数校验"""
    teeth = params.get("teeth", 0)
    pitch = params.get("pitch", 0)

    if teeth < 6:
        raise ValueError("链轮齿数不能少于 6")
    if pitch <= 0:
        raise ValueError("链条节距必须大于 0")

def _draw_sprocket(doc, params):
    """绘制滚子链链轮（简化视图）"""
    teeth = params.get("teeth", 20)
    pitch = params.get("pitch", 12.7)  # 链条节距
    bore_dia = params.get("bore_diameter", 20)
    roller_dia = params.get("roller_diameter", 8)

    msp = doc.modelspace()

    # 计算链轮参数
    pitch_diameter = pitch / math.sin(math.pi / teeth)
    outer_radius = pitch_diameter / 2 + roller_dia
    root_radius = pitch_diameter / 2 - roller_dia

    msp = doc.modelspace()

    # 简化的齿形（梯形）
    tooth_angle = 360 / teeth
    points = []

    for i in range(teeth):
        base_angle = i * tooth_angle

        # 齿根点
        angle1 = math.radians(base_angle)
        points.append((
            root_radius * math.cos(angle1),
            root_radius * math.sin(angle1)
        ))

        # 齿顶点（简化为单点）
        angle2 = math.radians(base_angle + tooth_angle / 2)
        points.append((
            outer_radius * math.cos(angle2),
            outer_radius * math.sin(angle2)
        ))

    points.append(points[0])  # 闭合

    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "outline"})

    # 中心孔
    bore_radius = bore_dia / 2
    msp.add_circle((0, 0), bore_radius, dxfattribs={"layer": "hole"})

    # 节圆（虚线）
    pitch_radius = pitch_diameter / 2
    msp.add_circle((0, 0), pitch_radius, dxfattribs={"layer": "center", "linetype": "DASHED"})

def _validate_snap_ring(params):
    """卡簧参数校验"""
    inner_dia = params.get("inner_diameter", 0)
    wire_dia = params.get("wire_diameter", 0)

    if inner_dia <= 0 or wire_dia <= 0:
        raise ValueError("卡簧尺寸参数无效")

def _draw_snap_ring(doc, params):
    """绘制卡簧（简化视图）"""
    inner_dia = params.get("inner_diameter", 20)
    wire_dia = params.get("wire_diameter", 1.5)

    msp = doc.modelspace()

    mean_radius = inner_dia / 2 + wire_dia / 2

    # 绘制开口环（C形）
    # 使用圆弧表示，留一个开口
    gap_angle = 20  # 开口角度
    msp.add_arc(
        (0, 0),
        mean_radius,
        gap_angle / 2,
        360 - gap_angle / 2,
        dxfattribs={"layer": "outline"}
    )

    # 开口处的耳
    ear_length = wire_dia * 2
    msp.add_line(
        (mean_radius * math.cos(math.radians(gap_angle / 2)),
         mean_radius * math.sin(math.radians(gap_angle / 2))),
        (mean_radius * math.cos(math.radians(gap_angle / 2)) + ear_length,
         mean_radius * math.sin(math.radians(gap_angle / 2))),
        dxfattribs={"layer": "outline"}
    )

def _validate_retainer(params):
    """挡圈参数校验"""
    outer_dia = params.get("outer_diameter", 0)
    inner_dia = params.get("inner_diameter", 0)
    thickness = params.get("thickness", 0)

    if outer_dia <= inner_dia:
        raise ValueError("挡圈外径必须大于内径")
    if thickness <= 0:
        raise ValueError("挡圈厚度必须大于 0")

def _draw_retainer(doc, params):
    """绘制挡圈（截面视图）"""
    outer_dia = params.get("outer_diameter", 30)
    inner_dia = params.get("inner_diameter", 25)
    thickness = params.get("thickness", 1.5)

    msp = doc.modelspace()

    outer_r = outer_dia / 2
    inner_r = inner_dia / 2

    # 截面 - 矩形环
    msp.add_lwpolyline(
        [(inner_r, 0), (outer_r, 0), (outer_r, thickness), (inner_r, thickness), (inner_r, 0)],
        close=True,
        dxfattribs={"layer": "outline"}
    )

    # 中心线
    msp.add_line((0, -2), (0, thickness + 2),
                dxfattribs={"layer": "center", "linetype": "CENTER"})

# 注册生成器
GENERATORS = {
    "plate": {
        "validate": _validate_plate,
        "draw": _draw_plate
    },
    "screw": {
        "validate": _validate_screw,
        "draw": _draw_screw
    },
    "gear": {
        "validate": _validate_gear,
        "draw": _draw_gear
    },
    "bearing": {
        "validate": _validate_bearing,
        "draw": _draw_bearing
    },
    "flange": {
        "validate": _validate_flange,
        "draw": _draw_flange
    },
    "bolt": {
        "validate": _validate_bolt,
        "draw": _draw_bolt
    },
    "spring": {
        "validate": _validate_spring,
        "draw": _draw_spring
    },
    "chassis_frame": {
        "validate": _validate_chassis_frame,
        "draw": _draw_chassis_frame
    },
    "bracket": {
        "validate": _validate_bracket,
        "draw": _draw_bracket
    },
    "custom_code": {
        "validate": _validate_custom_code,
        "draw": _draw_custom_code
    },
    # 新增零件类型
    "nut": {
        "validate": _validate_nut,
        "draw": _draw_nut
    },
    "washer": {
        "validate": _validate_washer,
        "draw": _draw_washer
    },
    "shaft": {
        "validate": _validate_shaft,
        "draw": _draw_shaft
    },
    "stepped_shaft": {
        "validate": _validate_stepped_shaft,
        "draw": _draw_stepped_shaft
    },
    "coupling": {
        "validate": _validate_coupling,
        "draw": _draw_coupling
    },
    "pulley": {
        "validate": _validate_pulley,
        "draw": _draw_pulley
    },
    "sprocket": {
        "validate": _validate_sprocket,
        "draw": _draw_sprocket
    },
    "snap_ring": {
        "validate": _validate_snap_ring,
        "draw": _draw_snap_ring
    },
    "retainer": {
        "validate": _validate_retainer,
        "draw": _draw_retainer
    }
}

def generate_part(spec, output_file):
    """
    根据 spec 生成 DXF。
    spec 格式: {"type": "plate", "parameters": {...}}
    或者兼容旧格式: {"length": ...} (默认为 plate)
    """
    # 优先使用新的 registry + parts 生成器
    try:
        from core.base import PartSpec
        from core.registry import create_generator
        from core.exceptions import RegistrationError
        import parts  # noqa: F401  # 触发注册

        part_spec = PartSpec.from_dict(spec)
        generator = create_generator(part_spec.type)
        generator.generate(part_spec.parameters, output_file)
        return
    except (RegistrationError, ModuleNotFoundError, ImportError):
        # 若 registry 不支持该类型或模块不可用，则回退到旧的 GENERATORS
        pass

    # 1. 解析类型（旧路径）
    part_type = spec.get("type")
    params = spec.get("parameters")

    # 兼容旧格式
    if not part_type and "length" in spec:
        part_type = "plate"
        params = spec

    if part_type not in GENERATORS:
        raise ValueError(f"不支持的零件类型: {part_type}")

    generator = GENERATORS[part_type]

    # 2. 校验参数
    generator["validate"](params)

    # 3. 初始化 DXF
    doc = ezdxf.new("R2010", setup=True)
    doc.units = units.MM
    doc.layers.add("outline", color=7) # 白色/黑色
    doc.layers.add("hole", color=2)    # 黄色
    doc.layers.add("thread", color=3)  # 绿色
    doc.layers.add("center", color=1)  # 红色

    # 4. 绘制
    generator["draw"](doc, params)

    # 5. 保存
    doc.saveas(output_file)
    return True
