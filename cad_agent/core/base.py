# -*- coding: utf-8 -*-
"""
零件生成器基类
定义生成器的统一接口和规范
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, TYPE_CHECKING
import ezdxf
from ezdxf import units

# 类型注解避免循环导入
if TYPE_CHECKING:
    import ezdxf


@dataclass
class PartSpec:
    """零件规格数据类"""
    type: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（兼容旧格式）"""
        return {
            "type": self.type,
            "parameters": self.parameters,
            **self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PartSpec':
        """从字典创建（兼容旧格式）"""
        part_type = data.get("type", "plate")
        parameters = data.get("parameters", data) if "type" in data else data
        metadata = {k: v for k, v in data.items() if k not in ["type", "parameters"]}
        return cls(type=part_type, parameters=parameters, metadata=metadata)


class PartGenerator(ABC):
    """
    零件生成器基类

    所有零件生成器必须继承此类并实现:
    - part_type: 零件类型标识符
    - validate(): 参数验证
    - draw(): 绘制图纸
    """

    # 子类必须定义
    part_type: str = None

    # 可选配置
    dxf_version: str = "R2010"
    default_units: int = units.MM

    # 图层配置（子类可覆盖）
    layer_config: Dict[str, int] = None

    def __init__(self):
        if self.part_type is None:
            raise ValueError(f"{self.__class__.__name__} 必须定义 part_type 属性")
        if self.layer_config is None:
            self.layer_config = {
                "outline": 7,  # 白色/黑色
                "hole": 2,     # 黄色
                "thread": 3,   # 绿色
                "center": 1,   # 红色
                "dimension": 4,  # 青色
                "hatch": 5,    # 蓝色
            }

    @abstractmethod
    def validate(self, params: Dict[str, Any]) -> None:
        """
        验证零件参数

        Raises:
            ValidationError: 参数验证失败
        """
        pass

    @abstractmethod
    def draw(self, doc: Any, params: Dict[str, Any]) -> None:
        """
        绘制零件图纸

        Args:
            doc: ezdxf 文档对象
            params: 零件参数
        """
        pass

    def setup_dxf(self) -> Any:
        """
        创建并配置 DXF 文档

        Returns:
            配置好的 ezdxf.Document 对象
        """
        doc = ezdxf.new(self.dxf_version, setup=True)
        doc.units = self.default_units

        # 设置图层
        for layer_name, color in self.layer_config.items():
            if layer_name not in doc.layers:
                doc.layers.add(layer_name, color=color)

        return doc

    def generate(self, params: Dict[str, Any], output_file: str) -> Any:
        """
        生成零件 DXF 文件

        Args:
            params: 零件参数
            output_file: 输出文件路径

        Returns:
            生成的 ezdxf.Document 对象

        Raises:
            ValidationError: 参数验证失败
            GenerationError: 生成过程出错
        """
        from .exceptions import GenerationError

        # 验证参数
        try:
            self.validate(params)
        except Exception as e:
            from .exceptions import ValidationError
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(self.part_type, "unknown", str(e))

        # 创建 DXF 文档
        doc = self.setup_dxf()

        # 绘制零件
        try:
            self.draw(doc, params)
        except Exception as e:
            raise GenerationError(self.part_type, str(e))

        # 保存文件
        try:
            doc.saveas(output_file)
        except Exception as e:
            raise GenerationError(self.part_type, f"保存文件失败: {str(e)}")

        return doc

    @classmethod
    def get_description(cls) -> str:
        """获取零件类型描述（子类可覆盖）"""
        return cls.__doc__ or f"{cls.part_type} 零件生成器"

    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        """
        获取参数模式（用于前端表单生成）

        返回格式:
            {
                "length": {"type": "float", "min": 0, "description": "长度"},
                "width": {"type": "float", "min": 0, "description": "宽度"},
                ...
            }
        """
        return {}

    def _get_layer(self, doc: Any, layer_name: str) -> str:
        """获取图层名（带安全检查）"""
        if layer_name in doc.layers:
            return layer_name
        return "0"  # 默认图层


class CompoundPartGenerator(PartGenerator):
    """
    复合零件生成器基类
    用于需要组合多个子零件的情况（如装配体）
    """

    def generate_assembly(
        self,
        parts: List[Dict[str, Any]],
        output_file: str,
        verbose: bool = True
    ) -> Any:
        """
        生成装配体

        Args:
            parts: 零件列表，格式:
                [{"type": "gear", "parameters": {...}, "position": (x, y)}, ...]
            output_file: 输出文件路径
            verbose: 是否打印详细信息

        Returns:
            生成的 ezdxf.Document 对象
        """
        from .registry import create_generator
        from .exceptions import GenerationError

        doc = self.setup_dxf()
        msp = doc.modelspace()

        if verbose:
            print(f"\n🔧 开始生成装配体，包含 {len(parts)} 个零件...")

        for i, part_spec in enumerate(parts):
            part_type = part_spec.get("type", "plate")
            part_params = part_spec.get("parameters", {})
            part_pos = part_spec.get("position", (0, 0))

            if verbose:
                print(f"\n   零件 {i+1}: {part_type}")
                print(f"      位置: {part_pos}")

            try:
                # 创建临时 DXF
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as f:
                    temp_dxf = f.name

                generator = create_generator(part_type)
                generator.generate(part_params, temp_dxf)

                # 读取并合并到主文件
                temp_doc = ezdxf.readfile(temp_dxf)
                temp_msp = temp_doc.modelspace()

                # 偏移所有实体
                x_offset, y_offset = part_pos
                for entity in temp_msp:
                    new_entity = entity.copy()
                    if hasattr(new_entity, 'move'):
                        new_entity.move(x_offset, y_offset)
                    msp.add_entity(new_entity)

                # 删除临时文件
                os.remove(temp_dxf)

                if verbose:
                    print(f"      ✅ 已添加")

            except Exception as e:
                if verbose:
                    print(f"      ⚠️  跳过（出错）: {e}")
                continue

        # 保存装配体
        doc.saveas(output_file)
        if verbose:
            print(f"\n✅ 装配体已生成: {output_file}")

        return doc
