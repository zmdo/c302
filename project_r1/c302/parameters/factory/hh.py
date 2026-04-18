# =============================================================================
# 功能描述：
#   HH 族模型：Level C（单室 HH）、Level C0（HH + ca_simple + GradedSynapse2）、
#   Level C1（HH + GradedSynapse）。
#
# 类与方法索引：
#   _HHModel                             (L37)   — Level C：单室 HH 导电模型
#     create_models                      (L40)   — 创建细胞、偏置、浓度和突触
#     create_generic_muscle_cell         (L48)   — create_hh_cell (muscle)
#     create_generic_neuron_cell         (L54)   — create_hh_cell (neuron)
#     create_offsetcurrent_concentrationmodel (L60) — 偏置电流 + CaPool
#   _HHC0Model                           (L79)   — Level C0：修正继承 _HHModel
#     create_generic_muscle_cell         (L93)   — create_c0_cell (muscle)
#     create_generic_neuron_cell         (L99)   — create_c0_cell (neuron)
#   _HHC1Model                           (L105)  — Level C1：GradedSynapse 化学突触
#
# 更新日志：
#   2026-04-19  Copilot  计划5阶段四：从 factory.py 迁移 HH 族
#
# 当前维护者：Copilot
# =============================================================================
"""HH 族模型工厂。"""
from neuroml import (
    FixedFactorConcentrationModel,
    GapJunction,
    GradedSynapse,
    PulseGenerator,
)

from c302.parameters.cell_builder import create_c0_cell, create_hh_cell
from c302.parameters.custom_types import GradedSynapse2
from c302.parameters.factory.base import _GradedSynapse2Mixin, _ModelBase


class _HHModel(_ModelBase):
    """Level C 族：单室 HH 导电模型 + ExpTwoSynapse + GapJunction。"""

    _elec_syn_cls: type = GapJunction

    def create_models(self) -> None:
        """创建肌肉/神经元细胞、偏置电流、浓度模型和突触。"""
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_offsetcurrent_concentrationmodel()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()

    def create_generic_muscle_cell(self) -> None:
        """创建通用肌肉 HH 细胞。"""
        self.generic_muscle_cell = create_hh_cell(
            self, "GenericMuscleCell", is_muscle=True
        )

    def create_generic_neuron_cell(self) -> None:
        """创建通用神经元 HH 细胞。"""
        self.generic_neuron_cell = create_hh_cell(
            self, "GenericNeuronCell", is_muscle=False
        )

    def create_offsetcurrent_concentrationmodel(self) -> None:
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


class _HHC0Model(_GradedSynapse2Mixin, _HHModel):
    """Level C0：HH 导电模型 + ca_simple 通道 + GradedSynapse2 突触。

    修正：继承 ``_HHModel`` 而非原来的 ``_ModelBase``，
    复用 ``create_models`` / ``create_offsetcurrent_concentrationmodel``。
    ``_GradedSynapse2Mixin`` 提供 ``create_n_connection_synapse`` / ``is_analog_conn``。
    """

    _exc_syn_cls: type = GradedSynapse2
    _inh_syn_cls: type = GradedSynapse2
    _exc_param_fields: tuple[str, ...] = ("conductance", "erev", "ar", "ad", "beta", "vth")
    _inh_param_fields: tuple[str, ...] = ("conductance", "erev", "ar", "ad", "beta", "vth")
    _exc_param_to_kwarg: dict[str, str] | None = None
    _inh_param_to_kwarg: dict[str, str] | None = None
    _chem_prefix: str = ""

    def create_generic_muscle_cell(self) -> None:
        """创建通用肌肉 HH 细胞（ca_simple 通道变体）。"""
        self.generic_muscle_cell = create_c0_cell(
            self, "GenericMuscleCell", is_muscle=True
        )

    def create_generic_neuron_cell(self) -> None:
        """创建通用神经元 HH 细胞（ca_simple 通道变体）。"""
        self.generic_neuron_cell = create_c0_cell(
            self, "GenericNeuronCell", is_muscle=False
        )


class _HHC1Model(_HHModel):
    """Level C1：HH 导电模型 + 标准 GradedSynapse 化学突触。

    通过类属性切换到 GradedSynapse，模板方法自动适配。
    """

    _exc_syn_cls: type = GradedSynapse
    _inh_syn_cls: type = GradedSynapse
    _exc_param_fields: tuple[str, ...] = ("conductance", "erev", "delta", "vth", "k")
    _inh_param_fields: tuple[str, ...] = ("conductance", "erev", "delta", "vth", "k")
    _exc_param_to_kwarg: dict[str, str] | None = {"vth": "Vth"}
    _inh_param_to_kwarg: dict[str, str] | None = {"vth": "Vth"}
    _chem_prefix: str = ""
