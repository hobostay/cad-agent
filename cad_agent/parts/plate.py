# -*- coding: utf-8 -*-
"""
底板零件生成器
支持多种特征：孔、腰形孔、螺纹孔、沉孔、倒角、倒圆、键槽
"""
import math
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("plate")
class PlateGenerator(PartGenerator):
    """底板零件生成器"""
    part_type = "plate"

    def validate(self, params: Dict[str, Any]) -> None:
        length = params.get("length", 0)
        width = params.get("width", 0)
        hole_diameter = params.get("hole_diameter", 0)
        corner_offset = params.get("corner_offset", 0)

        chamfer_size = params.get("chamfer_size", 0)
        fillet_radius = params.get("fillet_radius", 0)

        if length <= 0 or width <= 0:
            raise ValidationError(self.part_type, "length/width", "必须大于 0")

        # 如果有孔，校验孔参数
        if hole_diameter > 0:
            radius = hole_diameter / 2.0
            if corner_offset > 0 and corner_offset + radius > length:
                raise ValidationError(self.part_type, "corner_offset", "孔位置超出板材范围 (X方向)")
            if corner_offset > 0 and corner_offset + radius > width:
                raise ValidationError(self.part_type, "corner_offset", "孔位置超出板材范围 (Y方向)")

        # 校验腰形孔参数
        slots = params.get("slots", [])
        for slot in slots:
            slot_length = slot.get("length", 0)
            slot_width = slot.get("width", 0)
            if slot_length <= 0 or slot_width <= 0:
                raise ValidationError(self.part_type, "slot", "腰形孔尺寸必须大于 0")
            if slot_width >= slot_length:
                raise ValidationError(self.part_type, "slot", "腰形孔宽度应小于长度")

            # 检查位置
            if "x" in slot and "y" in slot:
                x, y = slot["x"], slot["y"]
                if x < 0 or x > length or y < 0 or y > width:
                    raise ValidationError(self.part_type, "slot", "腰形孔位置超出板材范围")

        # 校验螺纹孔参数
        threaded_holes = params.get("threaded_holes", [])
        for th in threaded_holes:
            th_dia = th.get("diameter", 0)
            if th_dia <= 0:
                raise ValidationError(self.part_type, "threaded_hole", "螺纹孔直径必须大于 0")

        # 校验沉孔参数
        counterbores = params.get("counterbores", [])
        for cb in counterbores:
            cb_dia = cb.get("diameter", 0)
            cb_depth = cb.get("depth", 0)
            if cb_dia <= 0:
                raise ValidationError(self.part_type, "counterbore", "沉孔直径必须大于 0")
            if cb_depth <= 0:
                raise ValidationError(self.part_type, "counterbore", "沉孔深度必须大于 0")

        # 校验键槽参数
        keyway = params.get("keyway")
        if keyway:
            kw_width = keyway.get("width", 0)
            kw_length = keyway.get("length", 0)
            if kw_width <= 0 or kw_length <= 0:
                raise ValidationError(self.part_type, "keyway", "键槽尺寸必须大于 0")

        # 倒角和倒圆不能同时设置
        if chamfer_size > 0 and fillet_radius > 0:
            raise ValidationError(self.part_type, "chamfer/fillet", "倒角和倒圆不能同时设置")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        from ..turtle_cad import TurtleCAD

        length = params.get("length", 100)
        width = params.get("width", 100)
        hole_diameter = params.get("hole_diameter", 0)
        corner_offset = params.get("corner_offset", 10)

        chamfer_size = params.get("chamfer_size", 0)
        fillet_radius = params.get("fillet_radius", 0)
        slots = params.get("slots", [])
        threaded_holes = params.get("threaded_holes", [])
        counterbores = params.get("counterbores", [])
        keyway = params.get("keyway")

        msp = doc.modelspace()

        # 1. 绘制外轮廓
        if chamfer_size > 0:
            self._draw_chamfered_outline(msp, length, width, chamfer_size)
        elif fillet_radius > 0:
            self._draw_rounded_outline(msp, length, width, fillet_radius)
        else:
            self._draw_simple_outline(msp, length, width)

        # 2. 绘制四角孔
        if hole_diameter > 0:
            self._draw_corner_holes(msp, length, width, hole_diameter, corner_offset)

        # 3. 绘制腰形孔
        for slot in slots:
            self._draw_slot(msp, slot, length, width)

        # 4. 绘制螺纹孔
        for th in threaded_holes:
            self._draw_threaded_hole(msp, th, length, width)

        # 5. 绘制沉孔
        for cb in counterbores:
            self._draw_counterbore(msp, cb)

        # 6. 绘制键槽
        if keyway:
            self._draw_keyway(msp, keyway, length)

    def _draw_simple_outline(self, msp, length: float, width: float) -> None:
        msp.add_lwpolyline(
            [(0, 0), (length, 0), (length, width), (0, width), (0, 0)],
            close=True,
            dxfattribs={"layer": "outline"},
        )

    def _draw_chamfered_outline(self, msp, length: float, width: float, c: float) -> None:
        points = [
            (c, 0),
            (length, 0),
            (length, width - c),
            (length - c, width),
            (0, width),
            (0, c),
            (c, 0),
        ]
        # 绘制倒角线
        msp.add_line((c, 0), (0, c), dxfattribs={"layer": "outline"})
        msp.add_line((length, width - c), (length - c, width), dxfattribs={"layer": "outline"})

        msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "outline"})

    def _draw_rounded_outline(self, msp, length: float, width: float, r: float) -> None:
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

    def _draw_corner_holes(self, msp, length: float, width: float,
                          hole_diameter: float, corner_offset: float) -> None:
        radius = hole_diameter / 2.0
        centers = [
            (corner_offset, corner_offset),
            (length - corner_offset, corner_offset),
            (length - corner_offset, width - corner_offset),
            (corner_offset, width - corner_offset),
        ]
        for cx, cy in centers:
            msp.add_circle(center=(cx, cy), radius=radius, dxfattribs={"layer": "hole"})

    def _draw_slot(self, msp, slot: Dict, length: float, width: float) -> None:
        from ..turtle_cad import TurtleCAD
        slot_length = slot.get("length", 20)
        slot_width = slot.get("width", 10)
        slot_x = slot.get("x", length / 2)
        slot_y = slot.get("y", width / 2)
        slot_angle = slot.get("angle", 0)

        half_length = slot_length / 2
        half_width = slot_width / 2

        if slot_angle == 0:
            left_center = (slot_x - half_length, slot_y)
            right_center = (slot_x + half_length, slot_y)
            msp.add_arc(left_center, half_width, 90, 270, dxfattribs={"layer": "hole"})
            msp.add_arc(right_center, half_width, 270, 90, dxfattribs={"layer": "hole"})
            msp.add_line((slot_x - half_length, slot_y + half_width),
                        (slot_x + half_length, slot_y + half_width),
                        dxfattribs={"layer": "hole"})
            msp.add_line((slot_x - half_length, slot_y - half_width),
                        (slot_x + half_length, slot_y - half_width),
                        dxfattribs={"layer": "hole"})
        else:
            t = TurtleCAD(msp)
            t.jump_to(slot_x, slot_y)
            t.set_heading(slot_angle)
            t.slot(slot_length, slot_width)

    def _draw_threaded_hole(self, msp, th: Dict, length: float, width: float) -> None:
        th_dia = th.get("diameter", 6)
        th_x = th.get("x", length / 2)
        th_y = th.get("y", width / 2)

        msp.add_circle((th_x, th_y), th_dia / 2, dxfattribs={"layer": "hole"})
        thread_radius = th_dia / 2 * 0.85
        msp.add_circle((th_x, th_y), thread_radius,
                      dxfattribs={"layer": "thread", "linetype": "DASHED"})
        msp.add_line((th_x - th_dia, th_y), (th_x + th_dia, th_y),
                    dxfattribs={"layer": "center", "linetype": "CENTER"})
        msp.add_line((th_x, th_y - th_dia), (th_x, th_y + th_dia),
                    dxfattribs={"layer": "center", "linetype": "CENTER"})

    def _draw_counterbore(self, msp, cb: Dict) -> None:
        cb_dia = cb.get("diameter", 12)
        cb_depth = cb.get("depth", 5)
        cb_x = cb.get("x", 0)
        cb_y = cb.get("y", 0)
        cb_through_dia = cb.get("through_diameter", 6)

        msp.add_circle((cb_x, cb_y), cb_dia / 2, dxfattribs={"layer": "hole"})
        msp.add_circle((cb_x, cb_y), cb_through_dia / 2, dxfattribs={"layer": "hole"})

        if cb_depth > 0:
            text = msp.add_text(f"Depth:{cb_depth}", dxfattribs={"height": min(cb_dia, 3)})
            text.dxf.insert = (cb_x + cb_dia/2 + 2, cb_y)

    def _draw_keyway(self, msp, keyway: Dict, length: float) -> None:
        kw_width = keyway.get("width", 6)
        kw_length = keyway.get("length", 20)
        kw_x = keyway.get("x", length / 2)
        kw_y = keyway.get("y", 0)
        kw_orientation = keyway.get("orientation", "horizontal")

        half_length = kw_length / 2
        half_width = kw_width / 2

        if kw_orientation == "horizontal":
            points = [
                (kw_x - half_length, kw_y),
                (kw_x + half_length, kw_y),
                (kw_x + half_length, kw_y + kw_width),
                (kw_x - half_length, kw_y + kw_width),
                (kw_x - half_length, kw_y),
            ]
        else:
            points = [
                (kw_x, kw_y - half_length),
                (kw_x + kw_width, kw_y - half_length),
                (kw_x + kw_width, kw_y + half_length),
                (kw_x, kw_y + half_length),
                (kw_x, kw_y - half_length),
            ]

        msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "hole"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "length": {"type": "float", "min": 0, "description": "长度 (mm)"},
            "width": {"type": "float", "min": 0, "description": "宽度 (mm)"},
            "thickness": {"type": "float", "min": 0, "description": "厚度 (mm)"},
            "hole_diameter": {"type": "float", "min": 0, "description": "四角孔直径 (mm)"},
            "corner_offset": {"type": "float", "min": 0, "description": "孔心距板边距离 (mm)"},
            "chamfer_size": {"type": "float", "min": 0, "description": "倒角尺寸 (mm)"},
            "fillet_radius": {"type": "float", "min": 0, "description": "倒圆半径 (mm)"},
            "slots": {"type": "array", "description": "腰形孔数组"},
            "threaded_holes": {"type": "array", "description": "螺纹孔数组"},
            "counterbores": {"type": "array", "description": "沉孔数组"},
            "keyway": {"type": "object", "description": "键槽参数"},
        }
