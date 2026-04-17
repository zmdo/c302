# =============================================================================
# 功能描述：
#   参数化模型工厂，根据层级名称创建 c302ModelPrototype 实例。
#   从 YAML 加载生物参数，按层级族系实现 create_models / get_*_syn 等方法。
#   支持层级：A, B, C, C0, C1, D, D1（可扩展 BC1, C2, W2D）。
#
# 类与方法索引：
#   IafActivityCell                      (L113)  — IafCell 变体，增加 tau1 时间常数（对应 cell_B.xml 中的 iafActivityCell）
#     __init__                           (L116)  — __init__ 函数
#     export                             (L125)  — 将 iafActivityCell 写入 NeuroML XML
#   GradedSynapse2                       (L143)  — 自定义 GradedSynapse2（对应 custom_synapses.xml 中的 gradedSynapse2）
#     __init__                           (L146)  — __init__ 函数
#     export                             (L155)  — 将 gradedSynapse2 写入 NeuroML XML
#   _ModelBase                           (L178)  — 所有层级模型的基类，从 YAML 加载生物参数
#     __init__                           (L181)  — __init__ 函数
#     get_exc_syn                        (L198)  — 创建兴奋性化学突触（ExpTwoSynapse）
#     get_inh_syn                        (L233)  — 创建抑制性化学突触（ExpTwoSynapse）
#     _get_elec_syn_params               (L268)  — 提取电突触连接参数（gbase + 可选 erev/decay/rise）
#   _IafModel                            (L304)  — Level A：积分放电模型 + 事件突触
#     create_models                      (L307)  — 创建所有细胞和突触模型
#     create_generic_muscle_cell         (L315)  — 创建通用肌肉 IafCell
#     create_generic_neuron_cell         (L326)  — 创建通用神经元 IafCell
#     create_offset                      (L337)  — 创建偏置电流生成器
#     create_neuron_to_neuron_syn        (L346)  — 创建神经元间突触（全部 ExpTwoSynapse）
#     create_neuron_to_muscle_syn        (L371)  — 创建神经元到肌肉突触（全部 ExpTwoSynapse）
#     get_elec_syn                       (L395)  — Level A 的电突触 — 返回 ExpTwoSynapse（假电突触）
#   _IafActivityModel                    (L418)  — Level B：IafActivityCell + 真实 GapJunction 电突触
#     create_generic_muscle_cell         (L421)  — 创建通用肌肉 IafActivityCell
#     create_generic_neuron_cell         (L433)  — 创建通用神经元 IafActivityCell
#     create_neuron_to_neuron_syn        (L445)  — 创建神经元间突触（化学 ExpTwoSynapse + 电 GapJunction）
#     create_neuron_to_muscle_syn        (L466)  — 创建神经元到肌肉突触（化学 ExpTwoSynapse + 电 GapJunction）
#     get_elec_syn                       (L487)  — Level B 的电突触 — 返回 GapJunction
#   _create_hh_cell                      (L498)  — 创建单室 HH 导电细胞（供 C/D 族共用）
#   _HHModel                             (L608)  — Level C 族：单室 HH 导电模型
#     create_models                      (L611)  — 创建肌肉/神经元细胞、偏置电流、浓度模型和突触
#     create_generic_muscle_cell         (L619)  — 创建通用肌肉 HH 细胞
#     create_generic_neuron_cell         (L625)  — 创建通用神经元 HH 细胞
#     create_offsetcurrent_concentrationmodel (L631)  — 创建偏置电流和钙浓度模型
#     create_neuron_to_neuron_syn        (L647)  — 创建神经元间突触（ExpTwoSynapse + GapJunction）
#     create_neuron_to_muscle_syn        (L668)  — 创建神经元到肌肉突触（ExpTwoSynapse + GapJunction）
#     get_elec_syn                       (L689)  — Level C 的电突触 — 返回 GapJunction
#   _create_c0_cell                      (L700)  — 创建 C0 级 HH 导电细胞（使用 ca_simple 通道和分离比膜电容）
#   _HHC0Model                           (L787)  — Level C0：HH 导电模型 + ca_simple 通道 + GradedSynapse2 突触
#     create_models                      (L790)  — 创建所有细胞和突触模型
#     create_generic_muscle_cell         (L798)  — 创建通用肌肉 HH 细胞（ca_simple 通道）
#     create_generic_neuron_cell         (L804)  — 创建通用神经元 HH 细胞（ca_simple 通道）
#     create_offsetcurrent_concentrationmodel (L810)  — 创建偏置电流和钙浓度模型
#     create_neuron_to_neuron_syn        (L826)  — 创建神经元间突触（GradedSynapse2 + GapJunction）
#     create_neuron_to_muscle_syn        (L855)  — 创建神经元到肌肉突触（GradedSynapse2 + GapJunction）
#     get_elec_syn                       (L884)  — 电突触 — GapJunction
#     get_exc_syn                        (L889)  — 兴奋性突触 — GradedSynapse2
#     get_inh_syn                        (L929)  — 抑制性突触 — GradedSynapse2
#     create_n_connection_synapse        (L969)  — 注册突触原型（含 GradedSynapse2 支持）
#     is_analog_conn                     (L981)  — 判断是否为模拟连接
#   _HHC1Model                           (L991)  — Level C1：HH 导电模型 + 标准 GradedSynapse 化学突触
#     create_neuron_to_neuron_syn        (L994)  — 创建神经元间突触（GradedSynapse + GapJunction）
#     create_neuron_to_muscle_syn        (L1021) — 创建神经元到肌肉突触（GradedSynapse + GapJunction）
#     get_exc_syn                        (L1048) — 兴奋性突触 — GradedSynapse
#     get_inh_syn                        (L1081) — 抑制性突触 — GradedSynapse
#   _HHMultiCompModel                    (L1120) — Level D：导电模型，无通用神经元细胞（按名称从 NML 创建）
#     create_models                      (L1123) — 创建肌肉细胞、偏置电流、浓度模型和突触（不创建通用神经元）
#     create_neuron_cell                 (L1131) — 创建单个神经元 Cell（D 族特有的逐个构建方式）
#   _HHGradedModel                       (L1224) — Level D1：导电模型 + GradedSynapse2 化学突触
#     create_neuron_to_neuron_syn        (L1227) — 创建神经元间突触（GradedSynapse2 + GapJunction）
#     create_neuron_to_muscle_syn        (L1256) — 创建神经元到肌肉突触（GradedSynapse2 + GapJunction）
#     get_exc_syn                        (L1285) — Level D1 的兴奋性突触 — 返回 GradedSynapse2
#     get_inh_syn                        (L1328) — Level D1 的抑制性突触 — 返回 GradedSynapse2
#     create_n_connection_synapse        (L1371) — 注册突触原型（含 GradedSynapse2 支持）
#     is_analog_conn                     (L1385) — 判断是否为模拟连接（含 GradedSynapse2）
#   create_model                         (L1406) — 根据层级名称创建参数化模型实例
#
# 更新日志：
#   2026-04-18  Copilot  计划3阶段八：新建模型工厂，弥合 YAML→generate 调用链
#
# 当前维护者：Copilot
# =============================================================================
"""参数化模型工厂。"""
import logging

from neuroml import (
    BiophysicalProperties,
    Cell,
    ChannelDensity,
    ExpTwoSynapse,
    FixedFactorConcentrationModel,
    GapJunction,
    GradedSynapse,
    IafCell,
    InitMembPotential,
    IntracellularProperties,
    MembraneProperties,
    Morphology,
    Point3DWithDiam,
    PulseGenerator,
    Resistivity,
    Segment,
    SpecificCapacitance,
    Species,
    SpikeThresh,
)

from c302.parameters.loader import ParameterLoader
from c302.parameters.model import c302ModelPrototype

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 自定义 NeuroML 类型（非标准 NeuroML，由自定义 XML 定义）
# ---------------------------------------------------------------------------


class IafActivityCell:
    """IafCell 变体，增加 tau1 时间常数（对应 cell_B.xml 中的 iafActivityCell）。"""

    def __init__(self, id, C, thresh, reset, leak_conductance, leak_reversal, tau1):
        self.id = id
        self.C = C
        self.thresh = thresh
        self.reset = reset
        self.leak_conductance = leak_conductance
        self.leak_reversal = leak_reversal
        self.tau1 = tau1

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        """将 iafActivityCell 写入 NeuroML XML。"""
        outfile.write(
            "    " * level
            + '<iafCell type="iafActivityCell" id="%s" C="%s" thresh="%s" reset="%s"'
            ' leakConductance="%s" leakReversal="%s" tau1="%s"/>\n'
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


class GradedSynapse2:
    """自定义 GradedSynapse2（对应 custom_synapses.xml 中的 gradedSynapse2）。"""

    def __init__(self, id, conductance, ar, ad, beta, vth, erev):
        self.id = id
        self.conductance = conductance
        self.ar = ar
        self.ad = ad
        self.beta = beta
        self.vth = vth
        self.erev = erev

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        """将 gradedSynapse2 写入 NeuroML XML。"""
        outfile.write(
            "    " * level
            + '<gradedSynapse2 id="%s" conductance="%s" ar="%s" ad="%s"'
            ' beta="%s" vth="%s" erev="%s"/>\n'
            % (
                self.id,
                self.conductance,
                self.ar,
                self.ad,
                self.beta,
                self.vth,
                self.erev,
            )
        )


# ---------------------------------------------------------------------------
# 模型基类
# ---------------------------------------------------------------------------


class _ModelBase(c302ModelPrototype):
    """所有层级模型的基类，从 YAML 加载生物参数。"""

    def __init__(self, level: str) -> None:
        super().__init__()
        self.level = level

        # 从 YAML 加载生物参数
        loader = ParameterLoader()
        for bp in loader.load_parameters(level):
            self.add_bioparameter_obj(bp)

        # 加载元数据
        raw = loader.load_raw(level)
        self.custom_component_types_definitions = raw.get(
            "custom_component_types_definitions"
        )

    # -- 共享的化学突触工厂 (A/B/C/D 通用) --

    def get_exc_syn(self, pre_cell, post_cell, type):
        """创建兴奋性化学突触（ExpTwoSynapse）。"""
        self.found_specific_param = False
        specific = "%s_to_%s_chem_exc_syn_%s"

        if type == "neuron_to_neuron":
            default = "neuron_to_neuron_chem_exc_syn_%s"
        elif type == "neuron_to_muscle":
            default = "neuron_to_muscle_chem_exc_syn_%s"
        else:
            default = "neuron_to_neuron_chem_exc_syn_%s"

        gbase = self.get_conn_param(pre_cell, post_cell, specific, default, "gbase")
        erev = self.get_conn_param(
            pre_cell, post_cell, specific, "chem_exc_syn_%s", "erev"
        )
        decay = self.get_conn_param(
            pre_cell, post_cell, specific, "chem_exc_syn_%s", "decay"
        )
        rise = self.get_conn_param(
            pre_cell, post_cell, specific, "chem_exc_syn_%s", "rise"
        )

        conn_id = (
            "neuron_to_neuron_exc_syn"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_exc_syn"
        )
        if self.found_specific_param:
            conn_id = "%s_to_%s_exc_syn" % (pre_cell, post_cell)

        return ExpTwoSynapse(
            id=conn_id, gbase=gbase, erev=erev, tau_decay=decay, tau_rise=rise
        )

    def get_inh_syn(self, pre_cell, post_cell, type):
        """创建抑制性化学突触（ExpTwoSynapse）。"""
        self.found_specific_param = False
        specific = "%s_to_%s_chem_inh_syn_%s"

        if type == "neuron_to_neuron":
            default = "neuron_to_neuron_chem_inh_syn_%s"
        elif type == "neuron_to_muscle":
            default = "neuron_to_muscle_chem_inh_syn_%s"
        else:
            default = "neuron_to_neuron_chem_inh_syn_%s"

        gbase = self.get_conn_param(pre_cell, post_cell, specific, default, "gbase")
        erev = self.get_conn_param(
            pre_cell, post_cell, specific, "chem_inh_syn_%s", "erev"
        )
        decay = self.get_conn_param(
            pre_cell, post_cell, specific, "chem_inh_syn_%s", "decay"
        )
        rise = self.get_conn_param(
            pre_cell, post_cell, specific, "chem_inh_syn_%s", "rise"
        )

        conn_id = (
            "neuron_to_neuron_inh_syn"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_inh_syn"
        )
        if self.found_specific_param:
            conn_id = "%s_to_%s_inh_syn" % (pre_cell, post_cell)

        return ExpTwoSynapse(
            id=conn_id, gbase=gbase, erev=erev, tau_decay=decay, tau_rise=rise
        )

    def _get_elec_syn_params(self, pre_cell, post_cell, type):
        """提取电突触连接参数（gbase + 可选 erev/decay/rise）。"""
        self.found_specific_param = False
        specific = "%s_to_%s_elec_syn_%s"

        if type == "neuron_to_neuron":
            default_gbase = "neuron_to_neuron_elec_syn_%s"
        elif type == "neuron_to_muscle":
            default_gbase = "neuron_to_muscle_elec_syn_%s"
        elif type == "muscle_to_muscle":
            default_gbase = "muscle_to_muscle_elec_syn_%s"
        else:
            default_gbase = "neuron_to_neuron_elec_syn_%s"

        gbase = self.get_conn_param(
            pre_cell, post_cell, specific, default_gbase, "gbase"
        )

        # 构造 conn_id
        id_map = {
            "neuron_to_neuron": "neuron_to_neuron_elec_syn",
            "neuron_to_muscle": "neuron_to_muscle_elec_syn",
            "muscle_to_muscle": "muscle_to_muscle_elec_syn",
        }
        conn_id = id_map.get(type, "neuron_to_neuron_elec_syn")
        if self.found_specific_param:
            conn_id = "%s_to_%s_elec_syn" % (pre_cell, post_cell)

        return gbase, conn_id


# ---------------------------------------------------------------------------
# Level A — IafCell + 全部 ExpTwoSynapse
# ---------------------------------------------------------------------------


class _IafModel(_ModelBase):
    """Level A：积分放电模型 + 事件突触。"""

    def create_models(self):
        """创建所有细胞和突触模型。"""
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_offset()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()

    def create_generic_muscle_cell(self):
        """创建通用肌肉 IafCell。"""
        self.generic_muscle_cell = IafCell(
            id="generic_muscle_iaf_cell",
            C=self.get_bioparameter("muscle_iaf_C").value,
            thresh=self.get_bioparameter("muscle_iaf_thresh").value,
            reset=self.get_bioparameter("muscle_iaf_reset").value,
            leak_conductance=self.get_bioparameter("muscle_iaf_conductance").value,
            leak_reversal=self.get_bioparameter("muscle_iaf_leak_reversal").value,
        )

    def create_generic_neuron_cell(self):
        """创建通用神经元 IafCell。"""
        self.generic_neuron_cell = IafCell(
            id="generic_neuron_iaf_cell",
            C=self.get_bioparameter("neuron_iaf_C").value,
            thresh=self.get_bioparameter("neuron_iaf_thresh").value,
            reset=self.get_bioparameter("neuron_iaf_reset").value,
            leak_conductance=self.get_bioparameter("neuron_iaf_conductance").value,
            leak_reversal=self.get_bioparameter("neuron_iaf_leak_reversal").value,
        )

    def create_offset(self):
        """创建偏置电流生成器。"""
        self.offset_current = PulseGenerator(
            id="offset_current",
            delay=self.get_bioparameter("unphysiological_offset_current_del").value,
            duration=self.get_bioparameter("unphysiological_offset_current_dur").value,
            amplitude=self.get_bioparameter("unphysiological_offset_current").value,
        )

    def create_neuron_to_neuron_syn(self):
        """创建神经元间突触（全部 ExpTwoSynapse）。"""
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
        # Level A 的"电突触"实际是 ExpTwoSynapse（gbase=0，无真实 GapJunction）
        self.neuron_to_neuron_elec_syn = ExpTwoSynapse(
            id="neuron_to_neuron_elec_syn",
            gbase=self.get_bioparameter("neuron_to_neuron_elec_syn_gbase").value,
            erev=self.get_bioparameter("elec_syn_erev").value,
            tau_decay=self.get_bioparameter("elec_syn_decay").value,
            tau_rise=self.get_bioparameter("elec_syn_rise").value,
        )

    def create_neuron_to_muscle_syn(self):
        """创建神经元到肌肉突触（全部 ExpTwoSynapse）。"""
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

    def get_elec_syn(self, pre_cell, post_cell, type):
        """Level A 的电突触 — 返回 ExpTwoSynapse（假电突触）。"""
        gbase, conn_id = self._get_elec_syn_params(pre_cell, post_cell, type)
        # 还需要 erev / decay / rise
        erev = self.get_conn_param(
            pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "erev"
        )
        decay = self.get_conn_param(
            pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "decay"
        )
        rise = self.get_conn_param(
            pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "rise"
        )
        return ExpTwoSynapse(
            id=conn_id, gbase=gbase, erev=erev, tau_decay=decay, tau_rise=rise
        )


# ---------------------------------------------------------------------------
# Level B — IafActivityCell + GapJunction
# ---------------------------------------------------------------------------


class _IafActivityModel(_IafModel):
    """Level B：IafActivityCell + 真实 GapJunction 电突触。"""

    def create_generic_muscle_cell(self):
        """创建通用肌肉 IafActivityCell。"""
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
        """创建通用神经元 IafActivityCell。"""
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
        """创建神经元间突触（化学 ExpTwoSynapse + 电 GapJunction）。"""
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
        """创建神经元到肌肉突触（化学 ExpTwoSynapse + 电 GapJunction）。"""
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
        """Level B 的电突触 — 返回 GapJunction。"""
        gbase, conn_id = self._get_elec_syn_params(pre_cell, post_cell, type)
        return GapJunction(id=conn_id, conductance=gbase)


# ---------------------------------------------------------------------------
# Level C 族 — 单室 HH 导电模型 + ExpTwoSynapse + GapJunction
# ---------------------------------------------------------------------------


def _create_hh_cell(model, cell_id, is_muscle=True):
    """创建单室 HH 导电细胞（供 C/D 族共用）。

    :param model: 模型实例（含 bioparameters）
    :param cell_id: 细胞 ID 字符串
    :param is_muscle: True 使用肌肉参数前缀，False 使用神经元参数前缀
    :return: Cell 对象
    """
    cell = Cell(id=cell_id)
    morphology = Morphology()
    morphology.id = "morphology_" + cell.id
    cell.morphology = morphology

    diameter = model.get_bioparameter("cell_diameter").value
    prox = Point3DWithDiam(x="0", y="0", z="0", diameter=diameter)

    if is_muscle:
        # 肌肉有长度
        length = model.get_bioparameter("muscle_length").value
        dist = Point3DWithDiam(x="0", y=length, z="0", diameter=diameter)
    else:
        # 神经元为球形（prox == dist）
        dist = Point3DWithDiam(x="0", y="0", z="0", diameter=diameter)

    segment = Segment(id="0", name="soma", proximal=prox, distal=dist)
    morphology.segments.append(segment)

    # 生物物理属性
    cell.biophysical_properties = BiophysicalProperties(id="biophys_" + cell.id)
    mp = MembraneProperties()
    cell.biophysical_properties.membrane_properties = mp

    mp.init_memb_potentials.append(
        InitMembPotential(value=model.get_bioparameter("initial_memb_pot").value)
    )
    mp.specific_capacitances.append(
        SpecificCapacitance(
            value=model.get_bioparameter("specific_capacitance").value
        )
    )

    # 放电阈值
    prefix = "muscle" if is_muscle else "neuron"
    mp.spike_threshes.append(
        SpikeThresh(value=model.get_bioparameter(f"{prefix}_spike_thresh").value)
    )

    # 离子通道密度
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(f"{prefix}_leak_cond_density").value,
            id="Leak_all",
            ion_channel="Leak",
            erev=model.get_bioparameter("leak_erev").value,
            ion="non_specific",
        )
    )
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(f"{prefix}_k_slow_cond_density").value,
            id="k_slow_all",
            ion_channel="k_slow",
            erev=model.get_bioparameter("k_slow_erev").value,
            ion="k",
        )
    )
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(f"{prefix}_k_fast_cond_density").value,
            id="k_fast_all",
            ion_channel="k_fast",
            erev=model.get_bioparameter("k_fast_erev").value,
            ion="k",
        )
    )
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(
                f"{prefix}_ca_boyle_cond_density"
            ).value,
            id="ca_boyle_all",
            ion_channel="ca_boyle",
            erev=model.get_bioparameter("ca_boyle_erev").value,
            ion="ca",
        )
    )

    # 胞内属性
    ip = IntracellularProperties()
    cell.biophysical_properties.intracellular_properties = ip

    # resistivity 参数：D 族在 YAML 中定义，C 族写死
    resis_bp = model.get_bioparameter("resistivity")
    ip.resistivities.append(
        Resistivity(value=resis_bp.value if resis_bp else "0.1 kohm_cm")
    )

    # 钙离子物种
    species = Species(
        id="ca",
        ion="ca",
        concentration_model="CaPool",
        initial_concentration="0 mM",
        initial_ext_concentration="2E-6 mol_per_cm3",
    )
    ip.species.append(species)

    return cell


class _HHModel(_ModelBase):
    """Level C 族：单室 HH 导电模型。"""

    def create_models(self):
        """创建肌肉/神经元细胞、偏置电流、浓度模型和突触。"""
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_offsetcurrent_concentrationmodel()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()

    def create_generic_muscle_cell(self):
        """创建通用肌肉 HH 细胞。"""
        self.generic_muscle_cell = _create_hh_cell(
            self, "GenericMuscleCell", is_muscle=True
        )

    def create_generic_neuron_cell(self):
        """创建通用神经元 HH 细胞。"""
        self.generic_neuron_cell = _create_hh_cell(
            self, "GenericNeuronCell", is_muscle=False
        )

    def create_offsetcurrent_concentrationmodel(self):
        """创建偏置电流和钙浓度模型。"""
        self.offset_current = PulseGenerator(
            id="offset_current",
            delay=self.get_bioparameter("unphysiological_offset_current_del").value,
            duration=self.get_bioparameter("unphysiological_offset_current_dur").value,
            amplitude=self.get_bioparameter("unphysiological_offset_current").value,
        )
        self.concentration_model = FixedFactorConcentrationModel(
            id="CaPool",
            ion="ca",
            resting_conc="0 mM",
            decay_constant=self.get_bioparameter("ca_conc_decay_time").value,
            rho=self.get_bioparameter("ca_conc_rho").value,
        )

    def create_neuron_to_neuron_syn(self):
        """创建神经元间突触（ExpTwoSynapse + GapJunction）。"""
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
        """创建神经元到肌肉突触（ExpTwoSynapse + GapJunction）。"""
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
        """Level C 的电突触 — 返回 GapJunction。"""
        gbase, conn_id = self._get_elec_syn_params(pre_cell, post_cell, type)
        return GapJunction(id=conn_id, conductance=gbase)


# ---------------------------------------------------------------------------
# Level C0 — HH 导电模型 + ca_simple 通道 + GradedSynapse2
# ---------------------------------------------------------------------------


def _create_c0_cell(model, cell_id, is_muscle=True):
    """创建 C0 级 HH 导电细胞（使用 ca_simple 通道和分离比膜电容）。"""
    cell = Cell(id=cell_id)
    morphology = Morphology()
    morphology.id = "morphology_" + cell.id
    cell.morphology = morphology

    diameter = model.get_bioparameter("cell_diameter").value
    prox = Point3DWithDiam(x="0", y="0", z="0", diameter=diameter)

    if is_muscle:
        length = model.get_bioparameter("muscle_length").value
        dist = Point3DWithDiam(x="0", y=length, z="0", diameter=diameter)
    else:
        dist = Point3DWithDiam(x="0", y="0", z="0", diameter=diameter)

    segment = Segment(id="0", name="soma", proximal=prox, distal=dist)
    morphology.segments.append(segment)

    cell.biophysical_properties = BiophysicalProperties(id="biophys_" + cell.id)
    mp = MembraneProperties()
    cell.biophysical_properties.membrane_properties = mp

    mp.init_memb_potentials.append(
        InitMembPotential(value=model.get_bioparameter("initial_memb_pot").value)
    )

    # C0 使用分离的 muscle/neuron specific_capacitance
    prefix = "muscle" if is_muscle else "neuron"
    mp.specific_capacitances.append(
        SpecificCapacitance(
            value=model.get_bioparameter(f"{prefix}_specific_capacitance").value
        )
    )
    mp.spike_threshes.append(
        SpikeThresh(value=model.get_bioparameter(f"{prefix}_spike_thresh").value)
    )

    # 漏泄通道
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(f"{prefix}_leak_cond_density").value,
            id="Leak_all",
            ion_channel="Leak",
            erev=model.get_bioparameter("leak_erev").value,
            ion="non_specific",
        )
    )
    # 慢钾通道
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(f"{prefix}_k_slow_cond_density").value,
            id="k_slow_all",
            ion_channel="k_slow",
            erev=model.get_bioparameter("k_slow_erev").value,
            ion="k",
        )
    )
    # C0 使用 ca_simple 通道（而非 ca_boyle）
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(
                f"{prefix}_ca_simple_cond_density"
            ).value,
            id="ca_simple_all",
            ion_channel="ca_simple",
            erev=model.get_bioparameter("ca_simple_erev").value,
            ion="ca",
        )
    )

    ip = IntracellularProperties()
    cell.biophysical_properties.intracellular_properties = ip
    ip.resistivities.append(Resistivity(value="0.1 kohm_cm"))

    species = Species(
        id="ca",
        ion="ca",
        concentration_model="CaPool",
        initial_concentration="0 mM",
        initial_ext_concentration="2E-6 mol_per_cm3",
    )
    ip.species.append(species)

    return cell


class _HHC0Model(_ModelBase):
    """Level C0：HH 导电模型 + ca_simple 通道 + GradedSynapse2 突触。"""

    def create_models(self):
        """创建所有细胞和突触模型。"""
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_offsetcurrent_concentrationmodel()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()

    def create_generic_muscle_cell(self):
        """创建通用肌肉 HH 细胞（ca_simple 通道）。"""
        self.generic_muscle_cell = _create_c0_cell(
            self, "GenericMuscleCell", is_muscle=True
        )

    def create_generic_neuron_cell(self):
        """创建通用神经元 HH 细胞（ca_simple 通道）。"""
        self.generic_neuron_cell = _create_c0_cell(
            self, "GenericNeuronCell", is_muscle=False
        )

    def create_offsetcurrent_concentrationmodel(self):
        """创建偏置电流和钙浓度模型。"""
        self.offset_current = PulseGenerator(
            id="offset_current",
            delay=self.get_bioparameter("unphysiological_offset_current_del").value,
            duration=self.get_bioparameter("unphysiological_offset_current_dur").value,
            amplitude=self.get_bioparameter("unphysiological_offset_current").value,
        )
        self.concentration_model = FixedFactorConcentrationModel(
            id="CaPool",
            ion="ca",
            resting_conc="0 mM",
            decay_constant=self.get_bioparameter("ca_conc_decay_time").value,
            rho=self.get_bioparameter("ca_conc_rho").value,
        )

    def create_neuron_to_neuron_syn(self):
        """创建神经元间突触（GradedSynapse2 + GapJunction）。"""
        self.neuron_to_neuron_exc_syn = GradedSynapse2(
            id="neuron_to_neuron_exc_syn",
            conductance=self.get_bioparameter(
                "neuron_to_neuron_exc_syn_conductance"
            ).value,
            ar=self.get_bioparameter("exc_syn_ar").value,
            ad=self.get_bioparameter("exc_syn_ad").value,
            beta=self.get_bioparameter("exc_syn_beta").value,
            vth=self.get_bioparameter("exc_syn_vth").value,
            erev=self.get_bioparameter("exc_syn_erev").value,
        )
        self.neuron_to_neuron_inh_syn = GradedSynapse2(
            id="neuron_to_neuron_inh_syn",
            conductance=self.get_bioparameter(
                "neuron_to_neuron_inh_syn_conductance"
            ).value,
            ar=self.get_bioparameter("inh_syn_ar").value,
            ad=self.get_bioparameter("inh_syn_ad").value,
            beta=self.get_bioparameter("inh_syn_beta").value,
            vth=self.get_bioparameter("inh_syn_vth").value,
            erev=self.get_bioparameter("inh_syn_erev").value,
        )
        self.neuron_to_neuron_elec_syn = GapJunction(
            id="neuron_to_neuron_elec_syn",
            conductance=self.get_bioparameter("neuron_to_neuron_elec_syn_gbase").value,
        )

    def create_neuron_to_muscle_syn(self):
        """创建神经元到肌肉突触（GradedSynapse2 + GapJunction）。"""
        self.neuron_to_muscle_exc_syn = GradedSynapse2(
            id="neuron_to_muscle_exc_syn",
            conductance=self.get_bioparameter(
                "neuron_to_muscle_exc_syn_conductance"
            ).value,
            ar=self.get_bioparameter("exc_syn_ar").value,
            ad=self.get_bioparameter("exc_syn_ad").value,
            beta=self.get_bioparameter("exc_syn_beta").value,
            vth=self.get_bioparameter("exc_syn_vth").value,
            erev=self.get_bioparameter("exc_syn_erev").value,
        )
        self.neuron_to_muscle_inh_syn = GradedSynapse2(
            id="neuron_to_muscle_inh_syn",
            conductance=self.get_bioparameter(
                "neuron_to_muscle_inh_syn_conductance"
            ).value,
            ar=self.get_bioparameter("inh_syn_ar").value,
            ad=self.get_bioparameter("inh_syn_ad").value,
            beta=self.get_bioparameter("inh_syn_beta").value,
            vth=self.get_bioparameter("inh_syn_vth").value,
            erev=self.get_bioparameter("inh_syn_erev").value,
        )
        self.neuron_to_muscle_elec_syn = GapJunction(
            id="neuron_to_muscle_elec_syn",
            conductance=self.get_bioparameter("neuron_to_muscle_elec_syn_gbase").value,
        )

    def get_elec_syn(self, pre_cell, post_cell, type):
        """电突触 — GapJunction。"""
        gbase, conn_id = self._get_elec_syn_params(pre_cell, post_cell, type)
        return GapJunction(id=conn_id, conductance=gbase)

    def get_exc_syn(self, pre_cell, post_cell, type):
        """兴奋性突触 — GradedSynapse2。"""
        self.found_specific_param = False
        specific = "%s_to_%s_exc_syn_%s"
        default = (
            "neuron_to_neuron_exc_syn_%s"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_exc_syn_%s"
        )
        conductance = self.get_conn_param(
            pre_cell, post_cell, specific, default, "conductance"
        )
        erev = self.get_conn_param(
            pre_cell, post_cell, specific, "exc_syn_%s", "erev"
        )
        ar = self.get_conn_param(pre_cell, post_cell, specific, "exc_syn_%s", "ar")
        ad = self.get_conn_param(pre_cell, post_cell, specific, "exc_syn_%s", "ad")
        beta = self.get_conn_param(
            pre_cell, post_cell, specific, "exc_syn_%s", "beta"
        )
        vth = self.get_conn_param(pre_cell, post_cell, specific, "exc_syn_%s", "vth")

        conn_id = (
            "neuron_to_neuron_exc_syn"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_exc_syn"
        )
        if self.found_specific_param:
            conn_id = "%s_to_%s_exc_syn" % (pre_cell, post_cell)

        return GradedSynapse2(
            id=conn_id,
            conductance=conductance,
            ar=ar,
            ad=ad,
            beta=beta,
            vth=vth,
            erev=erev,
        )

    def get_inh_syn(self, pre_cell, post_cell, type):
        """抑制性突触 — GradedSynapse2。"""
        self.found_specific_param = False
        specific = "%s_to_%s_inh_syn_%s"
        default = (
            "neuron_to_neuron_inh_syn_%s"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_inh_syn_%s"
        )
        conductance = self.get_conn_param(
            pre_cell, post_cell, specific, default, "conductance"
        )
        erev = self.get_conn_param(
            pre_cell, post_cell, specific, "inh_syn_%s", "erev"
        )
        ar = self.get_conn_param(pre_cell, post_cell, specific, "inh_syn_%s", "ar")
        ad = self.get_conn_param(pre_cell, post_cell, specific, "inh_syn_%s", "ad")
        beta = self.get_conn_param(
            pre_cell, post_cell, specific, "inh_syn_%s", "beta"
        )
        vth = self.get_conn_param(pre_cell, post_cell, specific, "inh_syn_%s", "vth")

        conn_id = (
            "neuron_to_neuron_inh_syn"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_inh_syn"
        )
        if self.found_specific_param:
            conn_id = "%s_to_%s_inh_syn" % (pre_cell, post_cell)

        return GradedSynapse2(
            id=conn_id,
            conductance=conductance,
            ar=ar,
            ad=ad,
            beta=beta,
            vth=vth,
            erev=erev,
        )

    def create_n_connection_synapse(self, prototype_syn, n, nml_doc, existing_synapses):
        """注册突触原型（含 GradedSynapse2 支持）。"""
        if prototype_syn.id in existing_synapses:
            return existing_synapses[prototype_syn.id]
        if isinstance(prototype_syn, GradedSynapse2):
            existing_synapses[prototype_syn.id] = prototype_syn
            nml_doc.graded_synapses.append(prototype_syn)
            return prototype_syn
        return super().create_n_connection_synapse(
            prototype_syn, n, nml_doc, existing_synapses
        )

    def is_analog_conn(self, syn):
        """判断是否为模拟连接。"""
        return super().is_analog_conn(syn) or isinstance(syn, GradedSynapse2)


# ---------------------------------------------------------------------------
# Level C1 — HH 导电模型 + GradedSynapse（标准 NeuroML）
# ---------------------------------------------------------------------------


class _HHC1Model(_HHModel):
    """Level C1：HH 导电模型 + 标准 GradedSynapse 化学突触。"""

    def create_neuron_to_neuron_syn(self):
        """创建神经元间突触（GradedSynapse + GapJunction）。"""
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
        """创建神经元到肌肉突触（GradedSynapse + GapJunction）。"""
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

    def get_exc_syn(self, pre_cell, post_cell, type):
        """兴奋性突触 — GradedSynapse。"""
        self.found_specific_param = False
        specific = "%s_to_%s_exc_syn_%s"
        default = (
            "neuron_to_neuron_exc_syn_%s"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_exc_syn_%s"
        )
        conductance = self.get_conn_param(
            pre_cell, post_cell, specific, default, "conductance"
        )
        erev = self.get_conn_param(
            pre_cell, post_cell, specific, "exc_syn_%s", "erev"
        )
        delta = self.get_conn_param(
            pre_cell, post_cell, specific, "exc_syn_%s", "delta"
        )
        vth = self.get_conn_param(pre_cell, post_cell, specific, "exc_syn_%s", "vth")
        k = self.get_conn_param(pre_cell, post_cell, specific, "exc_syn_%s", "k")

        conn_id = (
            "neuron_to_neuron_exc_syn"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_exc_syn"
        )
        if self.found_specific_param:
            conn_id = "%s_to_%s_exc_syn" % (pre_cell, post_cell)

        return GradedSynapse(
            id=conn_id, conductance=conductance, delta=delta, Vth=vth, erev=erev, k=k
        )

    def get_inh_syn(self, pre_cell, post_cell, type):
        """抑制性突触 — GradedSynapse。"""
        self.found_specific_param = False
        specific = "%s_to_%s_inh_syn_%s"
        default = (
            "neuron_to_neuron_inh_syn_%s"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_inh_syn_%s"
        )
        conductance = self.get_conn_param(
            pre_cell, post_cell, specific, default, "conductance"
        )
        erev = self.get_conn_param(
            pre_cell, post_cell, specific, "inh_syn_%s", "erev"
        )
        delta = self.get_conn_param(
            pre_cell, post_cell, specific, "inh_syn_%s", "delta"
        )
        vth = self.get_conn_param(pre_cell, post_cell, specific, "inh_syn_%s", "vth")
        k = self.get_conn_param(pre_cell, post_cell, specific, "inh_syn_%s", "k")

        conn_id = (
            "neuron_to_neuron_inh_syn"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_inh_syn"
        )
        if self.found_specific_param:
            conn_id = "%s_to_%s_inh_syn" % (pre_cell, post_cell)

        return GradedSynapse(
            id=conn_id, conductance=conductance, delta=delta, Vth=vth, erev=erev, k=k
        )


# ---------------------------------------------------------------------------
# Level D — HH 多室模型（肌肉通用，神经元按 NML 形态创建）
# ---------------------------------------------------------------------------


class _HHMultiCompModel(_HHModel):
    """Level D：导电模型，无通用神经元细胞（按名称从 NML 创建）。"""

    def create_models(self):
        """创建肌肉细胞、偏置电流、浓度模型和突触（不创建通用神经元）。"""
        self.create_generic_muscle_cell()
        # D 族不创建 generic_neuron_cell — 神经元由 generator 逐个创建
        self.create_offsetcurrent_concentrationmodel()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()

    def create_neuron_cell(self, cell_name, morphology):
        """创建单个神经元 Cell（D 族特有的逐个构建方式）。

        :param cell_name: 神经元名称
        :param morphology: Morphology 对象
        :return: Cell 对象
        """
        cell = Cell(id=cell_name)
        cell.notes = "Cell model created by c302 with custom electrical parameters"
        cell.morphology = morphology

        cell.biophysical_properties = BiophysicalProperties(id="biophys_" + cell.id)
        mp = MembraneProperties()
        cell.biophysical_properties.membrane_properties = mp

        mp.init_memb_potentials.append(
            InitMembPotential(value=self.get_bioparameter("initial_memb_pot").value)
        )
        mp.specific_capacitances.append(
            SpecificCapacitance(
                value=self.get_bioparameter("specific_capacitance").value
            )
        )
        mp.spike_threshes.append(
            SpikeThresh(value=self.get_bioparameter("neuron_spike_thresh").value)
        )

        # 离子通道
        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter("neuron_leak_cond_density").value,
                id="Leak_all",
                ion_channel="Leak",
                erev=self.get_bioparameter("leak_erev").value,
                ion="non_specific",
            )
        )
        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter(
                    "neuron_k_slow_cond_density"
                ).value,
                id="k_slow_all",
                ion_channel="k_slow",
                erev=self.get_bioparameter("k_slow_erev").value,
                ion="k",
            )
        )
        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter(
                    "neuron_k_fast_cond_density"
                ).value,
                id="k_fast_all",
                ion_channel="k_fast",
                erev=self.get_bioparameter("k_fast_erev").value,
                ion="k",
            )
        )
        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter(
                    "neuron_ca_boyle_cond_density"
                ).value,
                id="ca_boyle_all",
                ion_channel="ca_boyle",
                erev=self.get_bioparameter("ca_boyle_erev").value,
                ion="ca",
            )
        )

        ip = IntracellularProperties()
        cell.biophysical_properties.intracellular_properties = ip
        ip.resistivities.append(
            Resistivity(value=self.get_bioparameter("resistivity").value)
        )
        species = Species(
            id="ca",
            ion="ca",
            concentration_model="CaPool",
            initial_concentration="0 mM",
            initial_ext_concentration="2E-6 mol_per_cm3",
        )
        ip.species.append(species)

        return cell


# ---------------------------------------------------------------------------
# Level D1 — HH + GradedSynapse2 化学突触
# ---------------------------------------------------------------------------


class _HHGradedModel(_HHMultiCompModel):
    """Level D1：导电模型 + GradedSynapse2 化学突触。"""

    def create_neuron_to_neuron_syn(self):
        """创建神经元间突触（GradedSynapse2 + GapJunction）。"""
        self.neuron_to_neuron_exc_syn = GradedSynapse2(
            id="neuron_to_neuron_exc_syn",
            conductance=self.get_bioparameter(
                "neuron_to_neuron_exc_syn_conductance"
            ).value,
            ar=self.get_bioparameter("exc_syn_ar").value,
            ad=self.get_bioparameter("exc_syn_ad").value,
            beta=self.get_bioparameter("exc_syn_beta").value,
            vth=self.get_bioparameter("exc_syn_vth").value,
            erev=self.get_bioparameter("exc_syn_erev").value,
        )
        self.neuron_to_neuron_inh_syn = GradedSynapse2(
            id="neuron_to_neuron_inh_syn",
            conductance=self.get_bioparameter(
                "neuron_to_neuron_inh_syn_conductance"
            ).value,
            ar=self.get_bioparameter("inh_syn_ar").value,
            ad=self.get_bioparameter("inh_syn_ad").value,
            beta=self.get_bioparameter("inh_syn_beta").value,
            vth=self.get_bioparameter("inh_syn_vth").value,
            erev=self.get_bioparameter("inh_syn_erev").value,
        )
        self.neuron_to_neuron_elec_syn = GapJunction(
            id="neuron_to_neuron_elec_syn",
            conductance=self.get_bioparameter("neuron_to_neuron_elec_syn_gbase").value,
        )

    def create_neuron_to_muscle_syn(self):
        """创建神经元到肌肉突触（GradedSynapse2 + GapJunction）。"""
        self.neuron_to_muscle_exc_syn = GradedSynapse2(
            id="neuron_to_muscle_exc_syn",
            conductance=self.get_bioparameter(
                "neuron_to_muscle_exc_syn_conductance"
            ).value,
            ar=self.get_bioparameter("exc_syn_ar").value,
            ad=self.get_bioparameter("exc_syn_ad").value,
            beta=self.get_bioparameter("exc_syn_beta").value,
            vth=self.get_bioparameter("exc_syn_vth").value,
            erev=self.get_bioparameter("exc_syn_erev").value,
        )
        self.neuron_to_muscle_inh_syn = GradedSynapse2(
            id="neuron_to_muscle_inh_syn",
            conductance=self.get_bioparameter(
                "neuron_to_muscle_inh_syn_conductance"
            ).value,
            ar=self.get_bioparameter("inh_syn_ar").value,
            ad=self.get_bioparameter("inh_syn_ad").value,
            beta=self.get_bioparameter("inh_syn_beta").value,
            vth=self.get_bioparameter("inh_syn_vth").value,
            erev=self.get_bioparameter("inh_syn_erev").value,
        )
        self.neuron_to_muscle_elec_syn = GapJunction(
            id="neuron_to_muscle_elec_syn",
            conductance=self.get_bioparameter("neuron_to_muscle_elec_syn_gbase").value,
        )

    def get_exc_syn(self, pre_cell, post_cell, type):
        """Level D1 的兴奋性突触 — 返回 GradedSynapse2。"""
        self.found_specific_param = False
        specific = "%s_to_%s_exc_syn_%s"

        if type == "neuron_to_neuron":
            default = "neuron_to_neuron_exc_syn_%s"
        elif type == "neuron_to_muscle":
            default = "neuron_to_muscle_exc_syn_%s"
        else:
            default = "neuron_to_neuron_exc_syn_%s"

        conductance = self.get_conn_param(
            pre_cell, post_cell, specific, default, "conductance"
        )
        erev = self.get_conn_param(
            pre_cell, post_cell, specific, "exc_syn_%s", "erev"
        )
        ar = self.get_conn_param(pre_cell, post_cell, specific, "exc_syn_%s", "ar")
        ad = self.get_conn_param(pre_cell, post_cell, specific, "exc_syn_%s", "ad")
        beta = self.get_conn_param(
            pre_cell, post_cell, specific, "exc_syn_%s", "beta"
        )
        vth = self.get_conn_param(pre_cell, post_cell, specific, "exc_syn_%s", "vth")

        conn_id = (
            "neuron_to_neuron_exc_syn"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_exc_syn"
        )
        if self.found_specific_param:
            conn_id = "%s_to_%s_exc_syn" % (pre_cell, post_cell)

        return GradedSynapse2(
            id=conn_id,
            conductance=conductance,
            ar=ar,
            ad=ad,
            beta=beta,
            vth=vth,
            erev=erev,
        )

    def get_inh_syn(self, pre_cell, post_cell, type):
        """Level D1 的抑制性突触 — 返回 GradedSynapse2。"""
        self.found_specific_param = False
        specific = "%s_to_%s_inh_syn_%s"

        if type == "neuron_to_neuron":
            default = "neuron_to_neuron_inh_syn_%s"
        elif type == "neuron_to_muscle":
            default = "neuron_to_muscle_inh_syn_%s"
        else:
            default = "neuron_to_neuron_inh_syn_%s"

        conductance = self.get_conn_param(
            pre_cell, post_cell, specific, default, "conductance"
        )
        erev = self.get_conn_param(
            pre_cell, post_cell, specific, "inh_syn_%s", "erev"
        )
        ar = self.get_conn_param(pre_cell, post_cell, specific, "inh_syn_%s", "ar")
        ad = self.get_conn_param(pre_cell, post_cell, specific, "inh_syn_%s", "ad")
        beta = self.get_conn_param(
            pre_cell, post_cell, specific, "inh_syn_%s", "beta"
        )
        vth = self.get_conn_param(pre_cell, post_cell, specific, "inh_syn_%s", "vth")

        conn_id = (
            "neuron_to_neuron_inh_syn"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_inh_syn"
        )
        if self.found_specific_param:
            conn_id = "%s_to_%s_inh_syn" % (pre_cell, post_cell)

        return GradedSynapse2(
            id=conn_id,
            conductance=conductance,
            ar=ar,
            ad=ad,
            beta=beta,
            vth=vth,
            erev=erev,
        )

    def create_n_connection_synapse(self, prototype_syn, n, nml_doc, existing_synapses):
        """注册突触原型（含 GradedSynapse2 支持）。"""
        if prototype_syn.id in existing_synapses:
            return existing_synapses[prototype_syn.id]

        if isinstance(prototype_syn, GradedSynapse2):
            existing_synapses[prototype_syn.id] = prototype_syn
            nml_doc.graded_synapses.append(prototype_syn)
            return prototype_syn

        return super().create_n_connection_synapse(
            prototype_syn, n, nml_doc, existing_synapses
        )

    def is_analog_conn(self, syn):
        """判断是否为模拟连接（含 GradedSynapse2）。"""
        return super().is_analog_conn(syn) or isinstance(syn, GradedSynapse2)


# ---------------------------------------------------------------------------
# 层级 → 模型类映射
# ---------------------------------------------------------------------------


_LEVEL_TO_CLASS: dict[str, type[_ModelBase]] = {
    "A": _IafModel,
    "B": _IafActivityModel,
    "C": _HHModel,
    "C0": _HHC0Model,
    "C1": _HHC1Model,
    "D": _HHMultiCompModel,
    "D1": _HHGradedModel,
}


def create_model(level: str) -> c302ModelPrototype:
    """根据层级名称创建参数化模型实例。

    :param level: 参数层级名称（如 ``"A"``、``"C0"``、``"D1"``）
    :return: 已加载参数的 c302ModelPrototype 实例
    :raises KeyError: 未知的层级名称
    """
    level_upper = level.upper()
    cls = _LEVEL_TO_CLASS.get(level_upper)
    if cls is None:
        raise KeyError(
            f"未知的模型层级: {level}，可用: {list(_LEVEL_TO_CLASS.keys())}"
        )
    return cls(level_upper)
