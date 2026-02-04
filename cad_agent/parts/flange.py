# -*- coding: utf-8 -*-
"""
法兰零件生成器
绘制圆盘形法兰
"""
import math
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("flange")
class FlangeGenerator(PartGenerator):
    """法兰零件生成器"""
    part_type = "flange"

    def validate(self, params: Dict[str, Any]) -> None:
        outer_dia = params.get("outer_diameter", 0)
        inner_dia = params.get("inner_diameter", 0)
        bolt_circle_dia = params.get("bolt_circle_diameter", 0)
        bolt_count = params.get("bolt_count", 0)

        if outer_dia <= inner_dia:
            raise ValidationError(self.part_type, "outer_diameter", "外径必须大于内径")
        if bolt_count < 3:
            raise ValidationError(self.part_type, "bolt_count", "螺栓孔数不能少于 3")
        if bolt_circle_dia >= outer_dia or bolt_circle_dia <= inner_dia:
            raise ValidationError(self.part_type, "bolt_circle_diameter", "螺栓孔圆直径应在内径和外径之间")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        outer_dia = params.get("outer_diameter", 150)
        inner_dia = params.get("inner_diameter", 80)
        bolt_circle_dia = params.get("bolt_circle_diameter", 120)
        bolt_count = params.get("bolt_count", 8)
        bolt_size = params.get("bolt_size", 16)

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

        # 节圆
        msp.add_circle((0, 0), bolt_circle_r, dxfattribs={"layer": "center", "linetype": "DASHED"})

        # 中心标记
        msp.add_line((-outer_r * 1.1, 0), (outer_r * 1.1, 0),
                    dxfattribs={"layer": "center", "linetype": "CENTER"})
        msp.add_line((0, -outer_r * 1.1), (0, outer_r * 1.1),
                    dxfattribs={"layer": "center", "linetype": "CENTER"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "outer_diameter": {"type": "float", "min": 0, "description": "外径 (mm)"},
            "inner_diameter": {"type": "float", "min": 0, "description": "内径 (mm)"},
            "bolt_circle_diameter": {"type": "float", "min": 0, "description": "螺栓孔分布圆直径 (mm)"},
            "bolt_count": {"type": "int", "min": 3, "description": "螺栓孔数量"},
            "bolt_size": {"type": "float", "min": 0, "description": "螺栓孔直径 (mm)"},
        }
