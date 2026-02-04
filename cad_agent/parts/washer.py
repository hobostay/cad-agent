# -*- coding: utf-8 -*-
"""
垫圈零件生成器
绘制平垫圈截面图
"""
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("washer")
class WasherGenerator(PartGenerator):
    """垫圈零件生成器"""
    part_type = "washer"

    def validate(self, params: Dict[str, Any]) -> None:
        inner_dia = params.get("inner_diameter", 0)
        outer_dia = params.get("outer_diameter", 0)
        thickness = params.get("thickness", 0)

        if inner_dia <= 0:
            raise ValidationError(self.part_type, "inner_diameter", "内径必须大于 0")
        if outer_dia <= inner_dia:
            raise ValidationError(self.part_type, "outer_diameter", "外径必须大于内径")
        if thickness <= 0:
            raise ValidationError(self.part_type, "thickness", "厚度必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        inner_dia = params.get("inner_diameter", 11)
        outer_dia = params.get("outer_diameter", 20)
        thickness = params.get("thickness", 2)

        msp = doc.modelspace()

        inner_r = inner_dia / 2
        outer_r = outer_dia / 2

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

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "inner_diameter": {"type": "float", "min": 0, "description": "内径 (mm)"},
            "outer_diameter": {"type": "float", "min": 0, "description": "外径 (mm)"},
            "thickness": {"type": "float", "min": 0, "description": "厚度 (mm)"},
        }
