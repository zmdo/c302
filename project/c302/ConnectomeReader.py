# =============================================================================
# 功能描述：
#   线虫（C. elegans）连接组数据的读取与解析工具集。
#   提供 302 个标准神经元名称列表、96 个体壁肌肉名称列表，
#   以及判断细胞类型、校验神经元名称、统计连接关系的辅助函数。
#   ConnectionInfo 数据类用于统一表示突触连接记录。
#
# 类与方法索引：
#   convert_to_preferred_muscle_name     (L450)  — 将非标准体壁肌肉名称转换为标准命名格式
#   get_all_muscle_prefixes              (L470)  — 返回所有已知肌肉名称前缀列表（含体壁肌肉和咽部肌肉）
#   get_body_wall_muscle_prefixes        (L478)  — 返回体壁肌肉专属前缀列表，不含咽部肌肉前缀（pm/vm/um）
#   is_muscle                            (L486)  — 判断给定细胞名称是否为肌肉细胞（含体壁肌肉和咽部肌肉）
#   is_body_wall_muscle                  (L497)  — 判断给定细胞名称是否为体壁肌肉（排除咽部肌肉）
#   is_neuron                            (L508)  — 判断给定细胞是否为神经元（非体壁肌肉即视为神经元）
#   remove_leading_index_zero            (L518)  — Returns neuron name with an index without leading zero. E.g. VB01 -> VB1.
#   ConnectionInfo                       (L529)  — 表示两个细胞之间的一条突触连接记录
#     __init__                           (L536)  — __init__ 函数
#     __str__                            (L543)  — __str__ 函数
#     short                              (L552)  — 返回连接的简短文字描述（不含突触计数）
#     __eq__                             (L563)  — __eq__ 函数
#     __lt__                             (L572)  — __lt__ 函数
#     __repr__                           (L578)  — __repr__ 函数
#   check_neurons                        (L582)  — 将细胞列表与标准神经元名称集合做三路比对，返回比对结果
#   analyse_connections                  (L607)  — 打印连接组完整统计摘要，用于调试和验证数据读取器输出的完整性
#
# 更新日志：
#   2026-04-16  Copilot  计划2 阶段八收尾：补记汇总校验与最终勘误完成
#   2026-04-16  zmdo  添加中文注释（计划1 阶段二）
#
# 当前维护者：zmdo
# =============================================================================

############################################################

#    用于读取、写入和解析 NeuroML 2 文件的工具集

############################################################

from c302 import print_

# 302 个标准神经元名称列表，来源于 White et al. 1986 论文和 WormAtlas 数据库
# 用于 check_neurons() 校验数据读取器返回的神经元名称是否与该标准集一致
PREFERRED_NEURON_NAMES = [
    "ADAL",
    "ADAR",
    "ADEL",
    "ADER",
    "ADFL",
    "ADFR",
    "ADLL",
    "ADLR",
    "AFDL",
    "AFDR",
    "AIAL",
    "AIAR",
    "AIBL",
    "AIBR",
    "AIML",
    "AIMR",
    "AINL",
    "AINR",
    "AIYL",
    "AIYR",
    "AIZL",
    "AIZR",
    "ALA",
    "ALML",
    "ALMR",
    "ALNL",
    "ALNR",
    "AQR",
    "AS1",
    "AS10",
    "AS11",
    "AS2",
    "AS3",
    "AS4",
    "AS5",
    "AS6",
    "AS7",
    "AS8",
    "AS9",
    "ASEL",
    "ASER",
    "ASGL",
    "ASGR",
    "ASHL",
    "ASHR",
    "ASIL",
    "ASIR",
    "ASJL",
    "ASJR",
    "ASKL",
    "ASKR",
    "AUAL",
    "AUAR",
    "AVAL",
    "AVAR",
    "AVBL",
    "AVBR",
    "AVDL",
    "AVDR",
    "AVEL",
    "AVER",
    "AVFL",
    "AVFR",
    "AVG",
    "AVHL",
    "AVHR",
    "AVJL",
    "AVJR",
    "AVKL",
    "AVKR",
    "AVL",
    "AVM",
    "AWAL",
    "AWAR",
    "AWBL",
    "AWBR",
    "AWCL",
    "AWCR",
    "BAGL",
    "BAGR",
    "BDUL",
    "BDUR",
    "CANL",
    "CANR",
    "CEPDL",
    "CEPDR",
    "CEPVL",
    "CEPVR",
    "DA1",
    "DA2",
    "DA3",
    "DA4",
    "DA5",
    "DA6",
    "DA7",
    "DA8",
    "DA9",
    "DB1",
    "DB2",
    "DB3",
    "DB4",
    "DB5",
    "DB6",
    "DB7",
    "DD1",
    "DD2",
    "DD3",
    "DD4",
    "DD5",
    "DD6",
    "DVA",
    "DVB",
    "DVC",
    "FLPL",
    "FLPR",
    "HSNL",
    "HSNR",
    "I1L",
    "I1R",
    "I2L",
    "I2R",
    "I3",
    "I4",
    "I5",
    "I6",
    "IL1DL",
    "IL1DR",
    "IL1L",
    "IL1R",
    "IL1VL",
    "IL1VR",
    "IL2DL",
    "IL2DR",
    "IL2L",
    "IL2R",
    "IL2VL",
    "IL2VR",
    "LUAL",
    "LUAR",
    "M1",
    "M2L",
    "M2R",
    "M3L",
    "M3R",
    "M4",
    "M5",
    "MCL",
    "MCR",
    "MI",
    "NSML",
    "NSMR",
    "OLLL",
    "OLLR",
    "OLQDL",
    "OLQDR",
    "OLQVL",
    "OLQVR",
    "PDA",
    "PDB",
    "PDEL",
    "PDER",
    "PHAL",
    "PHAR",
    "PHBL",
    "PHBR",
    "PHCL",
    "PHCR",
    "PLML",
    "PLMR",
    "PLNL",
    "PLNR",
    "PQR",
    "PVCL",
    "PVCR",
    "PVDL",
    "PVDR",
    "PVM",
    "PVNL",
    "PVNR",
    "PVPL",
    "PVPR",
    "PVQL",
    "PVQR",
    "PVR",
    "PVT",
    "PVWL",
    "PVWR",
    "RIAL",
    "RIAR",
    "RIBL",
    "RIBR",
    "RICL",
    "RICR",
    "RID",
    "RIFL",
    "RIFR",
    "RIGL",
    "RIGR",
    "RIH",
    "RIML",
    "RIMR",
    "RIPL",
    "RIPR",
    "RIR",
    "RIS",
    "RIVL",
    "RIVR",
    "RMDDL",
    "RMDDR",
    "RMDL",
    "RMDR",
    "RMDVL",
    "RMDVR",
    "RMED",
    "RMEL",
    "RMER",
    "RMEV",
    "RMFL",
    "RMFR",
    "RMGL",
    "RMGR",
    "RMHL",
    "RMHR",
    "SAADL",
    "SAADR",
    "SAAVL",
    "SAAVR",
    "SABD",
    "SABVL",
    "SABVR",
    "SDQL",
    "SDQR",
    "SIADL",
    "SIADR",
    "SIAVL",
    "SIAVR",
    "SIBDL",
    "SIBDR",
    "SIBVL",
    "SIBVR",
    "SMBDL",
    "SMBDR",
    "SMBVL",
    "SMBVR",
    "SMDDL",
    "SMDDR",
    "SMDVL",
    "SMDVR",
    "URADL",
    "URADR",
    "URAVL",
    "URAVR",
    "URBL",
    "URBR",
    "URXL",
    "URXR",
    "URYDL",
    "URYDR",
    "URYVL",
    "URYVR",
    "VA1",
    "VA10",
    "VA11",
    "VA12",
    "VA2",
    "VA3",
    "VA4",
    "VA5",
    "VA6",
    "VA7",
    "VA8",
    "VA9",
    "VB1",
    "VB10",
    "VB11",
    "VB2",
    "VB3",
    "VB4",
    "VB5",
    "VB6",
    "VB7",
    "VB8",
    "VB9",
    "VC1",
    "VC2",
    "VC3",
    "VC4",
    "VC5",
    "VC6",
    "VD1",
    "VD10",
    "VD11",
    "VD12",
    "VD13",
    "VD2",
    "VD3",
    "VD4",
    "VD5",
    "VD6",
    "VD7",
    "VD8",
    "VD9",
]
# 线虫标准体壁肌肉名称列表，共 96 块（含 MANAL 和 MVULVA）
# 命名格式：MD/MV（背/腹）+ L/R（左/右）+ 两位数序号，例如 MDL01、MVR23
PREFERRED_MUSCLE_NAMES = [
    "MANAL",
    "MDL01",
    "MDL02",
    "MDL03",
    "MDL04",
    "MDL05",
    "MDL06",
    "MDL07",
    "MDL08",
    "MDL09",
    "MDL10",
    "MDL11",
    "MDL12",
    "MDL13",
    "MDL14",
    "MDL15",
    "MDL16",
    "MDL17",
    "MDL18",
    "MDL19",
    "MDL20",
    "MDL21",
    "MDL22",
    "MDL23",
    "MDL24",
    "MDR01",
    "MDR02",
    "MDR03",
    "MDR04",
    "MDR05",
    "MDR06",
    "MDR07",
    "MDR08",
    "MDR09",
    "MDR10",
    "MDR11",
    "MDR12",
    "MDR13",
    "MDR14",
    "MDR15",
    "MDR16",
    "MDR17",
    "MDR18",
    "MDR19",
    "MDR20",
    "MDR21",
    "MDR22",
    "MDR23",
    "MDR24",
    "MVL01",
    "MVL02",
    "MVL03",
    "MVL04",
    "MVL05",
    "MVL06",
    "MVL07",
    "MVL08",
    "MVL09",
    "MVL10",
    "MVL11",
    "MVL12",
    "MVL13",
    "MVL14",
    "MVL15",
    "MVL16",
    "MVL17",
    "MVL18",
    "MVL19",
    "MVL20",
    "MVL21",
    "MVL22",
    "MVL23",
    "MVR01",
    "MVR02",
    "MVR03",
    "MVR04",
    "MVR05",
    "MVR06",
    "MVR07",
    "MVR08",
    "MVR09",
    "MVR10",
    "MVR11",
    "MVR12",
    "MVR13",
    "MVR14",
    "MVR15",
    "MVR16",
    "MVR17",
    "MVR18",
    "MVR19",
    "MVR20",
    "MVR21",
    "MVR22",
    "MVR23",
    "MVR24",
    "MVULVA",
]


def convert_to_preferred_muscle_name(muscle):
    """将非标准体壁肌肉名称转换为标准命名格式。

    :param muscle: 原始肌肉名称字符串，如 'BWM-VL01'
    :return: 标准格式名称，如 'MVL01'；无法识别时返回原名加 '???'
    """
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


def get_all_muscle_prefixes():
    """返回所有已知肌肉名称前缀列表（含体壁肌肉和咽部肌肉）。

    :return: 肌肉前缀字符串列表
    """
    return ["pm", "vm", "um", "BWM-D", "BWM-V", "LegacyBodyWallMuscles", "vBWM", "dBWM"]


def get_body_wall_muscle_prefixes():
    """返回体壁肌肉专属前缀列表，不含咽部肌肉前缀（pm/vm/um）。

    :return: 体壁肌肉前缀字符串列表
    """
    return ["BWM-D", "BWM-V", "LegacyBodyWallMuscles", "vBWM", "dBWM"]


def is_muscle(cell):
    """判断给定细胞名称是否为肌肉细胞（含体壁肌肉和咽部肌肉）。

    :param cell: 细胞名称字符串
    :return: True 表示为肌肉细胞，False 表示不是
    """
    # 检查细胞名称前缀是否属于已知肌肉前缀列表（pm/vm/um/BWM-D/BWM-V 等）
    known_muscle_prefixes = get_all_muscle_prefixes()
    return cell.startswith(tuple(known_muscle_prefixes))


def is_body_wall_muscle(cell):
    """判断给定细胞名称是否为体壁肌肉（排除咽部肌肉）。

    :param cell: 细胞名称字符串
    :return: True 表示为体壁肌肉，False 表示不是
    """
    # 仅匹配体壁肌肉前缀（BWM-D/BWM-V/vBWM/dBWM），排除咽部肌肉（pm/vm/um）
    known_muscle_prefixes = get_body_wall_muscle_prefixes()
    return cell.startswith(tuple(known_muscle_prefixes))


def is_neuron(cell):
    """判断给定细胞是否为神经元（非体壁肌肉即视为神经元）。

    :param cell: 细胞名称字符串
    :return: True 表示为神经元，False 表示为体壁肌肉
    """
    # 非体壁肌肉即视为神经元，利用 is_body_wall_muscle 的互补逻辑快速判断
    return not is_body_wall_muscle(cell)


def remove_leading_index_zero(cell):
    """
    Returns neuron name with an index without leading zero. E.g. VB01 -> VB1.
    """
    # 规范化神经元编号：不同数据源对编号补零的处理不一致（如 VB01 vs VB1），
    # 统一去掉倒数第二位的前导零以匹配 PREFERRED_NEURON_NAMES 中的标准形式
    if is_neuron(cell) and cell[-2:].startswith("0"):
        return "%s%s" % (cell[:-2], cell[-1:])
    return cell


class ConnectionInfo:
    """表示两个细胞之间的一条突触连接记录。

    封装突触前/后细胞名称、突触数量、类型和神经递质分类，
    是 c302 各数据读取器统一返回的连接数据结构。
    """

    def __init__(self, pre_cell, post_cell, number, syntype, synclass):
        self.pre_cell = pre_cell  # 突触前细胞名称（发送信号方）
        self.post_cell = post_cell  # 突触后细胞名称（接收信号方）
        self.number = number  # 突触数量，表示该对细胞间的突触计数（连接权重）
        self.syntype = syntype  # 突触类型：'Send'（化学突触）或 'GapJunction'（电突触）
        self.synclass = synclass  # 突触分类：神经递质类别，如 'Acetylcholine'、'GABA'、'Generic_GJ'

    def __str__(self):
        return "Connection from %s to %s (%i times, type: %s, neurotransmitter: %s)" % (
            self.pre_cell,
            self.post_cell,
            self.number,
            self.syntype,
            self.synclass,
        )

    def short(self):
        """返回连接的简短文字描述（不含突触计数）。

        :return: 格式为 'Connection from X to Y (syntype)' 的字符串
        """
        return "Connection from %s to %s (%s)" % (
            self.pre_cell,
            self.post_cell,
            self.syntype,
        )

    def __eq__(self, other):
        return (
            other.pre_cell == self.pre_cell
            and other.post_cell == self.post_cell
            and other.number == self.number
            and other.syntype == self.syntype
            and other.synclass == self.synclass
        )

    def __lt__(self, other):
        if other.pre_cell + other.post_cell > self.pre_cell + self.post_cell:
            return True
        else:
            return False

    def __repr__(self):
        return self.__str__()


def check_neurons(cells):
    """将细胞列表与标准神经元名称集合做三路比对，返回比对结果。

    :param cells: 待校验的细胞名称列表
    :return: 三元组 (preferred, not_in_preferred, missing_preferred)
             - preferred: 在标准集中找到的名称
             - not_in_preferred: 不在标准集中的名称（可能为肌肉或未知细胞）
             - missing_preferred: 标准集中未出现的神经元名称
    """
    # 校验神经元名称：将输入列表与 PREFERRED_NEURON_NAMES 标准集做三路比较
    preferred = []  # 在标准集中找到的神经元
    not_in_preferred = []  # 不在标准集中的名称（可能是肌肉或未知细胞）
    missing_preferred = [n for n in PREFERRED_NEURON_NAMES]  # 标准集中尚未出现的神经元
    for c in cells:
        if c not in PREFERRED_NEURON_NAMES:
            not_in_preferred.append(c)
        else:
            preferred.append(c)
        # 从缺失列表中移除已出现的神经元，剩余即为数据中未覆盖的标准神经元
        if c in missing_preferred:
            missing_preferred.remove(c)

    return preferred, not_in_preferred, missing_preferred


def analyse_connections(cells, neuron_conns, neurons2muscles, muscles, muscle_conns):
    """打印连接组完整统计摘要，用于调试和验证数据读取器输出的完整性。

    :param cells: 神经元名称列表
    :param neuron_conns: 神经元间 ConnectionInfo 连接列表
    :param neurons2muscles: 有肌肉连接的运动神经元名称列表
    :param muscles: 肌肉细胞名称列表
    :param muscle_conns: 神经肌肉 ConnectionInfo 连接列表
    """
    # 打印连接组统计摘要，用于调试和验证数据读取器输出的完整性
    print_("Found %s cells: %s\n" % (len(cells), sorted(cells)))
    # [调试] 以下为保留的断言和调试输出，可取消注释以校验细胞数量
    # assert(len(cells) == 302)
    # print_("Expected number of cells correct if include_nonconnected_cells=True")

    # 校验神经元名称，找出非标准名称和标准集中缺失的神经元
    preferred, not_in_preferred, missing_preferred = check_neurons(cells)

    print_(
        "Found %s non-neuron(s) here: %s\n"
        % (len(not_in_preferred), sorted(not_in_preferred))
    )
    print_("Known neurons not present: %s\n" % (sorted(missing_preferred)))

    print_("Found %s connections..." % (len(neuron_conns)))
    for c in neuron_conns[:5]:
        print_("   %s" % c)

    print_("   ...\n")
    # 按神经递质类别统计神经元间连接条数和突触总数
    nts = {}  # 每种神经递质类型的连接条数
    nts_tot = {}  # 每种神经递质类型的突触总数
    for c in neuron_conns:
        nt = c.synclass
        if nt not in nts:
            nts[nt] = 0
            nts_tot[nt] = 0
        nts[nt] += 1
        nts_tot[nt] += c.number

    for nt in sorted(nts.keys()):
        print_(
            "   %s present in %s connections, %s synapses total (avg %.3f syns per conn)"
            % (nt, nts[nt], nts_tot[nt], nts_tot[nt] / nts[nt])
        )

    print_("")
    print_("   ---  Muscles  ---")
    print_("")

    # 打印肌肉细胞统计，包括未识别的肌肉和神经肌肉连接情况
    print_("Found %s muscles: %s\n" % (len(muscles), sorted(muscles)))
    not_in_preferred = []
    for m in muscles:
        if m not in PREFERRED_MUSCLE_NAMES:
            not_in_preferred.append(m)

    print_(
        "Found %s unidentified muscles: %s\n"
        % (len(not_in_preferred), sorted(not_in_preferred))
    )

    print_(
        "Found %i neurons connected to muscles: %s\n"
        % (len(neurons2muscles), sorted(neurons2muscles))
    )
    print_(
        "Found %i muscles connected to neurons: %s\n" % (len(muscles), sorted(muscles))
    )

    print_(
        "Found %i connections between neurons and muscles%s\n"
        % (
            len(muscle_conns),
            (", e.g. %s" % muscle_conns[0]) if len(muscle_conns) > 0 else "",
        )
    )

    nts = {}
    nts_tot = {}
    # 按神经递质类别统计神经肌肉连接条数和突触总数
    for c in muscle_conns:
        nt = c.synclass
        if nt not in nts:
            nts[nt] = 0
            nts_tot[nt] = 0
        nts[nt] += 1
        nts_tot[nt] += c.number

    for nt in nts:
        print_(
            "  %s present in %s connections, %s synapses total (avg %.3f syns per conn)"
            % (nt, nts[nt], nts_tot[nt], nts_tot[nt] / nts[nt])
        )

    core_set = ["AVBL", "PVCL", "VA6", "VB6", "VD6", "DB4", "DD4"]
    # [备选] 可替换为更小核心集合，聚焦特定神经元 pair
    # core_set = ['VA6', 'VD6']
    # 对小型核心神经元子集进行连接详细列印，便于调试网络拓扑
    print_("\n\nConnections between cells in the subset %s:\n" % (core_set))

    for c in neuron_conns:
        if c.pre_cell in core_set and c.post_cell in core_set:
            print_(str(c))

    print_details_on = ["AVBR", "NSMR"]
    # 对特定神经元详细打印其全部传出和传入连接，用于定向调试
    for cd in print_details_on:
        print_("\n\nAll outgoing connections of %s:\n" % (cd))
        for c in neuron_conns:
            if c.pre_cell == cd:
                print_(str(c))
        print_("\n\nAll incoming connections of %s:\n" % (cd))
        for c in neuron_conns:
            if c.post_cell == cd:
                print_(str(c))

    print_("")


if __name__ == "__main__":
    from SpreadsheetDataReader import read_data, read_muscle_data

    cells, neuron_conns = read_data(include_nonconnected_cells=True)
    neurons2muscles, muscles, muscle_conns = read_muscle_data()

    analyse_connections(cells, neuron_conns, neurons2muscles, muscles, muscle_conns)
