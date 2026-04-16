# =============================================================================
# 功能描述：
#   Level D1 参数层级定义。多室导电模型（继承自 D），但化学突触改为模拟型
#   （GradedSynapse / GradedSynapse2），可能是「完整规模」模型的中期目标。
#
# 类与方法索引：
#   ParameterisedModel                   (L46)   — ParameterisedModel 类
#     __init__                           (L47)   — 初始化 Level D1 参数模型，多室导电模型 + 模拟突触（GradedSynapse）
#     set_default_bioparameters          (L61)   — 设置 Level D1 的默认生物参数，使用较低内阻（3 kohm_cm vs D 的 12 kohm_cm），
#     create_neuron_to_neuron_syn        (L176)  — 创建神经元间模拟突触（``GradedSynapse``）和缝隙连接（``GapJunction``）
#     create_neuron_to_muscle_syn        (L207)  — 创建神经元到肌肉的模拟突触（``GradedSynapse``）和缝隙连接
#     get_elec_syn                       (L238)  — 根据连接类型获取缝隙连接（``GapJunction``）对象
#     get_exc_syn                        (L271)  — 根据连接类型获取兴奋性模拟突触（``GradedSynapse``）对象
#     get_inh_syn                        (L346)  — 根据连接类型获取抑制性模拟突触（``GradedSynapse``）对象
#     create_n_connection_synapse        (L422)  — D1 层级重载此方法以支持 ``GradedSynapse2`` 的注册
#     is_analog_conn                     (L443)  — D1 层级扩展模拟突触判断，将 ``GradedSynapse2`` 也视为模拟连接
#   GradedSynapse2                       (L454)  — GradedSynapse2 类
#     __init__                           (L455)  — 初始化 D1 层级自定义双分量模拟突触，存储 ID
#     export                             (L471)  — 将 D1 的 GradedSynapse2 以 NeuroML XML 格式写入输出流
#
# 更新日志：
#   2026-04-16  Copilot  添加中文 docstring 和行内注释（计划1阶段三）
#
# 当前维护者：Copilot
# =============================================================================
"""

Parameters D:
    Cells:           Multicompartmental, conductance based cell models with HH like ion channels
    Chem Synapses:   Analogue/graded synapses; continuous transmission (voltage dependent)
    Gap junctions:   Electrical connection; current linerly depends on difference in voltages

ASSESSMENT:
    May be the right target for the "full scale" model in the medium term...
    Similar issues to parameters D
    Note issue https://github.com/openworm/CElegansNeuroML/issues/71 regarding status of this


"""

from neuroml import GapJunction

from c302.parameters_D import ParameterisedModel as ParameterisedModel_D


class ParameterisedModel(ParameterisedModel_D):
    def __init__(self):
        """初始化 Level D1 参数模型，多室导电模型 + 模拟突触（GradedSynapse）。

        D1 是 D 的模拟突触变体（类似于 C→C1 的关系）：
        - 细胞仍为多室模型，继承 D 的形态加载机制
        - 突触从事件驱动改为模拟型（``GradedSynapse``），支持非放电神经元
        - 可能是"完整规模"模型的中期目标，但仍有 D 级内阻问题（GitHub #71）
        """
        super(ParameterisedModel, self).__init__()
        self.level = "D1"
        self.custom_component_types_definitions = ["cell_C.xml", "custom_synapses.xml"]

        self.set_default_bioparameters()

    def set_default_bioparameters(self):
        """设置 Level D1 的默认生物参数，使用较低内阻（3 kohm_cm vs D 的 12 kohm_cm），
        突触参数改为 GradedSynapse 类型。
        """
        self.add_bioparameter("cell_diameter", "5", "BlindGuess", "0.1")
        self.add_bioparameter("muscle_length", "20", "BlindGuess", "0.1")

        self.add_bioparameter("initial_memb_pot", "-45 mV", "BlindGuess", "0.1")

        self.add_bioparameter(
            "specific_capacitance", "1 uF_per_cm2", "BlindGuess", "0.1"
        )

        # D1 胸质电阐率低于 D（3 vs 12 kohm_cm），缩短突触位点间的电位梯度传播距离
        self.add_bioparameter("resistivity", "3 kohm_cm", "BlindGuess", "0.1")

        self.add_bioparameter("muscle_spike_thresh", "-26 mV", "BlindGuess", "0.1")
        self.add_bioparameter("neuron_spike_thresh", "-26 mV", "BlindGuess", "0.1")

        self.add_bioparameter(
            "muscle_leak_cond_density", "0.005 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_leak_cond_density", "0.005 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter("leak_erev", "-50 mV", "BlindGuess", "0.1")

        self.add_bioparameter(
            "muscle_k_slow_cond_density", "4 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_k_slow_cond_density",
            "1.8333751019872582 mS_per_cm2",
            "BlindGuess",
            "0.1",
        )
        self.add_bioparameter("k_slow_erev", "-60 mV", "BlindGuess", "0.1")

        self.add_bioparameter(
            "muscle_k_fast_cond_density", "0.2 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_k_fast_cond_density",
            "0.0711643917483308 mS_per_cm2",
            "BlindGuess",
            "0.1",
        )
        self.add_bioparameter("k_fast_erev", "-60 mV", "BlindGuess", "0.1")

        self.add_bioparameter(
            "muscle_ca_boyle_cond_density", "4 mS_per_cm2", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_ca_boyle_cond_density",
            "1.6862775772264702 mS_per_cm2",
            "BlindGuess",
            "0.1",
        )
        self.add_bioparameter("ca_boyle_erev", "40 mV", "BlindGuess", "0.1")

        self.add_bioparameter("ca_conc_decay_time", "11.5943 ms", "BlindGuess", "0.1")
        self.add_bioparameter(
            "ca_conc_rho", "0.000238919 mol_per_m_per_A_per_s", "BlindGuess", "0.1"
        )

        self.add_bioparameter(
            "global_connectivity_power_scaling", "0", "BlindGuess", "0.1"
        )

        # GradedSynapse2 兴奋性参数（ar/ad 激活/失活速率, beta/vth 电压 sigmoid 门控）
        self.add_bioparameter(
            "neuron_to_neuron_exc_syn_conductance", "2 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_exc_syn_conductance", "2 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("exc_syn_ar", ".5 per_s", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_ad", "20 per_s", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_beta", "0.25 per_mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_vth", "-35 mV", "BlindGuess", "0.1")
        self.add_bioparameter("exc_syn_erev", "0 mV", "BlindGuess", "0.1")

        # GradedSynapse2 抑制性参数（erev=-80 mV，产生超极化）
        self.add_bioparameter(
            "neuron_to_neuron_inh_syn_conductance", "26 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_inh_syn_conductance", "0.25 nS", "BlindGuess", "0.1"
        )

        self.add_bioparameter("inh_syn_ar", ".005 per_s", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_ad", "10 per_s", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_beta", "0.5 per_mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_vth", "-55 mV", "BlindGuess", "0.1")
        self.add_bioparameter("inh_syn_erev", "-80 mV", "BlindGuess", "0.1")

        # 缝隙连接（GapJunction）
        self.add_bioparameter(
            "neuron_to_neuron_elec_syn_gbase", "0.005 nS", "BlindGuess", "0.1"
        )
        self.add_bioparameter(
            "neuron_to_muscle_elec_syn_gbase", "0.0001 nS", "BlindGuess", "0.1"
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

    def create_neuron_to_neuron_syn(self):
        """创建神经元间模拟突触（``GradedSynapse``）和缝隙连接（``GapJunction``）。"""
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
        """创建神经元到肌肉的模拟突触（``GradedSynapse``）和缝隙连接。"""
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
        :return: 对应的突触对象（``GradedSynapse`` 或 ``GradedSynapse2``）
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
            ar = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "ar"
            )
            ad = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "ad"
            )
            beta = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "beta"
            )
            vth = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "vth"
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
            ar = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "ar"
            )
            ad = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "ad"
            )
            beta = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "beta"
            )
            vth = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "exc_syn_%s", "vth"
            )
            conn_id = "neuron_to_muscle_exc_syn"

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
            ar = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "ar"
            )
            ad = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "ad"
            )
            beta = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "beta"
            )
            vth = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "vth"
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
            ar = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "ar"
            )
            ad = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "ad"
            )
            beta = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "beta"
            )
            vth = self.get_conn_param(
                pre_cell, post_cell, specific_param_template, "inh_syn_%s", "vth"
            )

            conn_id = "neuron_to_muscle_inh_syn"

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
        """D1 层级重载此方法以支持 ``GradedSynapse2`` 的注册。

        :param prototype_syn: 突触原型对象
        :param n: 连接数（仅用于错误消息）
        :param nml_doc: NeuroML 文档对象
        :param existing_synapses: 已注册突触字典
        :return: 已注册的突触原型对象
        """
        if prototype_syn.id in existing_synapses:
            return existing_synapses[prototype_syn.id]

        if isinstance(prototype_syn, GradedSynapse2):
            existing_synapses[prototype_syn.id] = prototype_syn
            nml_doc.graded_synapses.append(prototype_syn)
            return prototype_syn
        else:
            return super(ParameterisedModel, self).create_n_connection_synapse(
                prototype_syn, n, nml_doc, existing_synapses
            )

    def is_analog_conn(self, syn):
        """D1 层级扩展模拟突触判断，将 ``GradedSynapse2`` 也视为模拟连接。

        :param syn: 突触对象
        :return: ``True`` 若为 ``GradedSynapse`` 或 ``GradedSynapse2`` 实例
        """
        return super(ParameterisedModel, self).is_analog_conn(syn) or isinstance(
            syn, GradedSynapse2
        )


class GradedSynapse2:
    def __init__(self, id, conductance, ar, ad, beta, vth, erev):
        """初始化 D1 层级自定义双分量模拟突触，存储 ID。

        定义于 ``custom_synapses.xml``，允许两个激活分量叠加，
        适合神经元间某些需要更精细突触动力学的连接。

        :param id: 突触唯一标识符
        """
        self.id = id
        self.conductance = conductance
        self.ar = ar
        self.ad = ad
        self.beta = beta
        self.vth = vth
        self.erev = erev

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        """将 D1 的 GradedSynapse2 以 NeuroML XML 格式写入输出流。

        :param outfile: 可写的输出流对象
        :param level: 缩进层级
        :param namespace: XML 命名空间（保留）
        :param name_: XML 元素名（保留）
        :param pretty_print: 是否美化输出
        """
        outfile.write(
            "    " * level
            + '<gradedSynapse2 id="%s" conductance="%s" ar="%s" ad="%s" beta="%s" vth="%s" erev="%s"/>\n'
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
