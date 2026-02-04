# -*- coding: utf-8 -*-
"""
车架零件生成器
绘制汽车梯形车架
"""
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("chassis_frame")
class ChassisFrameGenerator(PartGenerator):
    """车架零件生成器"""
    part_type = "chassis_frame"

    def validate(self, params: Dict[str, Any]) -> None:
        length = params.get("length", 0)
        width = params.get("width", 0)
        rail_height = params.get("rail_height", 0)

        if length <= 0:
            raise ValidationError(self.part_type, "length", "长度必须大于 0")
        if width <= 0:
            raise ValidationError(self.part_type, "width", "宽度必须大于 0")
        if rail_height <= 0:
            raise ValidationError(self.part_type, "rail_height", "纵梁高度必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
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

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "length": {"type": "float", "min": 0, "description": "车架长度 (mm)"},
            "width": {"type": "float", "min": 0, "description": "车架宽度 (mm)"},
            "rail_height": {"type": "float", "min": 0, "description": "纵梁高度 (mm)"},
            "rail_thickness": {"type": "float", "min": 0, "description": "纵梁厚度 (mm)"},
            "cross_members": {"type": "int", "min": 1, "description": "横梁数量"},
        }
