# =============================================================================
# 功能描述：
#   网络拓扑图生成模块（Graphviz DOT 格式）。重写自原 gen_graph.py。
#   从 NeuroML 网络描述生成 DOT 文件，支持 neato/dot 两种布局。
#
# 类与方法索引：
#   _is_muscle_graph                     (L38)   — 判断是否为肌肉细胞（简化版，用于图着色）
#   get_cells                            (L47)   — 从 XML 根节点提取种群 ID 列表
#   get_elec_conns                       (L60)   — 提取电突触连接边（DOT 格式）
#   get_chem_conns                       (L86)   — 提取化学突触连接边（DOT 格式）
#   write_graph_file                     (L113)  — 生成 Graphviz DOT 文件
#   find_nml_files                       (L159)  — 在目录中查找 .nml 文件
#   execute_graph_generator              (L178)  — 调用 Graphviz 将 DOT 文件渲染为 PNG
#   generate_graph                       (L199)  — 从单个 NeuroML 文件生成网络拓扑图（dot + neato 两种布局）
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段七：新建
#
# 当前维护者：Copilot
# =============================================================================
"""网络拓扑图生成（Graphviz DOT 格式）。"""

from __future__ import annotations

import logging
import os
import subprocess
import xml.etree.ElementTree as ET
from glob import glob
from pathlib import Path

logger = logging.getLogger(__name__)

# 运动神经元前缀
_MOTOR_PREFIXES = ("DA", "DB", "DD", "VA", "VB", "VD")


def _is_muscle_graph(cell: str) -> bool:
    """判断是否为肌肉细胞（简化版，用于图着色）。

    :param cell: 细胞名称
    :return: True 表示肌肉
    """
    return cell.startswith("MV") or cell.startswith("MD")


def get_cells(root: ET.Element) -> list[str]:
    """从 XML 根节点提取种群 ID 列表。

    :param root: XML ElementTree 根节点
    :return: 种群 ID 列表
    """
    cells: list[str] = []
    for elem in root.iter():
        if "population" in elem.tag:
            cells.append(elem.attrib["id"])
    return cells


def get_elec_conns(root: ET.Element) -> list[str]:
    """提取电突触连接边（DOT 格式）。

    去重反向连接（A→B 和 B→A 只保留一条）。

    :param root: XML ElementTree 根节点
    :return: DOT 格式边列表
    """
    elec_conns: list[str] = []
    for elem in root.iter():
        if "electricalProjection" not in elem.tag:
            continue
        pre = elem.attrib["presynapticPopulation"]
        post = elem.attrib["postsynapticPopulation"]

        # 去重反向连接
        reverse_exists = any(
            "{} -> {}".format(post, pre) in conn for conn in elec_conns
        )
        if not reverse_exists:
            elec_conns.append(
                '{} -> {} [style="dashed" minlen=2 arrowhead="none"]'.format(pre, post)
            )
    return elec_conns


def get_chem_conns(root: ET.Element) -> list[str]:
    """提取化学突触连接边（DOT 格式）。

    抑制性连接用红色 tee 箭头，兴奋性连接用黑色箭头。

    :param root: XML ElementTree 根节点
    :return: DOT 格式边列表
    """
    chem_conns: list[str] = []
    for elem in root.iter():
        if "continuousProjection" not in elem.tag:
            continue
        pre = elem.attrib["presynapticPopulation"]
        post = elem.attrib["postsynapticPopulation"]

        for child in elem:
            if "inh" in child.attrib.get("postComponent", ""):
                chem_conns.append(
                    '{} -> {} [minlen=2 color=red arrowhead="tee"]'.format(pre, post)
                )
            else:
                chem_conns.append(
                    '{} -> {} [minlen=2 color="black"]'.format(pre, post)
                )
    return chem_conns


def write_graph_file(
    filename: str,
    cells: list[str],
    elec_conns: list[str],
    chem_conns: list[str],
    layout: str = "neato",
) -> None:
    """生成 Graphviz DOT 文件。

    节点着色：肌肉=darkolivegreen3，运动神经元=slategray1，其他=thistle2。

    :param filename: 输出 DOT 文件路径
    :param cells: 种群 ID 列表
    :param elec_conns: 电突触 DOT 边列表
    :param chem_conns: 化学突触 DOT 边列表
    :param layout: 布局引擎名称（neato / dot）
    """
    with open(filename, "w", encoding="utf-8") as graph:
        graph.write("digraph exp {\n")
        graph.write("graph [layout = {}];\n".format(layout))
        graph.write('splines=true; sep="+25,25"; overlap=false; fontsize=12;\n')
        graph.write("node [fontsize=11;style=filled]; ")

        # 写入节点
        for cell in cells:
            if _is_muscle_graph(cell):
                color = "darkolivegreen3"
            elif cell.startswith(_MOTOR_PREFIXES):
                color = "slategray1"
            else:
                color = "thistle2"
            graph.write('{} [color="{}"];\n'.format(cell, color))

        graph.write("\n")

        # 写入边
        for edge in elec_conns:
            graph.write("{};\n".format(edge))
        for edge in chem_conns:
            graph.write("{};\n".format(edge))

        graph.write("}")

    logger.info("已写入 DOT 文件: %s", filename)


def find_nml_files(directory: str = ".", *, recursive: bool = False) -> list[str]:
    """在目录中查找 .nml 文件。

    :param directory: 搜索目录
    :param recursive: 是否递归搜索子目录
    :return: .nml 文件路径列表
    """
    if recursive:
        return [
            y for x in os.walk(directory) for y in glob(os.path.join(x[0], "*.nml"))
        ]

    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".nml")
    ]


def execute_graph_generator(graphviz_file: str, fig_file: str) -> None:
    """调用 Graphviz 将 DOT 文件渲染为 PNG。

    先用 neato 直接渲染，再用 dot→neato 管线渲染。

    :param graphviz_file: DOT 文件路径
    :param fig_file: 输出 PNG 文件路径
    """
    # neato 直接渲染
    with open(fig_file, "w") as fig:
        subprocess.call(["neato", "-Tpng", graphviz_file], stdout=fig)
    logger.info("neato 渲染: %s → %s", graphviz_file, fig_file)

    # dot → neato 管线
    cmd = "dot -Gsplines=none {} | neato -Gsplines=true -Tpng -o{}".format(
        graphviz_file, fig_file
    )
    os.system(cmd)  # noqa: S605 — 与原实现一致，路径来自内部控制
    logger.info("dot+neato 渲染: %s → %s", graphviz_file, fig_file)


def generate_graph(nml_file: str) -> None:
    """从单个 NeuroML 文件生成网络拓扑图（dot + neato 两种布局）。

    :param nml_file: NeuroML 文件路径
    """
    logger.info("生成网络图: %s", nml_file)
    dirname = os.path.dirname(nml_file)
    tree = ET.parse(nml_file)  # noqa: S314 — 内部文件
    root = tree.getroot()

    cells = get_cells(root)
    elec_conns = get_elec_conns(root)
    chem_conns = get_chem_conns(root)

    base = os.path.splitext(os.path.basename(nml_file))[0]

    # dot 布局
    gv_dot = os.path.join(dirname, base + "_dot.gv")
    fig_dot = os.path.join(dirname, base + "_dot.png")
    write_graph_file(gv_dot, cells, elec_conns, chem_conns, layout="dot")
    execute_graph_generator(gv_dot, fig_dot)

    # neato 布局
    gv_neato = os.path.join(dirname, base + "_neato.gv")
    fig_neato = os.path.join(dirname, base + "_neato.png")
    write_graph_file(gv_neato, cells, elec_conns, chem_conns, layout="neato")
    execute_graph_generator(gv_neato, fig_neato)
