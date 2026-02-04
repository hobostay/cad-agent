# -*- coding: utf-8 -*-
"""
联轴器零件生成器
绘制刚性联轴器
"""
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("coupling")
class CouplingGenerator(PartGenerator):
    """联轴器零件生成器"""
    part_type = "coupling"

    def validate(self, params: Dict[str, Any]) -> None:
        inner_dia = params.get("inner_diameter", 0)
        outer_dia = params.get("outer_diameter", 0)
        length = params.get("length", 0)

        if inner_dia <= 0:
            raise ValidationError(self.part_type, "inner_diameter", "内径必须大于 0")
        if outer_dia <= inner_dia:
            raise ValidationError(self.part_type, "outer_diameter", "外径必须大于内径")
        if length <= 0:
            raise ValidationError(self.part_type, "length", "长度必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
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

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "inner_diameter": {"type": "float", "min": 0, "description": "内径 (mm)"},
            "outer_diameter": {"type": "float", "min": 0, "description": "外径 (mm)"},
            "length": {"type": "float", "min": 0, "description": "长度 (mm)"},
        }
