# =============================================================================
# 功能描述：
#   Level C1 参数层级定义。保留 C 级完整 HH 离子通道，但化学突触从事件
#   驱动改为模拟型（GradedSynapse），是 C 和 C0 之间的混合方案。
#
# 类与方法索引：
#   ParameterisedModel                   (L40)   — ParameterisedModel 类
#     __init__                           (L41)   — 初始化 Level C1 参数模型，使用 HH 型导电细胞和模拟突触（GradedSynapse）
#     set_default_bioparameters          (L55)   — 设置 Level C1 的默认生物参数，从 C 继承细胞参数，替换突触参数为模拟型
#     create_neuron_to_neuron_syn        (L102)  — 创建神经元间模拟突触（``GradedSynapse``）和缝隙连接（``GapJunction``）
#     create_neuron_to_muscle_syn        (L131)  — 创建神经元到肌肉的模拟突触（``GradedSynapse``）和缝隙连接
#     get_elec_syn                       (L160)  — 根据连接类型获取缝隙连接（``GapJunction``）对象
#     get_exc_syn                        (L193)  — 根据连接类型获取兴奋性模拟突触（``GradedSynapse``）对象
#     get_inh_syn                        (L257)  — 根据连接类型获取抑制性模拟突触（``GradedSynapse``）对象
#
# 更新日志：
#   2026-04-16  Copilot  计划2 阶段八收尾：补记汇总校验与最终勘误完成
#   2026-04-16  Copilot  添加中文 docstring 和行内注释（计划1阶段三）
#
# 当前维护者：Copilot
# =============================================================================
"""

Parameters C1:
    Cells:           Single compartment, conductance based cell models with HH like ion channels
    Chem Synapses:   Analogue/graded synapses; continuous transmission (voltage dependent)
    Gap junctions:   Electrical connection; current linerly depends on difference in voltages

ASSESSMENT:
    A good prospect, but cell model could be simpler. See C0

"""

from neuroml import GradedSynapse
from neuroml import GapJunction

from c302.parameters_C import ParameterisedModel as ParameterisedModel_C


class ParameterisedModel(ParameterisedModel_C):
    def __init__(self):
        """初始化 Level C1 参数模型，使用 HH 型导电细胞和模拟突触（GradedSynapse）。

        C1 相对于 C 的关键差异：突触从事件驱动（``ExpTwoSynapse``）改为模拟型（``GradedSynapse``），
        允许非放电神经元传递连续信号；细胞模型保留完整的 HH 通道（与 C 相同）。
        这是 C0（简化细胞）和 C（事件突触）之间的混合方案。
        """
        super(ParameterisedModel, self).__init__()
        self.level = "C1"
        self.custom_component_types_definitions = "cell_C.xml"

        self.set_default_bioparameters()
        self.print_("Set default parameters for %s" % self.level)

    def set_default_bioparameters(self):
        """设置 Level C1 的默认生物参数，从 C 继承细胞参数，替换突触参数为模拟型。

        继承 C 的所有非突触参数，新增 ``GradedSynapse`` 参数组：
        ``conductance``、``delta``、``Vth``、``erev``、``k``。
        """
        param_C = ParameterisedModel_C()
        param_C.set_default_bioparameters()
        # C1 保留 C 的所有细胞（离子通道）参数，仅丢弃突触参数（由下方模拟突触替代）
        for b in param_C.bioparameters:
            if "syn" not in b.name:
                self.add_bioparameter_obj(b)

        # GradedSynapse 兴奋性参数：conductance 峰值电导，delta 斜率，Vth 激活阈值，erev 反转电位
        self.add_bioparameter(
            "neuron_to_neuron_exc_syn_conductance", "0.09 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_exc_syn_conductance", "0.09 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("exc_syn_delta", "5 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_vth", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_erev", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_k", "0.025per_ms", "BlindGuess", "0.1")

        # GradedSynapse 抑制性参数：erev 为负值（-70 mV）以产生超极化效果
        self.add_bioparameter(
            "neuron_to_neuron_inh_syn_conductance", "0.09 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_inh_syn_conductance", "0.09 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("inh_syn_delta", "5 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_vth", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_erev", "-70 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_k", "0.025per_ms", "BlindGuess", "0.1")

        # 缝隙连接：与 C 相比电导值不变（GapJunction，双向电流）
        self.add_bioparameter(
            "neuron_to_neuron_elec_syn_gbase", "0.00052 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_elec_syn_gbase", "0.00052 nS", "BlindGuess", "0.1"
        )

    def create_neuron_to_neuron_syn(self):
        """创建神经元间模拟突触（``GradedSynapse``）和缝隙连接（``GapJunction``）。"""
        self.neuron_to_neuron_exc_syn = GradedSynapse(
            id="neuron_to_neuron_exc_syn",
            conductance=self.get_bioparameter(
                "neuron_to_neuron_exc_syn_conductance"
            ).value,
            delta=self.get_bioparameter("exc_syn_delta").value,
            Vth=self.get_bioparameter("exc_syn_vth").value,
            erev=self.get_bioparameter("exc_syn_erev").value,
            k=self.get_bioparameter("exc_syn_k").value,
        )

        self.neuron_to_neuron_inh_syn = GradedSynapse(
            id="neuron_to_neuron_inh_syn",
            conductance=self.get_bioparameter(
                "neuron_to_neuron_inh_syn_conductance"
            ).value,
            delta=self.get_bioparameter("inh_syn_delta").value,
            Vth=self.get_bioparameter("inh_syn_vth").value,
            erev=self.get_bioparameter("inh_syn_erev").value,
            k=self.get_bioparameter("inh_syn_k").value,
        )

        self.neuron_to_neuron_elec_syn = GapJunction(
            id="neuron_to_neuron_elec_syn",
            conductance=self.get_bioparameter("neuron_to_neuron_elec_syn_gbase").value,
        )

    def create_neuron_to_muscle_syn(self):
        """创建神经元到肌肉的模拟突触（``GradedSynapse``）和缝隙连接。"""
        self.neuron_to_muscle_exc_syn = GradedSynapse(
            id="neuron_to_muscle_exc_syn",
            conductance=self.get_bioparameter(
                "neuron_to_muscle_exc_syn_conductance"
            ).value,
            delta=self.get_bioparameter("exc_syn_delta").value,
            Vth=self.get_bioparameter("exc_syn_vth").value,
            erev=self.get_bioparameter("exc_syn_erev").value,
            k=self.get_bioparameter("exc_syn_k").value,
        )

        self.neuron_to_muscle_inh_syn = GradedSynapse(
            id="neuron_to_muscle_inh_syn",
            conductance=self.get_bioparameter(
                "neuron_to_muscle_inh_syn_conductance"
            ).value,
            delta=self.get_bioparameter("inh_syn_delta").value,
            Vth=self.get_bioparameter("inh_syn_vth").value,
            erev=self.get_bioparameter("inh_syn_erev").value,
            k=self.get_bioparameter("inh_syn_k").value,
        )

        self.neuron_to_muscle_elec_syn = GapJunction(
            id="neuron_to_muscle_elec_syn",
            conductance=self.get_bioparameter("neuron_to_muscle_elec_syn_gbase").value,
        )

    def get_elec_syn(self, pre_cell, post_cell, type):
        """根据连接类型获取缝隙连接（``GapJunction``）对象。

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

        if self.found_specific_param:
            conn_id = "%s_to_%s_elec_syn" % (pre_cell, post_cell)

        return GapJunction(id=conn_id, conductance=gbase)

    def get_exc_syn(self, pre_cell, post_cell, type):
        """根据连接类型获取兴奋性模拟突触（``GradedSynapse``）对象。

        :param pre_cell: 突触前细胞名称
        :param post_cell: 突触后细胞名称
        :param type: 连接类型字符串
        :return: 配置好的 ``GradedSynapse`` 兴奋性突触对象
        """
        self.found_specific_param = False

        specific_param_template = "%s_to_%s_exc_syn_%s"
        if type == "neuron_to_neuron":
            conductance = self.get_conn_param(
                pre_cell,
                post_cell,
                specific_param_template,
                "neuron_to_neuron_exc_syn_%s",
                "conductance",
            )
            erev = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "erev"
            )
            delta = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "delta"
            )
            vth = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "vth"
            )
            k = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "k"
            )

            conn_id = "neuron_to_neuron_exc_syn"

        elif type == "neuron_to_muscle":
            conductance = self.get_conn_param(
                pre_cell,
                post_cell,
                specific_param_template,
                "neuron_to_muscle_exc_syn_%s",
                "conductance",
            )
            erev = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "erev"
            )
            delta = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "delta"
            )
            vth = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "vth"
            )
            k = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "k"
            )

            conn_id = "neuron_to_muscle_exc_syn"

        if self.found_specific_param:
            conn_id = "%s_to_%s_exc_syn" % (pre_cell, post_cell)

        return GradedSynapse(
            id=conn_id, conductance=conductance, delta=delta, Vth=vth, erev=erev, k=k
        )

    def get_inh_syn(self, pre_cell, post_cell, type):
        """根据连接类型获取抑制性模拟突触（``GradedSynapse``）对象。

        :param pre_cell: 突触前细胞名称
        :param post_cell: 突触后细胞名称
        :param type: 连接类型字符串
        :return: 配置好的 ``GradedSynapse`` 抑制性突触对象
        """
        self.found_specific_param = False

        specific_param_template = "%s_to_%s_inh_syn_%s"
        if type == "neuron_to_neuron":
            conductance = self.get_conn_param(
                pre_cell,
                post_cell,
                specific_param_template,
                "neuron_to_neuron_inh_syn_%s",
                "conductance",
            )
            erev = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "erev"
            )
            delta = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "delta"
            )
            vth = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "vth"
            )
            k = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "k"
            )

            conn_id = "neuron_to_neuron_inh_syn"

        elif type == "neuron_to_muscle":
            conductance = self.get_conn_param(
                pre_cell,
                post_cell,
                specific_param_template,
                "neuron_to_muscle_inh_syn_%s",
                "conductance",
            )
            erev = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "erev"
            )
            delta = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "delta"
            )
            vth = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "vth"
            )
            k = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "k"
            )

            conn_id = "neuron_to_muscle_inh_syn"

        if self.found_specific_param:
            conn_id = "%s_to_%s_inh_syn" % (pre_cell, post_cell)

        return GradedSynapse(
            id=conn_id, conductance=conductance, delta=delta, Vth=vth, erev=erev, k=k
        )
