#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAD Agent Web 界面
基于 Streamlit 的交互式 Web 应用
"""
import streamlit as st
import os
import sys
import json
import tempfile
from pathlib import Path

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gen_parts import generate_part
from gen_parts_3d import generate_part_3d
from engineering_validation import validate_part_design, recommend_material

# 页面配置
st.set_page_config(
    page_title="CAD Agent 3D",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)


def load_config():
    """加载 API 配置"""
    config_file = Path(__file__).parent / "config.env.local"
    if config_file.exists():
        config = {}
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        return config
    return {}


def render_part_type_selector():
    """渲染零件类型选择器"""
    part_types = {
        "基础零件": {
            "plate": "底板 (Plate)",
            "bolt": "螺栓 (Bolt)",
            "nut": "螺母 (Nut)",
            "washer": "垫圈 (Washer)",
        },
        "传动零件": {
            "gear": "齿轮 (Gear)",
            "sprocket": "链轮 (Sprocket)",
            "pulley": "皮带轮 (Pulley)",
            "shaft": "传动轴 (Shaft)",
            "stepped_shaft": "阶梯轴 (Stepped Shaft)",
            "coupling": "联轴器 (Coupling)",
        },
        "支撑零件": {
            "bearing": "轴承 (Bearing)",
            "flange": "法兰 (Flange)",
            "bracket": "支架 (Bracket)",
            "spring": "弹簧 (Spring)",
        },
        "结构件": {
            "chassis_frame": "车架 (Chassis Frame)",
            "snap_ring": "卡簧 (Snap Ring)",
            "retainer": "挡圈 (Retainer)",
        }
    }

    selected = []
    for category, types in part_types.items():
        with st.expander(f"**{category}**", expanded=False):
            cols = st.columns(2)
            for i, (key, label) in enumerate(types.items()):
                with cols[i % 2]:
                    if st.button(label, key=f"btn_{key}", use_container_width=True):
                        st.session_state.selected_type = key
                        st.rerun()

    return st.session_state.get('selected_type', None)


def render_parameter_form(part_type):
    """渲染参数表单"""
    st.subheader(f"📝 参数配置 - {part_type.upper()}")

    params = {}

    if part_type == "plate":
        col1, col2 = st.columns(2)
        with col1:
            params["length"] = st.number_input("长度 (mm)", value=500, min_value=10, max_value=5000)
            params["width"] = st.number_input("宽度 (mm)", value=300, min_value=10, max_value=5000)
        with col2:
            params["thickness"] = st.number_input("厚度 (mm)", value=10, min_value=1, max_value=100)
            params["hole_diameter"] = st.number_input("孔直径 (mm)", value=0, min_value=0, max_value=50)

        with st.expander("高级选项"):
            col1, col2 = st.columns(2)
            with col1:
                params["chamfer_size"] = st.number_input("倒角 (mm)", value=0, min_value=0, max_value=50)
            with col2:
                params["fillet_radius"] = st.number_input("倒圆 (mm)", value=0, min_value=0, max_value=50)

    elif part_type == "gear":
        col1, col2 = st.columns(2)
        with col1:
            params["module"] = st.selectbox("模数", options=[1, 1.5, 2, 2.5, 3, 4, 5, 6], index=2)
            params["teeth"] = st.number_input("齿数", value=20, min_value=5, max_value=200)
        with col2:
            params["pressure_angle"] = st.selectbox("压力角", options=[14.5, 20, 25], index=1)
            params["thickness"] = st.number_input("厚度 (mm)", value=10, min_value=1, max_value=100)

        with st.expander("轮毂参数"):
            col1, col2 = st.columns(2)
            with col1:
                params["bore_diameter"] = st.number_input("中心孔直径 (mm)", value=10, min_value=1, max_value=100)
                params["hub_diameter"] = st.number_input("轮毂直径 (mm)", value=25, min_value=1, max_value=200)
            with col2:
                params["hub_width"] = st.number_input("轮毂宽度 (mm)", value=8, min_value=1, max_value=50)

    elif part_type == "shaft":
        col1, col2 = st.columns(2)
        with col1:
            params["diameter"] = st.number_input("直径 (mm)", value=20, min_value=1, max_value=500)
        with col2:
            params["length"] = st.number_input("长度 (mm)", value=100, min_value=10, max_value=2000)

    elif part_type == "stepped_shaft":
        st.write("添加轴段（最多 5 段）")
        sections = []
        num_sections = st.slider("段数", min_value=2, max_value=5, value=3)

        for i in range(num_sections):
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    diameter = st.number_input(f"段 {i+1} 直径", value=30-i*5, min_value=1, max_value=500, key=f"diam_{i}")
                with col2:
                    length = st.number_input(f"段 {i+1} 长度", value=50, min_value=10, max_value=1000, key=f"len_{i}")
                sections.append({"diameter": diameter, "length": length})

        params["sections"] = sections

    elif part_type == "bolt":
        col1, col2 = st.columns(2)
        with col1:
            params["diameter"] = st.selectbox("公称直径", options=[6, 8, 10, 12, 16, 20], index=2)
        with col2:
            params["length"] = st.number_input("长度 (mm)", value=50, min_value=10, max_value=500)

    elif part_type == "nut":
        col1, col2 = st.columns(2)
        with col1:
            params["diameter"] = st.selectbox("公称直径", options=[6, 8, 10, 12, 16, 20], index=2)
        with col2:
            params["thickness"] = st.number_input("厚度 (mm)", value=8, min_value=1, max_value=50)

    elif part_type == "flange":
        col1, col2 = st.columns(2)
        with col1:
            params["outer_diameter"] = st.number_input("外径 (mm)", value=150, min_value=20, max_value=1000)
            params["inner_diameter"] = st.number_input("内径 (mm)", value=80, min_value=10, max_value=500)
        with col2:
            params["bolt_circle_diameter"] = st.number_input("螺栓孔分布圆直径", value=120, min_value=20, max_value=800)
            params["bolt_count"] = st.number_input("螺栓孔数量", value=8, min_value=3, max_value=24)
            params["bolt_size"] = st.number_input("螺栓孔直径", value=12, min_value=3, max_value=50)
            params["thickness"] = st.number_input("厚度 (mm)", value=20, min_value=5, max_value=100)

    elif part_type == "chassis_frame":
        col1, col2 = st.columns(2)
        with col1:
            params["length"] = st.number_input("长度 (mm)", value=2500, min_value=100, max_value=10000)
            params["width"] = st.number_input("宽度 (mm)", value=800, min_value=100, max_value=5000)
        with col2:
            params["rail_height"] = st.number_input("纵梁高度 (mm)", value=100, min_value=20, max_value=500)
            params["rail_thickness"] = st.number_input("纵梁厚度 (mm)", value=5, min_value=1, max_value=20)
            params["cross_members"] = st.number_input("横梁数量", value=5, min_value=2, max_value=10)

    elif part_type == "spring":
        col1, col2 = st.columns(2)
        with col1:
            params["wire_diameter"] = st.number_input("线径 (mm)", value=3, min_value=0.5, max_value=20)
            params["coil_diameter"] = st.number_input("线圈直径 (mm)", value=25, min_value=5, max_value=200)
        with col2:
            params["free_length"] = st.number_input("自由长度 (mm)", value=80, min_value=10, max_value=500)
            params["coils"] = st.number_input("有效圈数", value=8, min_value=2, max_value=20)

    else:
        st.info(f"⚠️ {part_type} 参数使用默认值")
        # 通用参数
        col1, col2 = st.columns(2)
        with col1:
            params["diameter"] = st.number_input("直径", value=20, min_value=1, max_value=500)
        with col2:
            params["length"] = st.number_input("长度", value=100, min_value=10, max_value=2000)

    return params


def main():
    # 初始化 session state
    if 'selected_type' not in st.session_state:
        st.session_state.selected_type = None

    # 标题
    st.markdown('<div class="main-header">🤖 CAD Agent 3D - 智能机械设计</div>', unsafe_allow_html=True)

    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 设置")

        # API 配置
        config = load_config()
        api_key = config.get("OPENAI_API_KEY", "")
        base_url = config.get("OPENAI_BASE_URL", "")
        model = config.get("OPENAI_MODEL", "")

        st.subheader("🔑 API 配置")
        use_llm = st.checkbox("使用 LLM 智能解析", value=False)
        if use_llm:
            if not api_key:
                st.warning("⚠️ 未配置 API Key，请在 config.env.local 中配置")
                st.info("💡 直接模式无需 API Key")
                use_llm = False

        # 输出格式选择
        st.subheader("📄 输出格式")
        output_format = st.radio("选择格式", ["3D STL (推荐)", "2D DXF"], horizontal=True)

        # 帮助信息
        with st.expander("❓ 使用说明"):
            st.markdown("""
            **步骤：**
            1. 选择零件类型
            2. 配置参数
            3. 点击"生成 CAD"
            4. 下载文件

            **格式说明：**
            - **3D STL**: 用于 3D 打印、建模软件
            - **2D DXF**: 用于工程图纸、激光切割
            """)

    # 主内容区
    if not st.session_state.selected_type:
        st.info("👈 请在左侧选择零件类型")

        # 显示示例
        st.markdown("---")
        st.markdown("### 💡 支持的零件类型")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            **基础零件**
            - 底板 (Plate)
            - 螺栓 (Bolt)
            - 螺母 (Nut)
            - 垫圈 (Washer)
            """)

        with col2:
            st.markdown("""
            **传动零件**
            - 齿轮 (Gear)
            - 传动轴 (Shaft)
            - 阶梯轴 (Stepped Shaft)
            - 联轴器 (Coupling)
            - 皮带轮 (Pulley)
            """)

        with col3:
            st.markdown("""
            **支撑零件**
            - 轴承 (Bearing)
            - 法兰 (Flange)
            - 支架 (Bracket)
            - 弹簧 (Spring)
            - 车架 (Chassis)
            """)
    else:
        part_type = st.session_state.selected_type

        # 参数配置区
        with st.container():
            params = render_parameter_form(part_type)

        # 生成按钮
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 2, 2])

        with col1:
            generate_clicked = st.button("🚀 生成 CAD", use_container_width=True, type="primary")

        with col2:
            validate_clicked = st.button("🔍 工程验证", use_container_width=True)

        with col3:
            material_clicked = st.button("💡 材料推荐", use_container_width=True)

        # 处理生成
        if generate_clicked:
            st.markdown("---")
            st.subheader("🎨 生成结果")

            # 创建 spec
            spec = {"type": part_type, "parameters": params}

            # 确定输出格式
            use_3d = "3D STL" in output_format
            default_filename = f"{part_type}_output.stl" if use_3d else f"{part_type}_output.dxf"

            try:
                with st.spinner(f"正在生成 {'3D 模型' if use_3d else '2D 图纸'}..."):
                    if use_3d:
                        generate_part_3d(spec, default_filename)
                    else:
                        generate_part(spec, default_filename)

                # 读取文件
                with open(default_filename, 'rb') as f:
                    file_data = f.read()

                # 显示成功信息
                st.success(f"✅ {'3D 模型' if use_3d else '2D 图纸'} 生成成功！")

                # 下载按钮
                st.download_button(
                    label=f"📥 下载 {default_filename}",
                    data=file_data,
                    file_name=default_filename,
                    mime="application/octet-stream" if use_3d else "application/dxf"
                )

                # 显示文件信息
                import os
                file_size = os.path.getsize(default_filename)
                st.info(f"📊 文件大小: {file_size/1024:.1f} KB")

            except Exception as e:
                st.error(f"❌ 生成失败: {e}")

        # 处理工程验证
        if validate_clicked:
            st.markdown("---")
            st.subheader("🔍 工程验证")

            spec = {"type": part_type, "parameters": params}
            valid, messages, recommendations = validate_part_design(part_type, params)

            if valid:
                st.success("✅ 设计验证通过")
            else:
                st.warning("⚠️ 发现潜在问题")

            for msg in messages:
                st.info(f"• {msg}")

            if recommendations:
                st.markdown("#### 💡 建议")
                for rec in recommendations:
                    if "suggestion" in rec:
                        st.info(f"💡 {rec['suggestion']}")

        # 处理材料推荐
        if material_clicked:
            st.markdown("---")
            st.subheader("💡 材料推荐")

            try:
                recommendations = recommend_material(part_type, "")

                for rec in recommendations:
                    material = rec.get("material", "")
                    reason = rec.get("reason", "")
                    st.info(f"📌 **{material}**: {reason}")
            except Exception as e:
                st.error(f"❌ 推荐失败: {e}")

        # 返回按钮
        if st.button("← 返回选择零件类型"):
            st.session_state.selected_type = None
            st.rerun()


if __name__ == "__main__":
    main()
