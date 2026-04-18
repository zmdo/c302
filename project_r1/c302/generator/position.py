# =============================================================================
# 功能描述：
#   3D 位置计算模块。提供从形态文件加载神经元 soma 位置、计算肌肉坐标、
#   以及肌肉名称相关的工具函数。
#
# 类与方法索引：
#   get_cell_position                    (L62)   — 从 NeuroML 形态文件中读取细胞 soma 位置
#   get_muscle_position                  (L78)   — 根据肌肉名称计算其在虫体中的三维坐标
#   is_body_wall_muscle                  (L118)  — 判断细胞名称是否为体壁肌肉（匹配 ``M[VD][LR]<digits>`` 模式）
#   get_muscle_names                     (L127)  — 生成全部 96 条体壁肌肉的名称列表
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段四：从 __init__.py 提取重写
#
# 当前维护者：Copilot
# =============================================================================
"""3D 位置计算模块。"""
import logging
import re

import neuroml.loaders as loaders

from c302.utils.helpers import get_morphology_dir

logger = logging.getLogger(__name__)

# 体壁肌肉名称正则：M[VD][LR]<digits>
MUSCLE_RE = re.compile(r"M([VD][LR])(\d+)")

# 四个象限名称前缀
QUADRANT_MDR = "MDR"
QUADRANT_MVR = "MVR"
QUADRANT_MVL = "MVL"
QUADRANT_MDL = "MDL"

# 运动神经元 soma 位置（来源：wormatlas.org - 2.2 神经元描述）
VB_SOMA_POS: dict[str, float] = {
    "VB1": 0.21,
    "VB2": 0.19,
    "VB3": 0.28,
    "VB4": 0.32,
    "VB5": 0.38,
    "VB6": 0.45,
    "VB7": 0.5,
    "VB8": 0.57,
    "VB9": 0.61,
    "VB10": 0.67,
    "VB11": 0.72,
}

DB_SOMA_POS: dict[str, float] = {
    "DB1": 0.24,
    "DB2": 0.21,
    "DB3": 0.3,
    "DB4": 0.39,
    "DB5": 0.51,
    "DB6": 0.62,
    "DB7": 0.72,
}


def get_cell_position(cell: str) -> tuple[float, float, float]:
    """从 NeuroML 形态文件中读取细胞 soma 位置。

    加载 ``data/morphology/{cell}.cell.nml`` 文件，
    返回第一个 segment 的 proximal 坐标。

    :param cell: 细胞名称
    :return: ``(x, y, z)`` 坐标元组
    """
    cell_file = get_morphology_dir() / f"{cell}.cell.nml"
    doc = loaders.NeuroMLLoader.load(str(cell_file))
    # 取第一个 segment 的 proximal 点作为 soma 位置
    location = doc.cells[0].morphology.segments[0].proximal
    return float(location.x), float(location.y), float(location.z)


def get_muscle_position(muscle: str) -> tuple[float, float, float]:
    """根据肌肉名称计算其在虫体中的三维坐标。

    按照命名模式 ``M[VD][LR]<index>`` 解析：
    - D/V 决定 z 轴方向（+80/-80）
    - L/R 决定 x 轴方向（+80/-80）
    - index 决定 y 轴位置（-300 + 30*index）

    特殊肌肉（MANAL/MVULVA）返回原点 ``(0, 0, 0)``。

    :param muscle: 肌肉名称字符串
    :return: ``(x, y, z)`` 坐标元组
    :raises ValueError: 无法识别的肌肉名称格式
    """
    # 特殊肌肉返回原点
    if muscle in ("MANAL", "MVULVA"):
        return 0.0, 0.0, 0.0

    # 尝试 M[VD][LR]<digits> 或 [VD][LR]<digits> 格式
    pat1 = r"M([VD])([LR])(\d+)"
    pat2 = r"([VD])([LR])(\d+)"
    md = re.fullmatch(pat1, muscle)
    if not md:
        md = re.fullmatch(pat2, muscle)

    if md:
        dv = md.group(1)
        lr = md.group(2)
        idx = md.group(3)
        # L → 正 x，R → 负 x
        x = 80.0 * (1 if lr == "L" else -1)
        # D → 正 z，V → 负 z
        z = 80.0 * (-1 if dv == "V" else 1)
        # 沿体轴按索引均匀分布
        y = -300.0 + 30.0 * int(idx)
        return x, y, z

    raise ValueError("无法识别的肌肉名称格式: %s" % muscle)


def is_body_wall_muscle(cell_name: str) -> bool:
    """判断细胞名称是否为体壁肌肉（匹配 ``M[VD][LR]<digits>`` 模式）。

    :param cell_name: 细胞名称字符串
    :return: True 表示为体壁肌肉
    """
    return MUSCLE_RE.fullmatch(cell_name) is not None


def get_muscle_names() -> list[str]:
    """生成全部 96 条体壁肌肉的名称列表。

    按象限顺序（MDR/MVR/MVL/MDL）× 24 条/象限生成，
    编号 01~24，低位数字补零（如 ``MDR01``）。

    :return: 96 个肌肉名称的列表
    """
    names: list[str] = []
    for quadrant in (QUADRANT_MDR, QUADRANT_MVR, QUADRANT_MVL, QUADRANT_MDL):
        for i in range(1, 25):
            # 1-9 补零为 01-09，10-24 保持原样
            names.append("%s%s" % (quadrant, ("0%i" % i) if i <= 9 else str(i)))
    return names
