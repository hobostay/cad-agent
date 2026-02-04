# -*- coding: utf-8 -*-
"""
螺母零件生成器
绘制六角螺母
"""
import math
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("nut")
class NutGenerator(PartGenerator):
    """螺母零件生成器"""
    part_type = "nut"

    def validate(self, params: Dict[str, Any]) -> None:
        diameter = params.get("diameter", 0)
        thickness = params.get("thickness", 0)

        if diameter <= 0:
            raise ValidationError(self.part_type, "diameter", "公称直径必须大于 0")
        if thickness <= 0:
            raise ValidationError(self.part_type, "thickness", "厚度必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        diameter = params.get("diameter", 10)
        thickness = params.get("thickness", diameter * 0.9)

        msp = doc.modelspace()

        # 六角螺母外轮廓
        across_flats = diameter * 1.75
        radius = across_flats / 2

        points = []
        for i in range(6):
            angle = math.radians(30 + i * 60)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle) + thickness / 2
            points.append((x, y))

        msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "outline"})

        # 内孔
        hole_radius = diameter / 2
        msp.add_circle((0, thickness / 2), hole_radius, dxfattribs={"layer": "hole"})

        # 螺纹示意
        thread_radius = hole_radius * 0.85
        msp.add_circle((0, thickness / 2), thread_radius,
                      dxfattribs={"layer": "thread", "linetype": "DASHED"})

        # 中心线
        msp.add_line((-radius * 1.2, thickness / 2), (radius * 1.2, thickness / 2),
                    dxfattribs={"layer": "center", "linetype": "CENTER"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "diameter": {"type": "float", "min": 0, "description": "公称直径 (mm)"},
            "thickness": {"type": "float", "min": 0, "description": "厚度 (mm)"},
        }
