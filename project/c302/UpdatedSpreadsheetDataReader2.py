# =============================================================================
# 功能描述：
#   与 UpdatedSpreadsheetDataReader 功能相同，但使用手动修正版数据文件
#   herm_full_edgelist_MODIFIED.csv，并对肌肉连接过滤规则做了调整
#   （仅保留 pre=神经元 且 post=体壁肌肉 的连接，过滤更严格）。
#
# 类与方法索引：
#   get_all_muscle_prefixes              (L52)   — 返回所有已知肌肉前缀列表（含体壁肌肉和咽部肌肉）
#   get_body_wall_muscle_prefixes        (L60)   — 返回体壁肌肉专属前缀列表
#   is_muscle                            (L68)   — 判断给定细胞名称是否为肌肉细胞
#   is_body_wall_muscle                  (L79)   — 判断给定细胞名称是否为体壁肌肉
#   is_neuron                            (L90)   — 判断给定细胞名称是否为神经元
#   remove_leading_index_zero            (L100)  — Returns neuron name with an index without leading zero. E.g. VB01 -> VB1.
#   get_old_muscle_name                  (L110)  — 将 herm_full_edgelist_MODIFIED 格式的肌肉名称转换为标准命名格式
#   get_syntype                          (L131)  — 将 CSV 中的穑触类型字符串映射为 ConnectionInfo 标准形式
#   get_synclass                         (L147)  — 根据穑触前细胞名称和穑触类型推断神经递质分类
#   parse_row                            (L165)  — 解析 CSV 中的单行数据，返回连接信息元组
#   read_data                            (L179)  — Args:
#   read_muscle_data                     (L222)  — Returns:
#   main                                 (L266)  — main 函数
#
# 更新日志：
#   2026-04-16  zmdo  添加中文注释（计划1 阶段二）
#
# 当前维护者：zmdo
# =============================================================================

############################################################

#    读取 herm_full_edgelist_MODIFIED.csv 中神经元连接数据的简单脚本。
#    与 UpdatedSpreadsheetDataReader 相比，使用的 CSV 为手动修改版（MODIFIED）。

#    该模块是多个可互换“数据读取器”之一，可为 c302 提供连接数据

############################################################

import csv


from c302.ConnectomeReader import ConnectionInfo
from c302.ConnectomeReader import analyse_connections
import os

from c302 import print_

# CSV 数据文件目录：和模块文件处于同一 data/ 子目录
spreadsheet_location = os.path.dirname(os.path.abspath(__file__)) + "/data/"
# MODIFIED 版本是在原始 herm_full_edgelist.csv 基础上手动调整的修正版本
filename = "%sherm_full_edgelist_MODIFIED.csv" % spreadsheet_location


def get_all_muscle_prefixes():
    """返回所有已知肌肉前缀列表（含体壁肌肉和咽部肌肉）。

    :return: 肌肉前缀字符串列表
    """
    return ["pm", "vm", "um", "dBWM", "vBWM"]


def get_body_wall_muscle_prefixes():
    """返回体壁肌肉专属前缀列表。

    :return: 体壁肌肉前缀字符串列表
    """
    return ["dBWM", "vBWM"]


def is_muscle(cell):
    """判断给定细胞名称是否为肌肉细胞。

    :param cell: 细胞名称字符串
    :return: True 表示为肌肉细胞
    """
    # 匹配 pm/vm/um/dBWM/vBWM 前缀的肌肉名称
    known_muscle_prefixes = get_all_muscle_prefixes()
    return cell.startswith(tuple(known_muscle_prefixes))


def is_body_wall_muscle(cell):
    """判断给定细胞名称是否为体壁肌肉。

    :param cell: 细胞名称字符串
    :return: True 表示为体壁肌肉
    """
    # 匹配 dBWM/vBWM 体壁肌肉前缀（舃/腹侧）
    known_muscle_prefixes = get_body_wall_muscle_prefixes()
    return cell.startswith(tuple(known_muscle_prefixes))


def is_neuron(cell):
    """判断给定细胞名称是否为神经元。

    :param cell: 细胞名称字符串
    :return: True 表示为神经元
    """
    # CSV 格式中神经元名以大写字母开头，肌肉细胞以小写前缀开头
    return cell[0].isupper()


def remove_leading_index_zero(cell):
    """
    Returns neuron name with an index without leading zero. E.g. VB01 -> VB1.
    """
    # 规范化神经元编号：去掉倒数第二位的前导零，使其与 PREFERRED_NEURON_NAMES 一致
    if is_neuron(cell) and cell[-2:].startswith("0"):
        return "%s%s" % (cell[:-2], cell[-1:])
    return cell


def get_old_muscle_name(muscle):
    """将 herm_full_edgelist_MODIFIED 格式的肌肉名称转换为标准命名格式。

    :param muscle: 原始肌肉名称，如 'vBWML05'
    :return: 标准名称，如 'MVL05'；无法匹配时返回 None
    """
    # 将 vBWML01 / dBWMR23 转换为标准名称 MVL01 / MDR23
    # 返回值格式与 ConnectomeReader.PREFERRED_MUSCLE_NAMES 中的名称一致
    index = int(muscle[5:])
    if index < 10:
        index = "0%s" % index
    if muscle.startswith("vBWML"):
        return "MVL%s" % index
    elif muscle.startswith("vBWMR"):
        return "MVR%s" % index
    elif muscle.startswith("dBWML"):
        return "MDL%s" % index
    elif muscle.startswith("dBWMR"):
        return "MDR%s" % index


def get_syntype(syntype):
    """将 CSV 中的穑触类型字符串映射为 ConnectionInfo 标准形式。

    :param syntype: CSV 中的穑触类型，如 'electrical' 或 'chemical'
    :return: 标准化穑触类型字符串
    :raises NotImplementedError: 无法解析的穑触类型时抛出
    """
    # 将 CSV 中的穑触类型字符串转换为 ConnectionInfo 中使用的标准形式
    if syntype == "electrical":
        return "GapJunction"
    elif syntype == "chemical":
        return "Send"
    else:
        raise NotImplementedError("Cannot parse syntype '%s'" % syntype)


def get_synclass(cell, syntype):
    """根据穑触前细胞名称和穑触类型推断神经递质分类。

    :param cell: 穑触前细胞名称
    :param syntype: 穑触类型（由 get_syntype 处理后的标准形式）
    :return: 神经递质分类字符串，如 'Generic_GJ'、'GABA'、'Acetylcholine'
    """
    # 简化处理：通过神经元名称前缀推断神经递质类型
    # DD/VD 类运动神经元发出 GABA，其他使用乙酰胆碱
    # dirty hack
    if syntype == "GapJunction":
        return "Generic_GJ"
    else:
        if cell.startswith("DD") or cell.startswith("VD"):
            return "GABA"
        return "Acetylcholine"


def parse_row(row):
    """解析 CSV 中的单行数据，返回连接信息元组。

    :param row: csv.DictReader 返回的字典行
    :return: 元组 (pre, post, num, syntype, synclass)
    """
    pre = str.strip(row["Source"])
    post = str.strip(row["Target"])
    num = int(row["Weight"])
    syntype = get_syntype(str.strip(row["Type"]))
    synclass = get_synclass(pre, syntype)
    return pre, post, num, syntype, synclass


def read_data(include_nonconnected_cells=False):
    """
    Args:
        include_nonconnected_cells (bool): Also append neurons without known connections to other neurons to the 'cells' list. True if they should get appended, False otherwise.
    Returns:
        cells (:obj:`list` of :obj:`str`): List of neurons
        conns (:obj:`list` of :obj:`ConnectionInfo`): List of connections from neuron to neuron
    """

    conns = []
    cells = []

    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        print_("Opened file: " + filename)

        known_nonconnected_cells = ["CANL", "CANR"]

        for row in reader:
            pre, post, num, syntype, synclass = parse_row(row)

            if not is_neuron(pre) or not is_neuron(post):
                continue  # 跳过：pre 或 post 不是神经元（可能是肌肉细胞）

            pre = remove_leading_index_zero(pre)
            post = remove_leading_index_zero(post)

            conns.append(ConnectionInfo(pre, post, num, syntype, synclass))
            # print ConnectionInfo(pre, post, num, syntype, synclass)
            # 将神经元加入并去重，保证神经元列表不重复
            if pre not in cells:
                cells.append(pre)
            if post not in cells:
                cells.append(post)

        if include_nonconnected_cells:
            for c in known_nonconnected_cells:
                if c not in cells:
                    cells.append(c)

    return cells, conns


def read_muscle_data():
    """
    Returns:
        neurons (:obj:`list` of :obj:`str`): List of motor neurons. Each neuron has at least one connection with a post-synaptic muscle cell.
        muscles (:obj:`list` of :obj:`str`): List of muscle cells.
        conns (:obj:`list` of :obj:`ConnectionInfo`): List of neuron-muscle connections.
    """

    neurons = []
    muscles = []
    conns = []

    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        print_("Opened file: " + filename)

        for row in reader:
            pre, post, num, syntype, synclass = parse_row(row)

            if (
                not is_neuron(pre) and not is_body_wall_muscle(pre)
            ) or not is_body_wall_muscle(post):
                # 跳过：只保留 pre=神经元 且 post=体壁肌肉 的连接
                # Don't add connections unless pre=neuron and post=body_wall_muscle
                continue

            if is_neuron(pre):
                pre = remove_leading_index_zero(pre)
            else:
                pre = get_old_muscle_name(pre)
            post = get_old_muscle_name(post)

            conns.append(ConnectionInfo(pre, post, num, syntype, synclass))
            # print ConnectionInfo(pre, post, num, syntype, synclass)
            if is_neuron(pre) and pre not in neurons:
                neurons.append(pre)
            elif is_body_wall_muscle(pre) and pre not in muscles:
                muscles.append(pre)
            if post not in muscles:
                muscles.append(post)

    return neurons, muscles, conns


def main():
    cells, neuron_conns = read_data(include_nonconnected_cells=True)
    neurons2muscles, muscles, muscle_conns = read_muscle_data()

    analyse_connections(cells, neuron_conns, neurons2muscles, muscles, muscle_conns)


if __name__ == "__main__":
    main()
