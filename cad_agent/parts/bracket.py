# -*- coding: utf-8 -*-
"""
支架零件生成器
绘制L型角支架
"""
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("bracket")
class BracketGenerator(PartGenerator):
    """支架零件生成器"""
    part_type = "bracket"

    def validate(self, params: Dict[str, Any]) -> None:
        length = params.get("length", 0)
        height = params.get("height", 0)
        thickness = params.get("thickness", 0)

        if length <= 0:
            raise ValidationError(self.part_type, "length", "长度必须大于 0")
        if height <= 0:
            raise ValidationError(self.part_type, "height", "高度必须大于 0")
        if thickness <= 0:
            raise ValidationError(self.part_type, "thickness", "厚度必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
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
            msp.add_circle((hole_offset, thickness/2), hole_r, dxfattribs={"layer": "hole"})
            msp.add_circle((length - hole_offset, thickness/2), hole_r, dxfattribs={"layer": "hole"})
            msp.add_circle((thickness/2, height - hole_offset), hole_r, dxfattribs={"layer": "hole"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "length": {"type": "float", "min": 0, "description": "水平边长度 (mm)"},
            "height": {"type": "float", "min": 0, "description": "竖直边高度 (mm)"},
            "thickness": {"type": "float", "min": 0, "description": "板材厚度 (mm)"},
            "hole_diameter": {"type": "float", "min": 0, "description": "安装孔直径 (mm)"},
            "hole_offset": {"type": "float", "min": 0, "description": "孔距边距离 (mm)"},
        }
