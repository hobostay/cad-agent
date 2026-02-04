# -*- coding: utf-8 -*-
"""
弹簧零件生成器
绘制压缩弹簧侧视图
"""
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("spring")
class SpringGenerator(PartGenerator):
    """弹簧零件生成器"""
    part_type = "spring"

    def validate(self, params: Dict[str, Any]) -> None:
        wire_dia = params.get("wire_diameter", 0)
        coil_dia = params.get("coil_diameter", 0)
        free_length = params.get("free_length", 0)

        if wire_dia <= 0:
            raise ValidationError(self.part_type, "wire_diameter", "线径必须大于 0")
        if coil_dia <= wire_dia:
            raise ValidationError(self.part_type, "coil_diameter", "线圈直径必须大于线径")
        if free_length <= 0:
            raise ValidationError(self.part_type, "free_length", "自由长度必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        wire_dia = params.get("wire_diameter", 2)
        coil_dia = params.get("coil_diameter", 20)
        free_length = params.get("free_length", 80)
        coils = params.get("coils", 8)

        msp = doc.modelspace()

        coil_r = coil_dia / 2
        wire_r = wire_dia / 2

        # 绘制弹簧波形
        points = []
        active_coils = coils - 2
        pitch = (free_length - 2 * wire_dia) / coils

        # 起始端
        points.append((0, 0))
        points.append((coil_r, wire_dia))

        # 主体螺旋
        y_start = wire_dia
        for i in range(active_coils * 2):
            y = y_start + (i / 2) * pitch
            x = coil_r if i % 2 == 0 else -coil_r
            points.append((x, y))

        # 结束端
        points.append((0, free_length - wire_dia))
        points.append((0, free_length))

        msp.add_lwpolyline(points, dxfattribs={"layer": "outline"})

        # 中心线
        msp.add_line((0, -2), (0, free_length + 2),
                    dxfattribs={"layer": "center", "linetype": "CENTER"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "wire_diameter": {"type": "float", "min": 0, "description": "线径 (mm)"},
            "coil_diameter": {"type": "float", "min": 0, "description": "线圈直径 (mm)"},
            "free_length": {"type": "float", "min": 0, "description": "自由长度 (mm)"},
            "coils": {"type": "int", "min": 2, "description": "有效圈数"},
        }
