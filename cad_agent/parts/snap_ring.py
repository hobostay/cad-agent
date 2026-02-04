# -*- coding: utf-8 -*-
"""
卡簧零件生成器
绘制轴用卡簧
"""
import math
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("snap_ring")
class SnapRingGenerator(PartGenerator):
    """卡簧零件生成器"""
    part_type = "snap_ring"

    def validate(self, params: Dict[str, Any]) -> None:
        inner_dia = params.get("inner_diameter", 0)
        wire_dia = params.get("wire_diameter", 0)

        if inner_dia <= 0:
            raise ValidationError(self.part_type, "inner_diameter", "内径必须大于 0")
        if wire_dia <= 0:
            raise ValidationError(self.part_type, "wire_diameter", "线径必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        inner_dia = params.get("inner_diameter", 20)
        wire_dia = params.get("wire_diameter", 1.5)

        msp = doc.modelspace()

        mean_radius = inner_dia / 2 + wire_dia / 2

        # 绘制开口环（C形）
        gap_angle = 20
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

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "inner_diameter": {"type": "float", "min": 0, "description": "内径 (mm)"},
            "wire_diameter": {"type": "float", "min": 0, "description": "线径 (mm)"},
        }
