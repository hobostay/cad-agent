# -*- coding: utf-8 -*-
"""
轴承零件生成器
绘制深沟球轴承侧视图
"""
import math
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("bearing")
class BearingGenerator(PartGenerator):
    """轴承零件生成器"""
    part_type = "bearing"

    def validate(self, params: Dict[str, Any]) -> None:
        inner_dia = params.get("inner_diameter", 0)
        outer_dia = params.get("outer_diameter", 0)
        width = params.get("width", 0)

        if inner_dia <= 0:
            raise ValidationError(self.part_type, "inner_diameter", "内径必须大于 0")
        if outer_dia <= inner_dia:
            raise ValidationError(self.part_type, "outer_diameter", "外径必须大于内径")
        if width <= 0:
            raise ValidationError(self.part_type, "width", "宽度必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        inner_dia = params.get("inner_diameter", 20)
        outer_dia = params.get("outer_diameter", 47)
        width = params.get("width", 14)
        ball_count = params.get("ball_count", 8)

        msp = doc.modelspace()

        inner_r = inner_dia / 2
        outer_r = outer_dia / 2
        ball_r = (outer_r - inner_r) * 0.3

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

        # 滚珠
        ball_center_r = inner_r + ball_r + (outer_r - inner_r - 2*ball_r) / 2
        for i in range(ball_count):
            angle = 2 * math.pi * i / ball_count
            cx = ball_center_r * math.cos(angle)
            cy = width / 2
            msp.add_circle((cx, cy), ball_r, dxfattribs={"layer": "outline"})

        # 中心线
        msp.add_line((0, -2), (0, width + 2), dxfattribs={"layer": "center", "linetype": "CENTER"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "inner_diameter": {"type": "float", "min": 0, "description": "内径 (mm)"},
            "outer_diameter": {"type": "float", "min": 0, "description": "外径 (mm)"},
            "width": {"type": "float", "min": 0, "description": "宽度 (mm)"},
            "ball_count": {"type": "int", "min": 4, "description": "滚珠数量"},
        }
