# =============================================================================
# 功能描述：
#   Level W2D 参数层级定义。来自 Worm2D 二维虫体运动模型的简化细胞
#   （仅偏置和增益参数），突触为连续型 OutputSynapse，参数数量极少。
#
# 类与方法索引：
#   ParameterisedModel                   (L49)   — ParameterisedModel 类
#     __init__                           (L50)   — 初始化 Level W2D 参数模型，使用 Worm2D 偏置-增益型细胞模型
#     set_default_bioparameters          (L69)   — 设置 Level W2D 的默认生物参数（参数数量极少）
#     create_models                      (L101)  — 按顺序创建所有网络组件：肌肉细胞、神经元细胞、偏置电流、神经元间突触、
#     create_generic_muscle_cell         (L111)  — 创建 W2D 通用肌肉细胞（``CellW2D``）
#     create_generic_neuron_cell         (L115)  — 创建 W2D 通用神经元细胞（``CellW2D``）
#     create_offsetcurrent               (L119)  — 创建偏置电流生成器（``PulseGenerator``）
#     create_neuron_to_neuron_syn        (L128)  — 创建神经元间兴奋性/抑制性输出突触（``OutputSynapse``）和缝隙连接（``GapJunction``）
#     create_neuron_to_muscle_syn        (L142)  — 创建神经元到肌肉的兴奋性/抑制性输出突触（``OutputSynapse``）和缝隙连接
#     create_muscle_to_muscle_syn        (L151)  — 创建肌肉间缝隙连接（``GapJunction``）
#     get_elec_syn                       (L160)  — 根据连接类型获取缝隙连接（``GapJunction``）对象
#     get_exc_syn                        (L183)  — 返回神经元间兴奋性输出突触（``OutputSynapse``）
#     get_inh_syn                        (L195)  — 返回神经元间抑制性输出突触（``OutputSynapse``）
#   CellW2D                              (L208)  — CellW2D 类
#     __init__                           (L209)  — 初始化 W2D 神经元/肌肉细胞，存储 ID
#   OutputSynapse                        (L220)  — OutputSynapse 类
#     __init__                           (L221)  — 初始化 W2D 输出突触，存储 ID
#
# 更新日志：
#   2026-04-16  Copilot  添加中文 docstring 和行内注释（计划1阶段三）
#
# 当前维护者：Copilot
# =============================================================================
"""

Parameters W2D:
    Cells:           Simple cell with just bias and gain from Worm2D
    Chem Synapses:   Continuous transmission of output of one cell to next
    Gap junctions:   Electrical connection; current linearly depends on difference in voltages

ASSESSMENT:
    Useful as tested in a number of 2D worm body models & very few parameters

"""

from c302.bioparameters import c302ModelPrototype
from c302.bioparameters import NonNeuroMLCustomType

from neuroml import PulseGenerator
from neuroml import GapJunction


class ParameterisedModel(c302ModelPrototype):
    def __init__(self):
        """初始化 Level W2D 参数模型，使用 Worm2D 偏置-增益型细胞模型。

        W2D 层级来源于二维虫体运动模型（Worm2D），其细胞模型非常简单：
        每个神经元只有偏置（bias）和增益（gain）两个参数，
        突触传递为连续型（``OutputSynapse``）。

        该层级在多个 2D 虫体运动模型中经过测试，参数数量极少，适合探索运动电路架构。
        """
        super(ParameterisedModel, self).__init__()
        self.level = "W2D"
        self.custom_component_types_definitions = [
            "cell_W2D.xml",
            "custom_synapses.xml",
        ]

        self.set_default_bioparameters()
        self.print_("Set default parameters for %s" % self.level)

    def set_default_bioparameters(self):
        """设置 Level W2D 的默认生物参数（参数数量极少）。

        当前参数：
        - ``initial_memb_pot``：初始膜电位（用于设置初始状态）
        - ``neuron_to_neuron_elec_syn_gbase``：神经元间电突触电导
        - ``neuron_to_muscle_elec_syn_gbase``：神经元到肌肉电突触电导
        - ``muscle_to_muscle_elec_syn_gbase``：肌肉间电突触电导
        - 偏置电流参数（默认为 0）
        """
        self.add_bioparameter("initial_memb_pot", "-45 mV", "BlindGuess", "0.1")

        self.add_bioparameter(
            "neuron_to_neuron_elec_syn_gbase", "1 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_elec_syn_gbase", "1 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "muscle_to_muscle_elec_syn_gbase", "1 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter(
            "unphysiological_offset_current", "0 pA", "KnownError", "0"
        )  # Can be activated later
        self.add_bioparameter(
            "unphysiological_offset_current_del", "0 ms", "KnownError", "0"
        )
        self.add_bioparameter(
            "unphysiological_offset_current_dur", "2000 ms", "KnownError", "0"
        )

    def create_models(self):
        """按顺序创建所有网络组件：肌肉细胞、神经元细胞、偏置电流、神经元间突触、
        神经元到肌肉突触、肌肉间突触。
        """
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_offsetcurrent()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()

    def create_generic_muscle_cell(self):
        """创建 W2D 通用肌肉细胞（``CellW2D``）。"""
        self.generic_muscle_cell = CellW2D(id="GenericMuscleCell")

    def create_generic_neuron_cell(self):
        """创建 W2D 通用神经元细胞（``CellW2D``）。"""
        self.generic_neuron_cell = CellW2D(id="GenericNeuronCell")

    def create_offsetcurrent(self):
        """创建偏置电流生成器（``PulseGenerator``）。"""
        self.offset_current = PulseGenerator(
            id="offset_current",
            delay=self.get_bioparameter("unphysiological_offset_current_del").value,
            duration=self.get_bioparameter("unphysiological_offset_current_dur").value,
            amplitude=self.get_bioparameter("unphysiological_offset_current").value,
        )

    def create_neuron_to_neuron_syn(self):
        """创建神经元间兴奋性/抑制性输出突触（``OutputSynapse``）和缝隙连接（``GapJunction``）。

        ``OutputSynapse`` 是 W2D 专有的连续型突触，定义于 ``custom_synapses.xml``。
        """
        # W2D 专有的连续型突触：only OutputSynapse，不依赖事件或离子通道
        self.neuron_to_neuron_exc_syn = OutputSynapse(id="neuron_to_neuron_exc_w2d")
        self.neuron_to_neuron_inh_syn = OutputSynapse(id="neuron_to_neuron_inh_w2d")

        self.neuron_to_neuron_elec_syn = GapJunction(
            id="neuron_to_neuron_elec_syn",
            conductance=self.get_bioparameter("neuron_to_neuron_elec_syn_gbase").value,
        )

    def create_neuron_to_muscle_syn(self):
        """创建神经元到肌肉的兴奋性/抑制性输出突触（``OutputSynapse``）和缝隙连接。"""
        self.neuron_to_muscle_exc_syn = OutputSynapse(id="neuron_to_muscle_w2d")

        self.neuron_to_muscle_elec_syn = GapJunction(
            id="neuron_to_muscle_elec_syn",
            conductance=self.get_bioparameter("neuron_to_muscle_elec_syn_gbase").value,
        )

    def create_muscle_to_muscle_syn(self):
        """创建肌肉间缝隙连接（``GapJunction``）。"""
        self.muscle_to_muscle_exc_syn = OutputSynapse(id="muscle_to_muscle_w2d")

        self.muscle_to_muscle_elec_syn = GapJunction(
            id="muscle_to_muscle_elec_syn",
            conductance=self.get_bioparameter("muscle_to_muscle_elec_syn_gbase").value,
        )

    def get_elec_syn(self, pre_cell, post_cell, type):
        """根据连接类型获取缝隙连接（``GapJunction``）对象。

        :param pre_cell: 突触前细胞名称
        :param post_cell: 突触后细胞名称
        :param type: 连接类型字符串
        :return: 配置好的 ``GapJunction`` 对象
        """
        if type == "neuron_to_neuron":
            gbase = self.get_bioparameter("neuron_to_neuron_elec_syn_gbase").value
            conn_id = "neuron_to_neuron_elec_syn"

        elif type == "neuron_to_muscle":
            gbase = self.get_bioparameter("neuron_to_muscle_elec_syn_gbase").value
            conn_id = "neuron_to_muscle_elec_syn"
        elif type == "muscle_to_muscle":
            gbase = self.get_bioparameter("muscle_to_muscle_elec_syn_gbase").value
            conn_id = "muscle_to_muscle_elec_syn"
        else:
            raise ValueError("Unknown electrical connection type: %s" % type)

        return GapJunction(id=conn_id, conductance=gbase)

    def get_exc_syn(self, pre_cell, post_cell, type):
        """返回神经元间兴奋性输出突触（``OutputSynapse``）。

        W2D 不区分连接类型，所有兴奋性突触共用同一对象。

        :param pre_cell: 突触前细胞名称（未使用）
        :param post_cell: 突触后细胞名称（未使用）
        :param type: 连接类型字符串（未使用）
        :return: ``neuron_to_neuron_exc_syn`` 或 ``neuron_to_muscle_exc_syn``
        """
        return self.neuron_to_neuron_exc_syn

    def get_inh_syn(self, pre_cell, post_cell, type):
        """返回神经元间抑制性输出突触（``OutputSynapse``）。

        W2D 不区分连接类型，所有抑制性突触共用同一对象。

        :param pre_cell: 突触前细胞名称（未使用）
        :param post_cell: 突触后细胞名称（未使用）
        :param type: 连接类型字符串（未使用）
        :return: ``neuron_to_neuron_inh_syn`` 或 ``neuron_to_muscle_inh_syn``
        """
        return self.neuron_to_neuron_inh_syn


class CellW2D(NonNeuroMLCustomType):
    def __init__(self, id):
        """初始化 W2D 神经元/肌肉细胞，存储 ID。

        ``CellW2D`` 对应自定义 LEMS 组件类型 ``cellW2D``，
        其核心参数为偏置（bias）和增益（gain），定义于 ``cell_W2D.xml``。

        :param id: 细胞唯一标识符（如 ``"GenericNeuronCell"``）
        """
        self.id = id


class OutputSynapse(NonNeuroMLCustomType):
    def __init__(self, id):
        """初始化 W2D 输出突触，存储 ID。

        ``OutputSynapse`` 将突触前细胞的输出（activity）直接连续传递给突触后细胞，
        定义于 ``custom_synapses.xml``。

        :param id: 突触唯一标识符
        """
        self.id = id
