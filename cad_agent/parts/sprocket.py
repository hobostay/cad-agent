# -*- coding: utf-8 -*-
"""
链轮零件生成器
绘制滚子链链轮
"""
import math
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("sprocket")
class SprocketGenerator(PartGenerator):
    """链轮零件生成器"""
    part_type = "sprocket"

    def validate(self, params: Dict[str, Any]) -> None:
        teeth = params.get("teeth", 0)
        pitch = params.get("pitch", 0)

        if teeth < 6:
            raise ValidationError(self.part_type, "teeth", "齿数不能少于 6")
        if pitch <= 0:
            raise ValidationError(self.part_type, "pitch", "链条节距必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        teeth = params.get("teeth", 20)
        pitch = params.get("pitch", 12.7)
        bore_dia = params.get("bore_diameter", 20)
        roller_dia = params.get("roller_diameter", 8)

        msp = doc.modelspace()

        # 计算链轮参数
        pitch_diameter = pitch / math.sin(math.pi / teeth)
        outer_radius = pitch_diameter / 2 + roller_dia
        root_radius = pitch_diameter / 2 - roller_dia

        # 简化的齿形（梯形）
        tooth_angle = 360 / teeth
        points = []

        for i in range(teeth):
            base_angle = i * tooth_angle

            # 齿根点
            angle1 = math.radians(base_angle)
            points.append((
                root_radius * math.cos(angle1),
                root_radius * math.sin(angle1)
            ))

            # 齿顶点
            angle2 = math.radians(base_angle + tooth_angle / 2)
            points.append((
                outer_radius * math.cos(angle2),
                outer_radius * math.sin(angle2)
            ))

        points.append(points[0])
        msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "outline"})

        # 中心孔
        bore_radius = bore_dia / 2
        msp.add_circle((0, 0), bore_radius, dxfattribs={"layer": "hole"})

        # 节圆
        pitch_radius = pitch_diameter / 2
        msp.add_circle((0, 0), pitch_radius, dxfattribs={"layer": "center", "linetype": "DASHED"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "teeth": {"type": "int", "min": 6, "description": "齿数"},
            "pitch": {"type": "float", "min": 0, "description": "链条节距 (mm)"},
            "bore_diameter": {"type": "float", "min": 0, "description": "内孔直径 (mm)"},
            "roller_diameter": {"type": "float", "min": 0, "description": "滚子直径 (mm)"},
        }
