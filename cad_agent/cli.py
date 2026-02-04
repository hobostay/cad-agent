#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAD Agent CLI - 统一命令行工具
支持 2D DXF/3D STL 生成、标准件查询、装配体生成
"""
import sys
import os
import shutil
import json
import argparse
from pathlib import Path

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import (
    get_config,
    setup_logger,
    run_agent,
    APIClientError
)
from advanced_agent_core import generate_assembly
from gen_parts import generate_part
from gen_parts_3d import generate_part_3d
from standard_parts_loader import StandardPartsLoader


def print_logo():
    """打印欢迎横幅"""
    logo = """
╔══════════════════════════════════════════════════════════╗
║                                                            ║
║         🤖 CAD Agent - 智能机械设计系统                    ║
║                                                            ║
║   支持零件: 底板|齿轮|轴承|法兰|车架|支架|螺栓|螺母|弹簧  ║
║            |轴|联轴器|皮带轮|链轮|卡簧|垫圈|挡圈|自定义  ║
║                                                            ║
║   输出格式: 2D DXF | 3D STL                               ║
║                                                            ║
╚══════════════════════════════════════════════════════════╝
"""
    print(logo)


def print_usage():
    """打印使用说明"""
    print("\n💡 使用示例:")
    print('   python3 cli.py "设计一个模数2、齿数20的齿轮"')
    print('   python3 cli.py "6204轴承"')
    print('   python3 cli.py "M10螺栓长度50mm"')
    print('   python3 cli.py "500×300底板，四角孔12mm"')
    print('   python3 cli.py "齿轮" --3d                    # 3D STL')
    print('   python3 cli.py --standard                     # 查看标准件')
    print('   python3 cli.py --assembly assembly.json       # 装配体')


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


def copy_to_desktop(output_file):
    """复制文件到桌面"""
    try:
        desktop = os.path.expanduser("~/Desktop")
        dest = os.path.join(desktop, os.path.basename(output_file))
        shutil.copy(output_file, dest)
        print(f"📋 已复制到桌面: {os.path.basename(dest)}")
    except Exception as e:
        print(f"⚠️  复制到桌面失败: {e}")


def main():
    # 加载配置
    try:
        config = get_config()
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        sys.exit(1)

    # 设置日志
    logger = setup_logger(config)

    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="CAD Agent - 智能机械设计助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "设计一个模数2、齿数20的齿轮"
  %(prog)s "6204轴承"
  %(prog)s "M10螺栓长度50mm" --3d
  %(prog)s --standard
  %(prog)s --assembly assembly.json

支持的零件类型:
  • 底板 (plate) - 支持倒角、倒圆、腰形孔、螺纹孔、沉孔、键槽
  • 齿轮 (gear) • 轴承 (bearing) • 法兰 (flange)
  • 螺栓 (bolt) • 螺母 (nut) • 垫圈 (washer)
  • 弹簧 (spring) • 车架 (chassis_frame) • 支架 (bracket)
  • 传动轴 (shaft) • 阶梯轴 (stepped_shaft)
  • 联轴器 (coupling) • 皮带轮 (pulley) • 链轮 (sprocket)
  • 卡簧 (snap_ring) • 挡圈 (retainer)
        """
    )

    parser.add_argument(
        "prompt",
        nargs="*",
        help="零件描述（自然语言）"
    )

    # API 配置
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API密钥（覆盖配置文件）"
    )

    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="API 基础 URL（覆盖配置文件）"
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="模型名称（覆盖配置文件）"
    )

    # 输出配置
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件名（默认: agent_output.dxf 或 agent_output.stl）"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="静默模式，减少输出"
    )

    # 扩展功能
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
        "--3d",
        dest="use_3d",
        action="store_true",
        help="生成 3D STL 文件"
    )

    # 直接模式（跳过 LLM）
    parser.add_argument(
        "--direct",
        action="store_true",
        help="直接模式（跳过 LLM，用参数直接生成）"
    )

    parser.add_argument(
        "--type",
        type=str,
        help="零件类型（用于 --direct 模式）"
    )

    parser.add_argument(
        "--params",
        type=str,
        help="JSON 格式的参数（用于 --direct 模式）"
    )

    args = parser.parse_args()

    # 显示标准件库
    if args.standard:
        print_logo()
        print_standard_parts()
        return

    # 生成装配体
    if args.assembly:
        if not args.quiet:
            print_logo()
        print(f"\n📋 从 {args.assembly} 读取装配体配置...")

        try:
            with open(args.assembly, "r", encoding="utf-8") as f:
                assembly_config = json.load(f)

            parts = assembly_config.get("parts", [])
            output = args.output or "assembly.dxf"

            if not args.quiet:
                print(f"   零件数量: {len(parts)}")
                print(f"   输出文件: {output}")

            success, result = generate_assembly(
                parts=parts,
                output_file=output,
                verbose=not args.quiet
            )

            if success:
                print(f"\n✅ 装配体生成成功: {result}")
                copy_to_desktop(result)
            else:
                print(f"\n❌ 装配体生成失败: {result}")
                sys.exit(1)

        except Exception as e:
            print(f"\n❌ 读取装配体配置失败: {e}")
            sys.exit(1)

        return

    # 直接模式
    if args.direct:
        if not args.type:
            print("\n❌ 直接模式需要指定 --type 参数")
            print("\n示例:")
            print("  python3 cli.py --direct --type gear --3d")
            print('  python3 cli.py --direct --type shaft --3d --params \'{"diameter":20,"length":100}\'')
            sys.exit(1)

        # 解析参数
        try:
            if args.params:
                params = json.loads(args.params)
            else:
                params = {}
        except json.JSONDecodeError as e:
            print(f"\n❌ 参数解析失败: {e}")
            print("提示: --params 需要是 JSON 格式")
            sys.exit(1)

        spec = {"type": args.type, "parameters": params}

        # 确定输出文件
        use_3d = args.use_3d
        default_output = "agent_output.stl" if use_3d else "agent_output.dxf"
        output_file = args.output or default_output

        if not args.quiet:
            print_logo()
            print(f"\n📝 直接生成: {args.type}")
            print(f"📄 输出: {output_file} ({'STL' if use_3d else 'DXF'})")

        try:
            if use_3d:
                generate_part_3d(spec, output_file)
            else:
                generate_part(spec, output_file)
        except Exception as e:
            print(f"\n❌ 生成失败: {e}")
            sys.exit(1)

        if not args.quiet:
            print(f"\n✅ 生成完成!")
            print(f"📁 文件: {output_file}")
            file_size = os.path.getsize(output_file)
            print(f"📊 文件大小: {file_size/1024:.1f} KB")
            copy_to_desktop(output_file)
        return

    # 检查 prompt
    if not args.prompt:
        print_logo()
        print_usage()
        sys.exit(1)

    # 检查 API Key
    api_key = args.api_key or config.api.api_key
    if not api_key or api_key == "your_api_key_here":
        print_logo()
        print("\n❌ 未配置 API Key！\n")
        print("请选择以下方式之一配置：\n")
        print("方式1: 创建配置文件 config.env.local：")
        print("  OPENAI_API_KEY=<API 密钥>")
        print("  OPENAI_BASE_URL=https://api.openai.com/v1")
        print("  OPENAI_MODEL=gpt-4\n")
        print("方式2: 使用环境变量")
        print("  export OPENAI_API_KEY=<API 密钥>\n")
        print("方式3: 命令行指定")
        print(f'  python3 {sys.argv[0]} --api-key <API 密钥> "设计一个齿轮"')
        print("\n推荐API:")
        print("  • 智谱GLM: https://open.bigmodel.cn (有免费额度)")
        print("  • DeepSeek: https://www.deepseek.com")
        print("  • 通义千问: https://dashscope.aliyuncs.com")
        sys.exit(1)

    # 覆盖配置
    if args.api_key:
        config.api.api_key = args.api_key
    if args.base_url:
        config.api.base_url = args.base_url
    if args.model:
        config.api.model = args.model
    if args.quiet:
        config.log.level = "WARNING"
        config.agent.verbose = False

    # 确定 2D/3D 模式
    use_3d = args.use_3d

    # 打印欢迎信息
    if not args.quiet:
        print_logo()
        print(f"\n📝 需求: {' '.join(args.prompt)}")
        print(f"🤖 模型: {config.api.model}")
        print(f"🔧 API: {config.api.base_url}")
        print(f"📄 输出: {'STL' if use_3d else 'DXF'}")
        print("\n" + "-" * 60 + "\n")

    # 运行 Agent
    user_input = " ".join(args.prompt)
    default_output = "agent_output.stl" if use_3d else "agent_output.dxf"
    output_file = args.output or default_output

    try:
        result = run_agent(user_input, config, output_file)

        if not args.quiet:
            print("\n" + "-" * 60 + "\n")

        if result.success:
            print(f"✅ 设计完成！")
            print(f"📄 输出文件: {result.output_file}")

            # 显示文件信息
            file_size = os.path.getsize(result.output_file)
            print(f"📊 文件大小: {file_size/1024:.1f} KB")

            # 复制到桌面
            if config.output.copy_to_desktop:
                copy_to_desktop(result.output_file)

        else:
            print(f"❌ 设计失败: {result.error}")
            sys.exit(1)

    except APIClientError as e:
        logger.error(f"API调用失败: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(1)

    except Exception as e:
        logger.error(f"未知错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
