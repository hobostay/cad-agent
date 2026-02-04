# -*- coding: utf-8 -*-
"""
传动轴零件生成器
绘制光轴侧视图
"""
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("shaft")
class ShaftGenerator(PartGenerator):
    """传动轴零件生成器"""
    part_type = "shaft"

    def validate(self, params: Dict[str, Any]) -> None:
        diameter = params.get("diameter", 0)
        length = params.get("length", 0)

        if diameter <= 0:
            raise ValidationError(self.part_type, "diameter", "直径必须大于 0")
        if length <= 0:
            raise ValidationError(self.part_type, "length", "长度必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        diameter = params.get("diameter", 20)
        length = params.get("length", 100)

        msp = doc.modelspace()

        radius = diameter / 2

        # 轴主体
        msp.add_lwpolyline(
            [(-radius, 0), (radius, 0), (radius, length), (-radius, length), (-radius, 0)],
            close=True,
            dxfattribs={"layer": "outline"}
        )

        # 中心线
        msp.add_line((0, -5), (0, length + 5),
                    dxfattribs={"layer": "center", "linetype": "CENTER"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "diameter": {"type": "float", "min": 0, "description": "直径 (mm)"},
            "length": {"type": "float", "min": 0, "description": "长度 (mm)"},
        }


@register_generator("stepped_shaft")
class SteppedShaftGenerator(PartGenerator):
    """阶梯轴零件生成器"""
    part_type = "stepped_shaft"

    def validate(self, params: Dict[str, Any]) -> None:
        sections = params.get("sections", [])
        if len(sections) < 2:
            raise ValidationError(self.part_type, "sections", "阶梯轴至少需要 2 段")

        for i, sec in enumerate(sections):
            dia = sec.get("diameter", 0)
            length = sec.get("length", 0)
            if dia <= 0:
                raise ValidationError(self.part_type, f"sections[{i}].diameter", "直径必须大于 0")
            if length <= 0:
                raise ValidationError(self.part_type, f"sections[{i}].length", "长度必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        sections = params.get("sections", [
            {"diameter": 30, "length": 40},
            {"diameter": 25, "length": 60},
            {"diameter": 20, "length": 30}
        ])

        msp = doc.modelspace()

        current_y = 0
        total_length = sum(sec["length"] for sec in sections)

        for sec in sections:
            dia = sec["diameter"]
            length = sec["length"]
            radius = dia / 2

            msp.add_lwpolyline(
                [(-radius, current_y), (radius, current_y),
                 (radius, current_y + length), (-radius, current_y + length),
                 (-radius, current_y)],
                close=True,
                dxfattribs={"layer": "outline"}
            )

            current_y += length

        # 中心线
        msp.add_line((0, -5), (0, total_length + 5),
                    dxfattribs={"layer": "center", "linetype": "CENTER"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "sections": {
                "type": "array",
                "description": "各段参数",
                "items": {
                    "diameter": {"type": "float", "min": 0},
                    "length": {"type": "float", "min": 0}
                }
            }
        }
