# =============================================================================
# 功能描述：
#   Level C2 参数化模型：HH 导电模型 + GradedSynapse + 多种自定义缝隙连接
#   （DelayedGapJunction / ProprioGapJunction / ProprioGapJunction2）。
#   从 special.py 拆分而来（计划6阶段一）。
#
# 类与方法索引：
#   _C2Model                             (L60)   — Level C2：HH 导电模型 + GradedSynapse + 多种自定义缝隙连接
#     create_models                      (L63)   — 创建所有组件：浓度模型、肌肉/神经元、突触
#     create_generic_muscle_cell         (L72)   — 创建 C2 肌肉细胞（独立膜参数和通道变体）
#     create_offsetcurrent_concentrationmodel (L164)  — 创建偏置电流和独立的神经元/肌肉钙浓度模型
#     create_neuron_to_neuron_syn        (L219)  — 创建神经元间突触（GradedSynapse + GapJunction + DelayedGapJunction）
#     create_neuron_to_muscle_syn        (L258)  — 创建神经元到肌肉突触（GradedSynapse + GapJunction）
#     create_muscle_to_muscle_syn        (L285)  — 创建肌肉间缝隙连接
#     get_elec_syn                       (L292)  — 电突触 — 支持 DelayedGapJunction / ProprioGapJunction(2) / GapJunction
#     get_exc_syn                        (L376)  — 兴奋性突触 — 支持 NeuronMuscle / GradedSynapse2 / GradedSynapse
#     get_inh_syn                        (L469)  — 抑制性突触 — GradedSynapse
#     create_n_connection_synapse        (L509)  — 注册突触原型（含 C2 自定义类型）
#     is_elec_conn                       (L535)  — 判断是否为电突触（含延迟/本体感觉变体）
#     is_analog_conn                     (L541)  — 判断是否为模拟连接（含 NeuronMuscle / GradedSynapse2）
#
# 更新日志：
#   2026-04-19  Copilot  计划5阶段六：从 factory.py 迁移特殊模型
#   2026-04-19  Copilot  计划6阶段一：从 special.py 拆分为独立文件
#
# 当前维护者：Copilot
# =============================================================================
"""C2 层级参数化模型。"""
from neuroml import (
    BiophysicalProperties,
    Cell,
    ChannelDensity,
    FixedFactorConcentrationModel,
    GapJunction,
    GradedSynapse,
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

from c302.parameters.custom_types import (
    DelayedGapJunction,
    GradedSynapse2,
    MuscleConcentrationModel2,
    NeuronMuscle,
    ProprioGapJunction,
    ProprioGapJunction2,
)
from c302.parameters.factory.hh import _HHModel


class _C2Model(_HHModel):
    """Level C2：HH 导电模型 + GradedSynapse + 多种自定义缝隙连接。"""

    def create_models(self):
        """创建所有组件：浓度模型、肌肉/神经元、突触。"""
        self.create_offsetcurrent_concentrationmodel()
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()
        self.create_muscle_to_muscle_syn()

    def create_generic_muscle_cell(self):
        """创建 C2 肌肉细胞（独立膜参数和通道变体）。"""
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
            InitMembPotential(
                value=self.get_bioparameter("muscle_initial_memb_pot").value
            )
        )
        mp.specific_capacitances.append(
            SpecificCapacitance(
                value=self.get_bioparameter("muscle_specific_capacitance").value
            )
        )
        mp.spike_threshes.append(
            SpikeThresh(value=self.get_bioparameter("muscle_spike_thresh").value)
        )
        # 4 个通道密度：Leak, k_slow_muscle, k_fast_muscle, ca_boyle_muscle
        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter("muscle_leak_cond_density").value,
                id="Leak_all",
                ion_channel="Leak",
                erev=self.get_bioparameter("muscle_leak_erev").value,
                ion="non_specific",
            )
        )
        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter("muscle_k_slow_cond_density").value,
                id="k_slow_all",
                ion_channel="k_slow_muscle",
                erev=self.get_bioparameter("muscle_k_slow_erev").value,
                ion="k",
            )
        )
        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter("muscle_k_fast_cond_density").value,
                id="k_fast_all",
                ion_channel="k_fast_muscle",
                erev=self.get_bioparameter("muscle_k_fast_erev").value,
                ion="k",
            )
        )
        mp.channel_densities.append(
            ChannelDensity(
                cond_density=self.get_bioparameter(
                    "muscle_ca_boyle_cond_density"
                ).value,
                id="ca_boyle_all",
                ion_channel="ca_boyle_muscle",
                erev=self.get_bioparameter("muscle_ca_boyle_erev").value,
                ion="ca",
            )
        )

        # 细胞内属性：电阻率 + 钙离子种类
        ip = IntracellularProperties()
        self.generic_muscle_cell.biophysical_properties.intracellular_properties = ip
        ip.resistivities.append(Resistivity(value="0.1 kohm_cm"))
        species = Species(
            id="ca",
            ion="ca",
            concentration_model="CaPoolMuscle",
            initial_concentration="0 mM",
            initial_ext_concentration="2E-6 mol_per_cm3",
        )
        ip.species.append(species)

    def create_offsetcurrent_concentrationmodel(self):
        """创建偏置电流和独立的神经元/肌肉钙浓度模型。"""
        self.offset_current = PulseGenerator(
            id="offset_current",
            delay=self.get_bioparameter("unphysiological_offset_current_del").value,
            duration=self.get_bioparameter("unphysiological_offset_current_dur").value,
            amplitude=self.get_bioparameter("unphysiological_offset_current").value,
        )

        # 神经元浓度模型
        self.concentration_model_neuron = FixedFactorConcentrationModel(
            id="CaPool",
            ion="ca",
            resting_conc="0 mM",
            decay_constant=self.get_bioparameter("ca_conc_decay_time").value,
            rho=self.get_bioparameter("ca_conc_rho").value,
        )

        # 肌肉浓度模型 — 支持 MuscleConcentrationModel2 或 FixedFactor
        if self.get_bioparameter("ca_conc_xRho_muscle"):
            self.concentration_model_muscle = MuscleConcentrationModel2(
                id="CaPoolMuscle",
                ion="ca",
                resting_conc="0 mM",
                decay_constant=self.get_bioparameter("ca_conc_decay_time_muscle").value,
                rho=self.get_bioparameter("ca_conc_rho_muscle").value,
                xRho=self.get_bioparameter("ca_conc_xRho_muscle").value,
                iCaSigmoidMid=self.get_bioparameter(
                    "ca_conc_iCaSigmoidMid_muscle"
                ).value,
                iCaSigmoidSlope=self.get_bioparameter(
                    "ca_conc_iCaSigmoidSlope_muscle"
                ).value,
                xSigmoidMid=self.get_bioparameter("ca_conc_xSigmoidMid_muscle").value,
                xSigmoidSlope=self.get_bioparameter(
                    "ca_conc_xSigmoidSlope_muscle"
                ).value,
                xDecay=self.get_bioparameter("ca_conc_xDecay_muscle").value,
                xrest=self.get_bioparameter("ca_conc_xrest_muscle").value,
            )
        else:
            self.concentration_model_muscle = FixedFactorConcentrationModel(
                id="CaPoolMuscle",
                ion="ca",
                resting_conc="0 mM",
                decay_constant=self.get_bioparameter("ca_conc_decay_time_muscle").value,
                rho=self.get_bioparameter("ca_conc_rho_muscle").value,
            )

        # 双浓度模型列表
        self.concentration_model = [
            self.concentration_model_neuron,
            self.concentration_model_muscle,
        ]

    def create_neuron_to_neuron_syn(self):
        """创建神经元间突触（GradedSynapse + GapJunction + DelayedGapJunction）。"""
        self.neuron_to_neuron_exc_syn = GradedSynapse(
            id="neuron_to_neuron_exc_syn",
            conductance=self.get_bioparameter(
                "neuron_to_neuron_exc_syn_conductance"
            ).value,
            delta=self.get_bioparameter("neuron_to_neuron_exc_syn_delta").value,
            Vth=self.get_bioparameter("neuron_to_neuron_exc_syn_vth").value,
            erev=self.get_bioparameter("neuron_to_neuron_exc_syn_erev").value,
            k=self.get_bioparameter("neuron_to_neuron_exc_syn_k").value,
        )
        self.neuron_to_neuron_inh_syn = GradedSynapse(
            id="neuron_to_neuron_inh_syn",
            conductance=self.get_bioparameter(
                "neuron_to_neuron_inh_syn_conductance"
            ).value,
            delta=self.get_bioparameter("neuron_to_neuron_inh_syn_delta").value,
            Vth=self.get_bioparameter("neuron_to_neuron_inh_syn_vth").value,
            erev=self.get_bioparameter("neuron_to_neuron_inh_syn_erev").value,
            k=self.get_bioparameter("neuron_to_neuron_inh_syn_k").value,
        )
        self.neuron_to_neuron_elec_syn = GapJunction(
            id="neuron_to_neuron_elec_syn",
            conductance=self.get_bioparameter("neuron_to_neuron_elec_syn_gbase").value,
        )
        # C2 特有：延迟电突触
        self.neuron_to_motor_elec_syn = DelayedGapJunction(
            id="neuron_to_motor_delayed_elec_syn",
            weight=self.get_bioparameter(
                "neuron_to_motor_delayed_elec_syn_weight"
            ).value,
            conductance=self.get_bioparameter(
                "neuron_to_motor_delayed_elec_syn_gbase"
            ).value,
            sigma=self.get_bioparameter("neuron_to_motor_delayed_elec_syn_sigma").value,
            mu=self.get_bioparameter("neuron_to_motor_delayed_elec_syn_mu").value,
        )

    def create_neuron_to_muscle_syn(self):
        """创建神经元到肌肉突触（GradedSynapse + GapJunction）。"""
        self.neuron_to_muscle_exc_syn = GradedSynapse(
            id="neuron_to_muscle_exc_syn",
            conductance=self.get_bioparameter(
                "neuron_to_muscle_exc_syn_conductance"
            ).value,
            delta=self.get_bioparameter("neuron_to_muscle_exc_syn_delta").value,
            Vth=self.get_bioparameter("neuron_to_muscle_exc_syn_vth").value,
            erev=self.get_bioparameter("neuron_to_muscle_exc_syn_erev").value,
            k=self.get_bioparameter("neuron_to_muscle_exc_syn_k").value,
        )
        self.neuron_to_muscle_inh_syn = GradedSynapse(
            id="neuron_to_muscle_inh_syn",
            conductance=self.get_bioparameter(
                "neuron_to_muscle_inh_syn_conductance"
            ).value,
            delta=self.get_bioparameter("neuron_to_muscle_inh_syn_delta").value,
            Vth=self.get_bioparameter("neuron_to_muscle_inh_syn_vth").value,
            erev=self.get_bioparameter("neuron_to_muscle_inh_syn_erev").value,
            k=self.get_bioparameter("neuron_to_muscle_inh_syn_k").value,
        )
        self.neuron_to_muscle_elec_syn = GapJunction(
            id="neuron_to_muscle_elec_syn",
            conductance=self.get_bioparameter("neuron_to_muscle_elec_syn_gbase").value,
        )

    def create_muscle_to_muscle_syn(self):
        """创建肌肉间缝隙连接。"""
        self.muscle_to_muscle_elec_syn = GapJunction(
            id="muscle_to_muscle_elec_syn",
            conductance=self.get_bioparameter("muscle_to_muscle_elec_syn_gbase").value,
        )

    def get_elec_syn(self, pre_cell, post_cell, conn_type):
        """电突触 — 支持 DelayedGapJunction / ProprioGapJunction(2) / GapJunction。"""
        self.found_specific_param = False
        sigma = mu = p_gbase = ar = ad = beta = gbase = vth = erev = conn_id = None

        if conn_type == "neuron_to_neuron":
            gbase = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s",
                "neuron_to_neuron_elec_syn_%s", "gbase",
            )
            sigma = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s",
                "neuron_to_neuron_elec_syn_%s", "sigma",
            )
            mu = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s",
                "neuron_to_neuron_elec_syn_%s", "mu",
            )
            p_gbase = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s",
                "neuron_to_neuron_elec_syn_%s", "p_gbase",
            )
            ar = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s",
                "neuron_to_neuron_elec_syn_%s", "p_ar",
            )
            ad = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s",
                "neuron_to_neuron_elec_syn_%s", "p_ad",
            )
            beta = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s",
                "neuron_to_neuron_elec_syn_%s", "beta",
            )
            vth = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s",
                "neuron_to_neuron_elec_syn_%s", "vth",
            )
            erev = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s",
                "neuron_to_neuron_elec_syn_%s", "erev",
            )
            if sigma and mu or p_gbase and mu:
                self.found_specific_param = True
            conn_id = "neuron_to_neuron_elec_syn"

        elif conn_type == "neuron_to_muscle":
            gbase = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s",
                "neuron_to_muscle_elec_syn_%s", "gbase",
            )
            conn_id = "neuron_to_muscle_elec_syn"

        elif conn_type == "muscle_to_muscle":
            gbase = self.get_conn_param(
                pre_cell, post_cell, "%s_to_%s_elec_syn_%s",
                "muscle_to_muscle_elec_syn_%s", "gbase",
            )
            conn_id = "muscle_to_muscle_elec_syn"

        if self.found_specific_param:
            conn_id = "%s_to_%s_elec_syn" % (pre_cell, post_cell)

        # 分派到不同的电突触类型
        if sigma and mu and not p_gbase:
            conn_id = "%s_to_%s_delayed_elec_syn" % (pre_cell, post_cell)
            return DelayedGapJunction(
                id=conn_id, conductance=gbase, sigma=sigma, mu=mu
            )
        elif p_gbase and sigma:
            conn_id = "%s_to_%s_proprioceptive_elec_syn" % (pre_cell, post_cell)
            if ar and ad:
                # ProprioGapJunction2 变体
                conn_id = "%s_to_%s_proprioceptive2_elec_syn" % (pre_cell, post_cell)
                return ProprioGapJunction2(
                    id=conn_id, conductance=gbase, p_conductance=p_gbase,
                    ar=ar, ad=ad, beta=beta, vth=vth, erev=erev, sigma=sigma, mu=mu,
                )
            return ProprioGapJunction(
                id=conn_id, conductance=gbase, p_conductance=p_gbase,
                sigma=sigma, mu=mu,
            )
        return GapJunction(id=conn_id, conductance=gbase)

    def get_exc_syn(self, pre_cell, post_cell, conn_type):
        """兴奋性突触 — 支持 NeuronMuscle / GradedSynapse2 / GradedSynapse。"""
        self.found_specific_param = False
        specific = "%s_to_%s_exc_syn_%s"
        cath = ar = ad = beta = vth = erev = delta = k = None

        if conn_type == "neuron_to_neuron":
            default = "neuron_to_neuron_exc_syn_%s"
            conductance = self.get_conn_param(
                pre_cell, post_cell, specific, default, "conductance"
            )
            erev = self.get_conn_param(
                pre_cell, post_cell, specific, default, "erev"
            )
            delta = self.get_conn_param(
                pre_cell, post_cell, specific, default, "delta"
            )
            vth = self.get_conn_param(
                pre_cell, post_cell, specific, default, "vth"
            )
            k = self.get_conn_param(
                pre_cell, post_cell, specific, default, "k"
            )
            ar = self.get_conn_param(
                pre_cell, post_cell, specific, default, "ar"
            )
            ad = self.get_conn_param(
                pre_cell, post_cell, specific, default, "ad"
            )
            beta = self.get_conn_param(
                pre_cell, post_cell, specific, default, "beta"
            )
            conn_id = "neuron_to_neuron_exc_syn"

        elif conn_type == "neuron_to_muscle":
            default = "neuron_to_muscle_exc_syn_%s"
            conductance = self.get_conn_param(
                pre_cell, post_cell, specific, default, "conductance"
            )
            erev = self.get_conn_param(
                pre_cell, post_cell, specific, default, "erev"
            )
            delta = self.get_conn_param(
                pre_cell, post_cell, specific, default, "delta"
            )
            vth = self.get_conn_param(
                pre_cell, post_cell, specific, default, "vth"
            )
            k = self.get_conn_param(
                pre_cell, post_cell, specific, default, "k"
            )
            conn_id = "neuron_to_muscle_exc_syn"

        elif conn_type == "muscle_to_neuron":
            default = "muscle_to_neuron_exc_syn_%s"
            conductance = self.get_conn_param(
                pre_cell, post_cell, specific, default, "conductance"
            )
            erev = self.get_conn_param(
                pre_cell, post_cell, specific, default, "erev"
            )
            ar = self.get_conn_param(
                pre_cell, post_cell, specific, default, "ar"
            )
            ad = self.get_conn_param(
                pre_cell, post_cell, specific, default, "ad"
            )
            beta = self.get_conn_param(
                pre_cell, post_cell, specific, default, "beta"
            )
            cath = self.get_conn_param(
                pre_cell, post_cell, specific, default, "cath"
            )
            conn_id = "muscle_to_neuron_exc_syn"

        if self.found_specific_param:
            conn_id = "%s_to_%s_exc_syn" % (pre_cell, post_cell)

        # 分派到不同的兴奋性突触类型
        if cath:
            return NeuronMuscle(
                id=conn_id, conductance=conductance,
                ar=ar, ad=ad, beta=beta, cath=cath, erev=erev,
            )
        if ar and ad and beta:
            return GradedSynapse2(
                id=conn_id, conductance=conductance,
                ar=ar, ad=ad, beta=beta, vth=vth, erev=erev,
            )
        return GradedSynapse(
            id=conn_id, conductance=conductance, delta=delta, Vth=vth, erev=erev, k=k
        )

    def get_inh_syn(self, pre_cell, post_cell, conn_type):
        """抑制性突触 — GradedSynapse。"""
        self.found_specific_param = False
        specific = "%s_to_%s_inh_syn_%s"

        if conn_type == "neuron_to_neuron":
            default = "neuron_to_neuron_inh_syn_%s"
        elif conn_type == "neuron_to_muscle":
            default = "neuron_to_muscle_inh_syn_%s"
        else:
            default = "neuron_to_neuron_inh_syn_%s"

        conductance = self.get_conn_param(
            pre_cell, post_cell, specific, default, "conductance"
        )
        erev = self.get_conn_param(
            pre_cell, post_cell, specific, default, "erev"
        )
        delta = self.get_conn_param(
            pre_cell, post_cell, specific, default, "delta"
        )
        vth = self.get_conn_param(
            pre_cell, post_cell, specific, default, "vth"
        )
        k = self.get_conn_param(
            pre_cell, post_cell, specific, default, "k"
        )

        conn_id = (
            "neuron_to_neuron_inh_syn"
            if conn_type == "neuron_to_neuron"
            else "neuron_to_muscle_inh_syn"
        )
        if self.found_specific_param:
            conn_id = "%s_to_%s_inh_syn" % (pre_cell, post_cell)

        return GradedSynapse(
            id=conn_id, conductance=conductance, delta=delta, Vth=vth, erev=erev, k=k
        )

    def create_n_connection_synapse(self, prototype_syn, n, nml_doc, existing_synapses):
        """注册突触原型（含 C2 自定义类型）。"""
        if prototype_syn.id in existing_synapses:
            return existing_synapses[prototype_syn.id]

        # C2 自定义电突触类型
        if isinstance(
            prototype_syn,
            (DelayedGapJunction, ProprioGapJunction, ProprioGapJunction2),
        ):
            existing_synapses[prototype_syn.id] = prototype_syn
            nml_doc.gap_junctions.append(prototype_syn)
            return prototype_syn
        # C2 自定义化学突触类型
        elif isinstance(
            prototype_syn, (NeuronMuscle, GradedSynapse, GradedSynapse2)
        ):
            existing_synapses[prototype_syn.id] = prototype_syn
            nml_doc.graded_synapses.append(prototype_syn)
            return prototype_syn

        # 其他类型委托给父类
        return super().create_n_connection_synapse(
            prototype_syn, n, nml_doc, existing_synapses
        )

    def is_elec_conn(self, syn):
        """判断是否为电突触（含延迟/本体感觉变体）。"""
        return super().is_elec_conn(syn) or isinstance(
            syn, (DelayedGapJunction, ProprioGapJunction, ProprioGapJunction2)
        )

    def is_analog_conn(self, syn):
        """判断是否为模拟连接（含 NeuronMuscle / GradedSynapse2）。"""
        return super().is_analog_conn(syn) or isinstance(
            syn, (NeuronMuscle, GradedSynapse2)
        )
