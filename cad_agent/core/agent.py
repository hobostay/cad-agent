# -*- coding: utf-8 -*-
"""
简化的Agent核心模块
将复杂流程拆分为可组合的组件
"""
import json
import os
from typing import Dict, Any, List, Tuple, Optional, Callable
from dataclasses import dataclass, field

from .config import Config
from .logger import get_logger
from .api_client import APIClient, create_client
from standard_parts_loader import StandardPartsLoader


@dataclass
class AgentResult:
    """Agent执行结果"""
    success: bool
    output_file: Optional[str] = None
    spec: Optional[Dict[str, Any]] = None
    reasoning: str = ""
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class AgentContext:
    """Agent执行上下文"""
    user_input: str
    attempt: int = 0
    feedback: Optional[str] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)
    detected_standard: Optional[Dict[str, Any]] = None


class StandardPartDetector:
    """标准件检测器"""

    def __init__(self):
        self.loader = StandardPartsLoader()
        self._bearing_index = self._build_bearing_index()
        self._bolt_index = self._build_fastener_index()

    def _build_bearing_index(self):
        data = self.loader.load_json("bearings.json")
        index = []
        for cat_data in data.get("categories", {}).values():
            for code, params in cat_data.get("parts", {}).items():
                index.append((code, params))
        # 长型号优先，避免短串误匹配
        index.sort(key=lambda x: len(x[0]), reverse=True)
        return index

    def _build_fastener_index(self):
        data = self.loader.load_json("bolts.json")
        index = {
            "bolt": [],
            "nut": [],
            "washer": [],
        }
        category_map = {
            "hex_bolt": "bolt",
            "hex_nut": "nut",
            "washer": "washer",
        }
        for cat_name, cat_data in data.get("categories", {}).items():
            part_type = category_map.get(cat_name)
            if not part_type:
                continue
            for code, params in cat_data.get("parts", {}).items():
                index[part_type].append((code, params))
        for key in index:
            index[key].sort(key=lambda x: len(x[0]), reverse=True)
        return index

    def detect(self, user_input: str) -> Optional[Dict[str, Any]]:
        """检测输入中的标准件"""
        if not user_input:
            return None

        user_input_upper = user_input.upper()

        # 1) 轴承检测（型号数字）
        for code, params in self._bearing_index:
            if code in user_input:
                return {
                    "type": "轴承",
                    "code": code,
                    "params": {
                        "inner_diameter": params.get("inner"),
                        "outer_diameter": params.get("outer"),
                        "width": params.get("width"),
                    },
                }

        # 2) 紧固件检测（M 系列）
        hint_type = None
        if "螺母" in user_input:
            hint_type = "nut"
        elif "垫圈" in user_input or "垫片" in user_input:
            hint_type = "washer"
        elif "螺栓" in user_input:
            hint_type = "bolt"

        fastener_order = [hint_type] if hint_type else ["bolt", "nut", "washer"]
        for part_type in fastener_order:
            for code, params in self._bolt_index.get(part_type, []):
                if code.upper() in user_input_upper:
                    return {
                        "type": "螺栓" if part_type == "bolt" else "螺母" if part_type == "nut" else "垫圈",
                        "code": code,
                        "params": params,
                    }
        return None


class SpecGenerator:
    """规格生成器 - 使用LLM生成零件规格"""

    # 系统提示词（保持原有的详细提示词）
    SYSTEM_PROMPT = """你是一个资深机械设计工程师（CAD Agent）。你的任务是根据用户的模糊需求，运用工程知识进行推理，选择合适的零件类型，并计算出具体的制造参数。

支持的零件类型及参数定义：

1. **底板 (type: "plate")**
   - 基础参数 (mm): length, width, thickness, hole_diameter, corner_offset
   - 倒角/倒圆: chamfer_size, fillet_radius
   - 腰形孔: slots 数组，每个包含 length, width, x, y, angle
   - 螺纹孔: threaded_holes 数组
   - 沉孔: counterbores 数组

2. **齿轮 (type: "gear")**
   - 参数 (mm): module, teeth, pressure_angle, bore_diameter, hub_diameter, hub_width

3. **轴承 (type: "bearing")**
   - 参数 (mm): inner_diameter, outer_diameter, width, ball_count

4. **螺栓 (type: "bolt")**
   - 参数 (mm): diameter, length, head_height

输出格式：严格的JSON
```json
{
  "type": "gear",
  "parameters": {
    "module": 2,
    "teeth": 20
  }
}
```

标准值参考：
- 齿轮模数：1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10
- 标准螺栓：M3, M4, M5, M6, M8, M10, M12, M16, M20
- 轴承系列：6200, 6204, 6208, 6300, 6308
"""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.logger = get_logger()

    def generate(
        self,
        context: AgentContext,
        temperature: float = 0.7
    ) -> Tuple[Dict[str, Any], str]:
        """
        生成零件规格

        Returns:
            (spec, reasoning)
        """
        user_message = f"用户需求：{context.user_input}\n"

        # 添加标准件信息
        if context.detected_standard:
            user_message += f"\n参考标准件：{context.detected_standard}"

        # 添加历史案例
        if context.examples:
            user_message += "\n参考历史案例：\n"
            for ex in context.examples[:3]:  # 最多3个
                user_message += f"- {ex.get('input', '')}: {json.dumps(ex.get('spec', {}), ensure_ascii=False)}\n"

        # 添加反馈
        if context.feedback:
            user_message += f"\n【重要】上一轮失败，反馈：{context.feedback}\n请修正参数。"

        try:
            content, model = self.api_client.chat_completion(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=user_message,
                temperature=temperature
            )

            spec, reasoning = self._parse_response(content)
            reasoning += f"\n(Model: {model})"
            return spec, reasoning

        except Exception as e:
            self.logger.error(f"LLM调用失败: {e}")
            raise

    def _parse_response(self, content: str) -> Tuple[Dict[str, Any], str]:
        """解析LLM响应"""
        import re

        content = content.strip()

        # 查找JSON块
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
        if m:
            json_str = m.group(1).strip()
            reasoning = content[:m.start()].strip()
        else:
            m = re.search(r"\{[\s\S]*\}", content)
            if m:
                json_str = m.group(0)
                reasoning = content[:m.start()].strip()
            else:
                raise ValueError(f"未找到JSON: {content[:200]}")

        spec = json.loads(json_str)
        return spec, reasoning


class PartGenerator:
    """零件生成器 - 调用gen_parts生成DXF"""

    def __init__(self):
        self.logger = get_logger()

    def generate(self, spec: Dict[str, Any], output_file: str) -> None:
        """生成零件DXF文件"""
        from gen_parts import generate_part
        generate_part(spec, output_file)
        self.logger.info(f"DXF文件已生成: {output_file}")


class PartValidator:
    """零件验证器 - 验证生成的DXF"""

    def __init__(self, enable_engineering: bool = True):
        self.logger = get_logger()
        self.enable_engineering = enable_engineering

    def validate(
        self,
        spec: Dict[str, Any],
        output_file: str
    ) -> Tuple[bool, str, List[str]]:
        """
        验证生成的零件

        Returns:
            (is_valid, message, warnings)
        """
        from validate_dxf import validate_dxf_file

        # DXF文件验证
        ok, msg = validate_dxf_file(output_file, "temp_spec.json")

        warnings = []
        if self.enable_engineering:
            # 工程验证
            from engineering_validation import validate_part_design
            part_type = spec.get("type", "plate")
            part_params = spec.get("parameters", spec)

            eng_valid, eng_msgs, eng_recs = validate_part_design(part_type, part_params)
            warnings.extend(eng_msgs)

            if eng_recs:
                for rec in eng_recs:
                    if "suggestion" in rec:
                        warnings.append(f"建议: {rec['suggestion']}")

            if not eng_valid:
                warnings.append("⚠️ 工程验证发现问题")

        return ok, msg, warnings


class MemoryManager:
    """记忆管理器 - 保存和加载历史案例"""

    def __init__(self, memory_file: str = "agent_memory.json"):
        self.memory_file = memory_file
        self.logger = get_logger()

    def load_examples(self, limit: int = 5) -> List[Dict[str, Any]]:
        """加载历史案例"""
        from memory import get_examples
        examples = get_examples(limit=limit)
        if examples:
            self.logger.debug(f"已加载 {len(examples)} 个历史案例")
        return examples

    def save_success(self, user_input: str, spec: Dict[str, Any]) -> None:
        """保存成功案例"""
        from memory import add_example
        add_example(user_input, spec)
        self.logger.debug("已保存成功案例")


class CADAgent:
    """
    CAD Agent - 主Agent类

    使用策略模式组合各个组件
    """

    def __init__(self, config: Optional[Config] = None):
        """
        初始化Agent

        Args:
            config: 配置对象，为None时自动加载
        """
        from .config import get_config

        self.config = config or get_config()
        self.logger = get_logger(config=self.config)

        # 创建组件
        self.api_client = create_client(self.config.api)
        self.spec_generator = SpecGenerator(self.api_client)
        self.part_generator = PartGenerator()
        self.part_validator = PartValidator(enable_engineering=True)
        self.memory_manager = MemoryManager(self.config.agent.memory_file)
        self.standard_detector = StandardPartDetector()

    def run(
        self,
        user_input: str,
        output_file: Optional[str] = None,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> AgentResult:
        """
        运行Agent

        Args:
            user_input: 用户输入
            output_file: 输出文件名
            status_callback: 状态回调函数

        Returns:
            AgentResult
        """
        if output_file is None:
            output_file = self.config.output.default_dxf

        # 创建上下文
        context = AgentContext(user_input=user_input)

        # 加载历史案例
        if self.config.agent.enable_memory:
            context.examples = self.memory_manager.load_examples()

        # 检测标准件
        if self.config.agent.enable_standard_parts:
            context.detected_standard = self.standard_detector.detect(user_input)
            if context.detected_standard:
                self.logger.info(f"检测到标准件: {context.detected_standard['code']}")

        # 主循环
        max_attempts = self.config.agent.max_iterations
        for context.attempt in range(1, max_attempts + 1):
            self.logger.step(context.attempt, max_attempts, f"尝试生成")

            try:
                # 生成规格
                self.logger.progress("调用LLM生成设计...")
                spec, reasoning = self.spec_generator.generate(context)

                if self.config.agent.verbose:
                    self.logger.result(f"设计推理:\n{reasoning}")
                    self.logger.result(f"规格参数:\n{json.dumps(spec, indent=2, ensure_ascii=False)}")

                # 保存临时spec
                with open("temp_spec.json", "w", encoding="utf-8") as f:
                    json.dump(spec, f, indent=2, ensure_ascii=False)

                # 生成零件
                self.logger.progress("生成CAD图纸...")
                self.part_generator.generate(spec, output_file)

                # 验证
                if self.config.agent.enable_validation:
                    self.logger.progress("验证图纸...")
                    is_valid, msg, warnings = self.part_validator.validate(spec, output_file)

                    for warning in warnings:
                        self.logger.warning(warning)

                    if is_valid:
                        self.logger.success(f"验证通过: {msg}")
                    else:
                        self.logger.warning(f"验证失败: {msg}")
                        context.feedback = f"验证失败: {msg}"
                        continue

                # 保存到记忆
                if self.config.agent.enable_memory:
                    self.memory_manager.save_success(user_input, spec)

                self.logger.success("设计完成！")

                return AgentResult(
                    success=True,
                    output_file=output_file,
                    spec=spec,
                    reasoning=reasoning
                )

            except ValueError as e:
                # 参数校验失败
                self.logger.warning(f"参数校验失败: {e}")
                context.feedback = f"参数校验失败: {str(e)}"
                continue

            except Exception as e:
                # 其他错误
                self.logger.error(f"生成失败: {e}")
                return AgentResult(
                    success=False,
                    error=str(e)
                )

        return AgentResult(
            success=False,
            error="已达到最大重试次数"
        )


# 便捷函数
def run_agent(
    user_input: str,
    config: Optional[Config] = None,
    output_file: Optional[str] = None
) -> AgentResult:
    """
    运行CAD Agent（便捷函数）

    Args:
        user_input: 用户输入
        config: 配置对象
        output_file: 输出文件名

    Returns:
        AgentResult
    """
    agent = CADAgent(config)
    return agent.run(user_input, output_file)
