# =============================================================================
# 功能描述：
#   Level B 参数层级定义。在 Level A 基础上增加 activity 变量和真实缝隙
#   连接（GapJunction），使用自定义 IafActivityCell 组件。
#
# 类与方法索引：
#   ParameterisedModel                   (L53)   — ParameterisedModel 类
#     __init__                           (L54)   — 初始化 Level B 参数模型，继承 Level A 并添加真实缝隙连接和 activity 变量
#     set_default_bioparameters          (L67)   — 设置 Level B 的默认生物参数，在 Level A 基础上新增 tau1 和真实电突触参数
#     create_generic_muscle_cell         (L107)  — 创建带 activity 变量的通用肌肉细胞（``IafActivityCell``）
#     create_generic_neuron_cell         (L123)  — 创建带 activity 变量的通用神经元细胞（``IafActivityCell``）
#     create_neuron_to_neuron_syn        (L135)  — 创建神经元间化学突触（``ExpTwoSynapse``）和真实缝隙连接（``GapJunction``）
#     create_neuron_to_muscle_syn        (L162)  — 创建神经元到肌肉的化学突触（``ExpTwoSynapse``）和缝隙连接（``GapJunction``）
#     get_elec_syn                       (L185)  — 根据连接类型获取真实缝隙连接（``GapJunction``）对象
#   IafActivityCell                      (L230)  — IafActivityCell 类
#     __init__                           (L231)  — 初始化带 activity 变量的积分放电细胞，存储所有膜特性参数
#     export                             (L253)  — 将细胞定义以 NeuroML XML 格式写入输出流
#
# 更新日志：
#   2026-04-16  Copilot  添加中文 docstring 和行内注释（计划1阶段三）
#
# 当前维护者：Copilot
# =============================================================================
"""

Parameters B:
    Cells:           Simple integrate and fire cells, custom component type, with an "activity" variable
    Chem Synapses:   Event based, ohmic; one rise & one decay constant
    Gap junctions:   Electrical connection; current linerly depends on difference in voltages

ASSESSMENT:
    Not very useful in longer term; same criticisms as parameters A


We are very aware that:

    C elegans neurons do NOT behave like Integrate & Fire neurons
    Their synapses are NOT like double exponential, conductance based synapses
    Electrical synapses are very different from event triggered, conductance based synapses

The values below are a FIRST APPROXIMATION of neurons for use in a network to
investigate the synaptic connectivity of C elegans


"""

from neuroml import ExpTwoSynapse
from neuroml import GapJunction

from c302.parameters_A import ParameterisedModel as ParameterisedModel_A


class ParameterisedModel(ParameterisedModel_A):
    def __init__(self):
        """初始化 Level B 参数模型，继承 Level A 并添加真实缝隙连接和 activity 变量。

        Level B 相对于 A 的关键改进：
        1. 使用带 ``activity`` 状态变量的自定义细胞模型（``IafActivityCell``，定义于 ``cell_B.xml``）
        2. 使用真实的 ``GapJunction`` 替换事件触发的伪电突触
        """
        super(ParameterisedModel, self).__init__()
        self.level = "B"
        self.custom_component_types_definitions = "cell_B.xml"

        self.set_default_bioparameters()

    def set_default_bioparameters(self):
        """设置 Level B 的默认生物参数，在 Level A 基础上新增 tau1 和真实电突触参数。

        从 Level A 继承 IaF 细胞参数、化学突触参数和偏置电流参数，
        丢弃 A 级中的电突触事件参数（``elec_syn_erev/rise/decay``），
        新增 ``tau1`` 活动衰减时间常数（控制 activity 变量的恢复速度），
        以及 ``GapJunction`` 的 ``gbase`` 电导参数。
        """
        param_C = ParameterisedModel_A()
        param_C.set_default_bioparameters()
        # 从 Level A 选择性继承：只保留 IaF 细胞参数、化学突触参数、偏置电流参数
        # 丢弃 Level A 的电突触事件参数（elec_syn_erev/rise/decay），因为 B 级使用真正的 GapJunction
        for b in param_C.bioparameters:
            if (
                "iaf" in b.name
                or "exc" in b.name
                or "inh" in b.name
                or "current" in b.name
            ):
                self.add_bioparameter_obj(b)
            else:
                self.print_(" - Ignoring inherited param: %s" % b)

        # tau1：activity 变量的恢复时间常数（控制神经元兴奋性衰减速度）
        self.add_bioparameter("neuron_iaf_tau1", "50ms", "BlindGuess", "0.1")
        self.add_bioparameter(
            "muscle_iaf_tau1",
            self.get_bioparameter("neuron_iaf_tau1").value,
            "BlindGuess",
            "0.1",
        )

        # 真实缝隙连接（GapJunction）电导，与 Level A 中的伪电突触本质不同
        self.add_bioparameter(
            "neuron_to_neuron_elec_syn_gbase", "0.01 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_elec_syn_gbase", "0.01 nS", "BlindGuess", "0.1"
        )

    def create_generic_muscle_cell(self):
        """创建带 activity 变量的通用肌肉细胞（``IafActivityCell``）。

        ``IafActivityCell`` 相较于标准 ``IafCell`` 新增 ``tau1`` 参数，
        用于描述膜电位恢复的时间常数。
        """
        self.generic_muscle_cell = IafActivityCell(
            id="generic_muscle_iaf_cell",
            C=self.get_bioparameter("muscle_iaf_C").value,
            thresh=self.get_bioparameter("muscle_iaf_thresh").value,
            reset=self.get_bioparameter("muscle_iaf_reset").value,
            leak_conductance=self.get_bioparameter("muscle_iaf_conductance").value,
            leak_reversal=self.get_bioparameter("muscle_iaf_leak_reversal").value,
            tau1=self.get_bioparameter("muscle_iaf_tau1").value,
        )

    def create_generic_neuron_cell(self):
        """创建带 activity 变量的通用神经元细胞（``IafActivityCell``）。"""
        self.generic_neuron_cell = IafActivityCell(
            id="generic_neuron_iaf_cell",
            C=self.get_bioparameter("neuron_iaf_C").value,
            thresh=self.get_bioparameter("neuron_iaf_thresh").value,
            reset=self.get_bioparameter("neuron_iaf_reset").value,
            leak_conductance=self.get_bioparameter("neuron_iaf_conductance").value,
            leak_reversal=self.get_bioparameter("neuron_iaf_leak_reversal").value,
            tau1=self.get_bioparameter("neuron_iaf_tau1").value,
        )

    def create_neuron_to_neuron_syn(self):
        """创建神经元间化学突触（``ExpTwoSynapse``）和真实缝隙连接（``GapJunction``）。

        Level B 中电突触使用真实 ``GapJunction``，电流与膜电位差成线性比例，
        与 Level A 中的事件触发假电突触有本质区别。
        """
        self.neuron_to_neuron_exc_syn = ExpTwoSynapse(
            id="neuron_to_neuron_exc_syn",
            gbase=self.get_bioparameter("neuron_to_neuron_chem_exc_syn_gbase").value,
            erev=self.get_bioparameter("chem_exc_syn_erev").value,
            tau_decay=self.get_bioparameter("chem_exc_syn_decay").value,
            tau_rise=self.get_bioparameter("chem_exc_syn_rise").value,
        )

        self.neuron_to_neuron_inh_syn = ExpTwoSynapse(
            id="neuron_to_neuron_inh_syn",
            gbase=self.get_bioparameter("neuron_to_neuron_chem_inh_syn_gbase").value,
            erev=self.get_bioparameter("chem_inh_syn_erev").value,
            tau_decay=self.get_bioparameter("chem_inh_syn_decay").value,
            tau_rise=self.get_bioparameter("chem_inh_syn_rise").value,
        )

        self.neuron_to_neuron_elec_syn = GapJunction(
            id="neuron_to_neuron_elec_syn",
            conductance=self.get_bioparameter("neuron_to_neuron_elec_syn_gbase").value,
        )

    def create_neuron_to_muscle_syn(self):
        """创建神经元到肌肉的化学突触（``ExpTwoSynapse``）和缝隙连接（``GapJunction``）。"""
        self.neuron_to_muscle_exc_syn = ExpTwoSynapse(
            id="neuron_to_muscle_exc_syn",
            gbase=self.get_bioparameter("neuron_to_muscle_chem_exc_syn_gbase").value,
            erev=self.get_bioparameter("chem_exc_syn_erev").value,
            tau_decay=self.get_bioparameter("chem_exc_syn_decay").value,
            tau_rise=self.get_bioparameter("chem_exc_syn_rise").value,
        )

        self.neuron_to_muscle_inh_syn = ExpTwoSynapse(
            id="neuron_to_muscle_inh_syn",
            gbase=self.get_bioparameter("neuron_to_muscle_chem_inh_syn_gbase").value,
            erev=self.get_bioparameter("chem_inh_syn_erev").value,
            tau_decay=self.get_bioparameter("chem_inh_syn_decay").value,
            tau_rise=self.get_bioparameter("chem_inh_syn_rise").value,
        )

        self.neuron_to_muscle_elec_syn = GapJunction(
            id="neuron_to_muscle_elec_syn",
            conductance=self.get_bioparameter("neuron_to_muscle_elec_syn_gbase").value,
        )

    def get_elec_syn(self, pre_cell, post_cell, type):
        """根据连接类型获取真实缝隙连接（``GapJunction``）对象。

        支持 ``"neuron_to_neuron"``、``"neuron_to_muscle"``、``"muscle_to_muscle"`` 三种类型。

        :param pre_cell: 突触前细胞名称
        :param post_cell: 突触后细胞名称
        :param type: 连接类型字符串
        :return: 配置好的 ``GapJunction`` 对象
        """
        self.found_specific_param = False
        if type == "neuron_to_neuron":
            gbase = self.get_conn_param(
                pre_cell,
                post_cell,
                "%s_to_%s_elec_syn_%s",
                "neuron_to_neuron_elec_syn_%s",
                "gbase",
            )
            conn_id = "neuron_to_neuron_elec_syn"
        elif type == "neuron_to_muscle":
            gbase = self.get_conn_param(
                pre_cell,
                post_cell,
                "%s_to_%s_elec_syn_%s",
                "neuron_to_muscle_elec_syn_%s",
                "gbase",
            )
            conn_id = "neuron_to_muscle_elec_syn"
        elif type == "muscle_to_muscle":
            gbase = self.get_conn_param(
                pre_cell,
                post_cell,
                "%s_to_%s_elec_syn_%s",
                "muscle_to_muscle_elec_syn_%s",
                "gbase",
            )
            conn_id = "muscle_to_muscle_elec_syn"

        if self.found_specific_param:
            conn_id = "%s_to_%s_elec_syn" % (pre_cell, post_cell)

        return GapJunction(id=conn_id, conductance=gbase)


class IafActivityCell:
    def __init__(self, id, C, thresh, reset, leak_conductance, leak_reversal, tau1):
        """初始化带 activity 变量的积分放电细胞，存储所有膜特性参数。

        该类是 NeuroML ``IafActivityCell`` 自定义组件类型的 Python 封装，
        组件类型定义于 ``cell_B.xml``。

        :param id: 细胞 ID
        :param C: 膜电容
        :param thresh: 阈值电压
        :param reset: 复位电压
        :param leak_conductance: 漏电导
        :param leak_reversal: 漏电流反转电压
        :param tau1: activity 变量恢复时间常数
        """
        self.id = id
        self.C = C
        self.thresh = thresh
        self.reset = reset
        self.leak_conductance = leak_conductance
        self.leak_reversal = leak_reversal
        self.tau1 = tau1

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        """将细胞定义以 NeuroML XML 格式写入输出流。

        生成 ``<iafCell type="iafActivityCell" .../>`` 格式的 XML 元素。

        :param outfile: 可写的输出流对象
        :param level: 缩进层级（每层 4 空格）
        :param namespace: XML 命名空间（保留参数，当前未使用）
        :param name_: XML 元素名（保留参数，当前未使用）
        :param pretty_print: 是否美化输出（含换行与缩进）
        """
        outfile.write(
            "    " * level
            + '<iafCell type="iafActivityCell" id="%s" C="%s" thresh="%s" reset="%s" leakConductance="%s" leakReversal="%s" tau1="%s"/>\n'
            % (
                self.id,
                self.C,
                self.thresh,
                self.reset,
                self.leak_conductance,
                self.leak_reversal,
                self.tau1,
            )
        )
