# =============================================================================
# 功能描述：
#   NeuroML 网络拓扑图生成工具。
#   解析 .nml 文件中的种群和连接信息，生成 Graphviz DOT 文件并转换为 PNG 图片。
#   节点颜色编码：肌肉（橄榄绿）、运动神经元（浅灰蓝）、其他神经元（淡紫）。
#   边样式编码：电突触（虚线无箭头）、兴奋性化学突触（黑色箭头）、抑制性（红色T形）。
#
# 类与方法索引：
#   usage                                (L40)   — 打印命令行用法说明并退出程序
#   is_muscle                            (L49)   — 判断细胞名称是否为肌肉（以 ``MV`` 或 ``MD`` 开头）
#   get_cells                            (L58)   — 从 NeuroML XML 根节点提取所有种群（Population）的细胞名称
#   get_elec_conns                       (L77)   — 从 NeuroML XML 中提取所有电突触（缝隙连接）并生成 Graphviz 边描述
#   get_chem_conns                       (L109)  — 从 NeuroML XML 中提取所有化学突触连接并生成 Graphviz 边描述
#   write_graph_file                     (L141)  — 将细胞和连接数据写入 Graphviz DOT 格式文件
#   find_nml_files                       (L195)  — 在指定目录中查找所有 ``.nml`` 文件
#   execute_graph_generator              (L215)  — 调用 Graphviz 命令行工具将 DOT 文件转换为 PNG 图片
#   main                                 (L239)  — gen_graph 主入口：解析命令行参数，批量生成网络拓扑图
#
# 更新日志：
#   2026-04-16  Copilot  计划2 阶段八收尾：补记汇总校验与最终勘误完成
#   2026-04-16  Copilot  添加中文 docstring 和行内注释
#
# 当前维护者：Copilot
# =============================================================================
#!/usr/bin/python
"""
Utility for converting NeuroML descriptions to graphs

Originally developed by David Lung: https://github.com/lungd/nml_to_graph
"""

import os
import sys
import xml.etree.ElementTree as ET

from glob import glob
from subprocess import call


def usage(script):
    """打印命令行用法说明并退出程序。

    :param script: 脚本文件名
    """
    print("USAGE: python %s directory [r]" % (script))
    sys.exit(-1)


def is_muscle(cell):
    """判断细胞名称是否为肌肉（以 ``MV`` 或 ``MD`` 开头）。

    :param cell: 细胞名称字符串
    :return: ``True`` 表示是肌肉
    """
    return cell.startswith("MV") or cell.startswith("MD")


def get_cells(root):
    """从 NeuroML XML 根节点提取所有种群（Population）的细胞名称。

    :param root: XML ElementTree 根节点
    :return: 细胞名称列表
    """
    cells = []
    # [废弃] 以下为早期直接定位 network 节点的写法，现改为全树遍历 population 标签
    # network = root.find('network')
    for cell in root.getiterator():
        if "population" not in cell.tag:
            continue
        # [备选] 以下过滤逻辑可在仅绘制神经元时启用，当前保留肌肉节点
        # if is_muscle(cell.attrib['id']):
        #    continue
        cells.append(cell.attrib["id"])
    return cells


def get_elec_conns(root):
    """从 NeuroML XML 中提取所有电突触（缝隙连接）并生成 Graphviz 边描述。

    电连接使用虚线样式（``dashed``）和无箭头（``arrowhead=none``）表示。
    自动去重反向连接（A→B 和 B→A 只保留一条）。

    :param root: XML ElementTree 根节点
    :return: Graphviz 边描述字符串列表
    """
    elec_conns = []
    for elec_conn in root.getiterator():
        if "electricalProjection" not in elec_conn.tag:
            continue
        pre = elec_conn.attrib["presynapticPopulation"]
        post = elec_conn.attrib["postsynapticPopulation"]

        append = True
        for conn in elec_conns:
            if "%s -> %s" % (post, pre) in conn:
                append = False  # 去重：反向连接已存在，不重复添加

        # [备选] 可取消以下过滤，仅保留纯神经元之间的电突触
        # if is_muscle(pre) or is_muscle(post):
        #    continue

        if append:
            elec_conns.append(
                '%s -> %s [style="dashed" minlen=2 arrowhead="none"]' % (pre, post)
            )
    return elec_conns


def get_chem_conns(root):
    """从 NeuroML XML 中提取所有化学突触连接并生成 Graphviz 边描述。

    抑制性连接（含 ``inh``）使用红色 T 形箭头，
    兴奋性连接使用黑色普通箭头。

    :param root: XML ElementTree 根节点
    :return: Graphviz 边描述字符串列表
    """
    chem_conns = []
    for chem_conn in root.getiterator():
        if "continuousProjection" not in chem_conn.tag:
            continue
        pre = chem_conn.attrib["presynapticPopulation"]
        post = chem_conn.attrib["postsynapticPopulation"]

        # [备选] 可取消以下过滤，仅保留纯神经元之间的化学突触
        # if is_muscle(pre) or is_muscle(post):
        #    continue

        for child in chem_conn:
            if "inh" in child.attrib["postComponent"]:
                # 抑制性连接：红色 T 形箭头
                chem_conns.append(
                    '%s -> %s [minlen=2 color=red arrowhead="tee"]' % (pre, post)
                )
            else:
                # 兴奋性连接：黑色普通箭头
                chem_conns.append('%s -> %s [minlen=2 color="black"]' % (pre, post))
    return chem_conns


def write_graph_file(filename, cells, elec_conns, chem_conns, layout="neato"):
    """将细胞和连接数据写入 Graphviz DOT 格式文件。

    节点颜色编码：肌肉为橄榄绿、运动神经元为浅灰蓝、其他为淡紫。

    :param filename: 输出 ``.gv`` 文件路径
    :param cells: 细胞名称列表
    :param elec_conns: 电连接边描述列表
    :param chem_conns: 化学连接边描述列表
    :param layout: Graphviz 布局引擎（默认 ``neato``）
    """
    with open(filename, "w") as graph:
        graph.write("digraph exp {\n")
        graph.write("graph [layout = %s];\n" % layout)

        graph.write("splines=true; ")
        # [备选] Graphviz 的 concentrate 选项可合并平行边，当前为保留细节而关闭
        # graph.write('concentrate=false; ')
        graph.write('sep="+25,25"; ')
        graph.write("overlap=false; ")
        graph.write("fontsize=12;\n")

        graph.write("node [fontsize=11;style=filled]; ")
        for cell in cells:
            graph.write("%s " % cell)
            if is_muscle(cell):
                graph.write('[color="darkolivegreen3"]')   # 肌肉：橄榄绿
            elif (
                cell.startswith("DA")
                or cell.startswith("DB")
                or cell.startswith("DD")
                or cell.startswith("VA")
                or cell.startswith("VB")
                or cell.startswith("VD")
            ):
                graph.write('[color="slategray1"]')        # 运动神经元：浅灰蓝
            else:
                graph.write('[color="thistle2"]')           # 其他神经元：淡紫

            graph.write(";\n")

        graph.write("\n")

        for elec in elec_conns:
            graph.write("%s;\n" % elec)

        for chem in chem_conns:
            graph.write("%s;\n" % chem)

        graph.write("}")

    print("Written file: %s" % filename)


def find_nml_files(directory=".", recursive=False):
    """在指定目录中查找所有 ``.nml`` 文件。

    :param directory: 搜索目录路径
    :param recursive: 是否递归搜索子目录
    :return: ``.nml`` 文件路径列表
    """
    files = []
    for file in os.listdir(directory):
        if file.endswith(".nml"):
            files.append(os.path.join(directory, file))

    if recursive:
        return [
            y for x in os.walk(directory) for y in glob(os.path.join(x[0], "*.nml"))
        ]

    return files


def execute_graph_generator(graphviz_file, fig_file):
    """调用 Graphviz 命令行工具将 DOT 文件转换为 PNG 图片。

    先用 ``neato`` 直接渲染，再用 ``dot → neato`` 两步渲染以优化布局。

    :param graphviz_file: 输入 ``.gv`` 文件路径
    :param fig_file: 输出 ``.png`` 文件路径
    """
    with open(fig_file, "w") as fig:
        call(["neato", "-Tpng", graphviz_file], stdout=fig)
    print(
        "Converted file: %s using neato to %s"
        % (graphviz_file, graphviz_file.replace("gv", "png"))
    )
    os.system(
        "dot -Gsplines=none %s | neato -Gsplines=true -Tpng -o%s"
        % (graphviz_file, fig_file)
    )
    print(
        "Converted file: %s using dot to %s"
        % (graphviz_file, graphviz_file.replace("gv", "png"))
    )


def main():
    """gen_graph 主入口：解析命令行参数，批量生成网络拓扑图。

    对每个 ``.nml`` 文件生成 dot 和 neato 两种布局的图形。
    """
    if len(sys.argv) >= 3:
        filenames = find_nml_files(sys.argv[1], recursive=True)
    else:
        if os.path.isfile(sys.argv[1]):
            filenames = [sys.argv[1]]
        else:
            filenames = find_nml_files(sys.argv[1])

    for filename in sorted(filenames)[:5]:  # 最多处理 5 个文件
        if filename.endswith("nml") and not filename.endswith("cell.nml"):
            print("=============================\nCreating graph for %s" % filename)
            dirname = os.path.dirname(filename)
            tree = ET.parse(filename)
            root = tree.getroot()

            cells = get_cells(root)
            elec_conns = get_elec_conns(root)
            chem_conns = get_chem_conns(root)

            base = os.path.basename(filename)
            graphviz_file = os.path.splitext(base)[0]
            graphviz_file1 = graphviz_file + "_dot.gv"
            graphviz_file2 = graphviz_file + "_neato.gv"

            fig_file = os.path.splitext(base)[0]
            fig_file1 = fig_file + "_dot.png"
            fig_file2 = fig_file + "_neato.png"

            write_graph_file(
                os.path.join(dirname, graphviz_file1),
                cells,
                elec_conns,
                chem_conns,
                layout="dot",
            )
            execute_graph_generator(
                os.path.join(dirname, graphviz_file1), os.path.join(dirname, fig_file1)
            )

            write_graph_file(
                os.path.join(dirname, graphviz_file2),
                cells,
                elec_conns,
                chem_conns,
                layout="neato",
            )
            execute_graph_generator(
                os.path.join(dirname, graphviz_file2), os.path.join(dirname, fig_file2)
            )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage(sys.argv[0])

    main()
