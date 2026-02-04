# -*- coding: utf-8 -*-
"""
零件生成器模块
使用基于类的架构，支持装饰器注册
"""

from .basic import (
    PlateGenerator,
    BoltGenerator,
    NutGenerator,
    WasherGenerator,
    ScrewGenerator,
)
from .transmission import (
    GearGenerator,
    ShaftGenerator,
    SteppedShaftGenerator,
    SprocketGenerator,
    PulleyGenerator,
    CouplingGenerator,
)
from .support import (
    BearingGenerator,
    FlangeGenerator,
    BracketGenerator,
)
from .fastening import (
    SpringGenerator,
    SnapRingGenerator,
    RetainerGenerator,
)
from .structural import (
    ChassisFrameGenerator,
)
from .custom import (
    CustomCodeGenerator,
)

# 导出所有生成器类型
__all__ = [
    # 基础零件
    'PlateGenerator',
    'BoltGenerator',
    'NutGenerator',
    'WasherGenerator',
    'ScrewGenerator',
    # 传动零件
    'GearGenerator',
    'ShaftGenerator',
    'SteppedShaftGenerator',
    'SprocketGenerator',
    'PulleyGenerator',
    'CouplingGenerator',
    # 支撑零件
    'BearingGenerator',
    'FlangeGenerator',
    'BracketGenerator',
    # 紧固件
    'SpringGenerator',
    'SnapRingGenerator',
    'RetainerGenerator',
    # 结构件
    'ChassisFrameGenerator',
    # 自定义
    'CustomCodeGenerator',
]
