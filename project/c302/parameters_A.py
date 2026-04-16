# =============================================================================
# 功能描述：
#   Level A 参数层级定义。使用最简单的积分放电（Integrate & Fire）神经元
#   和事件驱动双指数突触（ExpTwoSynapse），缝隙连接通过事件突触近似
#   （非真实 GapJunction）。
#
# 类与方法索引：
#   ParameterisedModel                   (L55)   — ParameterisedModel 类
#     __init__                           (L56)   — 初始化 Level A 参数模型，设置层级标识并调用默认参数初始化
#     set_default_bioparameters          (L68)   — 设置 Level A 的全套默认生物参数
#     create_generic_muscle_cell         (L166)  — 创建通用肌肉细胞模型（``IafCell``），从生物参数表读取各项膜特性
#     create_generic_neuron_cell         (L177)  — 创建通用神经元细胞模型（``IafCell``），从生物参数表读取各项膜特性
#     create_offset                      (L188)  — 创建偏置电流生成器（``PulseGenerator``），用于向特定细胞注入固定幅度的偏置电流
#     create_neuron_to_neuron_syn        (L201)  — 创建神经元间兴奋性、抑制性和电突触（事件驱动 ``ExpTwoSynapse``）
#     create_neuron_to_muscle_syn        (L231)  — 创建神经元到肌肉的兴奋性、抑制性和电突触（事件驱动 ``ExpTwoSynapse``）
#     create_models                      (L257)  — 按顺序创建所有细胞和突触模型，供网络生成主循环调用
#     get_elec_syn                       (L268)  — 根据连接类型获取电突触对象（Level A 中为 ``ExpTwoSynapse`` 模拟）
#     get_exc_syn                        (L342)  — 根据连接类型获取兴奋性化学突触对象（``ExpTwoSynapse``）
#     get_inh_syn                        (L399)  — 根据连接类型获取抑制性化学突触对象（``ExpTwoSynapse``）
#
# 更新日志：
#   2026-04-16  Copilot  添加中文 docstring 和行内注释（计划1阶段三）
#
# 当前维护者：Copilot
# =============================================================================
"""

Parameters A:
    Cells:           Simple integrate and fire cells
    Chem Synapses:   Event based, ohmic; one rise & one decay constant
    Gap junctions:   NOT REAL GJs: using event based synapses, generally set to zero conductance

ASSESSMENT:
    Not very useful in longer term; tendency for cells to over excite; difficult to tune networks


We are very aware that:

    C elegans neurons do NOT behave like Integrate & Fire neurons
    Their synapses are NOT like double exponential, conductance based synapses
    Electrical synapses are very different from event triggered, conductance based synapses

The values below are a FIRST APPROXIMATION of neurons for use in a network to
investigate the synaptic connectivity of C elegans

"""

from neuroml import IafCell
from neuroml import ExpTwoSynapse
from neuroml import PulseGenerator

from c302.bioparameters import c302ModelPrototype


class ParameterisedModel(c302ModelPrototype):
    def __init__(self):
        """初始化 Level A 参数模型，设置层级标识并调用默认参数初始化。

        Level A 使用 ``IafCell`` 积分放电神经元和双指数事件突触，
        是 c302 框架中最简单的参数层级，适合快速验证连接组结构，
        但不具有 C. elegans 神经元的生物真实性。
        """
        super(ParameterisedModel, self).__init__()
        self.level = "A"
        self.custom_component_types_definitions = None
        self.set_default_bioparameters()

    def set_default_bioparameters(self):
        """设置 Level A 的全套默认生物参数。

        参数分为以下几组：
        - 神经元 / 肌肉 IaF 细胞参数（leakReversal、reset、thresh、C、conductance）
        - 兴奋性化学突触参数（gbase、erev、rise、decay）
        - 抑制性化学突触参数（gbase、erev、rise、decay）
        - 电突触参数（用事件突触模拟，默认电导为 0）
        - 非生理偏置电流参数（用于调试，默认幅度为 0）

        所有参数 source 标为 ``"BlindGuess"``，certainty 为 ``"0.1"``，
        表明这些值是初步估计值，需要进一步根据实验数据调整。
        """
        self.add_bioparameter("neuron_iaf_leak_reversal", "-50mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_reset", "-50mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_thresh", "-30mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_C", "3pF", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_conductance", "0.1nS", "BlindGuess", "0.1")

        # 肌肉细胞 IaF 参数继承自神经元（初始假设两者相同）
        self.add_bioparameter(
            "muscle_iaf_leak_reversal",
            self.get_bioparameter("neuron_iaf_leak_reversal").value,
            "BlindGuess",
            "0.1",
        )
        self.add_bioparameter(
            "muscle_iaf_reset",
            self.get_bioparameter("neuron_iaf_reset").value,
            "BlindGuess",
            "0.1",
        )
        self.add_bioparameter(
            "muscle_iaf_thresh",
            self.get_bioparameter("neuron_iaf_thresh").value,
            "BlindGuess",
            "0.1",
        )
        self.add_bioparameter(
            "muscle_iaf_C",
            self.get_bioparameter("neuron_iaf_C").value,
            "BlindGuess",
            "0.1",
        )
        self.add_bioparameter(
            "muscle_iaf_conductance",
            self.get_bioparameter("neuron_iaf_conductance").value,
            "BlindGuess",
            "0.1",
        )

        # 兴奋性化学突触参数（gbase 峰值电导 / erev 反转电位 / rise 上升时间 / decay 衰减时间）
        self.add_bioparameter(
            "neuron_to_neuron_chem_exc_syn_gbase", "0.01nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_chem_exc_syn_gbase", "0.01nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("chem_exc_syn_erev", "0mV", "BlindGuess", "0.1")
        self.add_bioparameter("chem_exc_syn_rise", "3ms", "BlindGuess", "0.1")
        self.add_bioparameter("chem_exc_syn_decay", "10ms", "BlindGuess", "0.1")

        # 抑制性化学突触参数（erev 负值，如 -80mV，确保突触为抑制性）
        self.add_bioparameter(
            "neuron_to_neuron_chem_inh_syn_gbase", "0.01nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_chem_inh_syn_gbase", "0.01nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("chem_inh_syn_erev", "-80mV", "BlindGuess", "0.1")
        self.add_bioparameter("chem_inh_syn_rise", "3ms", "BlindGuess", "0.1")
        self.add_bioparameter("chem_inh_syn_decay", "10ms", "BlindGuess", "0.1")

        # 电突触参数：Level A 中用事件触发突触模拟，默认电导为 0（不传递）
        self.add_bioparameter(
            "neuron_to_neuron_elec_syn_gbase", "0nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_elec_syn_gbase", "0nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("elec_syn_erev", "0mV", "BlindGuess", "0.1")
        self.add_bioparameter("elec_syn_rise", "3ms", "BlindGuess", "0.1")
        self.add_bioparameter("elec_syn_decay", "10ms", "BlindGuess", "0.1")

        # 非生理偏置电流：KnownError 表示已知此参数不代表真实生物行为，仅供调试
        self.add_bioparameter(
            "unphysiological_offset_current", "0pA", "KnownError", "0"
        )  # 可在后续激活（当前值为 0，即禁用此非生理性偏置电流）
        self.add_bioparameter(
            "unphysiological_offset_current_del", "0ms", "KnownError", "0"
        )
        self.add_bioparameter(
            "unphysiological_offset_current_dur", "200ms", "KnownError", "0"
        )

    def create_generic_muscle_cell(self):
        """创建通用肌肉细胞模型（``IafCell``），从生物参数表读取各项膜特性。"""
        self.generic_muscle_cell = IafCell(
            id="generic_muscle_iaf_cell",
            C=self.get_bioparameter("muscle_iaf_C").value,
            thresh=self.get_bioparameter("muscle_iaf_thresh").value,
            reset=self.get_bioparameter("muscle_iaf_reset").value,
            leak_conductance=self.get_bioparameter("muscle_iaf_conductance").value,
            leak_reversal=self.get_bioparameter("muscle_iaf_leak_reversal").value,
        )

    def create_generic_neuron_cell(self):
        """创建通用神经元细胞模型（``IafCell``），从生物参数表读取各项膜特性。"""
        self.generic_neuron_cell = IafCell(
            id="generic_neuron_iaf_cell",
            C=self.get_bioparameter("neuron_iaf_C").value,
            thresh=self.get_bioparameter("neuron_iaf_thresh").value,
            reset=self.get_bioparameter("neuron_iaf_reset").value,
            leak_conductance=self.get_bioparameter("neuron_iaf_conductance").value,
            leak_reversal=self.get_bioparameter("neuron_iaf_leak_reversal").value,
        )

    def create_offset(self):
        """创建偏置电流生成器（``PulseGenerator``），用于向特定细胞注入固定幅度的偏置电流。

        偏置电流参数（``unphysiological_offset_current``）在默认状态下幅度为 0，
        可在测试脚本中手动覆盖以触发特定细胞的放电。
        """
        self.offset_current = PulseGenerator(
            id="offset_current",
            delay=self.get_bioparameter("unphysiological_offset_current_del").value,
            duration=self.get_bioparameter("unphysiological_offset_current_dur").value,
            amplitude=self.get_bioparameter("unphysiological_offset_current").value,
        )

    def create_neuron_to_neuron_syn(self):
        """创建神经元间兴奋性、抑制性和电突触（事件驱动 ``ExpTwoSynapse``）。

        Level A 中的"电突触"实际上是兴奋性事件突触（gbase 默认为 0），
        不是真正的缝隙连接，仅作占位用途。
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

        self.neuron_to_neuron_elec_syn = ExpTwoSynapse(
            id="neuron_to_neuron_elec_syn",
            gbase=self.get_bioparameter("neuron_to_neuron_elec_syn_gbase").value,
            erev=self.get_bioparameter("elec_syn_erev").value,
            tau_decay=self.get_bioparameter("elec_syn_decay").value,
            tau_rise=self.get_bioparameter("elec_syn_rise").value,
        )

    def create_neuron_to_muscle_syn(self):
        """创建神经元到肌肉的兴奋性、抑制性和电突触（事件驱动 ``ExpTwoSynapse``）。"""
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

        self.neuron_to_muscle_elec_syn = ExpTwoSynapse(
            id="neuron_to_muscle_elec_syn",
            gbase=self.get_bioparameter("neuron_to_muscle_elec_syn_gbase").value,
            erev=self.get_bioparameter("elec_syn_erev").value,
            tau_decay=self.get_bioparameter("elec_syn_decay").value,
            tau_rise=self.get_bioparameter("elec_syn_rise").value,
        )

    def create_models(self):
        """按顺序创建所有细胞和突触模型，供网络生成主循环调用。

        调用顺序：创建肌肉细胞、神经元细胞、偏置电流、神经元到肌肉突触、神经元到神经元突触。
        """
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_offset()
        self.create_neuron_to_muscle_syn()
        self.create_neuron_to_neuron_syn()

    def get_elec_syn(self, pre_cell, post_cell, type):
        """根据连接类型获取电突触对象（Level A 中为 ``ExpTwoSynapse`` 模拟）。

        支持 ``"neuron_to_neuron"``、``"neuron_to_muscle"``、``"muscle_to_muscle"`` 三种类型。
        若存在针对特定细胞对的精确参数覆盖，突触 ID 将使用 ``pre_to_post_elec_syn`` 格式。

        :param pre_cell: 突触前细胞名称
        :param post_cell: 突触后细胞名称
        :param type: 连接类型字符串
        :return: 配置好的 ``ExpTwoSynapse`` 对象
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
            erev = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "erev"
            )
            decay = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "decay"
            )
            rise = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "rise"
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
            erev = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "erev"
            )
            decay = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "decay"
            )
            rise = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "rise"
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
            erev = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "erev"
            )
            decay = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "decay"
            )
            rise = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "rise"
            )
            conn_id = "muscle_to_muscle_elec_syn"

        if self.found_specific_param:
            conn_id = "%s_to_%s_elec_syn" % (pre_cell, post_cell)

        return ExpTwoSynapse(
            id=conn_id, gbase=gbase, erev=erev, tau_decay=decay, tau_rise=rise
        )

    def get_exc_syn(self, pre_cell, post_cell, type):
        """根据连接类型获取兴奋性化学突触对象（``ExpTwoSynapse``）。

        :param pre_cell: 突触前细胞名称
        :param post_cell: 突触后细胞名称
        :param type: 连接类型字符串（``"neuron_to_neuron"`` 或 ``"neuron_to_muscle"``）
        :return: 配置好的 ``ExpTwoSynapse`` 兴奋性突触对象
        """
        self.found_specific_param = False

        specific_param_template = "%s_to_%s_chem_exc_syn_%s"
        if type == "neuron_to_neuron":
            gbase = self.get_conn_param(
                pre_cell,
                post_cell,
                specific_param_template,
                "neuron_to_neuron_chem_exc_syn_%s",
                "gbase",
            )
            erev = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "chem_exc_syn_%s", "erev"
            )
            decay = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "chem_exc_syn_%s", "decay"
            )
            rise = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "chem_exc_syn_%s", "rise"
            )

            conn_id = "neuron_to_neuron_exc_syn"

        elif type == "neuron_to_muscle":
            gbase = self.get_conn_param(
                pre_cell,
                post_cell,
                specific_param_template,
                "neuron_to_muscle_chem_exc_syn_%s",
                "gbase",
            )
            erev = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "chem_exc_syn_%s", "erev"
            )
            decay = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "chem_exc_syn_%s", "decay"
            )
            rise = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "chem_exc_syn_%s", "rise"
            )
            conn_id = "neuron_to_muscle_exc_syn"

        if self.found_specific_param:
            conn_id = "%s_to_%s_exc_syn" % (pre_cell, post_cell)

        return ExpTwoSynapse(
            id=conn_id, gbase=gbase, erev=erev, tau_decay=decay, tau_rise=rise
        )

    def get_inh_syn(self, pre_cell, post_cell, type):
        """根据连接类型获取抑制性化学突触对象（``ExpTwoSynapse``）。

        :param pre_cell: 突触前细胞名称
        :param post_cell: 突触后细胞名称
        :param type: 连接类型字符串（``"neuron_to_neuron"`` 或 ``"neuron_to_muscle"``）
        :return: 配置好的 ``ExpTwoSynapse`` 抑制性突触对象
        """
        self.found_specific_param = False

        specific_param_template = "%s_to_%s_chem_inh_syn_%s"
        if type == "neuron_to_neuron":
            gbase = self.get_conn_param(
                pre_cell,
                post_cell,
                specific_param_template,
                "neuron_to_neuron_chem_inh_syn_%s",
                "gbase",
            )
            erev = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "chem_inh_syn_%s", "erev"
            )
            decay = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "chem_inh_syn_%s", "decay"
            )
            rise = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "chem_inh_syn_%s", "rise"
            )

            conn_id = "neuron_to_neuron_inh_syn"

        elif type == "neuron_to_muscle":
            gbase = self.get_conn_param(
                pre_cell,
                post_cell,
                specific_param_template,
                "neuron_to_muscle_chem_inh_syn_%s",
                "gbase",
            )
            erev = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "chem_inh_syn_%s", "erev"
            )
            decay = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "chem_inh_syn_%s", "decay"
            )
            rise = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "chem_inh_syn_%s", "rise"
            )
            conn_id = "neuron_to_muscle_inh_syn"

        if self.found_specific_param:
            conn_id = "%s_to_%s_inh_syn" % (pre_cell, post_cell)

        return ExpTwoSynapse(
            id=conn_id, gbase=gbase, erev=erev, tau_decay=decay, tau_rise=rise
        )
