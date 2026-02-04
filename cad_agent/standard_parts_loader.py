# -*- coding: utf-8 -*-
"""
标准件库加载器
支持从 JSON 文件加载标准件数据，支持热重载和用户自定义目录
"""
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from core.exceptions import StandardPartNotFoundError


class StandardPartsLoader:
    """标准件库加载器（单例模式）"""

    _instance: Optional['StandardPartsLoader'] = None
    _cache: Dict[str, Any] = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, custom_dirs: List[str] = None, enable_cache: bool = True):
        """
        初始化加载器

        Args:
            custom_dirs: 用户自定义目录列表
            enable_cache: 是否启用缓存
        """
        if not hasattr(self, '_initialized'):
            self.base_dir = os.path.join(os.path.dirname(__file__), 'standard_parts')
            self.custom_dirs = custom_dirs or []
            self.enable_cache = enable_cache
            self._search_paths = self._build_search_paths()
            self._initialized = True

    def _build_search_paths(self) -> List[Path]:
        """构建文件搜索路径"""
        paths = [Path(self.base_dir)]
        for custom_dir in self.custom_dirs:
            if os.path.exists(custom_dir):
                paths.append(Path(custom_dir))
        return paths

    def add_custom_dir(self, dir_path: str) -> None:
        """添加用户自定义目录"""
        if os.path.exists(dir_path):
            self.custom_dirs.append(dir_path)
            self._search_paths = self._build_search_paths()
            # 清空缓存以重新加载
            if self.enable_cache:
                self._cache.clear()

    def reload(self) -> None:
        """重新加载所有数据"""
        self._cache.clear()
        self._search_paths = self._build_search_paths()

    def _find_file(self, filename: str) -> Optional[Path]:
        """在搜索路径中查找文件"""
        for search_path in self._search_paths:
            file_path = search_path / filename
            if file_path.exists():
                return file_path
        return None

    def load_json(self, filename: str) -> Dict[str, Any]:
        """
        加载 JSON 文件

        Args:
            filename: 文件名（如 bearings.json）

        Returns:
            JSON 数据字典

        Raises:
            FileNotFoundError: 文件未找到
            json.JSONDecodeError: JSON 解析失败
        """
        # 检查缓存
        if self.enable_cache and filename in self._cache:
            return self._cache[filename]

        # 查找文件
        file_path = self._find_file(filename)
        if file_path is None:
            raise FileNotFoundError(f"未找到文件: {filename}")

        # 加载数据
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 缓存
        if self.enable_cache:
            self._cache[filename] = data

        return data

    def query_bearing(self, code: str, category: str = None) -> Dict[str, Any]:
        """
        查询轴承标准件

        Args:
            code: 轴承型号（如 6208）
            category: 类别（如 62_series），为空时自动查找

        Returns:
            轴承参数字典

        Raises:
            StandardPartNotFoundError: 未找到对应轴承
        """
        data = self.load_json('bearings.json')

        if category:
            if category in data['categories']:
                if code in data['categories'][category]['parts']:
                    return {
                        'type': 'bearing',
                        'code': code,
                        'category': category,
                        'params': data['categories'][category]['parts'][code]
                    }
        else:
            # 自动查找
            for cat_name, cat_data in data['categories'].items():
                if code in cat_data['parts']:
                    return {
                        'type': 'bearing',
                        'code': code,
                        'category': cat_name,
                        'params': cat_data['parts'][code]
                    }

        raise StandardPartNotFoundError('bearing', code)

    def query_bolt(self, code: str, category: str = None) -> Dict[str, Any]:
        """查询螺栓标准件"""
        data = self.load_json('bolts.json')

        if category:
            if category in data['categories']:
                if code in data['categories'][category]['parts']:
                    return {
                        'type': 'bolt' if 'bolt' in category else 'nut' if 'nut' in category else 'washer',
                        'code': code,
                        'category': category,
                        'params': data['categories'][category]['parts'][code]
                    }
        else:
            for cat_name, cat_data in data['categories'].items():
                if code in cat_data['parts']:
                    return {
                        'type': 'bolt' if 'bolt' in cat_name else 'nut' if 'nut' in cat_name else 'washer',
                        'code': code,
                        'category': cat_name,
                        'params': cat_data['parts'][code]
                    }

        raise StandardPartNotFoundError('fastener', code)

    def get_gear_modules(self) -> List[float]:
        """获取标准模数列表"""
        data = self.load_json('gears.json')
        return data['modules']['standard']['values']

    def get_gear_pressure_angles(self) -> List[float]:
        """获取标准压力角列表"""
        data = self.load_json('gears.json')
        return data['pressure_angles']['standard']['values']

    def get_material(self, code: str) -> Dict[str, Any]:
        """
        查询材料信息

        Args:
            code: 材料代号（如 45, 40Cr, Q235）

        Returns:
            材料信息字典

        Raises:
            StandardPartNotFoundError: 未找到对应材料
        """
        data = self.load_json('materials.json')

        for cat_name, cat_data in data['categories'].items():
            if code in cat_data['materials']:
                material = cat_data['materials'][code].copy()
                material['category'] = cat_name
                material['code'] = code
                return material

        raise StandardPartNotFoundError('material', code)

    def get_materials_by_application(self, application: str) -> List[Dict[str, Any]]:
        """
        根据应用场景获取推荐材料

        Args:
            application: 应用场景（如 high_load, corrosion, general）

        Returns:
            材料推荐列表
        """
        data = self.load_json('materials.json')
        guide = data.get('selection_guide', {}).get('by_application', {})

        codes = guide.get(application, [])
        materials = []
        for code in codes:
            try:
                materials.append(self.get_material(code))
            except StandardPartNotFoundError:
                pass

        return materials

    def get_materials_by_part_type(self, part_type: str) -> List[Dict[str, Any]]:
        """
        根据零件类型获取推荐材料

        Args:
            part_type: 零件类型（如 gear, shaft, spring）

        Returns:
            材料推荐列表
        """
        data = self.load_json('materials.json')
        guide = data.get('selection_guide', {}).get('by_part_type', {})

        codes = guide.get(part_type, [])
        materials = []
        for code in codes:
            try:
                materials.append(self.get_material(code))
            except StandardPartNotFoundError:
                pass

        return materials

    def list_all_bearings(self) -> Dict[str, List[str]]:
        """列出所有轴承型号（按类别分组）"""
        data = self.load_json('bearings.json')
        result = {}
        for cat_name, cat_data in data['categories'].items():
            result[cat_name] = list(cat_data['parts'].keys())
        return result

    def list_all_bolts(self) -> Dict[str, List[str]]:
        """列出所有紧固件型号（按类别分组）"""
        data = self.load_json('bolts.json')
        result = {}
        for cat_name, cat_data in data['categories'].items():
            result[cat_name] = list(cat_data['parts'].keys())
        return result

    def list_all_materials(self) -> Dict[str, List[str]]:
        """列出所有材料（按类别分组）"""
        data = self.load_json('materials.json')
        result = {}
        for cat_name, cat_data in data['categories'].items():
            result[cat_name] = list(cat_data['materials'].keys())
        return result

    def detect_standard_part(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        从用户输入中检测标准件

        Args:
            user_input: 用户输入文本

        Returns:
            检测到的标准件信息，未检测到返回 None
        """
        import re

        # 检测轴承 (如 6208, 6300)
        bearing_pattern = r'\b(618|619|60|62|63)\d{2}\b'
        bearings = re.findall(bearing_pattern, user_input, re.IGNORECASE)
        if bearings:
            bearing_code = bearings[0].upper()
            if len(bearing_code) == 4:
                bearing_code = bearing_code[:2] + '0' + bearing_code[2:]
            try:
                return self.query_bearing(bearing_code)
            except StandardPartNotFoundError:
                pass

        # 检测螺栓 (如 M6, M10, M20)
        bolt_pattern = r'\bM(\d+(?:\.\d+)?)\b'
        bolts = re.findall(bolt_pattern, user_input, re.IGNORECASE)
        if bolts:
            bolt_code = 'M' + bolts[0]
            try:
                return self.query_bolt(bolt_code)
            except StandardPartNotFoundError:
                pass

        return None


# 全局单例实例
_loader_instance: Optional[StandardPartsLoader] = None


def get_loader(custom_dirs: List[str] = None, reload: bool = False) -> StandardPartsLoader:
    """
    获取标准件加载器实例

    Args:
        custom_dirs: 自定义目录列表
        reload: 是否重新加载

    Returns:
        StandardPartsLoader 实例
    """
    global _loader_instance

    if _loader_instance is None or reload:
        _loader_instance = StandardPartsLoader(custom_dirs=custom_dirs)

    return _loader_instance


# 便捷函数
def query_bearing(code: str, category: str = None) -> Dict[str, Any]:
    """查询轴承标准件"""
    return get_loader().query_bearing(code, category)


def query_bolt(code: str, category: str = None) -> Dict[str, Any]:
    """查询螺栓标准件"""
    return get_loader().query_bolt(code, category)


def get_material(code: str) -> Dict[str, Any]:
    """查询材料信息"""
    return get_loader().get_material(code)


def detect_standard_part(user_input: str) -> Optional[Dict[str, Any]]:
    """从用户输入中检测标准件"""
    return get_loader().detect_standard_part(user_input)


if __name__ == "__main__":
    # 测试
    loader = get_loader()

    print("=== 轴承查询 ===")
    bearing = loader.query_bearing("6208")
    print(f"6208轴承: {bearing}")

    print("\n=== 螺栓查询 ===")
    bolt = loader.query_bolt("M10")
    print(f"M10螺栓: {bolt}")

    print("\n=== 材料查询 ===")
    material = loader.get_material("45")
    print(f"45号钢: {material['name']}")
    print(f"抗拉强度: {material['tensile_strength']} MPa")

    print("\n=== 标准件检测 ===")
    test_input = "我需要一个6208轴承和M10螺栓"
    detected = loader.detect_standard_part(test_input)
    print(f"检测到: {detected}")

    print("\n=== 齿轮参数 ===")
    print(f"标准模数: {loader.get_gear_modules()}")
    print(f"标准压力角: {loader.get_gear_pressure_angles()}")
