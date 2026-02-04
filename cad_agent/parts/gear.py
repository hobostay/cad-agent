# -*- coding: utf-8 -*-
"""
齿轮零件生成器
绘制简化渐开线齿轮
"""
import math
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("gear")
class GearGenerator(PartGenerator):
    """齿轮零件生成器"""
    part_type = "gear"

    def validate(self, params: Dict[str, Any]) -> None:
        module = params.get("module", 0)
        teeth = params.get("teeth", 0)
        pressure_angle = params.get("pressure_angle", 20)

        if module <= 0:
            raise ValidationError(self.part_type, "module", "模数必须大于 0")
        if teeth < 5:
            raise ValidationError(self.part_type, "teeth", "齿数不能少于 5")
        if not (10 <= pressure_angle <= 30):
            raise ValidationError(self.part_type, "pressure_angle", "压力角应在 10-30 度之间")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        module = params.get("module", 2)
        teeth = params.get("teeth", 20)
        pressure_angle = params.get("pressure_angle", 20)
        bore_dia = params.get("bore_diameter", 10)
        hub_dia = params.get("hub_diameter", 20)
        hub_width = params.get("hub_width", 5)

        msp = doc.modelspace()

        # 计算齿轮参数
        pitch_diameter = module * teeth
        addendum = module
        dedendum = 1.25 * module
        outer_radius = (pitch_diameter + 2 * addendum) / 2
        root_radius = (pitch_diameter - 2 * dedendum) / 2
        pitch_radius = pitch_diameter / 2

        # 绘制齿形（简化为梯形）
        tooth_angle = 360 / teeth
        tooth_width_angle = tooth_angle / 2

        points = []
        for i in range(teeth):
            base_angle = i * tooth_angle

            # 齿根点
            angle1 = math.radians(base_angle)
            points.append((
                root_radius * math.cos(angle1),
                root_radius * math.sin(angle1)
            ))

            # 齿顶左点
            angle2 = math.radians(base_angle + tooth_width_angle * 0.3)
            points.append((
                outer_radius * math.cos(angle2),
                outer_radius * math.sin(angle2)
            ))

            # 齿顶右点
            angle3 = math.radians(base_angle + tooth_width_angle * 0.7)
            points.append((
                outer_radius * math.cos(angle3),
                outer_radius * math.sin(angle3)
            ))

            # 齿根点
            angle4 = math.radians(base_angle + tooth_width_angle)
            points.append((
                root_radius * math.cos(angle4),
                root_radius * math.sin(angle4)
            ))

        points.append(points[0])
        msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "outline"})

        # 绘制中心孔
        bore_radius = bore_dia / 2
        msp.add_circle((0, 0), bore_radius, dxfattribs={"layer": "hole"})

        # 绘制轮毂
        if hub_dia > bore_dia:
            hub_radius = hub_dia / 2
            msp.add_circle((0, 0), hub_radius, dxfattribs={"layer": "outline"})

        # 绘制节圆（虚线）
        msp.add_circle((0, 0), pitch_radius, dxfattribs={"layer": "center", "linetype": "DASHED"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "module": {"type": "float", "min": 0, "description": "模数"},
            "teeth": {"type": "int", "min": 5, "description": "齿数"},
            "pressure_angle": {"type": "float", "min": 10, "max": 30, "description": "压力角（度）"},
            "bore_diameter": {"type": "float", "min": 0, "description": "中心孔直径 (mm)"},
            "hub_diameter": {"type": "float", "min": 0, "description": "轮毂直径 (mm)"},
            "hub_width": {"type": "float", "min": 0, "description": "轮毂宽度 (mm)"},
        }
