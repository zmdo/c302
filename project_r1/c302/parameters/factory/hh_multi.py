# =============================================================================
# 功能描述：
#   HH 多隔室族模型：Level D（HH 多室，神经元按名称逐个创建）、
#   Level D1（HH 多室 + GradedSynapse2）。
#
# 类与方法索引：
#   _HHMultiCompModel                    (L37)   — Level D：导电模型，无通用神经元细胞（按名称从 NML 创建）
#     create_models                      (L40)   — 创建肌肉细胞、偏置电流、浓度模型和突触（不创建通用神经元）
#     create_neuron_cell                 (L48)   — 创建单个神经元 Cell（D 族特有的逐个构建方式）
#   _HHGradedModel                       (L138)  — Level D1：HH 多隔室 + GradedSynapse2 化学突触
#
# 更新日志：
#   2026-04-19  Copilot  计划5阶段五：从 factory.py 迁移 HH 多隔室族
#
# 当前维护者：Copilot
# =============================================================================
"""HH 多隔室族模型工厂。"""
from neuroml import (
    BiophysicalProperties,
    Cell,
    ChannelDensity,
    GradedSynapse,
    InitMembPotential,
    IntracellularProperties,
    MembraneProperties,
    Resistivity,
    SpecificCapacitance,
    Species,
    SpikeThresh,
)

from c302.parameters.custom_types import GradedSynapse2
from c302.parameters.factory.base import _GradedSynapse2Mixin
from c302.parameters.factory.hh import _HHModel


class _HHMultiCompModel(_HHModel):
    """Level D：导电模型，无通用神经元细胞（按名称从 NML 创建）。"""

    def create_models(self) -> None:
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

        # 基本膜属性
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

        # 4 个离子通道：Leak, k_slow, k_fast, ca_boyle
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

        # 细胞内属性：电阻率 + 钙离子种类
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


class _HHGradedModel(_GradedSynapse2Mixin, _HHMultiCompModel):
    """Level D1：HH 多隔室 + GradedSynapse2 化学突触。

    ``_GradedSynapse2Mixin`` 提供 ``create_n_connection_synapse`` / ``is_analog_conn``。
    """

    _exc_syn_cls: type = GradedSynapse2
    _inh_syn_cls: type = GradedSynapse2
    _exc_param_fields: tuple[str, ...] = ("conductance", "erev", "ar", "ad", "beta", "vth")
    _inh_param_fields: tuple[str, ...] = ("conductance", "erev", "ar", "ad", "beta", "vth")
    _exc_param_to_kwarg: dict[str, str] | None = None
    _inh_param_to_kwarg: dict[str, str] | None = None
    _chem_prefix: str = ""
