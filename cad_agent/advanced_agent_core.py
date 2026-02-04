# -*- coding: utf-8 -*-
"""
高级 CAD Agent 核心模块
支持：
1. 多步骤任务规划
2. 装配体生成
3. 复杂工程推理
4. 标准件库查询
"""
import json
import os
import sys
import time
from typing import List, Dict, Any, Tuple

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gen_parts import generate_part
from validate_dxf import validate_dxf_file
from nl_to_spec_llm import parse_with_llm
from memory import get_examples, add_example
from engineering_validation import validate_part_design, recommend_material
from standard_parts_loader import StandardPartsLoader
from core.agent import StandardPartDetector

MAX_RETRIES = 3
OUTPUT_DXF = "agent_output.dxf"
TEMP_SPEC_JSON = "agent_spec.json"

_standard_loader = StandardPartsLoader()
_standard_detector = StandardPartDetector()


def query_standard_part(part_type: str, part_code: str) -> Dict[str, Any]:
    """查询标准件库"""
    if part_type == "轴承":
        try:
            part = _standard_loader.query_bearing(part_code)
            params = part.get("params", {})
            return {
                "inner_diameter": params.get("inner"),
                "outer_diameter": params.get("outer"),
                "width": params.get("width"),
            }
        except Exception:
            return None
    if part_type in ("螺栓", "螺母", "垫圈"):
        try:
            part = _standard_loader.query_bolt(part_code)
            return part.get("params", {})
        except Exception:
            return None
    return None


def run_advanced_agent(
    user_input: str,
    api_key: str = None,
    base_url: str = None,
    model: str = None,
    verbose: bool = True,
    status_callback: callable = None
) -> Tuple[bool, str, str]:
    """
    运行高级 CAD Agent 循环：

    1. 任务分析 - 识别零件类型和复杂度
    2. 标准件查询 - 检查是否为标准件
    3. 设计推理 - 应用工程知识
    4. 参数生成 - 计算具体参数
    5. 图纸生成 - 生成 DXF
    6. 工程验收 - 验证图纸质量
    7. 记忆存储 - 保存成功案例

    返回: (success, result, reasoning)
    """

    feedback = None

    def log(msg):
        if verbose:
            print(msg)
        if status_callback:
            status_callback(msg)

    # 获取历史成功案例
    examples = get_examples(limit=5)
    if examples:
        log(f"📚 已加载 {len(examples)} 个历史案例")

    # ============== 步骤1: 任务分析 ==============
    log("\n🔍 步骤 1: 分析用户需求...")
    log(f"   输入: {user_input}")

    # ============== 步骤2: 标准件查询 ==============
    log("\n📖 步骤 2: 查询标准件库...")
    detected_standard = None

    # 标准件检测（使用标准件库）
    detected_standard = _standard_detector.detect(user_input)
    if detected_standard:
        log(f"   ✅ 检测到标准件: {detected_standard['type']} {detected_standard['code']}")

    if not detected_standard:
        log("   ℹ️  未检测到标准件，使用自定义设计")

    # ============== 步骤 3-6: LLM 解析与生成循环 ==============
    for attempt in range(MAX_RETRIES):
        log(f"\n🔄 尝试 {attempt + 1}/{MAX_RETRIES}...")

        try:
            # 步骤 3: LLM 解析
            log("   🧠 调用 AI 进行设计推理...")

            # 如果检测到标准件，将其信息加入 prompt
            enhanced_input = user_input
            if detected_standard:
                enhanced_input += f"\n\n参考标准件参数：{detected_standard}"

            spec, reasoning = parse_with_llm(
                enhanced_input,
                api_key,
                base_url,
                model,
                feedback=feedback,
                examples=examples
            )

            if verbose:
                print(f"\n📋 设计推理:\n{reasoning}\n")
                print(f"📐 生成的参数:\n{json.dumps(spec, indent=2, ensure_ascii=False)}\n")

            # 保存 spec 到文件
            with open(TEMP_SPEC_JSON, "w", encoding="utf-8") as f:
                json.dump(spec, f, indent=2, ensure_ascii=False)

        except Exception as e:
            msg = f"❌ LLM 调用失败: {e}"
            log(msg)
            return False, f"LLM calling failed: {str(e)}", ""

        try:
            # 步骤 4: 图纸生成
            log("   ✏️  生成 CAD 图纸...")
            generate_part(spec, OUTPUT_DXF)
            log("   ✅ DXF 文件已生成")

        except ValueError as e:
            # 参数校验失败
            error_msg = str(e)
            log(f"   ⚠️  参数校验失败: {error_msg}")
            feedback = f"参数校验失败: {error_msg}\n请检查参数是否符合工程规范。"
            continue

        except Exception as e:
            msg = f"❌ 生成过程出错: {e}"
            log(msg)
            return False, f"Generation failed: {str(e)}", reasoning

        try:
            # 步骤 5: 工程验收 - DXF 文件验证
            log("   🔍 进行工程验收...")
            ok, msg = validate_dxf_file(OUTPUT_DXF, TEMP_SPEC_JSON)

            if ok:
                log(f"   ✅ DXF 验收通过: {msg}")

            # 步骤 5.5: 工程验证 - 工程合理性检查
            log("   🔧 进行工程合理性验证...")
            part_type = spec.get("type", "plate")
            part_params = spec.get("parameters", spec)

            eng_valid, eng_msgs, eng_recs = validate_part_design(part_type, part_params)

            for eng_msg in eng_msgs:
                log(f"   {eng_msg}")

            if eng_recs:
                log("   💡 工程建议:")
                for rec in eng_recs:
                    if "suggestion" in rec:
                        log(f"      • {rec['suggestion']}")

            # 工程验证失败不阻止流程，只给出警告
            if not eng_valid:
                log("   ⚠️  工程验证发现问题，但继续生成图纸")

            if ok:
                # 步骤 6: 保存到记忆
                log("   💾 保存成功案例到记忆库...")
                add_example(user_input, spec)

                return True, OUTPUT_DXF, reasoning

            else:
                log(f"   ⚠️  DXF 验收失败: {msg}")
                feedback = f"工程验收失败: {msg}\n请修正参数。"
                time.sleep(1)  # API 限流

        except Exception as e:
            log(f"   ⚠️  验收过程出错: {e}")
            feedback = f"验收出错: {str(e)}"

    return False, "❌ 已达到最大重试次数。请更具体地描述您的需求。", ""


def generate_assembly(
    parts: List[Dict[str, Any]],
    output_file: str = "assembly.dxf",
    verbose: bool = True
) -> Tuple[bool, str]:
    """
    生成装配体（多个零件组合）

    Args:
        parts: 零件列表，格式: [{"type": "gear", "parameters": {...}, "position": (x, y)}, ...]
        output_file: 输出文件名
        verbose: 是否打印详细信息

    Returns:
        (success, message)
    """
    import ezdxf
    from ezdxf import units

    def log(msg):
        if verbose:
            print(msg)

    log(f"\n🔧 开始生成装配体，包含 {len(parts)} 个零件...")

    try:
        # 创建新 DXF
        doc = ezdxf.new("R2010", setup=True)
        doc.units = units.MM

        # 设置图层
        doc.layers.add("outline", color=7)
        doc.layers.add("hole", color=2)
        doc.layers.add("center", color=1)
        doc.layers.add("thread", color=3)

        msp = doc.modelspace()

        # 为每个零件生成图纸
        for i, part_spec in enumerate(parts):
            part_type = part_spec.get("type", "plate")
            part_params = part_spec.get("parameters", {})
            part_pos = part_spec.get("position", (0, 0))

            log(f"\n   零件 {i+1}: {part_type}")
            log(f"      位置: {part_pos}")

            # 生成临时 DXF
            temp_dxf = f"temp_part_{i}.dxf"
            temp_spec = {"type": part_type, "parameters": part_params}

            try:
                generate_part(temp_spec, temp_dxf)

                # 读取临时 DXF 并复制到主文件
                temp_doc = ezdxf.readfile(temp_dxf)
                temp_msp = temp_doc.modelspace()

                # 偏移所有实体
                x_offset, y_offset = part_pos
                for entity in temp_msp:
                    # 复制实体到主文件
                    new_entity = entity.copy()
                    # 移动实体
                    if hasattr(new_entity, 'move'):
                        new_entity.move(x_offset, y_offset)
                    msp.add_entity(new_entity)

                # 删除临时文件
                import os
                os.remove(temp_dxf)

                log(f"      ✅ 已添加")

            except Exception as e:
                log(f"      ⚠️  跳过（出错）: {e}")
                continue

        # 保存装配体
        doc.saveas(output_file)
        log(f"\n✅ 装配体已生成: {output_file}")

        return True, output_file

    except Exception as e:
        log(f"\n❌ 生成装配体失败: {e}")
        return False, str(e)


if __name__ == "__main__":
    # 测试高级 Agent
    import sys

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = input("请描述您需要的机械零件: ")

    success, result, reasoning = run_advanced_agent(prompt)

    if success:
        print(f"\n" + "="*60)
        print(f"✅ 成功生成图纸: {result}")
        print(f"="*60)
    else:
        print(f"\n" + "="*60)
        print(f"❌ 生成失败: {result}")
        print(f"="*60)
