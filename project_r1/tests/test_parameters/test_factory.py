# =============================================================================
# 功能描述：
#   针对 parameters/factory/ 子包中工厂类的单元测试。
#   直接实例化模型并验证 create_models、create_neuron_cell、
#   get_exc_syn/get_inh_syn、create_n_connection_synapse 等方法。
#
# 类与方法索引：
#   TestCreateModel                      — create_model 工厂函数
#   TestDModel / TestD1Model             — D/D1 族模型
#   TestCustomTypes                      — IafActivityCell / GradedSynapse2 自定义类型
#   TestModelBaseElecSynParams           — _ModelBase 电突触参数多路径
#   TestC0ModelSynapse / TestC1ModelSynapse — C0/C1 突触覆盖
#   TestIafModel                         — A 级 _IafModel
#   TestIafActivityModel                 — B 级 _IafActivityModel
#   TestBC1Model                         — BC1 级 _BC1Model
#   TestHHModel                          — C 级 _HHModel
#   TestC2Model                          — C2 级 _C2Model
#   TestW2DModel                         — W2D 级 _W2DModel
#
# 更新日志：
#   2026-04-18  Copilot  计划3阶段九：补充 D/D1 族覆盖率
#   2026-04-19  Copilot  计划5阶段十：补全 6 个工厂类直接测试
#
# 当前维护者：Copilot
# =============================================================================
"""工厂类单元测试。"""
import pytest
from neuroml import GapJunction, Morphology, NeuroMLDocument, Segment
from neuroml.nml.nml import Point3DWithDiam

from c302.parameters.factory import (
    GradedSynapse2,
    IafActivityCell,
    _HHGradedModel,
    _HHMultiCompModel,
    _IafActivityModel,
    _IafModel,
    _HHC0Model,
    _HHC1Model,
    _HHModel,
    _ModelBase,
    create_model,
)


class TestCreateModel:
    """验证 create_model 工厂函数。"""

    @pytest.mark.parametrize("level", ["A", "B", "BC1", "C", "C0", "C1", "C2", "D", "D1", "W2D"])
    def test_create_all_levels(self, level):
        """每个级别都能成功创建模型。"""
        model = create_model(level)
        assert model.level == level

    def test_unknown_level_raises(self):
        """未知级别抛出 KeyError。"""
        with pytest.raises(KeyError, match="未知的模型层级"):
            create_model("Z99")

    def test_case_insensitive(self):
        """支持大小写不敏感。"""
        model = create_model("d1")
        assert model.level == "D1"


class TestDModel:
    """D 族模型测试。"""

    @pytest.fixture()
    def model(self):
        """创建 D 级模型并初始化。"""
        m = create_model("D")
        m.create_models()
        return m

    def test_no_generic_neuron(self, model):
        """D 族不创建 generic_neuron_cell。"""
        assert not hasattr(model, "generic_neuron_cell") or model.generic_neuron_cell is None

    def test_has_muscle_cell(self, model):
        """D 族有通用肌肉细胞。"""
        assert model.generic_muscle_cell is not None

    def test_create_neuron_cell(self, model):
        """D 族 create_neuron_cell 创建神经元。"""
        # 构造简易形态
        morph = Morphology(id="morphology_TestCell")
        prox = Point3DWithDiam(x="0", y="0", z="0", diameter="1")
        dist = Point3DWithDiam(x="0", y="10", z="0", diameter="1")
        seg = Segment(id="0", name="soma", proximal=prox, distal=dist)
        morph.segments.append(seg)

        cell = model.create_neuron_cell("TestCell", morph)
        assert cell.id == "TestCell"
        assert cell.morphology is morph
        # 检查生物物理属性
        bp = cell.biophysical_properties
        assert bp is not None
        mp = bp.membrane_properties
        assert len(mp.channel_densities) >= 4  # Leak, k_slow, k_fast, ca_boyle
        ip = bp.intracellular_properties
        assert len(ip.species) == 1
        assert ip.species[0].id == "ca"

    def test_has_concentration_model(self, model):
        """D 族有钙浓度模型。"""
        assert model.concentration_model is not None

    def test_has_offset_current(self, model):
        """D 族有偏置电流。"""
        assert model.offset_current is not None

    def test_elec_syn_is_gap_junction(self, model):
        """D 族电突触为 GapJunction。"""
        syn = model.get_elec_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, GapJunction)

    def test_exc_syn(self, model):
        """D 族兴奋性突触为 ExpTwoSynapse。"""
        from neuroml import ExpTwoSynapse
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, ExpTwoSynapse)


class TestD1Model:
    """D1 族模型测试。"""

    @pytest.fixture()
    def model(self):
        """创建 D1 级模型并初始化。"""
        m = create_model("D1")
        m.create_models()
        return m

    def test_exc_syn_is_graded(self, model):
        """D1 兴奋性突触为 GradedSynapse2。"""
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, GradedSynapse2)

    def test_inh_syn_is_graded(self, model):
        """D1 抑制性突触为 GradedSynapse2。"""
        syn = model.get_inh_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, GradedSynapse2)

    def test_exc_syn_muscle(self, model):
        """D1 神经元到肌肉兴奋性突触。"""
        syn = model.get_exc_syn("ADAL", "MDL01", "neuron_to_muscle")
        assert isinstance(syn, GradedSynapse2)
        assert "muscle" in syn.id

    def test_inh_syn_muscle(self, model):
        """D1 神经元到肌肉抑制性突触。"""
        syn = model.get_inh_syn("ADAL", "MDL01", "neuron_to_muscle")
        assert isinstance(syn, GradedSynapse2)
        assert "muscle" in syn.id

    def test_is_analog_conn(self, model):
        """D1 GradedSynapse2 判定为模拟连接。"""
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert model.is_analog_conn(syn) is True

    def test_is_not_analog_for_gap(self, model):
        """D1 GapJunction 不判定为模拟连接。"""
        syn = model.get_elec_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert model.is_analog_conn(syn) is False

    def test_create_n_connection_synapse_graded(self, model):
        """D1 create_n_connection_synapse 处理 GradedSynapse2。"""
        doc = NeuroMLDocument(id="test")
        existing = {}
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        result = model.create_n_connection_synapse(syn, 3, doc, existing)
        assert result.id == syn.id
        assert syn.id in existing

    def test_create_n_connection_synapse_existing(self, model):
        """D1 create_n_connection_synapse 复用已有突触。"""
        doc = NeuroMLDocument(id="test")
        existing = {}
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        # 第一次注册
        model.create_n_connection_synapse(syn, 3, doc, existing)
        # 第二次复用
        result = model.create_n_connection_synapse(syn, 5, doc, existing)
        assert result.id == syn.id

    def test_create_neuron_cell(self, model):
        """D1 继承 D 的 create_neuron_cell。"""
        morph = Morphology(id="morphology_TestCell")
        prox = Point3DWithDiam(x="0", y="0", z="0", diameter="1")
        dist = Point3DWithDiam(x="0", y="10", z="0", diameter="1")
        seg = Segment(id="0", name="soma", proximal=prox, distal=dist)
        morph.segments.append(seg)
        cell = model.create_neuron_cell("TestCell", morph)
        assert cell.id == "TestCell"


class TestCustomTypes:
    """自定义类型测试。"""

    def test_iaf_activity_cell_export(self):
        """IafActivityCell export 生成 XML。"""
        import io
        cell = IafActivityCell(
            id="test_cell",
            C="1.0 nF",
            thresh="-20 mV",
            reset="-70 mV",
            leak_conductance="0.1 nS",
            leak_reversal="-70 mV",
            tau1="10 ms",
        )
        buf = io.StringIO()
        cell.export(buf, level=0, namespace="", name_="iafActivityCell")
        xml = buf.getvalue()
        assert "iafActivityCell" in xml
        assert 'id="test_cell"' in xml
        assert 'tau1="10 ms"' in xml

    def test_graded_synapse2_export(self):
        """GradedSynapse2 export 生成 XML。"""
        import io
        syn = GradedSynapse2(
            id="test_syn",
            conductance="1 nS",
            ar="1",
            ad="0.5",
            beta="0.1",
            vth="-20 mV",
            erev="0 mV",
        )
        buf = io.StringIO()
        syn.export(buf, level=0, namespace="", name_="gradedSynapse2")
        xml = buf.getvalue()
        assert "gradedSynapse2" in xml
        assert 'id="test_syn"' in xml
        assert 'beta="0.1"' in xml


class TestModelBaseElecSynParams:
    """测试 _ModelBase._get_elec_syn_params 的多种路径。"""

    @pytest.fixture()
    def model_a(self):
        """Level A 模型。"""
        m = create_model("A")
        m.create_models()
        return m

    @pytest.fixture()
    def model_b(self):
        """Level B 模型。"""
        m = create_model("B")
        m.create_models()
        return m

    def test_a_elec_syn_neuron_to_muscle(self, model_a):
        """A 级神经元到肌肉电突触。"""
        from neuroml import ExpTwoSynapse
        syn = model_a.get_elec_syn("ADAL", "MDL01", "neuron_to_muscle")
        assert isinstance(syn, ExpTwoSynapse)

    def test_b_elec_syn_neuron_to_muscle(self, model_b):
        """B 级神经元到肌肉电突触。"""
        syn = model_b.get_elec_syn("ADAL", "MDL01", "neuron_to_muscle")
        assert isinstance(syn, GapJunction)

    def test_b_inh_syn(self, model_b):
        """B 级抑制性突触。"""
        from neuroml import ExpTwoSynapse
        syn = model_b.get_inh_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, ExpTwoSynapse)


class TestC0ModelSynapse:
    """C0 模型的突触覆盖测试。"""

    @pytest.fixture()
    def model(self):
        """Level C0 模型。"""
        m = create_model("C0")
        m.create_models()
        return m

    def test_create_n_connection_graded(self, model):
        """C0 create_n_connection_synapse 处理 GradedSynapse2。"""
        doc = NeuroMLDocument(id="test")
        existing = {}
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        result = model.create_n_connection_synapse(syn, 3, doc, existing)
        assert result.id == syn.id

    def test_is_analog_conn(self, model):
        """C0 GradedSynapse2 判定为模拟连接。"""
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert model.is_analog_conn(syn) is True

    def test_inh_syn_neuron_to_muscle(self, model):
        """C0 神经元到肌肉抑制性突触。"""
        syn = model.get_inh_syn("ADAL", "MDL01", "neuron_to_muscle")
        assert isinstance(syn, GradedSynapse2)


class TestC1ModelSynapse:
    """C1 模型的突触覆盖测试。"""

    @pytest.fixture()
    def model(self):
        """Level C1 模型。"""
        m = create_model("C1")
        m.create_models()
        return m

    def test_exc_syn_nn(self, model):
        """C1 neuron_to_neuron 兴奋性突触为 GradedSynapse。"""
        from neuroml import GradedSynapse
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, GradedSynapse)

    def test_inh_syn_nn(self, model):
        """C1 neuron_to_neuron 抑制性突触为 GradedSynapse。"""
        from neuroml import GradedSynapse
        syn = model.get_inh_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, GradedSynapse)

    def test_exc_syn_nm(self, model):
        """C1 neuron_to_muscle 兴奋性突触为 GradedSynapse。"""
        from neuroml import GradedSynapse
        syn = model.get_exc_syn("ADAL", "MDL01", "neuron_to_muscle")
        assert isinstance(syn, GradedSynapse)

    def test_inh_syn_nm(self, model):
        """C1 neuron_to_muscle 抑制性突触为 GradedSynapse。"""
        from neuroml import GradedSynapse
        syn = model.get_inh_syn("ADAL", "MDL01", "neuron_to_muscle")
        assert isinstance(syn, GradedSynapse)


# -- 计划5阶段十：补全工厂类单元测试 --


class TestIafModel:
    """A 级 _IafModel 测试。"""

    @pytest.fixture()
    def model(self):
        m = create_model("A")
        m.create_models()
        return m

    def test_create_models(self, model):
        """create_models 后有 generic_neuron_cell。"""
        assert model.generic_neuron_cell is not None

    def test_generic_neuron_is_iaf(self, model):
        """generic_neuron_cell 是 IafCell。"""
        from neuroml import IafCell
        assert isinstance(model.generic_neuron_cell, IafCell)

    def test_create_neuron_to_neuron_syn(self, model):
        """A 级 neuron_to_neuron 化学突触为 ExpTwoSynapse。"""
        from neuroml import ExpTwoSynapse
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, ExpTwoSynapse)

    def test_elec_syn_is_exp_two(self, model):
        """A 级电突触为 ExpTwoSynapse（非 GapJunction）。"""
        from neuroml import ExpTwoSynapse
        syn = model.get_elec_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, ExpTwoSynapse)


class TestIafActivityModel:
    """B 级 _IafActivityModel 测试。"""

    @pytest.fixture()
    def model(self):
        m = create_model("B")
        m.create_models()
        return m

    def test_generic_neuron_is_iaf_activity(self, model):
        """generic_neuron_cell 是 IafActivityCell。"""
        assert isinstance(model.generic_neuron_cell, IafActivityCell)

    def test_elec_syn_is_gap_junction(self, model):
        """B 级电突触为 GapJunction。"""
        syn = model.get_elec_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, GapJunction)


class TestBC1Model:
    """BC1 级 _BC1Model 测试。"""

    @pytest.fixture()
    def model(self):
        m = create_model("BC1")
        m.create_models()
        return m

    def test_exc_syn_is_graded(self, model):
        """BC1 兴奋性突触为 GradedSynapse。"""
        from neuroml import GradedSynapse
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, GradedSynapse)

    def test_inh_syn_is_graded(self, model):
        """BC1 抑制性突触为 GradedSynapse。"""
        from neuroml import GradedSynapse
        syn = model.get_inh_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, GradedSynapse)

    def test_neuron_to_muscle_syn(self, model):
        """BC1 neuron_to_muscle 突触为 GradedSynapse。"""
        from neuroml import GradedSynapse
        syn = model.get_exc_syn("ADAL", "MDL01", "neuron_to_muscle")
        assert isinstance(syn, GradedSynapse)


class TestHHModel:
    """C 级 _HHModel 测试。"""

    @pytest.fixture()
    def model(self):
        m = create_model("C")
        m.create_models()
        return m

    def test_create_models(self, model):
        """create_models 后有 generic_neuron_cell。"""
        assert model.generic_neuron_cell is not None

    def test_generic_neuron_is_hh(self, model):
        """generic_neuron_cell 是 Cell（HH 导电细胞）。"""
        from neuroml import Cell
        assert isinstance(model.generic_neuron_cell, Cell)

    def test_concentration_model(self, model):
        """C 级有钙浓度模型。"""
        assert model.concentration_model is not None

    def test_offset_current(self, model):
        """C 级有偏置电流。"""
        assert model.offset_current is not None


class TestC2Model:
    """C2 级 _C2Model 测试。"""

    @pytest.fixture()
    def model(self):
        m = create_model("C2")
        m.create_models()
        return m

    def test_create_models(self, model):
        """create_models 成功。"""
        assert model.generic_muscle_cell is not None

    def test_exc_syn_nn(self, model):
        """C2 neuron_to_neuron 兴奋性突触。"""
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert syn is not None

    def test_inh_syn_nn(self, model):
        """C2 neuron_to_neuron 抑制性突触。"""
        syn = model.get_inh_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert syn is not None

    def test_is_analog_conn(self, model):
        """C2 GradedSynapse2 判定为模拟连接。"""
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert model.is_analog_conn(syn) is True

    def test_is_elec_conn(self, model):
        """C2 GapJunction 判定为电连接。"""
        syn = model.get_elec_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert model.is_elec_conn(syn) is True


class TestW2DModel:
    """W2D 级 _W2DModel 测试。"""

    @pytest.fixture()
    def model(self):
        m = create_model("W2D")
        m.create_models()
        return m

    def test_create_models(self, model):
        """create_models 成功。"""
        assert model.generic_neuron_cell is not None

    def test_generic_neuron_is_cellw2d(self, model):
        """generic_neuron_cell 是 CellW2D。"""
        from c302.parameters.custom_types import CellW2D
        assert isinstance(model.generic_neuron_cell, CellW2D)

    def test_exc_syn_nn(self, model):
        """W2D 兴奋性突触为 OutputSynapse。"""
        from c302.parameters.custom_types import OutputSynapse
        syn = model.get_exc_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, OutputSynapse)

    def test_inh_syn_nn(self, model):
        """W2D 抑制性突触为 OutputSynapse。"""
        from c302.parameters.custom_types import OutputSynapse
        syn = model.get_inh_syn("ADAL", "ADAR", "neuron_to_neuron")
        assert isinstance(syn, OutputSynapse)
