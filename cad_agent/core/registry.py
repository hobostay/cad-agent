# -*- coding: utf-8 -*-
"""
零件生成器注册机制
使用装饰器模式自动注册生成器类
"""
from typing import Dict, Type, List, Optional, TypeVar
from .base import PartGenerator
from .exceptions import RegistrationError

T = TypeVar('T', bound=PartGenerator)


class GeneratorRegistry:
    """生成器注册表（单例模式）"""

    _instance: Optional['GeneratorRegistry'] = None
    _generators: Dict[str, Type[PartGenerator]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, part_type: str, generator_class: Type[PartGenerator]) -> None:
        """注册生成器"""
        if part_type in cls._generators:
            raise RegistrationError(
                part_type,
                f"类型 '{part_type}' 已被 {cls._generators[part_type].__name__} 注册"
            )
        cls._generators[part_type] = generator_class

    @classmethod
    def get(cls, part_type: str) -> Optional[Type[PartGenerator]]:
        """获取生成器类"""
        return cls._generators.get(part_type)

    @classmethod
    def list_types(cls) -> List[str]:
        """列出所有已注册的零件类型"""
        return sorted(cls._generators.keys())

    @classmethod
    def create_instance(cls, part_type: str) -> PartGenerator:
        """创建生成器实例"""
        generator_class = cls.get(part_type)
        if generator_class is None:
            raise RegistrationError(part_type, f"未找到类型 '{part_type}' 的生成器")
        return generator_class()

    @classmethod
    def clear(cls) -> None:
        """清空注册表（主要用于测试）"""
        cls._generators.clear()


def register_generator(part_type: str = None):
    """
    生成器注册装饰器

    用法:
        @register_generator("plate")
        class PlateGenerator(PartGenerator):
            part_type = "plate"
            ...
    """
    def decorator(generator_class: Type[T]) -> Type[T]:
        # 从类属性获取类型，或使用装饰器参数
        pt = part_type or getattr(generator_class, 'part_type', None)
        if not pt:
            raise RegistrationError(
                generator_class.__name__,
                "必须指定 part_type 类属性或装饰器参数"
            )
        GeneratorRegistry.register(pt, generator_class)
        return generator_class

    return decorator


def get_generator(part_type: str) -> Optional[Type[PartGenerator]]:
    """获取指定类型的生成器类"""
    return GeneratorRegistry.get(part_type)


def list_generators() -> List[str]:
    """列出所有已注册的零件类型"""
    return GeneratorRegistry.list_types()


def get_all_generators() -> Dict[str, Type[PartGenerator]]:
    """获取所有已注册的生成器"""
    return GeneratorRegistry._generators.copy()


# 便捷函数
def create_generator(part_type: str) -> PartGenerator:
    """创建生成器实例"""
    return GeneratorRegistry.create_instance(part_type)
