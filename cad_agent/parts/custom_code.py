# -*- coding: utf-8 -*-
"""
自定义代码零件生成器
使用 TurtleCAD 绘制任意复杂形状
"""
import math
from typing import Dict, Any
from ..core.base import PartGenerator
from ..core.registry import register_generator
from ..core.exceptions import ValidationError
from ..turtle_cad import TurtleCAD


@register_generator("custom_code")
class CustomCodeGenerator(PartGenerator):
    """自定义代码零件生成器"""
    part_type = "custom_code"

    def validate(self, params: Dict[str, Any]) -> None:
        code = params.get("code")
        if not code or not isinstance(code, str):
            raise ValidationError(self.part_type, "code", "必须包含非空 code 字符串")

    def draw(self, doc, params: Dict[str, Any]) -> None:
        code = params.get("code")
        msp = doc.modelspace()

        # Create a TurtleCAD instance
        t = TurtleCAD(msp)

        # 准备执行环境
        local_env = {
            "msp": msp,
            "doc": doc,
            "math": math,
            "t": t,
            "TurtleCAD": TurtleCAD,
            "abs": abs, "min": min, "max": max, "len": len, "range": range,
        }

        try:
            exec(code, {}, local_env)
            print("✅ Executed custom code with TurtleCAD support.")
        except Exception as e:
            print(f"❌ Error executing custom code: {e}")
            msp.add_text(f"Error: {str(e)}", height=5).set_pos((0, 0))

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        return {
            "code": {"type": "string", "description": "TurtleCAD Python 代码"},
        }
