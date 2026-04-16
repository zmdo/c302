# =============================================================================
# 功能描述：
#   连接组数据读取层的基础定义：ConnectionInfo 数据类、BaseDataReader 抽象基类、
#   细胞类型判断工具函数，以及从 YAML 加载的神经元/肌肉名称常量。
#
# 类与方法索引：
#   ConnectionInfo                       (L42)   — 两个细胞之间的一条突触连接记录
#     __str__                            (L73)   — 格式化连接信息为可读字符串
#     short                              (L83)   — 返回连接的简短文字描述
#     __eq__                             (L92)   — 判断两个连接记录是否相等
#     __lt__                             (L103)  — 按细胞名称拼接字符串排序
#     __repr__                           (L111)  — repr 输出
#   BaseDataReader                       (L115)  — 连接组数据读取器抽象基类
#     read_data                          (L119)  — 读取神经元连接组数据（抽象方法）
#     read_muscle_data                   (L131)  — 读取神经元-肌肉连接数据（抽象方法）
#   _load_names                          (L143)  — 从 YAML 文件加载名称列表
#   convert_to_preferred_muscle_name     (L159)  — 将 BWM-* 前缀的肌肉名称转换为标准格式
#   get_all_muscle_prefixes              (L178)  — 返回所有已知肌肉名称前缀
#   get_body_wall_muscle_prefixes        (L186)  — 返回体壁肌肉专属前缀
#   is_muscle                            (L194)  — 判断给定细胞是否为肌肉细胞
#   is_body_wall_muscle                  (L203)  — 判断给定细胞是否为体壁肌肉
#   is_neuron                            (L212)  — 判断给定细胞是否为神经元
#   remove_leading_index_zero            (L221)  — 去掉神经元编号的前导零
#   check_neurons                        (L232)  — 将细胞列表与标准神经元名称做三路比对
#   analyse_connections                  (L256)  — 打印连接组统计摘要
#
# 更新日志：
#   2026-04-17  yi  初始创建：从 ConnectomeReader.py 提取重写
#
# 当前维护者：yi
# =============================================================================
"""连接组数据读取层的基础定义。"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import yaml

from c302.utils.helpers import get_data_dir

logger = logging.getLogger(__name__)


@dataclass
class ConnectionInfo:
    """两个细胞之间的一条突触连接记录。

    :param pre_cell: 突触前细胞名称（发送信号方）
    :param post_cell: 突触后细胞名称（接收信号方）
    :param number: 突触数量（连接权重）
    :param syntype: 突触类型：``"Send"``（化学突触）或 ``"GapJunction"``（电突触）
    :param synclass: 神经递质分类，如 ``"Acetylcholine"``、``"GABA"``、``"Generic_GJ"``
    """

    pre_cell: str
    post_cell: str
    number: int
    syntype: str
    synclass: str

    def __str__(self) -> str:
        """格式化连接信息为可读字符串。"""
        return (
            "Connection from %s to %s (%i times, type: %s, neurotransmitter: %s)"
            % (self.pre_cell, self.post_cell, self.number, self.syntype, self.synclass)
        )

    def short(self) -> str:
        """返回连接的简短文字描述（不含突触计数）。

        :return: 格式为 ``"Connection from X to Y (syntype)"`` 的字符串
        """
        return "Connection from %s to %s (%s)" % (
            self.pre_cell,
            self.post_cell,
            self.syntype,
        )

    def __eq__(self, other: object) -> bool:
        """判断两个连接记录是否相等。"""
        if not isinstance(other, ConnectionInfo):
            return NotImplemented
        return (
            self.pre_cell == other.pre_cell
            and self.post_cell == other.post_cell
            and self.number == other.number
            and self.syntype == other.syntype
            and self.synclass == other.synclass
        )

    def __lt__(self, other: "ConnectionInfo") -> bool:
        """按细胞名称拼接字符串排序。"""
        return (self.pre_cell + self.post_cell) < (other.pre_cell + other.post_cell)

    def __repr__(self) -> str:
        """repr 输出。"""
        return self.__str__()


class BaseDataReader(ABC):
    """连接组数据读取器抽象基类。"""

    @staticmethod
    @abstractmethod
    def read_data(
        include_nonconnected_cells: bool = False,
    ) -> tuple[list[str], list[ConnectionInfo]]:
        """读取神经元连接组数据。

        :param include_nonconnected_cells: 是否包含无连接的细胞
        :return: ``(cells, conns)`` — 细胞名称列表和连接信息列表
        """
        ...

    @staticmethod
    @abstractmethod
    def read_muscle_data() -> tuple[list[str], list[str], list[ConnectionInfo]]:
        """读取神经元-肌肉连接数据。

        :return: ``(neurons, muscles, conns)`` — 运动神经元列表、肌肉列表、连接列表
        """
        ...


def _load_names(filename: str) -> list[str]:
    """从 YAML 文件加载名称列表。

    :param filename: 文件名（相对于 ``data/connectome/``）
    :return: 名称列表
    """
    path = get_data_dir() / "connectome" / filename
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # YAML 根键对应的列表
    key = list(data.keys())[0]
    return data[key]


def convert_to_preferred_muscle_name(muscle: str) -> str:
    """将 ``BWM-*`` 前缀的肌肉名称转换为标准格式。

    :param muscle: 原始肌肉名称，如 ``"BWM-VL01"``
    :return: 标准格式名称，如 ``"MVL01"``；无法识别时返回原名加 ``"???"``
    """
    # BWM-VL01 → MVL01, BWM-DR03 → MDR03
    if muscle.startswith("BWM-VL"):
        return "MVL%s" % muscle[6:]
    elif muscle.startswith("BWM-VR"):
        return "MVR%s" % muscle[6:]
    elif muscle.startswith("BWM-DL"):
        return "MDL%s" % muscle[6:]
    elif muscle.startswith("BWM-DR"):
        return "MDR%s" % muscle[6:]
    elif muscle == "LegacyBodyWallMuscles":
        return "BWM"
    else:
        return muscle + "???"


def get_all_muscle_prefixes() -> list[str]:
    """返回所有已知肌肉名称前缀（含体壁肌肉和咽部肌肉）。

    :return: 肌肉前缀字符串列表
    """
    return ["pm", "vm", "um", "BWM-D", "BWM-V", "LegacyBodyWallMuscles", "vBWM", "dBWM"]


def get_body_wall_muscle_prefixes() -> list[str]:
    """返回体壁肌肉专属前缀（不含咽部肌肉）。

    :return: 体壁肌肉前缀字符串列表
    """
    return ["BWM-D", "BWM-V", "LegacyBodyWallMuscles", "vBWM", "dBWM"]


def is_muscle(cell: str) -> bool:
    """判断给定细胞名称是否为肌肉细胞（含体壁肌肉和咽部肌肉）。

    :param cell: 细胞名称字符串
    :return: True 表示为肌肉细胞
    """
    return cell.startswith(tuple(get_all_muscle_prefixes()))


def is_body_wall_muscle(cell: str) -> bool:
    """判断给定细胞名称是否为体壁肌肉（排除咽部肌肉）。

    :param cell: 细胞名称字符串
    :return: True 表示为体壁肌肉
    """
    return cell.startswith(tuple(get_body_wall_muscle_prefixes()))


def is_neuron(cell: str) -> bool:
    """判断给定细胞是否为神经元（非体壁肌肉即视为神经元）。

    :param cell: 细胞名称字符串
    :return: True 表示为神经元
    """
    return not is_body_wall_muscle(cell)


def remove_leading_index_zero(cell: str) -> str:
    """去掉神经元编号的前导零。

    例如 ``VB01`` → ``VB1``。

    :param cell: 细胞名称字符串
    :return: 规范化后的名称
    """
    if is_neuron(cell) and cell[-2:].startswith("0"):
        return "%s%s" % (cell[:-2], cell[-1:])
    return cell


def check_neurons(cells: list[str]) -> tuple[list[str], list[str], list[str]]:
    """将细胞列表与标准神经元名称集合做三路比对。

    :param cells: 待校验的细胞名称列表
    :return: ``(preferred, not_in_preferred, missing_preferred)``
    """
    preferred = []
    not_in_preferred = []
    missing_preferred = list(NEURONS)
    for c in cells:
        if c not in NEURONS:
            not_in_preferred.append(c)
        else:
            preferred.append(c)
        if c in missing_preferred:
            missing_preferred.remove(c)
    return preferred, not_in_preferred, missing_preferred


def analyse_connections(
    cells: list[str],
    neuron_conns: list[ConnectionInfo],
    neurons2muscles: list[str],
    muscles: list[str],
    muscle_conns: list[ConnectionInfo],
) -> None:
    """打印连接组完整统计摘要，用于调试和验证数据读取器输出。

    :param cells: 神经元名称列表
    :param neuron_conns: 神经元间连接列表
    :param neurons2muscles: 有肌肉连接的运动神经元列表
    :param muscles: 肌肉细胞名称列表
    :param muscle_conns: 神经肌肉连接列表
    """
    logger.info("Found %s cells: %s", len(cells), sorted(cells))

    # 校验神经元名称
    preferred, not_in_preferred, missing_preferred = check_neurons(cells)
    logger.info("Found %s non-neuron(s): %s", len(not_in_preferred), sorted(not_in_preferred))
    logger.info("Known neurons not present: %s", sorted(missing_preferred))
    logger.info("Found %s neuron-neuron connections", len(neuron_conns))

    # 按神经递质分类统计神经元间连接
    nts: dict[str, int] = {}
    nts_tot: dict[str, int] = {}
    for c in neuron_conns:
        nt = c.synclass
        if nt not in nts:
            nts[nt] = 0
            nts_tot[nt] = 0
        nts[nt] += 1
        nts_tot[nt] += c.number
    for nt in sorted(nts.keys()):
        logger.info(
            "  %s: %s connections, %s synapses (avg %.3f)",
            nt, nts[nt], nts_tot[nt], nts_tot[nt] / nts[nt],
        )

    # 肌肉统计
    logger.info("Found %s muscles: %s", len(muscles), sorted(muscles))
    not_in_preferred_m = [m for m in muscles if m not in MUSCLES]
    logger.info("Unidentified muscles: %s", sorted(not_in_preferred_m))
    logger.info("Found %i neurons connected to muscles", len(neurons2muscles))
    logger.info("Found %i neuron-muscle connections", len(muscle_conns))

    # 按神经递质分类统计神经肌肉连接
    nts_m: dict[str, int] = {}
    nts_tot_m: dict[str, int] = {}
    for c in muscle_conns:
        nt = c.synclass
        if nt not in nts_m:
            nts_m[nt] = 0
            nts_tot_m[nt] = 0
        nts_m[nt] += 1
        nts_tot_m[nt] += c.number
    for nt in sorted(nts_m.keys()):
        logger.info(
            "  %s: %s muscle connections, %s synapses (avg %.3f)",
            nt, nts_m[nt], nts_tot_m[nt], nts_tot_m[nt] / nts_m[nt],
        )


# 302 个神经元名称（从 ConnectomeReader.py PREFERRED_NEURON_NAMES 提取）
NEURONS: list[str] = _load_names("neurons.yaml")

# 97 个肌肉名称（从 ConnectomeReader.py PREFERRED_MUSCLE_NAMES 提取）
MUSCLES: list[str] = _load_names("muscles.yaml")
