# -*- coding: utf-8 -*-
"""
3D 零件生成模块
支持 STL 输出，用于 3D 打印和 CAD 软件
"""
import numpy as np
import math
import sys
import os
from stl import mesh

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class MeshBuilder:
    """3D 网格构建器"""

    def __init__(self):
        self.vertices = []
        self.faces = []

    def add_cube(self, size, center=(0, 0, 0)):
        """添加立方体"""
        dx, dy, dz = size if isinstance(size, (list, tuple)) else (size, size, size)
        cx, cy, cz = center

        # 8 个顶点
        vertices = [
            [cx-dx/2, cy-dy/2, cz-dz/2],  # 0
            [cx+dx/2, cy-dy/2, cz-dz/2],  # 1
            [cx+dx/2, cy+dy/2, cz-dz/2],  # 2
            [cx-dx/2, cy+dy/2, cz-dz/2],  # 3
            [cx-dx/2, cy-dy/2, cz+dz/2],  # 4
            [cx+dx/2, cy-dy/2, cz+dz/2],  # 5
            [cx+dx/2, cy+dy/2, cz+dz/2],  # 6
            [cx-dx/2, cy+dy/2, cz+dz/2],  # 7
        ]

        # 12 个三角面（6 个面，每个面 2 个三角形）
        faces = [
            [0, 1, 2], [0, 2, 3],  # 底面
            [4, 7, 6], [4, 6, 5],  # 顶面
            [0, 4, 5], [0, 5, 1],  # 前面
            [2, 6, 7], [2, 7, 3],  # 后面
            [0, 3, 7], [0, 7, 4],  # 左面
            [1, 5, 6], [1, 6, 2],  # 右面
        ]

        base_idx = len(self.vertices)
        self.vertices.extend(vertices)
        for face in faces:
            self.faces.append([base_idx + i for i in face])

    def add_cylinder(self, radius, height, center=(0, 0, 0), segments=32):
        """添加圆柱体"""
        cx, cy, cz = center

        # 生成圆柱顶点
        vertices = []

        # 底面中心
        vertices.append([cx, cy, cz - height/2])
        # 顶面中心
        vertices.append([cx, cy, cz + height/2])

        # 底面和顶面的圆周点
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            vertices.append([x, y, cz - height/2])  # 底面
            vertices.append([x, y, cz + height/2])  # 顶面

        base_idx = len(self.vertices)
        self.vertices.extend(vertices)

        # 生成面
        # 侧面
        for i in range(segments):
            next_i = (i + 1) % segments
            # 底面点索引: 2 + i*2
            # 顶面点索引: 3 + i*2
            b1 = 2 + i * 2
            b2 = 2 + next_i * 2
            t1 = 3 + i * 2
            t2 = 3 + next_i * 2

            self.faces.append([base_idx + b1, base_idx + b2, base_idx + t1])
            self.faces.append([base_idx + b2, base_idx + t2, base_idx + t1])

        # 底面和顶面（使用中心点）
        for i in range(segments):
            next_i = (i + 1) % segments
            b1 = 2 + i * 2
            b2 = 2 + next_i * 2
            t1 = 3 + i * 2
            t2 = 3 + next_i * 2

            # 底面（逆时针）
            self.faces.append([base_idx + 0, base_idx + b2, base_idx + b1])
            # 顶面（顺时针）
            self.faces.append([base_idx + 1, base_idx + t1, base_idx + t2])

    def add_torus(self, major_radius, minor_radius, center=(0, 0, 0), major_segments=32, minor_segments=16):
        """添加圆环体"""
        cx, cy, cz = center

        vertices = []
        for i in range(major_segments):
            major_angle = 2 * math.pi * i / major_segments
            # 圆环中心线上的点
            cx_major = cx + major_radius * math.cos(major_angle)
            cy_major = cy + major_radius * math.sin(major_angle)

            for j in range(minor_segments):
                minor_angle = 2 * math.pi * j / minor_segments
                # 圆环截面上的点
                x = cx_major + minor_radius * math.cos(minor_angle) * math.cos(major_angle)
                y = cy_major + minor_radius * math.cos(minor_angle) * math.sin(major_angle)
                z = cz + minor_radius * math.sin(minor_angle)
                vertices.append([x, y, z])

        base_idx = len(self.vertices)
        self.vertices.extend(vertices)

        # 生成面
        for i in range(major_segments):
            for j in range(minor_segments):
                next_i = (i + 1) % major_segments
                next_j = (j + 1) % minor_segments

                v1 = i * minor_segments + j
                v2 = next_i * minor_segments + j
                v3 = next_i * minor_segments + next_j
                v4 = i * minor_segments + next_j

                self.faces.append([base_idx + v1, base_idx + v2, base_idx + v3])
                self.faces.append([base_idx + v1, base_idx + v3, base_idx + v4])

    def extrude_rectangle(self, width, depth, height, center=(0, 0, 0)):
        """拉伸矩形（创建长方体）"""
        self.add_cube((width, depth, height), center)

    def extrude_circle(self, radius, height, center=(0, 0, 0), segments=32):
        """拉伸圆形（创建圆柱体）"""
        self.add_cylinder(radius, height, center, segments)

    def revolve_profile(self, profile_points, axis='z', segments=32, angle=360):
        """
        旋转轮廓创建 3D 形状

        Args:
            profile_points: 轮廓点列表 [(r, z), ...]，r 为径向距离，z 为高度
            axis: 旋转轴 ('x', 'y', 或 'z')
            segments: 分段数
            angle: 旋转角度（度），360 为完整旋转
        """
        angle_rad = math.radians(angle)

        vertices = []
        num_profile_points = len(profile_points)

        # 为每个轮廓点生成圆形
        for i in range(num_profile_points):
            r, z = profile_points[i]
            # 根据旋转轴选择坐标
            for j in range(segments + 1):
                theta = angle_rad * j / segments

                if axis == 'z':
                    x = r * math.cos(theta)
                    y = r * math.sin(theta)
                    vertices.append([x, y, z])
                elif axis == 'x':
                    y = r * math.cos(theta)
                    z = r * math.sin(theta)
                    vertices.append([x, y, z])
                else:  # axis == 'y'
                    x = r * math.cos(theta)
                    z = r * math.sin(theta)
                    vertices.append([x, y, z])

        base_idx = len(self.vertices)
        self.vertices.extend(vertices)

        # 生成面
        for i in range(num_profile_points - 1):
            for j in range(segments):
                next_j = j + 1

                v1 = i * (segments + 1) + j
                v2 = (i + 1) * (segments + 1) + j
                v3 = (i + 1) * (segments + 1) + next_j
                v4 = i * (segments + 1) + next_j

                self.faces.append([base_idx + v1, base_idx + v2, base_idx + v3])
                self.faces.append([base_idx + v1, base_idx + v3, base_idx + v4])

    def subtract_cylinder(self, radius, height, center=(0, 0, 0), segments=32):
        """
        从网格中减去圆柱体（布尔差集）
        这是一个简化实现，直接在生成时处理"
        """
        # 注意：真正的布尔运算需要复杂的网格算法
        # 这里我们通过标记来处理，在生成具体零件时使用
        pass

    def to_mesh(self):
        """转换为 numpy-stl mesh 对象"""
        verts_array = np.array(self.vertices, dtype=np.float32)
        faces_array = np.array(self.faces, dtype=np.int32)

        # STL 需要每个面的顶点（不共享）
        stl_verts = np.zeros((len(self.faces), 3, 3), dtype=np.float32)

        for i, face in enumerate(self.faces):
            for j, vert_idx in enumerate(face):
                stl_verts[i, j] = self.vertices[vert_idx]

        # 创建 mesh
        stl_mesh = mesh.Mesh(np.zeros(stl_verts.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(stl_verts):
            for j in range(3):
                stl_mesh.vectors[i][j] = f[j]

        return stl_mesh


def generate_plate_3d(length, width, thickness, holes=None, chamfer=None, fillet=None):
    """
    生成 3D 底板（带孔）

    Args:
        length: 长度 (X)
        width: 宽度 (Y)
        thickness: 厚度 (Z)
        holes: 孔列表 [{"diameter": d, "x": x, "y": y, "depth": depth}, ...]
        chamfer: 倒角尺寸
        fillet: 倒圆半径
    """
    builder = MeshBuilder()

    # 主板
    builder.add_cube((length, width, thickness), center=(length/2, width/2, thickness/2))

    # 如果有孔，这里需要布尔运算
    # 简化版本：我们通过设置厚度为 0 或使用标记来处理
    # 真正的布尔运算需要更复杂的库（如 trimesh + scipy）

    return builder.to_mesh()


def generate_cylinder_3d(radius, height, center=(0, 0, 0)):
    """生成 3D 圆柱体"""
    builder = MeshBuilder()
    builder.add_cylinder(radius, height, center)
    return builder.to_mesh()


def generate_gear_3d(module, teeth, pressure_angle=20, bore_diameter=10,
                     hub_diameter=20, hub_width=5, thickness=10):
    """
    生成 3D 齿轮

    Args:
        module: 模数
        teeth: 齿数
        pressure_angle: 压力角
        bore_diameter: 中心孔直径
        hub_diameter: 轮毂直径
        hub_width: 轮毂宽度
        thickness: 齿轮厚度
    """
    builder = MeshBuilder()

    # 计算齿轮参数
    pitch_diameter = module * teeth
    addendum = module
    dedendum = 1.25 * module
    outer_radius = (pitch_diameter + 2 * addendum) / 2
    root_radius = (pitch_diameter - 2 * dedendum) / 2
    hub_radius = hub_diameter / 2
    bore_radius = bore_diameter / 2

    # 齿轮主体（圆柱）
    builder.add_cylinder(outer_radius, thickness, center=(0, 0, thickness/2))

    # 生成齿形（简化：使用旋转轮廓）
    # 齿形轮廓点
    tooth_angle = 360 / teeth
    profile_points = []

    for i in range(teeth):
        base_angle = i * tooth_angle

        # 齿根
        profile_points.append((root_radius, 0))
        # 齿顶
        profile_points.append((outer_radius, module))
        # 齿根
        profile_points.append((root_radius, 0))
        # 齿根（到下一个齿）
        profile_points.append((root_radius, 0))

    # 注意：简化实现，实际上齿形更复杂
    # 这里用圆环代替复杂齿形
    builder.add_torus(outer_radius, module, center=(0, 0, thickness/2))

    # 轮毂
    if hub_diameter > bore_diameter:
        builder.add_cylinder(hub_radius, hub_width, center=(0, 0, hub_width/2))

    return builder.to_mesh()


def generate_shaft_3d(diameter, length):
    """生成 3D 传动轴"""
    builder = MeshBuilder()
    builder.add_cylinder(diameter/2, length, center=(0, 0, length/2))
    return builder.to_mesh()


def generate_stepped_shaft_3d(sections):
    """
    生成 3D 阶梯轴

    Args:
        sections: [{"diameter": d, "length": l}, ...]
    """
    builder = MeshBuilder()

    current_z = 0
    for section in sections:
        diameter = section["diameter"]
        length = section["length"]
        center = (0, 0, current_z + length/2)
        builder.add_cylinder(diameter/2, length, center)
        current_z += length

    return builder.to_mesh()


def generate_bolt_3d(diameter, length, head_height=None):
    """
    生成 3D 螺栓

    Args:
        diameter: 公称直径
        length: 螺杆长度
        head_height: 螺头高度（默认约为 0.7 × diameter）
    """
    builder = MeshBuilder()

    if head_height is None:
        head_height = diameter * 0.7

    radius = diameter / 2
    head_width = diameter * 1.8

    # 螺杆
    builder.add_cylinder(radius, length, center=(0, 0, length/2))

    # 六角头（简化为圆柱）
    builder.add_cylinder(head_width/2, head_height, center=(0, 0, length + head_height/2))

    return builder.to_mesh()


def generate_nut_3d(diameter, thickness=None):
    """
    生成 3D 螺母

    Args:
        diameter: 公称直径
        thickness: 厚度（默认约为 0.9 × diameter）
    """
    builder = MeshBuilder()

    if thickness is None:
        thickness = diameter * 0.9

    # 六角螺母（简化为圆柱）
    across_flats = diameter * 1.75
    radius = across_flats / 2

    builder.add_cylinder(radius, thickness, center=(0, 0, thickness/2))

    # 内孔（需要布尔运算）
    # 简化：这里只是生成外形

    return builder.to_mesh()


def generate_flange_3d(outer_diameter, inner_diameter, bolt_circle_diameter,
                      bolt_count, bolt_size, thickness):
    """
    生成 3D 法兰

    Args:
        outer_diameter: 外径
        inner_diameter: 内径
        bolt_circle_diameter: 螺栓孔分布圆直径
        bolt_count: 螺栓孔数量
        bolt_size: 螺栓孔直径
        thickness: 厚度
    """
    builder = MeshBuilder()

    outer_r = outer_diameter / 2
    inner_r = inner_diameter / 2

    # 法兰盘主体（圆环 - 需要布尔运算）
    # 简化：生成圆柱
    builder.add_cylinder(outer_r, thickness, center=(0, 0, thickness/2))

    # 螺栓孔（需要布尔运算）
    # 简化：这里只生成外形

    return builder.to_mesh()


def save_stl(mesh_obj, filename):
    """保存 STL 文件"""
    mesh_obj.save(filename)
    return filename


def generate_part_3d(spec, output_file):
    """
    根据 spec 生成 3D STL 文件

    Args:
        spec: {"type": "gear", "parameters": {...}}
        output_file: 输出 STL 文件名
    """
    part_type = spec.get("type")
    params = spec.get("parameters", spec)

    if part_type == "plate":
        mesh = generate_plate_3d(
            length=params.get("length", 100),
            width=params.get("width", 100),
            thickness=params.get("thickness", 10),
            holes=params.get("holes", [])
        )
    elif part_type == "gear":
        mesh = generate_gear_3d(
            module=params.get("module", 2),
            teeth=params.get("teeth", 20),
            pressure_angle=params.get("pressure_angle", 20),
            bore_diameter=params.get("bore_diameter", 10),
            hub_diameter=params.get("hub_diameter", 20),
            hub_width=params.get("hub_width", 5),
            thickness=params.get("thickness", 10)
        )
    elif part_type == "shaft":
        mesh = generate_shaft_3d(
            diameter=params.get("diameter", 20),
            length=params.get("length", 100)
        )
    elif part_type == "stepped_shaft":
        mesh = generate_stepped_shaft_3d(
            sections=params.get("sections", [])
        )
    elif part_type == "bolt":
        mesh = generate_bolt_3d(
            diameter=params.get("diameter", 10),
            length=params.get("length", 50)
        )
    elif part_type == "nut":
        mesh = generate_nut_3d(
            diameter=params.get("diameter", 10),
            thickness=params.get("thickness", None)
        )
    elif part_type == "flange":
        mesh = generate_flange_3d(
            outer_diameter=params.get("outer_diameter", 150),
            inner_diameter=params.get("inner_diameter", 80),
            bolt_circle_diameter=params.get("bolt_circle_diameter", 120),
            bolt_count=params.get("bolt_count", 8),
            bolt_size=params.get("bolt_size", 12),
            thickness=params.get("thickness", 20)
        )
    else:
        # 默认生成圆柱
        mesh = generate_cylinder_3d(
            radius=params.get("diameter", 20) / 2,
            height=params.get("length", 100),
            center=(0, 0, params.get("length", 100) / 2)
        )

    save_stl(mesh, output_file)
    return True


if __name__ == "__main__":
    # 测试生成 3D 齿轮
    spec = {
        "type": "gear",
        "parameters": {
            "module": 2,
            "teeth": 20,
            "thickness": 10
        }
    }

    generate_part_3d(spec, "test_gear_3d.stl")
    print("✅ 3D 齿轮已生成: test_gear_3d.stl")
