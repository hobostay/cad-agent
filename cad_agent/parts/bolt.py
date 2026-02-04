# -*- coding: utf-8 -*-
"""
螺栓零件生成器
绘制六角头螺栓
"""
import math
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError


@register_generator("bolt")
class BoltGenerator(PartGenerator):
    """螺栓零件生成器"""
    part_type = "bolt"

    def validate(self, params: Dict[str, Any]) -> None:
        diameter = params.get("diameter", 0)
        length = params.get("length", 0)

        if diameter <= 0:
            raise ValidationError(self.part_type, "diameter", "直径必须大于 0")
        if length <= 0:
            raise ValidationError(self.part_type, "length", "长度必须大于 0")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        diameter = params.get("diameter", 10)
        length = params.get("length", 50)
        head_height = params.get("head_height", diameter * 0.7)

        msp = doc.modelspace()

        r = diameter / 2

        # 螺杆
        msp.add_lwpolyline(
            [(0, 0), (r, 0), (r, length), (-r, length), (-r, 0), (0, 0)],
            close=True,
            dxfattribs={"layer": "outline"}
        )

        # 六角头
        hex_width = diameter * 1.8
        msp.add_lwpolyline(
            [(-hex_width/2, length), (hex_width/2, length),
             (hex_width/2, length + head_height), (-hex_width/2, length + head_height),
             (-hex_width/2, length)],
            close=True,
            dxfattribs={"layer": "outline"}
        )

        # 螺纹示意
        thread_length = length * 0.7
        for y in range(int(thread_length)):
            msp.add_line((-r * 0.9, y), (-r * 0.9, y + 1),
                        dxfattribs={"layer": "thread", "color": 3})
            msp.add_line((r * 0.9, y), (r * 0.9, y + 1),
                        dxfattribs={"layer": "thread", "color": 3})

        # 中心线
        msp.add_line((0, -2), (0, length + head_height + 2),
                    dxfattribs={"layer": "center", "linetype": "CENTER"})

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "diameter": {"type": "float", "min": 0, "description": "公称直径 (mm)"},
            "length": {"type": "float", "min": 0, "description": "螺杆长度 (mm)"},
            "head_height": {"type": "float", "min": 0, "description": "螺头高度 (mm)"},
        }
