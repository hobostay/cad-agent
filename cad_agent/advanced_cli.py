#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级 CAD Agent CLI
支持复杂零件设计、装配体生成、标准件查询
"""
import sys
import os
import argparse
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_agent_core import generate_assembly
from core.agent import run_agent
from core.config import get_config
from standard_parts_loader import StandardPartsLoader


def print_logo():
    logo = """
╔══════════════════════════════════════════════════════════╗
║                                                            ║
║         🤖 Advanced CAD Agent - 高级机械设计 AI           ║
║                                                            ║
║   支持零件: 底板|齿轮|轴承|法兰|车架|支架|螺栓|螺母|弹簧  ║
║            |轴|联轴器|皮带轮|链轮|卡簧|垫圈|挡圈|自定义  ║
║                                                            ║
╚══════════════════════════════════════════════════════════╝
"""
    print(logo)


def print_standard_parts():
    """打印标准件库"""
    print("\n📖 标准件库:")
    print("=" * 60)

    loader = StandardPartsLoader()

    # 轴承
    bearings = loader.load_json("bearings.json")
    print("\n轴承:")
    for cat_name, cat_data in bearings.get("categories", {}).items():
        print(f"  {cat_data.get('name', cat_name)}:")
        for code, params in cat_data.get("parts", {}).items():
            print(f"    {code}: {params}")

    # 螺栓/螺母/垫圈
    bolts = loader.load_json("bolts.json")
    print("\n紧固件:")
    for cat_name, cat_data in bolts.get("categories", {}).items():
        print(f"  {cat_data.get('name', cat_name)}:")
        for code, params in cat_data.get("parts", {}).items():
            print(f"    {code}: {params}")

    # 齿轮模数
    gears = loader.load_json("gears.json")
    modules = gears.get("modules", {}).get("standard", {}).get("values", [])
    if modules:
        print("\n齿轮模数:")
        print(f"  标准系列: {modules}")

    print("=" * 60)


def run_cli():
    print_logo()

    parser = argparse.ArgumentParser(
        description="高级 CAD Agent - 自动生成机械零件图纸",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "prompt",
        nargs="*",
        help="零件描述（自然语言）"
    )

    parser.add_argument(
        "--standard",
        action="store_true",
        help="显示标准件库"
    )

    parser.add_argument(
        "--assembly",
        type=str,
        metavar="JSON_FILE",
        help="生成装配体（从 JSON 文件读取）"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API 密钥"
    )

    parser.add_argument(
        "--base-url",
        type=str,
        help="API 基础 URL"
    )

    parser.add_argument(
        "--model",
        type=str,
        help="模型名称"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="agent_output.dxf",
        help="输出 DXF 文件名（默认: agent_output.dxf）"
    )

    args = parser.parse_args()

    # 显示标准件库
    if args.standard:
        print_standard_parts()
        return

    # 生成装配体
    if args.assembly:
        print(f"\n📋 从 {args.assembly} 读取装配体配置...")

        try:
            with open(args.assembly, "r", encoding="utf-8") as f:
                assembly_config = json.load(f)

            parts = assembly_config.get("parts", [])
            output = assembly_config.get("output", args.output)

            print(f"   零件数量: {len(parts)}")
            print(f"   输出文件: {output}")

            success, result = generate_assembly(
                parts=parts,
                output_file=output,
                verbose=True
            )

            if success:
                print(f"\n✅ 装配体生成成功: {result}")
            else:
                print(f"\n❌ 装配体生成失败: {result}")
                sys.exit(1)

        except Exception as e:
            print(f"\n❌ 读取装配体配置失败: {e}")
            sys.exit(1)

        return

    # 正常生成流程
    if not args.prompt:
        print("\n💡 使用方法:")
        print("   advanced_cli.py '设计一个模数2、齿数20的齿轮'")
        print("   advanced_cli.py '6204轴承'")
        print("   advanced_cli.py 'M10螺栓长度50mm'")
        print("   advanced_cli.py 'M8螺母'")
        print("   advanced_cli.py '直径20长度100的传动轴'")
        print("   advanced_cli.py --assembly assembly.json")
        print("   advanced_cli.py --standard  # 查看标准件库")
        print("\n💡 支持的零件类型:")
        print("   • 底板 (plate) - 支持倒角、倒圆、腰形孔、螺纹孔、沉孔、键槽")
        print("   • 齿轮 (gear) • 轴承 (bearing) • 法兰 (flange)")
        print("   • 螺栓 (bolt) • 螺母 (nut) • 垫圈 (washer)")
        print("   • 弹簧 (spring) • 车架 (chassis_frame) • 支架 (bracket)")
        print("   • 传动轴 (shaft) • 阶梯轴 (stepped_shaft)")
        print("   • 联轴器 (coupling) • 皮带轮 (pulley) • 链轮 (sprocket)")
        print("   • 卡簧 (snap_ring) • 挡圈 (retainer)")
        print("   • 自定义形状 (custom_code) - 使用 TurtleCAD")
        return

    prompt = " ".join(args.prompt)

    print(f"\n📝 需求描述: {prompt}")
    print("\n🚀 开始设计...\n")

    config = get_config()
    if args.api_key:
        config.api.api_key = args.api_key
    if args.base_url:
        config.api.base_url = args.base_url
    if args.model:
        config.api.model = args.model

    result = run_agent(
        user_input=prompt,
        config=config,
        output_file=args.output
    )

    if result.success:
        print(f"\n{'='*60}")
        print(f"✅ 设计完成！")
        print(f"📄 输出文件: {result.output_file}")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print(f"❌ 设计失败")
        print(f"💡 提示: {result.error}")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
