# =============================================================================
# 功能描述：
#   Level BC1 混合参数层级定义。细胞使用 B 级的 IafActivityCell，突触使用
#   C1 级的 GradedSynapse，兼顾计算效率和模拟型突触传递。
#
# 类与方法索引：
#   ParameterisedModel                   (L43)   — ParameterisedModel 类
#     __init__                           (L44)   — 初始化 Level BC1 参数模型，混合层级：B 级细胞 + C1 级模拟突触
#     set_default_bioparameters          (L60)   — 设置 Level BC1 的默认生物参数，同时包含 IaF 细胞参数和 GradedSynapse 参数
#     create_generic_muscle_cell         (L130)  — 创建带 activity 变量的肌肉细胞（``IafActivityCell``）
#     create_generic_neuron_cell         (L142)  — 创建带 activity 变量的神经元细胞（``IafActivityCell``）
#     create_offset                      (L154)  — 创建偏置电流生成器（``PulseGenerator``）
#     create_neuron_to_neuron_syn        (L163)  — 创建神经元间模拟突触（``GradedSynapse``）和缝隙连接（``GapJunction``）
#     create_neuron_to_muscle_syn        (L192)  — 创建神经元到肌肉的模拟突触（``GradedSynapse``）和缝隙连接（``GapJunction``）
#     create_models                      (L221)  — 按顺序创建所有网络组件：肌肉细胞、神经元细胞、偏置电流、神经元间突触、
#
# 更新日志：
#   2026-04-16  Copilot  添加中文 docstring 和行内注释（计划1阶段三）
#
# 当前维护者：Copilot
# =============================================================================
"""

Parameters BC1:
    Cells:           Simple integrate and fire cells, custom component type, with an "activity" variable (same as B)
    Chem Synapses:   Analogue/graded synapses; continuous transmission (voltage dependent) (same as C1)
    Gap junctions:   Electrical connection; current linerly depends on difference in voltages

ASSESSMENT:
    Probably not very useful in longer term; same criticisms as parameters A; see C0

"""

from neuroml import GradedSynapse
from neuroml import GapJunction
from neuroml import PulseGenerator

from c302.bioparameters import c302ModelPrototype

from c302.parameters_B import IafActivityCell


class ParameterisedModel(c302ModelPrototype):
    def __init__(self):
        """初始化 Level BC1 参数模型，混合层级：B 级细胞 + C1 级模拟突触。

        BC1 的设计动机：
        - 保留 B 级简单的 ``IafActivityCell``（带 activity 变量），降低计算复杂度
        - 但将突触改为 C1 级的 ``GradedSynapse``，允许非放电连续信号传递
        - 适合需要模拟连续突触但不需要真实离子通道的场景

        评估：长期而言可能不如 C0（简化导电 + 模拟突触）有用，见 ASSESSMENT 注释。
        """
        super(ParameterisedModel, self).__init__()
        self.level = "BC1"
        self.custom_component_types_definitions = "cell_B.xml"

        self.set_default_bioparameters()

    def set_default_bioparameters(self):
        """设置 Level BC1 的默认生物参数，同时包含 IaF 细胞参数和 GradedSynapse 参数。

        参数分组：
        - 肌肉/神经元 IaF 细胞参数（来自 Level B）
        - 兴奋性模拟突触参数：conductance、delta、Vth、erev、k
        - 抑制性模拟突触参数
        - 电突触（缝隙连接）参数
        - 偏置电流参数（默认幅度为 0）
        """
        # IaF 肌肉细胞参数（与 B 级相同）：漏电位/复位/阈值/膜电容/电导/tau1
        self.add_bioparameter("muscle_iaf_leak_reversal", "-50mV", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_iaf_reset", "-50mV", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_iaf_thresh", "-30mV", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_iaf_C", "3pF", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_iaf_conductance", "0.1nS", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_iaf_tau1", "50ms", "BlindGuess", "0.1")

        # IaF 神经元细胞参数（与肌肉相同，均为 B 级简单积分-发放模型）
        self.add_bioparameter("neuron_iaf_leak_reversal", "-50mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_reset", "-50mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_thresh", "-30mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_C", "3pF", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_conductance", "0.1nS", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_iaf_tau1", "50ms", "BlindGuess", "0.1")

        # GradedSynapse 兴奋性突触（C1 级，连续传递）
        self.add_bioparameter(
            "neuron_to_neuron_exc_syn_conductance", "8 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_exc_syn_conductance", "8 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("exc_syn_delta", "5 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_vth", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_erev", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_k", "0.025per_ms", "BlindGuess", "0.1")

        # GradedSynapse 抑制性突触（erev=-70 mV）
        self.add_bioparameter(
            "neuron_to_neuron_inh_syn_conductance", "8 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_inh_syn_conductance", "8 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("inh_syn_delta", "5 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_vth", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_erev", "-70 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_k", "0.025per_ms", "BlindGuess", "0.1")

        # 缝隙连接（GapJunction）
        self.add_bioparameter(
            "neuron_to_neuron_elec_syn_gbase", "0.3 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_elec_syn_gbase", "0.3 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter(
            "unphysiological_offset_current", "0 nA", "KnownError", "0"
        )  # Can be activated later
        self.add_bioparameter(
            "unphysiological_offset_current_del", "0 ms", "KnownError", "0"
        )
        self.add_bioparameter(
            "unphysiological_offset_current_dur", "2000 ms", "KnownError", "0"
        )

    def create_generic_muscle_cell(self):
        """创建带 activity 变量的肌肉细胞（``IafActivityCell``）。"""
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
        """创建带 activity 变量的神经元细胞（``IafActivityCell``）。"""
        self.generic_neuron_cell = IafActivityCell(
            id="generic_neuron_iaf_cell",
            C=self.get_bioparameter("neuron_iaf_C").value,
            thresh=self.get_bioparameter("neuron_iaf_thresh").value,
            reset=self.get_bioparameter("neuron_iaf_reset").value,
            leak_conductance=self.get_bioparameter("neuron_iaf_conductance").value,
            leak_reversal=self.get_bioparameter("neuron_iaf_leak_reversal").value,
            tau1=self.get_bioparameter("neuron_iaf_tau1").value,
        )

    def create_offset(self):
        """创建偏置电流生成器（``PulseGenerator``）。"""
        self.offset_current = PulseGenerator(
            id="offset_current",
            delay=self.get_bioparameter("unphysiological_offset_current_del").value,
            duration=self.get_bioparameter("unphysiological_offset_current_dur").value,
            amplitude=self.get_bioparameter("unphysiological_offset_current").value,
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
        """创建神经元到肌肉的模拟突触（``GradedSynapse``）和缝隙连接（``GapJunction``）。"""
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

    def create_models(self):
        """按顺序创建所有网络组件：肌肉细胞、神经元细胞、偏置电流、神经元间突触、
        神经元到肌肉突触。
        """
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_offset()
        self.create_neuron_to_muscle_syn()
        self.create_neuron_to_neuron_syn()
