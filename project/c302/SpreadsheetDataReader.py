# -*- coding: utf-8 -*-
# =============================================================================
# 功能描述：
#   从 CElegansNeuronTables.xls 电子表格读取线虫神经元连接数据的数据读取器。
#   是 c302 框架多个可互换数据读取器之一，提供统一的 read_data() 和
#   read_muscle_data() 接口。支持两种 XLS 数据源（神经元连接/肌肉连接）。
#
# 类与方法索引：
#   read_data                            (L43)   — 从 XLS 文件读取神经元连接数据
#   read_muscle_data                     (L111)  — 从 CElegansNeuronTables.xls 第 1 工作表读取神经肌肉连接数据
#   main                                 (L147)  — main 函数
#
# 更新日志：
#   2026-04-16  zmdo  添加中文注释（计划1 阶段二）
#
# 当前维护者：zmdo
# =============================================================================

############################################################

#    读取 CElegansNeuronTables.xls 中神经元连接数据的简单脚本。
#    该模块是多个可互换“数据读取器”之一，可为 c302 提供连接数据

############################################################


from c302.ConnectomeReader import ConnectionInfo
from c302.ConnectomeReader import analyse_connections
from c302 import print_

from xlrd import open_workbook
import os

# XLS 数据文件目录：和模块文件处于同一 data/ 子目录
spreadsheet_location = os.path.dirname(os.path.abspath(__file__)) + "/data/"


READER_DESCRIPTION = (
    """Data extracted from CElegansNeuronTables.xls for neuronal connectivity"""
)


def read_data(include_nonconnected_cells=False, neuron_connect=False):
    """从 XLS 文件读取神经元连接数据。

    :param include_nonconnected_cells: 为 True 时将已知无连接神经元也加入返回列表
    :param neuron_connect: 为 True 时使用 NeuronConnectFormatted.xlsx；否则使用 CElegansNeuronTables.xls
    :return: 元组 (cells, conns)
             - cells: 神经元名称列表
             - conns: ConnectionInfo 连接对象列表
    """
    # 支持两种 XLS 数据源：
    # - neuron_connect=True  使用 NeuronConnectFormatted.xlsx（仅神经元间连接）
    # - neuron_connect=False 使用 CElegansNeuronTables.xls（神经元+肌肉连接）
    if neuron_connect:
        conns = []
        cells = []
        filename = "%sNeuronConnectFormatted.xlsx" % spreadsheet_location
        rb = open_workbook(filename)
        print_("Opened the Excel file: " + filename)

        for row in range(1, rb.sheet_by_index(0).nrows):
            pre = str(rb.sheet_by_index(0).cell(row, 0).value)
            post = str(rb.sheet_by_index(0).cell(row, 1).value)
            syntype = rb.sheet_by_index(0).cell(row, 2).value
            num = int(rb.sheet_by_index(0).cell(row, 3).value)
            # 判断突触类型：包含 'EJ'则为缝隙连接（电穑触），否则为化学穑触
            synclass = "Generic_GJ" if "EJ" in syntype else "Chemical_Synapse"

            conns.append(ConnectionInfo(pre, post, num, syntype, synclass))
            if pre not in cells:
                cells.append(pre)
            if post not in cells:
                cells.append(post)

        return cells, conns

    else:
        conns = []
        cells = []
        # CElegansNeuronTables.xls 表格结构：第 0 工作表为神经元连接，
        # 列顺序：0=pre 1=post 2=syntype 3=num 4=synclass
        filename = "%sCElegansNeuronTables.xls" % spreadsheet_location
        rb = open_workbook(filename)

        print_("Opened Excel file: " + filename)

        # CANL/CANR/VC6 在数据文件中没有连接记录，需要单独添加以包含它们
        known_nonconnected_cells = ["CANL", "CANR", "VC6"]

        for row in range(1, rb.sheet_by_index(0).nrows):
            pre = str(rb.sheet_by_index(0).cell(row, 0).value)
            post = str(rb.sheet_by_index(0).cell(row, 1).value)
            syntype = rb.sheet_by_index(0).cell(row, 2).value
            num = int(rb.sheet_by_index(0).cell(row, 3).value)
            synclass = rb.sheet_by_index(0).cell(row, 4).value

            conns.append(ConnectionInfo(pre, post, num, syntype, synclass))
            if pre not in cells:
                cells.append(pre)
            if post not in cells:
                cells.append(post)

        if include_nonconnected_cells:
            for c in known_nonconnected_cells:
                cells.append(c)

        return cells, conns


def read_muscle_data():
    """从 CElegansNeuronTables.xls 第 1 工作表读取神经肌肉连接数据。

    :return: 元组 (neurons, muscles, conns)
             - neurons: 有肌肉连接的运动神经元名称列表
             - muscles: 肌肉细胞名称列表
             - conns: 神经肌肉 ConnectionInfo 连接对象列表
    """
    conns = []
    neurons = []
    muscles = []

    # 肌肉连接存在于同一 XLS 文件的第 1 工作表（索引 1）
    filename = "%sCElegansNeuronTables.xls" % spreadsheet_location
    rb = open_workbook(filename)

    print_("Opened Excel file: " + filename)

    sheet = rb.sheet_by_index(1)

    for row in range(1, sheet.nrows):
        pre = str(sheet.cell(row, 0).value)
        post = str(sheet.cell(row, 1).value)
        syntype = "Send"  # 肌肉连接均为化学穑触（Send）
        num = int(sheet.cell(row, 2).value)
        synclass = sheet.cell(row, 3).value.replace(",", "plus").replace(" ", "_")

        conns.append(ConnectionInfo(pre, post, num, syntype, synclass))
        if pre not in neurons:
            neurons.append(pre)
        if post not in muscles:
            muscles.append(post)

    return neurons, muscles, conns


def main():
    cells, neuron_conns = read_data(include_nonconnected_cells=True)
    neurons2muscles, muscles, muscle_conns = read_muscle_data()

    analyse_connections(cells, neuron_conns, neurons2muscles, muscles, muscle_conns)


if __name__ == "__main__":
    main()
