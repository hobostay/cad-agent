# -*- coding: utf-8 -*-
"""
螺丝零件生成器
绘制外螺纹紧固件侧视图
"""
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("screw")
class ScrewGenerator(PartGenerator):
    """螺丝零件生成器"""
    part_type = "screw"

    def validate(self, params: Dict[str, Any]) -> None:
        head_diameter = params.get("head_diameter", 0)
        head_height = params.get("head_height", 0)
        body_diameter = params.get("body_diameter", 0)
        body_length = params.get("body_length", 0)

        if head_diameter <= 0:
            raise ValidationError(self.part_type, "head_diameter", "螺头直径必须大于 0")
        if head_height <= 0:
            raise ValidationError(self.part_type, "head_height", "螺头高度必须大于 0")
        if body_diameter <= 0:
            raise ValidationError(self.part_type, "body_diameter", "螺杆直径必须大于 0")
        if body_length <= 0:
            raise ValidationError(self.part_type, "body_length", "螺杆长度必须大于 0")
        if body_diameter >= head_diameter:
            raise ValidationError(self.part_type, "body_diameter", "螺杆直径必须小于螺头直径")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        hd = params.get("head_diameter", 10)
        hh = params.get("head_height", 5)
        bd = params.get("body_diameter", 5)
        bl = params.get("body_length", 20)

        msp = doc.modelspace()

        # 螺杆
        msp.add_lwpolyline(
            [(-bd/2, 0), (bd/2, 0), (bd/2, bl), (-bd/2, bl), (-bd/2, 0)],
            close=True,
            dxfattribs={"layer": "outline"}
        )

        # 螺头
        msp.add_lwpolyline(
            [(-hd/2, bl), (hd/2, bl), (hd/2, bl+hh), (-hd/2, bl+hh), (-hd/2, bl)],
            close=True,
            dxfattribs={"layer": "outline"}
        )

        # 螺纹示意线
        margin = 0.1 * bd
        msp.add_line((-bd/2 + margin, 0), (-bd/2 + margin, bl),
                    dxfattribs={"layer": "thread", "color": 3})
        msp.add_line((bd/2 - margin, 0), (bd/2 - margin, bl),
                    dxfattribs={"layer": "thread", "color": 3})

        # 中心线
        msp.add_line((0, -2), (0, bl + hh + 2),
                    dxfattribs={"layer": "center", "color": 1, "linetype": "CENTER"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "head_diameter": {"type": "float", "min": 0, "description": "螺头直径 (mm)"},
            "head_height": {"type": "float", "min": 0, "description": "螺头高度 (mm)"},
            "body_diameter": {"type": "float", "min": 0, "description": "螺杆直径 (mm)"},
            "body_length": {"type": "float", "min": 0, "description": "螺杆长度 (mm)"},
        }
