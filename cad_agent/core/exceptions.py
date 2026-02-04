# -*- coding: utf-8 -*-
"""
CAD Agent 自定义异常类
"""


class CADAgentError(Exception):
    """CAD Agent 基础异常类"""
    pass


class ValidationError(CADAgentError):
    """参数验证失败异常"""

    def __init__(self, part_type: str, param_name: str, message: str):
        self.part_type = part_type
        self.param_name = param_name
        self.message = message
        super().__init__(f"[{part_type}] {param_name}: {message}")


class GenerationError(CADAgentError):
    """图纸生成失败异常"""

    def __init__(self, part_type: str, message: str):
        self.part_type = part_type
        self.message = message
        super().__init__(f"[{part_type}] 生成失败: {message}")


class RegistrationError(CADAgentError):
    """生成器注册异常"""

    def __init__(self, part_type: str, message: str):
        self.part_type = part_type
        self.message = message
        super().__init__(f"[{part_type}] 注册失败: {message}")


class StandardPartNotFoundError(CADAgentError):
    """标准件未找到异常"""

    def __init__(self, part_type: str, code: str):
        self.part_type = part_type
        self.code = code
        super().__init__(f"未找到标准件: {part_type} {code}")


class LLMError(CADAgentError):
    """LLM 调用失败异常"""

    def __init__(self, message: str, model: str = None, retry_count: int = 0):
        self.message = message
        self.model = model
        self.retry_count = retry_count
        detail = f" [{model}]" if model else ""
        retry_detail = f" (已重试 {retry_count} 次)" if retry_count > 0 else ""
        super().__init__(f"LLM 调用失败{detail}: {message}{retry_detail}")


class InterferenceError(CADAgentError):
    """装配干涉检查异常"""

    def __init__(self, part1: str, part2: str, interference_type: str):
        self.part1 = part1
        self.part2 = part2
        self.interference_type = interference_type
        super().__init__(f"干涉检测: {part1} 与 {part2} 存在 {interference_type} 干涉")
