# =============================================================================
# 功能描述：
#   Level W2D 参数化模型：CellW2D 偏置-增益细胞 + OutputSynapse 连续突触。
#   从 special.py 拆分而来（计划6阶段一）。
#
# 类与方法索引：
#   _W2DModel                            (L28)
#     create_models                      (L31)
#     create_generic_muscle_cell         (L39)
#     create_generic_neuron_cell         (L43)
#     create_offset                      (L47)
#     create_neuron_to_neuron_syn        (L56)
#     create_neuron_to_muscle_syn        (L65)
#     get_elec_syn                       (L73)
#     get_exc_syn                        (L88)
#     get_inh_syn                        (L92)
#
# 更新日志：
#   2026-04-19  Copilot  计划5阶段六：从 factory.py 迁移特殊模型
#   2026-04-19  Copilot  计划6阶段一：从 special.py 拆分为独立文件
#
# 当前维护者：Copilot
# =============================================================================
"""W2D 层级参数化模型。"""
from neuroml import GapJunction, PulseGenerator

from c302.parameters.custom_types import CellW2D, OutputSynapse
from c302.parameters.factory.base import _ModelBase


class _W2DModel(_ModelBase):
    """Level W2D：CellW2D 偏置-增益细胞 + OutputSynapse 连续突触。"""

    def create_models(self):
        """创建肌肉/神经元细胞、偏置电流和突触。"""
        self.create_generic_muscle_cell()
        self.create_generic_neuron_cell()
        self.create_offset()
        self.create_neuron_to_neuron_syn()
        self.create_neuron_to_muscle_syn()

    def create_generic_muscle_cell(self):
        """创建 W2D 通用肌肉细胞。"""
        self.generic_muscle_cell = CellW2D(id="GenericMuscleCell")

    def create_generic_neuron_cell(self):
        """创建 W2D 通用神经元细胞。"""
        self.generic_neuron_cell = CellW2D(id="GenericNeuronCell")

    def create_offset(self):
        """创建偏置电流生成器。"""
        self.offset_current = PulseGenerator(
            id="offset_current",
            delay=self.get_bioparameter("unphysiological_offset_current_del").value,
            duration=self.get_bioparameter("unphysiological_offset_current_dur").value,
            amplitude=self.get_bioparameter("unphysiological_offset_current").value,
        )

    def create_neuron_to_neuron_syn(self):
        """创建神经元间突触（OutputSynapse + GapJunction）。"""
        self.neuron_to_neuron_exc_syn = OutputSynapse(id="neuron_to_neuron_exc_w2d")
        self.neuron_to_neuron_inh_syn = OutputSynapse(id="neuron_to_neuron_inh_w2d")
        self.neuron_to_neuron_elec_syn = GapJunction(
            id="neuron_to_neuron_elec_syn",
            conductance=self.get_bioparameter("neuron_to_neuron_elec_syn_gbase").value,
        )

    def create_neuron_to_muscle_syn(self):
        """创建神经元到肌肉突触（OutputSynapse + GapJunction）。"""
        self.neuron_to_muscle_exc_syn = OutputSynapse(id="neuron_to_muscle_w2d")
        self.neuron_to_muscle_elec_syn = GapJunction(
            id="neuron_to_muscle_elec_syn",
            conductance=self.get_bioparameter("neuron_to_muscle_elec_syn_gbase").value,
        )

    def get_elec_syn(self, pre_cell, post_cell, conn_type):
        """根据连接类型返回 GapJunction。"""
        if conn_type == "neuron_to_neuron":
            gbase = self.get_bioparameter("neuron_to_neuron_elec_syn_gbase").value
            conn_id = "neuron_to_neuron_elec_syn"
        elif conn_type == "neuron_to_muscle":
            gbase = self.get_bioparameter("neuron_to_muscle_elec_syn_gbase").value
            conn_id = "neuron_to_muscle_elec_syn"
        elif conn_type == "muscle_to_muscle":
            gbase = self.get_bioparameter("muscle_to_muscle_elec_syn_gbase").value
            conn_id = "muscle_to_muscle_elec_syn"
        else:
            raise ValueError("Unknown electrical connection type: %s" % conn_type)
        return GapJunction(id=conn_id, conductance=gbase)

    def get_exc_syn(self, pre_cell, post_cell, conn_type):
        """兴奋性突触 — 返回 OutputSynapse。"""
        return self.neuron_to_neuron_exc_syn

    def get_inh_syn(self, pre_cell, post_cell, conn_type):
        """抑制性突触 — 返回 OutputSynapse。"""
        return self.neuron_to_neuron_inh_syn
