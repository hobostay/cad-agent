# -*- coding: utf-8 -*-
"""
零件生成器模块
包含各种类型的零件生成器
"""

# 导入所有生成器（自动注册）
from .plate import PlateGenerator
from .gear import GearGenerator
from .bearing import BearingGenerator
from .bolt import BoltGenerator
from .screw import ScrewGenerator
from .nut import NutGenerator
from .washer import WasherGenerator
from .spring import SpringGenerator
from .flange import FlangeGenerator
from .shaft import ShaftGenerator
from .stepped_shaft import SteppedShaftGenerator
from .coupling import CouplingGenerator
from .pulley import PulleyGenerator
from .sprocket import SprocketGenerator
from .snap_ring import SnapRingGenerator
from .retainer import RetainerGenerator
from .chassis_frame import ChassisFrameGenerator
from .bracket import BracketGenerator
from .custom_code import CustomCodeGenerator

__all__ = [
    'PlateGenerator',
    'GearGenerator',
    'BearingGenerator',
    'BoltGenerator',
    'ScrewGenerator',
    'NutGenerator',
    'WasherGenerator',
    'SpringGenerator',
    'FlangeGenerator',
    'ShaftGenerator',
    'SteppedShaftGenerator',
    'CouplingGenerator',
    'PulleyGenerator',
    'SprocketGenerator',
    'SnapRingGenerator',
    'RetainerGenerator',
    'ChassisFrameGenerator',
    'BracketGenerator',
    'CustomCodeGenerator',
]

# 确保导入时自动注册
import sys
import os
sys.path.append(os.path.dirname(__file__))
