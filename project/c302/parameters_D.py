# =============================================================================
# 功能描述：
#   Level D 参数层级定义。使用多室导电模型，需加载 NeuroML 细胞形态文件
#   （_D.cell.nml），新增胞质电阻率（resistivity）参数，化学突触为事件
#   驱动 ExpTwoSynapse。
#
# 类与方法索引：
#   ParameterisedModel                   (L66)   — ParameterisedModel 类
#     __init__                           (L67)   — 初始化 Level D 参数模型，使用多室导电模型和 HH 型离子通道
#     set_default_bioparameters          (L84)   — 设置 Level D 的默认生物参数，与 C 相似但新增 ``resistivity`` 参数
#     create_models                      (L180)  — 按顺序创建所有网络组件模型
#     create_generic_muscle_cell         (L188)  — 创建 D 级单室导电肌肉细胞（``Cell``）
#     create_neuron_cell                 (L296)  — 从 NeuroML 多室形态文件加载特定神经元细胞，并为其配置生物物理属性
#     create_offsetcurrent_concentrationmodel (L393)  — 创建偏置电流生成器和钙浓度模型（``FixedFactorConcentrationModel``）
#     create_neuron_to_neuron_syn        (L410)  — 创建神经元间化学突触（``ExpTwoSynapse``）和缝隙连接（``GapJunction``）
#     create_neuron_to_muscle_syn        (L433)  — 创建神经元到肌肉的化学突触（``ExpTwoSynapse``）和缝隙连接
#     get_elec_syn                       (L456)  — 根据连接类型获取缝隙连接（``GapJunction``）对象
#     get_exc_syn                        (L489)  — 根据连接类型获取兴奋性双指数事件突触（``ExpTwoSynapse``）对象
#     get_inh_syn                        (L546)  — 根据连接类型获取抑制性双指数事件突触（``ExpTwoSynapse``）对象
#
# 更新日志：
#   2026-04-16  Copilot  添加中文 docstring 和行内注释（计划1阶段三）
#
# 当前维护者：Copilot
# =============================================================================
"""

Parameters D:
    Cells:           Multicompartmental, conductance based cell models with HH like ion channels
    Chem Synapses:   Event based, ohmic; one rise & one decay constant
    Gap junctions:   Electrical connection; current linerly depends on difference in voltages

ASSESSMENT:
    As with C, the use of event based synapses normally requires spiking in cells, so core neurons will
    have to have clear spikes.
    Also: either the cells have i) low internal resistance (cytoplasmic resistivity) & membrane potential changes rapidly propagate
    through cell or ii) high internal resistance and changes are concentrated around the soma. For i) this allows all synapses on
    cell (e.g. distant dendrites) to transmit if cell fires/depolarises, but it means bigger cells have much higher imput resistance,
    and so take much more syn input to respond.
    Note issue https://github.com/openworm/CElegansNeuroML/issues/71 regarding status of this

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
        """初始化 Level D 参数模型，使用多室导电模型和 HH 型离子通道。

        Level D 相对于 C 的核心改进：
        - 细胞为多室模型，需要从 ``_D.cell.nml`` 文件加载细胞形态（segment morphology）
        - 新增 ``resistivity``（胞质电阻率）参数，控制细胞内阻
        - ``create_neuron_cell()`` 需要从形态文件加载细胞，而非程序化构建

        已知问题：胞质电阻率影响较大——低内阻时所有突触位点等电位，
        高内阻时膜电位变化局限于树突近端。见 GitHub issue #71。
        """
        super(ParameterisedModel, self).__init__()
        self.level = "D"
        self.custom_component_types_definitions = "cell_C.xml"

        self.set_default_bioparameters()

    def set_default_bioparameters(self):
        """设置 Level D 的默认生物参数，与 C 相似但新增 ``resistivity`` 参数。"""
        self.add_bioparameter("cell_diameter", "5", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_length", "20", "BlindGuess", "0.1")

        self.add_bioparameter("initial_memb_pot", "-45 mV", "BlindGuess", "0.1")

        self.add_bioparameter(
            "specific_capacitance", "1 uF_per_cm2", "BlindGuess", "0.1"
        )

        # D 级新增参数：胞质电阻率（多室模型专有），控制细胞内轴向阻力
        self.add_bioparameter("resistivity", "12 kohm_cm", "BlindGuess", "0.1")

        self.add_bioparameter("muscle_spike_thresh", "-26 mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_spike_thresh", "-26 mV", "BlindGuess", "0.1")

        self.add_bioparameter(
            "muscle_leak_cond_density", "0.005 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_leak_cond_density", "0.02 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter("leak_erev", "-50 mV", "BlindGuess", "0.1")

        self.add_bioparameter(
            "muscle_k_slow_cond_density", "4 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_k_slow_cond_density", "2 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter("k_slow_erev", "-60 mV", "BlindGuess", "0.1")

        self.add_bioparameter(
            "muscle_k_fast_cond_density", "0.2 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_k_fast_cond_density", "0.2 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter("k_fast_erev", "-60 mV", "BlindGuess", "0.1")

        self.add_bioparameter(
            "muscle_ca_boyle_cond_density", "2 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_ca_boyle_cond_density", "2 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter("ca_boyle_erev", "40 mV", "BlindGuess", "0.1")

        self.add_bioparameter("ca_conc_decay_time", "11.5943 ms", "BlindGuess", "0.1")
        self.add_bioparameter(
            "ca_conc_rho", "0.000238919 mol_per_m_per_A_per_s", "BlindGuess", "0.1"
        )

        # ExpTwoSynapse 兴奋性化学突触（双指数上升/衰减，事件驱动）
        self.add_bioparameter(
            "neuron_to_neuron_chem_exc_syn_gbase", ".01 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_chem_exc_syn_gbase", ".01 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("chem_exc_syn_erev", "0 mV", "BlindGuess", "0.1")
        self.add_bioparameter("chem_exc_syn_rise", "1 ms", "BlindGuess", "0.1")
        self.add_bioparameter("chem_exc_syn_decay", "5 ms", "BlindGuess", "0.1")

        # ExpTwoSynapse 抑制性化学突触（erev=-60 mV，衰减更慢 40 ms）
        self.add_bioparameter(
            "neuron_to_neuron_chem_inh_syn_gbase", "3 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_chem_inh_syn_gbase", "3 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("chem_inh_syn_erev", "-60 mV", "BlindGuess", "0.1")
        self.add_bioparameter("chem_inh_syn_rise", "2 ms", "BlindGuess", "0.1")
        self.add_bioparameter("chem_inh_syn_decay", "40 ms", "BlindGuess", "0.1")

        # 缝隙连接（GapJunction）
        self.add_bioparameter(
            "neuron_to_neuron_elec_syn_gbase", "0.0005 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_elec_syn_gbase", "0.0005 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter(
            "unphysiological_offset_current", "0 pA", "KnownError", "0"
        )  # 可在后续激活（当前值为 0，即禁用此非生理性偏置电流）
        self.add_bioparameter(
            "unphysiological_offset_current_del", "0 ms", "KnownError", "0"
        )
        self.add_bioparameter(
            "unphysiological_offset_current_dur", "2000 ms", "KnownError", "0"
        )

    def create_models(self):
        """按顺序创建所有网络组件模型。"""
        self.create_generic_muscle_cell()

        self.create_offsetcurrent_concentrationmodel()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()

    def create_generic_muscle_cell(self):
        """创建 D 级单室导电肌肉细胞（``Cell``）。

        肌肉细胞仍是单室的（非多室），形态仍由代码生成，不从文件加载。
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

        # 注意：单室细胞模型不使用轴向电阻率/轴向电阻，此参数取值无影响
        ip.resistivities.append(
            Resistivity(value=self.get_bioparameter("resistivity").value)
        )

        # 注意：钙反转电位未通过 Nernst 方程计算，initial_ext_concentration 取值无影响
        species = Species(
            id="ca",
            ion="ca",
            concentration_model="CaPool",
            initial_concentration="0 mM",
            initial_ext_concentration="2E-6 mol_per_cm3",
        )

        ip.species.append(species)

    def create_neuron_cell(self, cell_name, morphology):
        """从 NeuroML 多室形态文件加载特定神经元细胞，并为其配置生物物理属性。

        与 Level C 不同，Level D 的神经元细胞形态从 ``{cell_name}_D.cell.nml`` 文件读取，
        支持真实的树突/轴突多室结构。离子通道密度则从生物参数表读取。

        :param cell_name: 神经元标准名称（如 ``"ADAL"``），用于定位形态文件
        :return: 配置好的 NeuroML ``Cell`` 对象
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
        cell.biophysical_properties.intracellular_properties = ip

        # 注意：单室细胞模型不使用轴向电阻率/轴向电阻，此参数取值无影响
        ip.resistivities.append(
            Resistivity(value=self.get_bioparameter("resistivity").value)
        )

        # 注意：钙反转电位未通过 Nernst 方程计算，initial_ext_concentration 取值无影响
        species = Species(
            id="ca",
            ion="ca",
            concentration_model="CaPool",
            initial_concentration="0 mM",
            initial_ext_concentration="2E-6 mol_per_cm3",
        )

        ip.species.append(species)

        return cell

    def create_offsetcurrent_concentrationmodel(self):
        """创建偏置电流生成器和钙浓度模型（``FixedFactorConcentrationModel``）。"""
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
        """创建神经元间化学突触（``ExpTwoSynapse``）和缝隙连接（``GapJunction``）。"""
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
        """创建神经元到肌肉的化学突触（``ExpTwoSynapse``）和缝隙连接。"""
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
