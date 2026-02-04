# -*- coding: utf-8 -*-
"""
皮带轮零件生成器
绘制V带轮
"""
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("pulley")
class PulleyGenerator(PartGenerator):
    """皮带轮零件生成器"""
    part_type = "pulley"

    def validate(self, params: Dict[str, Any]) -> None:
        outer_dia = params.get("outer_diameter", 0)
        bore_dia = params.get("bore_diameter", 0)
        width = params.get("width", 0)

        if outer_dia <= bore_dia:
            raise ValidationError(self.part_type, "outer_diameter", "外径必须大于内径")
        if width <= 0:
            raise ValidationError(self.part_type, "width", "宽度必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        outer_dia = params.get("outer_diameter", 100)
        bore_dia = params.get("bore_diameter", 20)
        hub_dia = params.get("hub_diameter", 35)
        width = params.get("width", 30)
        grooves = params.get("grooves", 1)

        msp = doc.modelspace()

        outer_r = outer_dia / 2
        bore_r = bore_dia / 2
        hub_r = hub_dia / 2

        groove_depth = 8
        groove_width = 10

        # 绘制轮缘轮廓（带槽）
        points = []
        points.append((-outer_r, 0))

        # 左侧槽
        for i in range(grooves):
            base_y = (width - (grooves - 1) * groove_width) / 2 + i * groove_width
            points.append((-outer_r, base_y))
            points.append((-(outer_r - groove_depth/2), base_y + groove_width/3))
            points.append((-(outer_r - groove_depth), base_y + groove_width))
            points.append((-(outer_r - groove_depth/2), base_y + groove_width*2/3))
            points.append((-outer_r, base_y + groove_width))

        points.append((-outer_r, width))
        points.append((outer_r, width))

        # 右侧槽（镜像）
        for i in range(grooves - 1, -1, -1):
            base_y = (width - (grooves - 1) * groove_width) / 2 + i * groove_width
            points.append((outer_r, base_y + groove_width))
            points.append((outer_r - groove_depth/2, base_y + groove_width*2/3))
            points.append((outer_r - groove_depth, base_y + groove_width))
            points.append((outer_r - groove_depth/2, base_y + groove_width/3))
            points.append((outer_r, base_y))

        points.append((outer_r, 0))
        points.append((-outer_r, 0))

        msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "outline"})

        # 中心孔
        msp.add_lwpolyline(
            [(-bore_r, 0), (bore_r, 0), (bore_r, width), (-bore_r, width), (-bore_r, 0)],
            close=True,
            dxfattribs={"layer": "hole"}
        )

        # 中心线
        msp.add_line((0, -5), (0, width + 5),
                    dxfattribs={"layer": "center", "linetype": "CENTER"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "outer_diameter": {"type": "float", "min": 0, "description": "外径 (mm)"},
            "bore_diameter": {"type": "float", "min": 0, "description": "内孔直径 (mm)"},
            "hub_diameter": {"type": "float", "min": 0, "description": "轮毂直径 (mm)"},
            "width": {"type": "float", "min": 0, "description": "宽度 (mm)"},
            "grooves": {"type": "int", "min": 1, "description": "槽数"},
        }
