# -*- coding: utf-8 -*-
"""
工程验证模块
提供工程计算和验证功能
"""
import math
from typing import Dict, List, Tuple, Any, Optional

# ============== 标准数据 ==============

# 齿轮标准模数系列 (GB/T 1357-2008)
STANDARD_MODULE = [1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20, 25, 32]

# 标准压力角
STANDARD_PRESSURE_ANGLE = [20, 14.5, 25]

# 材料属性数据库 (简化)
MATERIALS = {
    "Q235": {
        "name": "碳素结构钢 Q235",
        "tensile_strength": 375,  # MPa
        "yield_strength": 235,    # MPa
        "density": 7.85,          # g/cm³
        "applications": ["一般零件", "底板", "支架", "法兰"]
    },
    "45": {
        "name": "优质碳素结构钢 45号",
        "tensile_strength": 600,
        "yield_strength": 355,
        "density": 7.85,
        "applications": ["轴", "齿轮", "键", "销"]
    },
    "40Cr": {
        "name": "合金结构钢 40Cr",
        "tensile_strength": 980,
        "yield_strength": 785,
        "density": 7.85,
        "applications": ["齿轮", "轴", "高强度零件"]
    },
    "HT200": {
        "name": "灰铸铁 HT200",
        "tensile_strength": 200,
        "yield_strength": 0,  # 铸铁无明显屈服点
        "density": 7.2,
        "applications": ["机座", "轴承座", "低速齿轮"]
    },
    "65Mn": {
        "name": "弹簧钢 65Mn",
        "tensile_strength": 980,
        "yield_strength": 785,
        "density": 7.85,
        "applications": ["弹簧", "卡簧", "挡圈"]
    },
    "304": {
        "name": "不锈钢 304",
        "tensile_strength": 520,
        "yield_strength": 205,
        "density": 7.93,
        "applications": ["耐腐蚀零件", "食品机械"]
    }
}

# 公差等级 (GB/T 1800)
TOLERANCE_GRADES = {
    "IT5": "精密加工",
    "IT6": "细加工",
    "IT7": "一般精密",
    "IT8": "中等精度",
    "IT9": "粗糙",
    "IT10": "较粗糙"
}

# 轴承公差配合
BEARING_FITS = {
    "heavy_load": {
        "shaft": "k6",  # 过渡配合
        "housing": "N7"  # 过盈配合
    },
    "normal_load": {
        "shaft": "j6",
        "housing": "K7"
    },
    "light_load": {
        "shaft": "h6",
        "housing": "J7"
    }
}

# ============== 齿轮传动验证 ==============

def validate_gear_pair(gear1: Dict, gear2: Dict, center_distance: float) -> Tuple[bool, List[str]]:
    """
    验证齿轮传动副

    Args:
        gear1: 第一个齿轮参数 {"module": 2, "teeth": 20}
        gear2: 第二个齿轮参数
        center_distance: 实际中心距 (mm)

    Returns:
        (is_valid, messages)
    """
    messages = []
    is_valid = True

    m1 = gear1.get("module", 0)
    z1 = gear1.get("teeth", 0)
    m2 = gear2.get("module", 0)
    z2 = gear2.get("teeth", 0)

    # 1. 检查模数是否匹配
    if abs(m1 - m2) > 0.01:
        is_valid = False
        messages.append(f"❌ 模数不匹配: 齿轮1模数={m1}, 齿轮2模数={m2}")
    else:
        messages.append(f"✅ 模数匹配: m={m1}")

    # 2. 检查模数是否为标准值
    if m1 not in STANDARD_MODULE:
        messages.append(f"⚠️  模数 {m1} 不是标准值")
    else:
        messages.append(f"✅ 模数为标准值")

    # 3. 计算理论中心距
    theoretical_center = m1 * (z1 + z2) / 2
    center_error = abs(center_distance - theoretical_center)

    if center_error > 0.1:
        is_valid = False
        messages.append(f"❌ 中心距偏差过大: 实际={center_distance:.2f}, 理论={theoretical_center:.2f}, 误差={center_error:.2f}")
    else:
        messages.append(f"✅ 中心距正确: {theoretical_center:.2f}mm")

    # 4. 检查齿数
    if z1 < 17 or z2 < 17:
        messages.append(f"⚠️  齿数少于17，可能发生根切 (z1={z1}, z2={z2})")

    # 5. 传动比
    ratio = z2 / z1 if z1 > 0 else 0
    messages.append(f"ℹ️  传动比 i = {ratio:.2f}:1")

    if ratio > 5 or ratio < 0.2:
        messages.append(f"⚠️  传动比过大或过小，建议使用多级传动")

    return is_valid, messages

def calculate_gear_parameters(module: float, teeth: int, pressure_angle: float = 20) -> Dict:
    """
    计算齿轮参数

    Returns:
        包含分度圆直径、齿顶圆直径、齿根圆直径等的字典
    """
    pitch_diameter = module * teeth
    addendum = module
    dedendum = 1.25 * module

    return {
        "module": module,
        "teeth": teeth,
        "pressure_angle": pressure_angle,
        "pitch_diameter": pitch_diameter,
        "tip_diameter": pitch_diameter + 2 * addendum,
        "root_diameter": pitch_diameter - 2 * dedendum,
        "addendum": addendum,
        "dedendum": dedendum,
        "tooth_thickness": math.pi * module / 2
    }

# ============== 轴承配合验证 ==============

def validate_bearing_fit(bearing: Dict, shaft_diameter: float, housing_diameter: float) -> Tuple[bool, List[str]]:
    """
    验证轴承与轴、孔的配合

    Args:
        bearing: 轴承参数 {"inner_diameter": 20, "outer_diameter": 47, "type": "62..."}
        shaft_diameter: 轴直径
        housing_diameter: 座孔直径

    Returns:
        (is_valid, messages)
    """
    messages = []
    is_valid = True

    inner_dia = bearing.get("inner_diameter", 0)
    outer_dia = bearing.get("outer_diameter", 0)

    # 1. 检查轴与轴承内孔配合
    shaft_diff = shaft_diameter - inner_dia

    if shaft_diff > 0.02:  # 轴太大
        is_valid = False
        messages.append(f"❌ 轴径 {shaft_diameter} 大于轴承内孔 {inner_dia}")
    elif shaft_diff < -0.01:  # 轴太小，间隙过大
        messages.append(f"⚠️  轴径 {shaft_diameter} 小于轴承内孔 {inner_dia}，可能导致松动")
    else:
        messages.append(f"✅ 轴与轴承内孔配合良好")

    # 2. 检查轴承与座孔配合
    housing_diff = housing_diameter - outer_dia

    if housing_diff < -0.02:  # 孔太小
        is_valid = False
        messages.append(f"❌ 座孔径 {housing_diameter} 小于轴承外径 {outer_dia}")
    elif housing_diff > 0.05:  # 孔太大
        messages.append(f"⚠️  座孔径 {housing_diameter} 大于轴承外径 {outer_dia}，可能导致松动")
    else:
        messages.append(f"✅ 轴承与座孔配合良好")

    # 3. 推荐配合
    bearing_type = bearing.get("type", "")
    if bearing_type.startswith("62") or bearing_type.startswith("63"):
        messages.append(f"ℹ️  推荐配合: 轴 k6/m6, 座孔 H7/J7")

    return is_valid, messages

# ============== 强度校验 ==============

def validate_shaft_strength(diameter: float, torque: float, material: str = "45") -> Tuple[bool, List[str]]:
    """
    简化的轴强度校验（纯扭转）

    Args:
        diameter: 轴直径 (mm)
        torque: 扭矩 (N·m)
        material: 材料代码

    Returns:
        (is_valid, messages)
    """
    messages = []
    is_valid = True

    # 获取材料属性
    mat = MATERIALS.get(material, MATERIALS["45"])
    yield_strength = mat["yield_strength"]  # MPa

    # 计算剪切应力
    # τ = T / W, W = π*d³/16 (实心圆轴抗扭截面系数)
    diameter_m = diameter / 1000  # mm -> m
    W = math.pi * diameter_m ** 3 / 16
    torque_Nm = torque  # N·m

    shear_stress = torque_Nm / W / 1e6  # Pa -> MPa

    # 安全系数
    safety_factor = 2.0
    allowable_stress = yield_strength / safety_factor

    messages.append(f"ℹ️  材料: {mat['name']}")
    messages.append(f"ℹ️  剪切应力: {shear_stress:.1f} MPa")
    messages.append(f"ℹ️  许用应力: {allowable_stress:.1f} MPa (安全系数 {safety_factor})")

    if shear_stress > allowable_stress:
        is_valid = False
        messages.append(f"❌ 强度不足! 建议增大直径或更换高强材料")
    else:
        utilization = shear_stress / allowable_stress * 100
        messages.append(f"✅ 强度满足要求 (利用率 {utilization:.0f}%)")

    return is_valid, messages

def validate_plate_strength(length: float, width: float, thickness: float, load: float,
                            material: str = "Q235") -> Tuple[bool, List[str]]:
    """
    简化的板强度校验（简化梁模型）

    Args:
        length: 长度 (mm)
        width: 宽度 (mm)
        thickness: 厚度 (mm)
        load: 均布载荷 (N)
        material: 材料代码

    Returns:
        (is_valid, messages)
    """
    messages = []
    is_valid = True

    mat = MATERIALS.get(material, MATERIALS["Q235"])
    yield_strength = mat["yield_strength"]

    # 简化为简支梁，最大应力 σ = M/W
    # M_max = qL²/8 (均布载荷)
    # W = bh²/6 (矩形截面抗弯系数)

    span = length  # 假设长度为跨度
    q = load / span  # 线载荷 N/mm
    M_max = q * span ** 2 / 8  # N·mm
    W_section = width * thickness ** 2 / 6  # mm³

    bending_stress = M_max / W_section  # MPa

    # 安全系数
    safety_factor = 1.5
    allowable_stress = yield_strength / safety_factor

    messages.append(f"ℹ️  材料: {mat['name']}")
    messages.append(f"ℹ️  弯曲应力: {bending_stress:.1f} MPa")
    messages.append(f"ℹ️  许用应力: {allowable_stress:.1f} MPa")

    if bending_stress > allowable_stress:
        is_valid = False
        messages.append(f"❌ 强度不足! 建议增加厚度")
    else:
        messages.append(f"✅ 强度满足要求")

    return is_valid, messages

# ============== 材料推荐 ==============

def recommend_material(part_type: str, application: str = "") -> List[Dict]:
    """
    根据零件类型和应用场景推荐材料

    Args:
        part_type: 零件类型
        application: 应用描述

    Returns:
        材料推荐列表
    """
    recommendations = []

    # 基于零件类型的推荐
    if part_type in ["gear", "shaft", "stepped_shaft", "key", "pin"]:
        if "high_load" in application or "high_speed" in application:
            recommendations.append({"material": "40Cr", "reason": "高强度，适合重载高速"})
        recommendations.append({"material": "45", "reason": "常用调质钢，性价比高"})
    elif part_type in ["spring", "snap_ring", "retainer"]:
        recommendations.append({"material": "65Mn", "reason": "弹簧钢，弹性好"})
    elif part_type in ["plate", "bracket", "chassis_frame", "flange"]:
        if "corrosion" in application:
            recommendations.append({"material": "304", "reason": "不锈钢，耐腐蚀"})
        recommendations.append({"material": "Q235", "reason": "普通碳钢，成本低易加工"})
        recommendations.append({"material": "HT200", "reason": "铸铁，适合大型件"})
    elif part_type in ["bearing_housing", "base"]:
        recommendations.append({"material": "HT200", "reason": "铸铁，减震好"})
        recommendations.append({"material": "Q235", "reason": "焊接性好"})

    # 默认推荐
    if not recommendations:
        recommendations.append({"material": "Q235", "reason": "通用材料"})

    return recommendations

# ============== 公差分析 ==============

def recommend_tolerance(feature_type: str, nominal_size: float, precision_level: str = "normal") -> Dict:
    """
    推荐公差等级和数值

    Args:
        feature_type: 特征类型 ("hole", "shaft", "length", "thread")
        nominal_size: 公称尺寸 (mm)
        precision_level: 精度等级 ("high", "normal", "low")

    Returns:
        公差推荐 {"grade": "IT7", "value": 0.021, "code": "H7"}
    """
    # 简化的公差计算（基于 GB/T 1800）
    # 实际应用中需要查表或使用更精确的公式

    # 根据精度等级选择 IT 等级
    grade_map = {
        "high": "IT6",
        "normal": "IT7",
        "low": "IT9"
    }
    grade = grade_map.get(precision_level, "IT7")

    # 简化的公差值计算 (μm)
    # IT = K * i, where i = 0.45 * D^(1/3) + 0.001 * D
    D_mm = nominal_size
    i = 0.45 * (D_mm ** (1/3)) + 0.001 * D_mm  # μm

    K_map = {
        "IT5": 7,
        "IT6": 10,
        "IT7": 16,
        "IT8": 25,
        "IT9": 40,
        "IT10": 64
    }
    K = K_map.get(grade, 16)

    tolerance_value = K * i / 1000  # μm -> mm

    # 公差代号
    code_map = {
        "hole": {"high": "H6", "normal": "H7", "low": "H8"},
        "shaft": {"high": "h6", "normal": "h7", "low": "h9"},
        "length": {"high": "js6", "normal": "js7", "low": "js9"},
        "thread": {"high": "6H", "normal": "6H", "low": "7H"}
    }
    code = code_map.get(feature_type, {}).get(precision_level, "H7")

    return {
        "grade": grade,
        "value": round(tolerance_value, 4),
        "code": code,
        "description": TOLERANCE_GRADES.get(grade, "")
    }

# ============== 综合验证入口 ==============

def validate_part_design(part_type: str, params: Dict) -> Tuple[bool, List[str], List[Dict]]:
    """
    综合验证零件设计

    Args:
        part_type: 零件类型
        params: 零件参数

    Returns:
        (is_valid, messages, recommendations)
    """
    messages = []
    recommendations = []
    is_valid = True

    # 齿轮验证
    if part_type == "gear":
        module = params.get("module", 0)
        teeth = params.get("teeth", 0)

        if module not in STANDARD_MODULE:
            is_valid = False
            messages.append(f"❌ 模数 {module} 不是标准值，应选择: {STANDARD_MODULE[:5]}")
        else:
            messages.append(f"✅ 模数 {module} 为标准值")

        if teeth < 17:
            messages.append(f"⚠️  齿数 {teeth} < 17，可能根切")

        # 材料推荐
        mat_recs = recommend_material("gear", "")
        for rec in mat_recs:
            recommendations.append({
                "category": "材料",
                "suggestion": f"推荐使用 {rec['material']}: {rec['reason']}"
            })

    # 轴承验证
    elif part_type == "bearing":
        inner = params.get("inner_diameter", 0)
        outer = params.get("outer_diameter", 0)

        if inner <= 0 or outer <= inner:
            is_valid = False
            messages.append("❌ 轴承尺寸参数无效")

        messages.append(f"ℹ️  轴承系列推断: {inner}mm 内径")

    # 底板验证
    elif part_type == "plate":
        length = params.get("length", 0)
        width = params.get("width", 0)
        thickness = params.get("thickness", 0)

        if thickness < length / 50:
            messages.append(f"⚠️  厚度 {thickness} 相对长度 {length} 过小，可能刚度不足")

        # 材料推荐
        mat_recs = recommend_material("plate", "")
        for rec in mat_recs:
            recommendations.append({
                "category": "材料",
                "suggestion": f"推荐使用 {rec['material']}: {rec['reason']}"
            })

    # 通用公差推荐
    if is_valid:
        tol = recommend_tolerance("length", params.get("length", 100), "normal")
        recommendations.append({
            "category": "公差",
            "suggestion": f"推荐公差等级: {tol['grade']} ({tol['code']}, ±{tol['value']}mm)"
        })

    return is_valid, messages, recommendations


if __name__ == "__main__":
    # 测试齿轮验证
    print("=== 齿轮传动验证 ===")
    gear1 = {"module": 2, "teeth": 20}
    gear2 = {"module": 2, "teeth": 40}
    valid, msgs = validate_gear_pair(gear1, gear2, 60)
    for msg in msgs:
        print(msg)

    print("\n=== 材料推荐 ===")
    recs = recommend_material("gear", "high_load")
    for rec in recs:
        print(f"{rec['material']}: {rec['reason']}")

    print("\n=== 公差推荐 ===")
    tol = recommend_tolerance("hole", 20, "normal")
    print(f"公差等级: {tol['grade']}, 代号: {tol['code']}, 数值: ±{tol['value']}mm")
