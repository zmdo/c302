# =============================================================================
# 功能描述：
#   IAF 族模型：Level A（IafCell）、Level B（IafActivityCell）、
#   Level BC1（IafActivityCell + GradedSynapse）。
#
# 类与方法索引：
#   _IafModel                            (L29)   — Level A：积分放电模型 + 事件突触
#     create_models                      (L37)   — 创建所有细胞和突触模型
#     create_generic_muscle_cell         (L45)   — 创建通用肌肉 IafCell
#     create_generic_neuron_cell         (L56)   — 创建通用神经元 IafCell
#     create_offset                      (L67)   — 创建偏置电流生成器
#   _IafActivityModel                    (L77)   — Level B：IafActivityCell + 真实 GapJunction 电突触
#     create_generic_muscle_cell         (L83)   — 创建通用肌肉 IafActivityCell（含 tau1 参数）
#     create_generic_neuron_cell         (L95)   — 创建通用神经元 IafActivityCell（含 tau1 参数）
#   _BC1Model                            (L108)  — Level BC1：IafActivityCell 细胞 + 标准 GradedSynapse 化学突触
#
# 更新日志：
#   2026-04-19  Copilot  计划5阶段三：从 factory.py 迁移 IAF 族
#
# 当前维护者：Copilot
# =============================================================================
"""IAF 族模型工厂。"""
from neuroml import ExpTwoSynapse, GapJunction, GradedSynapse, IafCell, PulseGenerator

from c302.parameters.custom_types import IafActivityCell
from c302.parameters.factory.base import _ModelBase


class _IafModel(_ModelBase):
    """Level A：积分放电模型 + 事件突触。

    电突触也使用 ExpTwoSynapse（gbase=0 的假电突触）。
    """

    _elec_syn_cls: type = ExpTwoSynapse

    def create_models(self) -> None:
        """创建所有细胞和突触模型。"""
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_offset()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()

    def create_generic_muscle_cell(self) -> None:
        """创建通用肌肉 IafCell。"""
        self.generic_muscle_cell = IafCell(
            id="generic_muscle_iaf_cell",
            C=self.get_bioparameter("muscle_iaf_C").value,
            thresh=self.get_bioparameter("muscle_iaf_thresh").value,
            reset=self.get_bioparameter("muscle_iaf_reset").value,
            leak_conductance=self.get_bioparameter("muscle_iaf_conductance").value,
            leak_reversal=self.get_bioparameter("muscle_iaf_leak_reversal").value,
        )

    def create_generic_neuron_cell(self) -> None:
        """创建通用神经元 IafCell。"""
        self.generic_neuron_cell = IafCell(
            id="generic_neuron_iaf_cell",
            C=self.get_bioparameter("neuron_iaf_C").value,
            thresh=self.get_bioparameter("neuron_iaf_thresh").value,
            reset=self.get_bioparameter("neuron_iaf_reset").value,
            leak_conductance=self.get_bioparameter("neuron_iaf_conductance").value,
            leak_reversal=self.get_bioparameter("neuron_iaf_leak_reversal").value,
        )

    def create_offset(self) -> None:
        """创建偏置电流生成器。"""
        self.offset_current = PulseGenerator(
            id="offset_current",
            delay=self.get_bioparameter("unphysiological_offset_current_del").value,
            duration=self.get_bioparameter("unphysiological_offset_current_dur").value,
            amplitude=self.get_bioparameter("unphysiological_offset_current").value,
        )


class _IafActivityModel(_IafModel):
    """Level B：IafActivityCell + 真实 GapJunction 电突触。"""

    # 覆盖 A 级的假电突触类型
    _elec_syn_cls: type = GapJunction

    def create_generic_muscle_cell(self) -> None:
        """创建通用肌肉 IafActivityCell（含 tau1 参数）。"""
        self.generic_muscle_cell = IafActivityCell(
            id="generic_muscle_iaf_cell",
            C=self.get_bioparameter("muscle_iaf_C").value,
            thresh=self.get_bioparameter("muscle_iaf_thresh").value,
            reset=self.get_bioparameter("muscle_iaf_reset").value,
            leak_conductance=self.get_bioparameter("muscle_iaf_conductance").value,
            leak_reversal=self.get_bioparameter("muscle_iaf_leak_reversal").value,
            tau1=self.get_bioparameter("muscle_iaf_tau1").value,
        )

    def create_generic_neuron_cell(self) -> None:
        """创建通用神经元 IafActivityCell（含 tau1 参数）。"""
        self.generic_neuron_cell = IafActivityCell(
            id="generic_neuron_iaf_cell",
            C=self.get_bioparameter("neuron_iaf_C").value,
            thresh=self.get_bioparameter("neuron_iaf_thresh").value,
            reset=self.get_bioparameter("neuron_iaf_reset").value,
            leak_conductance=self.get_bioparameter("neuron_iaf_conductance").value,
            leak_reversal=self.get_bioparameter("neuron_iaf_leak_reversal").value,
            tau1=self.get_bioparameter("neuron_iaf_tau1").value,
        )


class _BC1Model(_IafActivityModel):
    """Level BC1：IafActivityCell 细胞 + 标准 GradedSynapse 化学突触。

    通过类属性切换到 GradedSynapse，模板方法自动适配。
    """

    _exc_syn_cls: type = GradedSynapse
    _inh_syn_cls: type = GradedSynapse
    _exc_param_fields: tuple[str, ...] = ("conductance", "erev", "delta", "vth", "k")
    _inh_param_fields: tuple[str, ...] = ("conductance", "erev", "delta", "vth", "k")
    _exc_param_to_kwarg: dict[str, str] | None = {"vth": "Vth"}
    _inh_param_to_kwarg: dict[str, str] | None = {"vth": "Vth"}
    _chem_prefix: str = ""
