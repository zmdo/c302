# =============================================================================
# 功能描述：
#   连接组数据比较工具。
#   比较两个 XLS 格式的线虫连接组数据文件，找出匹配的连接对、
#   仅存在于某一文件的独有连接，以及方向相反的连接对。
#
# 类与方法索引：
#   comparitor                           (L28)   — 比较两个 XLS 连接组数据文件的差异
#   getColumns                           (L106)  — 从制表符分隔的文本文件中读取列数据
#   getColumnsXls                        (L140)  — 从 XLS 电子表格文件中读取列数据
#   sortTwoColumns                       (L182)  — 按前两列（From/To 神经元）对字典进行排序
#   formatNames                          (L191)  — 格式化神经元名称，移除中间的填充零
#   matchLists                           (L204)  — 比较两个连接列表，提取匹配对并从原列表中移除
#   typeMapping                          (L332)  — 连接类型映射（未完成）
#
# 更新日志：
#   2026-04-16  Copilot  添加中文 docstring 和行内注释
#
# 当前维护者：Copilot
# =============================================================================
__author__ = "Ari"

from operator import itemgetter
import xlrd
import os


def comparitor(fName1, fName2):
    """比较两个 XLS 连接组数据文件的差异。

    读取两个 XLS 文件，格式化名称后进行配对匹配，
    输出匹配对、仅存在于文件1的连接、仅存在于文件2的连接。

    :param fName1: 第一个 XLS 文件路径
    :param fName2: 第二个 XLS 文件路径
    """
    path1 = fName1
    path2 = fName2
    dir = os.path.dirname(__file__)
    file1 = os.path.join(dir, path1)
    file2 = os.path.join(dir, path2)

    # 读取 XLS 文件，将数据存入字典
    cols1, indexName1 = getColumnsXls(file1)
    cols2, indexName2 = getColumnsXls(file2)

    # 格式化神经元名称并按字母顺序排列
    formatNames(cols1, indexName1)
    formatNames(cols2, indexName2)
    sortTwoColumns(cols1)
    sortTwoColumns(cols2)

    # 提取匹配的连接对，并从原列表中移除已匹配项
    matches, col1, col2 = matchLists(cols1, cols2, indexName1, indexName2)

    # 输出结果：匹配对数、文件1独有对、文件2独有对
    print("Number of matching pairs: " + str(len(matches[indexName2[0]])))
    for p in range(len(matches[indexName2[0]])):
        print(
            str(matches[indexName2[0]][p])
            + " -> "
            + str(matches[indexName2[1]][p])
            + " ("
            + str(matches[indexName2[2]][p])
            + ", "
            + str(matches[indexName2[3]][p])
            + ")"
        )
    print(
        "\nNumber of pairs unmatched in "
        + fName1
        + " is: "
        + str(len(col1[indexName2[0]]))
    )
    for p in range(len(col1[indexName2[0]])):
        print(
            str(col1[indexName2[0]][p])
            + " -> "
            + str(col1[indexName2[1]][p])
            + " ("
            + str(col1[indexName2[2]][p])
            + ", "
            + str(col1[indexName2[3]][p])
            + ")"
        )
    print(
        "\nNumber of pairs unmatched in "
        + fName2
        + " is: "
        + str(len(col2[indexName1[0]]))
    )
    for p in range(len(col2[indexName1[0]])):
        print(
            str(col2[indexName1[0]][p])
            + " -> "
            + str(col2[indexName1[1]][p])
            + " ("
            + str(col2[indexName1[2]][p])
            + ", "
            + str(col2[indexName1[3]][p])
            + ")"
        )


# 从制表符分隔的文本文件中读取列数据
def getColumns(fileIn, delim="\t", header=True):
    """从制表符分隔的文本文件中读取列数据。

    :param fileIn: 已打开的文件对象
    :param delim: 列分隔符（默认制表符）
    :param header: 首行是否为表头
    :return: ``(cols, indexName)`` 二元组，cols 为列数据字典，indexName 为列索引映射
    """
    cols = {}
    indexName = {}
    for lineNum, line in enumerate(fileIn):
        if lineNum == 0:
            headings = line.split(delim)
            i = 0
            for heading in headings:
                heading = heading.strip()
                if header:
                    cols[heading] = []
                    indexName[i] = heading
                else:
                    cols[i] = [heading]
                    indexName[i] = i
                i += 1
        else:
            cells = line.split(delim)
            i = 0
            for cell in cells:
                cell = cell.strip()
                cols[indexName[i]] += [cell]
                i += 1
    return cols, indexName


# 从 XLS 电子表格中读取列数据
def getColumnsXls(fileIn):
    """从 XLS 电子表格文件中读取列数据。

    使用 xlrd 打开工作簿，读取第一个工作表的前 4 列。

    :param fileIn: XLS 文件路径
    :return: ``(cols, indexName)`` 二元组，cols 为列数据字典，indexName 为列索引映射
    """
    cols = {}
    indexName = {}
    workbook = xlrd.open_workbook(fileIn)
    # [废弃] 以下为按工作表名称读取的旧写法，当前统一读取第一个工作表
    # worksheet = workbook.sheet_by_name('Sheet1')
    worksheet = workbook.sheet_by_index(0)
    num_rows = worksheet.nrows - 1
    # [备选] 也可读取工作表的全部列数，当前仅处理前 4 列
    # num_cells = worksheet.ncols
    num_cells = 3
    curr_row = 0
    for c in range(4):
        indexName[c] = str(worksheet.cell_value(curr_row, c))
        cols[indexName[c]] = []
        # [调试] 可取消注释以检查表头列名是否读取正确
        # print(indexName[c])
    while curr_row < num_rows:
        curr_row += 1
        # [调试] 以下为逐行读取工作表时的旧调试输出
        # row = worksheet.row(curr_row)
        # print('Row:', curr_row)
        curr_cell = -1
        while curr_cell < num_cells:
            curr_cell += 1
            # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
            # [调试] 可取消注释以检查 xlrd 解析出的单元格类型与内容
            # cell_type = worksheet.cell_type(curr_row, curr_cell)
            cell_value = str(worksheet.cell_value(curr_row, curr_cell))
            # print('	', cell_type, ':', cell_value)
            cols[indexName[curr_cell]] += [cell_value]
    return cols, indexName


# 按前两列（From/To 神经元）对字典排序
def sortTwoColumns(cols):
    """按前两列（From/To 神经元）对字典进行排序。

    :param cols: 列数据字典
    """
    cols = sorted(cols, key=itemgetter(0, 1))


# 格式化神经元名称，移除字符串中间的填充零
def formatNames(cols, indexName):
    """格式化神经元名称，移除中间的填充零。

    :param cols: 列数据字典
    :param indexName: 列索引映射
    """
    for i in range(2):
        for char in cols[indexName[i]]:
            if char[-1] != "0":
                char = "".join(char.split("0", 1))


# 比较两个列表，提取匹配对并从原列表中移除
def matchLists(cols1, cols2, indexName1, indexName2):
    # 确保 col1 始终是较长的列表
    """比较两个连接列表，提取匹配对并从原列表中移除。

    执行三轮匹配：
    1. 在长列表与短列表之间查找完全匹配的连接对
    2. 在长列表与已匹配列表之间查找重复连接
    3. 在长列表中查找与已匹配对方向相反的连接（A→B vs B→A）

    :param cols1: 第一个连接列表
    :param cols2: 第二个连接列表
    :param indexName1: 第一个列表的列索引映射
    :param indexName2: 第二个列表的列索引映射
    :return: ``(matches, col1, col2)`` 三元组
    """
    if len(cols1[indexName1[0]]) > len(cols2[indexName2[0]]):
        col1 = cols1.copy()
        col2 = cols2.copy()
        indexNames1 = indexName1.copy()
        indexNames2 = indexName2.copy()
    else:
        col1 = cols2.copy()
        col2 = cols1.copy()
        indexNames1 = indexName2.copy()
        indexNames2 = indexName1.copy()

    # 初始化匹配结果字典
    matches = {}
    for i in range(len(indexNames1)):
        matches[indexNames1[i]] = []

    # ── 第 1 轮：在长列表与短列表之间查找完全匹配的连接对 ──
    for pair in zip(col1[indexNames1[0]], col1[indexNames1[1]]):
        for p1, x1 in enumerate(zip(col1[indexNames1[0]], col1[indexNames1[1]])):
            if x1 == pair:
                index1 = p1
        # [废弃] 以下为早期使用列表推导查找匹配索引的旧实现
        # ind = [p for p,x in enumerate(zip(cols1[indexName1[0], cols1[indexName1[1]]])) if x == pair]
        # 若短列表中包含当前连接对...
        if zip(col2[indexNames2[0]], col2[indexNames2[1]]).__contains__(pair):
            for p2, x2 in enumerate(zip(col2[indexNames2[0]], col2[indexNames2[1]])):
                if x2 == pair:
                    index2 = p2
            # 若匹配结果中尚不包含当前对，则添加
            if not zip(matches[indexNames1[0]], matches[indexNames1[1]]).__contains__(
                ([pair[0]], [pair[1]])
            ):
                # [调试] 以下为检查 matches 内容和中间条件分支的旧调试输出
                # print(matches[indexNames1[0]], matches[indexNames1[1]])
                for i in range(len(indexNames1)):
                    if col1[indexNames1[i]][index1] == col2[indexNames2[i]][index2]:
                        # if i < 2 & len(col1[indexNames1[i]][index1]):
                        #     print("HO")
                        matches[indexNames1[i]] += [[col1[indexNames1[i]][index1]]]
                        del col2[indexNames2[i]][index2]
                        del col1[indexNames1[i]][index1]
                    else:
                        matches[indexNames1[i]] += [
                            [col1[indexNames1[i]][index1], col2[indexNames2[i]][index2]]
                        ]
                        del col2[indexNames2[i]][index2]
                        del col1[indexNames1[i]][index1]
            # 若当前对已在匹配结果中，则将后两列（连接类型/数量）追加到已有记录
            else:
                for p3, x3 in enumerate(
                    zip(matches[indexNames1[0]], matches[indexNames1[1]])
                ):
                    if x3 == ([pair[0]], [pair[1]]):
                        index3 = p3
                for i in range(len(indexNames1)):
                    if i > 1:
                        matches[indexNames1[i]][index3] += [
                            col1[indexNames1[i]][index1]
                        ]
                    del col1[indexNames1[i]][index1]
                    del col2[indexNames2[i]][index2]

    # ── 第 2 轮：在长列表与已匹配列表之间查找重复连接 ──
    for pair in zip(col1[indexNames1[0]], col1[indexNames1[1]]):
        for p1, x1 in enumerate(zip(col1[indexNames1[0]], col1[indexNames1[1]])):
            if x1 == pair:
                index1 = p1
        # 若当前对在已匹配结果中存在，则追加连接类型和数量
        if zip(matches[indexNames1[0]], matches[indexNames1[1]]).__contains__(
            ([pair[0]], [pair[1]])
        ):
            for p3, x3 in enumerate(
                zip(matches[indexNames1[0]], matches[indexNames1[1]])
            ):
                if x3 == ([pair[0]], [pair[1]]):
                    index3 = p3
            for i in range(len(indexNames1)):
                if i > 1:
                    matches[indexNames1[i]][index3] += [col1[indexNames1[i]][index1]]
                del col1[indexNames1[i]][index1]

    # ── 第 3 轮：在长列表中查找与已匹配对方向相反的连接（A→B vs B→A） ──
    for pair in zip(col1[indexNames1[0]], col1[indexNames1[1]]):
        # [废弃] 以下为构造反向连接对的旧辅助变量，当前直接内联比较
        # reversepair = [pair[1],pair[0]]
        for p1, x1 in enumerate(zip(col1[indexNames1[0]], col1[indexNames1[1]])):
            if x1 == pair:
                index1 = p1
        # [废弃] 以下为旧版反向匹配条件判断，现已由下方统一逻辑替代
        # if zip(matches[indexNames1[1]],matches[indexNames1[0]]).__contains__(([pair[0]], [pair[1]])):
        for p4, x4 in enumerate(zip(matches[indexNames1[0]], matches[indexNames1[1]])):
            if x4 == ([pair[1]], [pair[0]]):
                index4 = p4
        if zip(matches[indexNames1[0]], matches[indexNames1[1]]).__contains__(
            ([pair[1]], [pair[0]])
        ):
            # [调试] 以下为检查反向匹配索引和列表长度的旧调试输出
            # print(zip(matches[indexNames1[0]], matches[indexNames1[1]]))
            # print(([pair[1]], [pair[0]]))
            for i in range(len(indexNames1)):
                if i > 1:
                    # print(len(matches[indexNames1[i]]), index4)
                    # print(len(col1[indexNames1[i]]), index1)
                    matches[indexNames1[i]][index4] += [col1[indexNames1[i]][index1]]
                del col1[indexNames1[i]][index1]

    return matches, col1, col2


# 连接类型映射（未完成）。
# 'EJ' 映射为 'GapJunction'（缝隙连接）。
# 'R', 'Rp', 'S', 'Sp' 映射为 'Send'（化学突触）。
# 'NMJ' 无对应映射。
def typeMapping(cols1, cols2, indexName1, indexName2):
    # [备选] 以下为早期预设的连接类型映射表，当前函数仍保留为占位实现
    # list1 = ["GapJunction", "Send"]
    # list2 = ["EJ", "NMJ", "R", "Rp", "S", "Sp"]
    # type1 = cols1[indexName1[2]]
    # type2 = cols2[indexName2[2]]
    """连接类型映射（未完成）。

    预期将 ``EJ`` 映射为 ``GapJunction``，
    ``R``/``Rp``/``S``/``Sp`` 映射为 ``Send``。

    :param cols1: 第一个连接列表
    :param cols2: 第二个连接列表
    :param indexName1: 第一个列表的列索引映射
    :param indexName2: 第二个列表的列索引映射
    """
    pass


if __name__ == "__main__":
    fName1 = "CElegansNeuronTables.xls"
    fName2 = "NeuronConnectFormatted.xlsx"

    # [废弃] 以下为开发阶段使用的本地绝对路径，当前已改为仓库相对文件名
    # file1 = "C:\\Users\\Ari\\Documents\\Projects\\OpenWorm\\book1.txt"
    # file2 = "C:\\Users\\Ari\\Documents\\Projects\\OpenWorm\\book2.txt"
    # xfile1 = "C:\\Users\\Ari\\Documents\\Projects\\OpenWorm\\CElegansNeuroML\\CElegansNeuronTables.xls"
    # xfile2 = "C:\\Users\\Ari\\Documents\\Projects\\OpenWorm\\CElegansNeuroML\\NeuronConnectFormatted.xlsx"
    comparitor(fName1, fName2)
