#
# 类与方法索引：
#   ParameterisedModel                   (L36)   — ParameterisedModel 类
#     __init__                           (L37)   — 初始化 Level C 参数模型，使用单室导电模型和 Hodgkin-Huxley 型离子通道
#     set_default_bioparameters          (L52)   — 设置 Level C 的默认生物参数，涵盖细胞形态、离子通道密度和突触参数
#     create_models                      (L157)  — 按顺序创建所有网络组件模型
#     create_generic_muscle_cell         (L169)  — 创建单室导电基础肌肉细胞（``Cell``），包含三类离子通道和钙浓度模型
#     create_generic_neuron_cell         (L276)  — 创建单室导电基础神经元细胞（``Cell``），包含三类离子通道和钙浓度模型
#     create_offsetcurrent_concentrationmodel (L379)  — 创建偏置电流生成器和固定因子钙浓度模型（``FixedFactorConcentrationModel``）
#     create_neuron_to_neuron_syn        (L400)  — 创建神经元间兴奋性、抑制性化学突触（``ExpTwoSynapse``）和缝隙连接（``GapJunction``）
#     create_neuron_to_muscle_syn        (L423)  — 创建神经元到肌肉的兴奋性、抑制性化学突触和缝隙连接
#     get_elec_syn                       (L446)  — 根据连接类型获取缝隙连接（``GapJunction``）对象
#     get_exc_syn                        (L479)  — 根据连接类型获取兴奋性双指数事件突触（``ExpTwoSynapse``）对象
#     get_inh_syn                        (L536)  — 根据连接类型获取抑制性双指数事件突触（``ExpTwoSynapse``）对象
"""

Parameters C:
    Cells:           Single compartment, conductance based cell models with HH like ion channels
    Chem Synapses:   Event based, ohmic; one rise & one decay constant
    Gap junctions:   Electrical connection; current linerly depends on difference in voltages

ASSESSMENT:
    May be possible to use this to generate oscilliatory behaviour, but use of event based synapses normally requires
    spiking in cells, so core neurons will have to have clear spikes.

"""

from neuroml import Cell
from neuroml import Morphology
from neuroml import Point3DWithDiam
from neuroml import Segment
from neuroml import BiophysicalProperties
from neuroml import IntracellularProperties
from neuroml import Resistivity
from neuroml import Species
from neuroml import MembraneProperties
from neuroml import InitMembPotential
from neuroml import SpecificCapacitance
from neuroml import ChannelDensity
from neuroml import SpikeThresh
from neuroml import FixedFactorConcentrationModel

from neuroml import ExpTwoSynapse
from neuroml import GapJunction
from neuroml import PulseGenerator

from c302.bioparameters import c302ModelPrototype


class ParameterisedModel(c302ModelPrototype):
    def __init__(self):
        """初始化 Level C 参数模型，使用单室导电模型和 Hodgkin-Huxley 型离子通道。

        Level C 相对于 A/B 的核心改进：
        - 细胞采用标准 NeuroML ``Cell`` + ``BiophysicalProperties``，含钾、钙、漏三种离子通道
        - 引入钙离子浓度动力学（``FixedFactorConcentrationModel``）
        - 突触仍为事件驱动型（``ExpTwoSynapse``），需要细胞发放动作电位才能传递信号
        """
        super(ParameterisedModel, self).__init__()
        self.level = "C"
        self.custom_component_types_definitions = "cell_C.xml"

        self.set_default_bioparameters()
        self.print_("Set default parameters for %s" % self.level)

    def set_default_bioparameters(self):
        """设置 Level C 的默认生物参数，涵盖细胞形态、离子通道密度和突触参数。

        参数分组：
        - 形态参数：``cell_diameter``（细胞直径）、``muscle_length``（肌肉长度）
        - 初始条件：``initial_memb_pot``、``specific_capacitance``
        - 放电阈值：``muscle_spike_thresh``、``neuron_spike_thresh``
        - 漏通道：``*_leak_cond_density``、``leak_erev``
        - 慢钾通道（Kv）：``*_k_slow_cond_density``、``k_slow_erev``
        - 快钾通道（Kv）：``*_k_fast_cond_density``、``k_fast_erev``
        - 钙通道（Ca Boyle 模型）：``*_ca_boyle_cond_density``、``ca_boyle_erev``
        - 钙浓度动力学：``ca_conc_decay_time``、``ca_conc_rho``
        - 化学突触（兴奋性/抑制性）参数
        """
        # 细胞形态参数：单室球形细胞的直径和肌肉长度（μm）
        self.add_bioparameter("cell_diameter", "5", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_length", "20", "BlindGuess", "0.1")

        # 初始状态：初始膜电位（mV）和比膜电容（uF/cm²）
        self.add_bioparameter("initial_memb_pot", "-45 mV", "BlindGuess", "0.1")

        self.add_bioparameter(
            "specific_capacitance", "1 uF_per_cm2", "BlindGuess", "0.1"
        )

        # 动作电位阈值：超过此电压则判定为发放（spike），触发事件突触
        self.add_bioparameter("muscle_spike_thresh", "-20 mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_spike_thresh", "-20 mV", "BlindGuess", "0.1")

        # 漏通道：所有膜面均匀分布，维持静息膜电位
        self.add_bioparameter(
            "muscle_leak_cond_density", "5e-7 S_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_leak_cond_density", "0.005 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter("leak_erev", "-50 mV", "BlindGuess", "0.1")

        # 慢钾通道（Kv 延迟整流）：控制动作电位复极化过程
        self.add_bioparameter(
            "muscle_k_slow_cond_density", "0.0006 S_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_k_slow_cond_density", "3 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter("k_slow_erev", "-60 mV", "BlindGuess", "0.1")

        # 快钾通道（Kv 瞬时外向）：控制动作电位峰值后的快速复极化
        self.add_bioparameter(
            "muscle_k_fast_cond_density", "0.0001 S_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_k_fast_cond_density",
            "0.0711643917483308 mS_per_cm2",
            "BlindGuess",
            "0.1",
        )
        self.add_bioparameter("k_fast_erev", "-60 mV", "BlindGuess", "0.1")

        # 钙通道（Boyle-Cohen 模型）：触发 Ca²⁺ 内流，驱动钙浓度上升和肌肉收缩
        self.add_bioparameter(
            "muscle_ca_boyle_cond_density", "0.0007 S_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_ca_boyle_cond_density", "3 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter("ca_boyle_erev", "40 mV", "BlindGuess", "0.1")

        # 钙浓度动力学：decay_time 决定 Ca²⁺ 衰减速度，rho 为电流到浓度的转换系数
        self.add_bioparameter("ca_conc_decay_time", "11.5943 ms", "BlindGuess", "0.1")
        self.add_bioparameter(
            "ca_conc_rho", "0.000238919 mol_per_m_per_A_per_s", "BlindGuess", "0.1"
        )

        # 兴奋性化学突触参数（gbase 峰值电导 / erev 接近 0mV）
        self.add_bioparameter(
            "neuron_to_neuron_chem_exc_syn_gbase", ".1 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_chem_exc_syn_gbase", ".1 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("chem_exc_syn_erev", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("chem_exc_syn_rise", "1 ms", "Bli ndGuess", "0.1")
        self.add_bioparameter("chem_exc_syn_decay", "5 ms", "BlindGuess", "0.1")

        # 抑制性化学突触参数（gbase 峰值电导 / erev 负值维持抑制性）
        self.add_bioparameter(
            "neuron_to_neuron_chem_inh_syn_gbase", ".1 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_chem_inh_syn_gbase", ".1 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("chem_inh_syn_erev", "-60 mV", "BlindGuess", "0.1")
        self.add_bioparameter("chem_inh_syn_rise", "2 ms", "BlindGuess", "0.1")
        self.add_bioparameter("chem_inh_syn_decay", "40 ms", "BlindGuess", "0.1")

        # 缝隙连接（GapJunction）电导：电流与膜电位差成线性比例
        self.add_bioparameter(
            "neuron_to_neuron_elec_syn_gbase", "0.0005 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_elec_syn_gbase", "0.0005 nS", "BlindGuess", "0.1"
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
        """按顺序创建所有网络组件模型。

        调用顺序：通用肌肉细胞、神经元细胞、偏置电流与浓度模型、
        神经元间突触、神经元到肌肉突触。
        """
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_offsetcurrent_concentrationmodel()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()

    def create_generic_muscle_cell(self):
        """创建单室导电基础肌肉细胞（``Cell``），包含三类离子通道和钙浓度模型。

        细胞形态为单个球形段，通道密度从生物参数表读取。
        离子通道实现定义于 ``cell_C.xml`` 自定义组件文件。
        """
        self.generic_muscle_cell = Cell(id="GenericMuscleCell")

        morphology = Morphology()
        morphology.id = "morphology_" + self.generic_muscle_cell.id

        self.generic_muscle_cell.morphology = morphology

        prox_point = Point3DWithDiam(
            x="0", y="0", z="0", diameter=self.get_bioparameter("cell_diameter").value
        )
        dist_point = Point3DWithDiam(
            x="0",
            y=self.get_bioparameter("muscle_length").value,
            z="0",
            diameter=self.get_bioparameter("cell_diameter").value,
        )

        segment = Segment(id="0", name="soma", proximal=prox_point, distal=dist_point)

        morphology.segments.append(segment)

        self.generic_muscle_cell.biophysical_properties = BiophysicalProperties(
            id="biophys_" + self.generic_muscle_cell.id
        )

        mp = MembraneProperties()
        self.generic_muscle_cell.biophysical_properties.membrane_properties = mp

        mp.init_memb_potentials.append(
            InitMembPotential(value=self.get_bioparameter("initial_memb_pot").value)
        )

        mp.specific_capacitances.append(
            SpecificCapacitance(
                value=self.get_bioparameter("specific_capacitance").value
            )
        )

        mp.spike_threshes.append(
            SpikeThresh(value=self.get_bioparameter("muscle_spike_thresh").value)
        )

        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter("muscle_leak_cond_density").value,
                id="Leak_all",
                ion_channel="Leak",
                erev=self.get_bioparameter("leak_erev").value,
                ion="non_specific",
            )
        )

        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter("muscle_k_slow_cond_density").value,
                id="k_slow_all",
                ion_channel="k_slow",
                erev=self.get_bioparameter("k_slow_erev").value,
                ion="k",
            )
        )

        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter("muscle_k_fast_cond_density").value,
                id="k_fast_all",
                ion_channel="k_fast",
                erev=self.get_bioparameter("k_fast_erev").value,
                ion="k",
            )
        )

        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter(
                    "muscle_ca_boyle_cond_density"
                ).value,
                id="ca_boyle_all",
                ion_channel="ca_boyle",
                erev=self.get_bioparameter("ca_boyle_erev").value,
                ion="ca",
            )
        )

        ip = IntracellularProperties()
        self.generic_muscle_cell.biophysical_properties.intracellular_properties = ip

        # NOTE: resistivity/axial resistance not used for single compartment cell models, so value irrelevant!
        ip.resistivities.append(Resistivity(value="0.1 kohm_cm"))

        # NOTE: Ca reversal potential not calculated by Nernst, so initial_ext_concentration value irrelevant!
        species = Species(
            id="ca",
            ion="ca",
            concentration_model="CaPool",
            initial_concentration="0 mM",
            initial_ext_concentration="2E-6 mol_per_cm3",
        )

        ip.species.append(species)

    def create_generic_neuron_cell(self):
        """创建单室导电基础神经元细胞（``Cell``），包含三类离子通道和钙浓度模型。

        与肌肉细胞结构相同，但通道密度参数不同（神经元通道密度通常高于肌肉）。
        """
        self.generic_neuron_cell = Cell(id="GenericNeuronCell")

        morphology = Morphology()
        morphology.id = "morphology_" + self.generic_neuron_cell.id

        self.generic_neuron_cell.morphology = morphology

        prox_point = Point3DWithDiam(
            x="0", y="0", z="0", diameter=self.get_bioparameter("cell_diameter").value
        )
        dist_point = Point3DWithDiam(
            x="0", y="0", z="0", diameter=self.get_bioparameter("cell_diameter").value
        )

        segment = Segment(id="0", name="soma", proximal=prox_point, distal=dist_point)

        morphology.segments.append(segment)

        self.generic_neuron_cell.biophysical_properties = BiophysicalProperties(
            id="biophys_" + self.generic_neuron_cell.id
        )

        mp = MembraneProperties()
        self.generic_neuron_cell.biophysical_properties.membrane_properties = mp

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
                cond_density=self.get_bioparameter("neuron_k_slow_cond_density").value,
                id="k_slow_all",
                ion_channel="k_slow",
                erev=self.get_bioparameter("k_slow_erev").value,
                ion="k",
            )
        )

        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter("neuron_k_fast_cond_density").value,
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
        self.generic_neuron_cell.biophysical_properties.intracellular_properties = ip

        # NOTE: resistivity/axial resistance not used for single compartment cell models, so value irrelevant!
        ip.resistivities.append(Resistivity(value="0.1 kohm_cm"))

        # NOTE: Ca reversal potential not calculated by Nernst, so initial_ext_concentration value irrelevant!
        species = Species(
            id="ca",
            ion="ca",
            concentration_model="CaPool",
            initial_concentration="0 mM",
            initial_ext_concentration="2E-6 mol_per_cm3",
        )

        ip.species.append(species)

    def create_offsetcurrent_concentrationmodel(self):
        """创建偏置电流生成器和固定因子钙浓度模型（``FixedFactorConcentrationModel``）。

        钙浓度模型（``ca_conc_decay_time``、``ca_conc_rho``）控制细胞内 Ca²⁺ 的衰减速率，
        是钙通道门控和浓度反馈的基础。
        """
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
        """创建神经元间兴奋性、抑制性化学突触（``ExpTwoSynapse``）和缝隙连接（``GapJunction``）。"""
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
        """创建神经元到肌肉的兴奋性、抑制性化学突触和缝隙连接。"""
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
        """根据连接类型获取缝隙连接（``GapJunction``）对象。

        :param pre_cell: 突触前细胞名称
        :param post_cell: 突触后细胞名称
        :param type: 连接类型（``"neuron_to_neuron"``、``"neuron_to_muscle"``、``"muscle_to_muscle"``）
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
        """根据连接类型获取兴奋性双指数事件突触（``ExpTwoSynapse``）对象。

        :param pre_cell: 突触前细胞名称
        :param post_cell: 突触后细胞名称
        :param type: 连接类型字符串
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
        """根据连接类型获取抑制性双指数事件突触（``ExpTwoSynapse``）对象。

        :param pre_cell: 突触前细胞名称
        :param post_cell: 突触后细胞名称
        :param type: 连接类型字符串
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
