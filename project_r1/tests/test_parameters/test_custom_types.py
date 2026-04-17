# =============================================================================
# 功能描述：
#   自定义组件类型（custom_types.py）单元测试。
#   测试所有自定义类型的创建和 XML export。
#
# 类与方法索引：
#   TestIafActivityCell                  (L39)   — IafActivityCell 创建和 export 测试
#     test_create                        (L42)   — 属性正确设置
#     test_export_xml                    (L52)   — export 输出有效 XML 片段
#   TestGradedSynapse2                   (L66)   — GradedSynapse2 创建和 export 测试
#     test_create                        (L69)   — 属性正确设置
#     test_export_xml                    (L79)   — export 输出有效 XML 片段
#     test_export_indentation            (L92)   — export 的缩进级别正确
#   TestDelayedGapJunction               (L105)  — DelayedGapJunction 创建和 export 测试
#     test_create                        (L108)  — 属性正确设置
#     test_export_xml                    (L117)  — export 输出有效 XML 片段
#   TestProprioGapJunction               (L132)  — ProprioGapJunction 创建和 export 测试
#     test_create                        (L135)  — 属性正确设置
#     test_export_xml                    (L144)  — export 输出有效 XML 片段
#   TestProprioGapJunction2              (L157)  — ProprioGapJunction2 创建和 export 测试
#     test_create                        (L160)  — 属性正确设置（含门控参数）
#     test_export_xml                    (L171)  — export 输出有效 XML 片段
#   TestNeuronMuscle                     (L186)  — NeuronMuscle 创建和 export 测试
#     test_create                        (L189)  — 属性正确设置
#     test_export_xml                    (L198)  — export 输出有效 XML 片段（标签名 proprio）
#   TestMuscleConcentrationModel2        (L211)  — MuscleConcentrationModel2 创建和 export 测试
#     test_create                        (L214)  — 属性正确设置
#     test_export_xml                    (L225)  — export 输出有效 XML 片段
#   TestCellW2D                          (L242)  — CellW2D 创建测试
#     test_create                        (L245)  — 属性正确设置
#   TestOutputSynapse                    (L251)  — OutputSynapse 创建测试
#     test_create                        (L254)  — 属性正确设置
#
# 更新日志：
#   2026-04-18  Copilot  计划4阶段二：自定义组件类型测试
#   2026-04-19  Copilot  计划4阶段八：补充 C2/W2D 自定义类型测试
#
# 当前维护者：Copilot
# =============================================================================
"""自定义组件类型单元测试。"""
import io

from c302.parameters.custom_types import (
    CellW2D,
    DelayedGapJunction,
    GradedSynapse2,
    IafActivityCell,
    MuscleConcentrationModel2,
    NeuronMuscle,
    OutputSynapse,
    ProprioGapJunction,
    ProprioGapJunction2,
)


class TestIafActivityCell:
    """IafActivityCell 创建和 export 测试。"""

    def test_create(self):
        """属性正确设置。"""
        cell = IafActivityCell(
            id="test_cell", C="3pF", thresh="-30mV", reset="-50mV",
            leak_conductance="0.1nS", leak_reversal="-50mV", tau1="10ms",
        )
        assert cell.id == "test_cell"
        assert cell.C == "3pF"
        assert cell.tau1 == "10ms"

    def test_export_xml(self):
        """export 输出有效 XML 片段。"""
        cell = IafActivityCell(
            id="test_cell", C="3pF", thresh="-30mV", reset="-50mV",
            leak_conductance="0.1nS", leak_reversal="-50mV", tau1="10ms",
        )
        buf = io.StringIO()
        cell.export(buf, level=0, namespace="", name_="iafActivityCell")
        xml = buf.getvalue()
        assert "iafActivityCell" in xml
        assert 'id="test_cell"' in xml
        assert 'tau1="10ms"' in xml


class TestGradedSynapse2:
    """GradedSynapse2 创建和 export 测试。"""

    def test_create(self):
        """属性正确设置。"""
        syn = GradedSynapse2(
            id="test_syn", conductance="1nS", ar="0.5",
            ad="0.1", beta="0.125", vth="-35mV", erev="0mV",
        )
        assert syn.id == "test_syn"
        assert syn.conductance == "1nS"
        assert syn.erev == "0mV"

    def test_export_xml(self):
        """export 输出有效 XML 片段。"""
        syn = GradedSynapse2(
            id="test_syn", conductance="1nS", ar="0.5",
            ad="0.1", beta="0.125", vth="-35mV", erev="0mV",
        )
        buf = io.StringIO()
        syn.export(buf, level=0, namespace="", name_="gradedSynapse2")
        xml = buf.getvalue()
        assert "gradedSynapse2" in xml
        assert 'id="test_syn"' in xml
        assert 'conductance="1nS"' in xml

    def test_export_indentation(self):
        """export 的缩进级别正确。"""
        syn = GradedSynapse2(
            id="s", conductance="1nS", ar="0.5",
            ad="0.1", beta="0.125", vth="-35mV", erev="0mV",
        )
        buf = io.StringIO()
        syn.export(buf, level=2, namespace="", name_="gradedSynapse2")
        xml = buf.getvalue()
        # level=2 → 8 个空格缩进
        assert xml.startswith("        <")


class TestDelayedGapJunction:
    """DelayedGapJunction 创建和 export 测试。"""

    def test_create(self):
        """属性正确设置。"""
        gj = DelayedGapJunction(
            id="dgj1", conductance="0.5nS", sigma="0.3 per_mV", mu="10 ms",
        )
        assert gj.id == "dgj1"
        assert gj.weight == 1  # 默认值
        assert gj.sigma == "0.3 per_mV"

    def test_export_xml(self):
        """export 输出有效 XML 片段。"""
        gj = DelayedGapJunction(
            id="dgj1", conductance="0.5nS", sigma="0.3 per_mV",
            mu="10 ms", weight=2,
        )
        buf = io.StringIO()
        gj.export(buf, level=0, namespace="", name_="delayedGapJunction")
        xml = buf.getvalue()
        assert "delayedGapJunction" in xml
        assert 'id="dgj1"' in xml
        assert 'sigma="0.3 per_mV"' in xml
        assert 'weight="2"' in xml


class TestProprioGapJunction:
    """ProprioGapJunction 创建和 export 测试。"""

    def test_create(self):
        """属性正确设置。"""
        gj = ProprioGapJunction(
            id="pgj1", conductance="0.5nS", p_conductance="0.1nS",
            mu="10 ms",
        )
        assert gj.id == "pgj1"
        assert gj.sigma == "0.3 per_mV"  # 默认值

    def test_export_xml(self):
        """export 输出有效 XML 片段。"""
        gj = ProprioGapJunction(
            id="pgj1", conductance="0.5nS", p_conductance="0.1nS",
            mu="10 ms", sigma="0.5 per_mV",
        )
        buf = io.StringIO()
        gj.export(buf, level=0, namespace="", name_="proprioGapJunction")
        xml = buf.getvalue()
        assert "proprioGapJunction" in xml
        assert 'p_conductance="0.1nS"' in xml


class TestProprioGapJunction2:
    """ProprioGapJunction2 创建和 export 测试。"""

    def test_create(self):
        """属性正确设置（含门控参数）。"""
        gj = ProprioGapJunction2(
            id="pgj2", conductance="0.5nS", p_conductance="0.1nS",
            mu="10 ms", ar="0.5", ad="0.1", beta="0.125",
            vth="-35mV", erev="0mV",
        )
        assert gj.id == "pgj2"
        assert gj.ar == "0.5"
        assert gj.erev == "0mV"

    def test_export_xml(self):
        """export 输出有效 XML 片段。"""
        gj = ProprioGapJunction2(
            id="pgj2", conductance="0.5nS", p_conductance="0.1nS",
            mu="10 ms", ar="0.5", ad="0.1", beta="0.125",
            vth="-35mV", erev="0mV",
        )
        buf = io.StringIO()
        gj.export(buf, level=0, namespace="", name_="proprioGapJunction2")
        xml = buf.getvalue()
        assert "proprioGapJunction2" in xml
        assert 'ar="0.5"' in xml
        assert 'erev="0mV"' in xml


class TestNeuronMuscle:
    """NeuronMuscle 创建和 export 测试。"""

    def test_create(self):
        """属性正确设置。"""
        nm = NeuronMuscle(
            id="nm1", conductance="1nS", ar="0.5", ad="0.1",
            beta="0.125", cath="0.5", erev="0mV",
        )
        assert nm.id == "nm1"
        assert nm.cath == "0.5"

    def test_export_xml(self):
        """export 输出有效 XML 片段（标签名 proprio）。"""
        nm = NeuronMuscle(
            id="nm1", conductance="1nS", ar="0.5", ad="0.1",
            beta="0.125", cath="0.5", erev="0mV",
        )
        buf = io.StringIO()
        nm.export(buf, level=0, namespace="", name_="proprio")
        xml = buf.getvalue()
        assert "proprio" in xml
        assert 'cath="0.5"' in xml


class TestMuscleConcentrationModel2:
    """MuscleConcentrationModel2 创建和 export 测试。"""

    def test_create(self):
        """属性正确设置。"""
        mcm = MuscleConcentrationModel2(
            id="CaPoolMuscle", ion="ca", resting_conc="0 mM",
            decay_constant="11.5 ms", rho="0.002 mol_per_m_per_A_per_s",
            xRho="0.001", xrest="0.5",
        )
        assert mcm.id == "CaPoolMuscle"
        assert mcm.xRho == "0.001"
        assert mcm.xrest == "0.5"

    def test_export_xml(self):
        """export 输出有效 XML 片段。"""
        mcm = MuscleConcentrationModel2(
            id="CaPoolMuscle", ion="ca", resting_conc="0 mM",
            decay_constant="11.5 ms", rho="0.002 mol_per_m_per_A_per_s",
            xRho="0.001", iCaSigmoidMid="-25 mV", iCaSigmoidSlope="0.1",
            xSigmoidMid="0.5", xSigmoidSlope="10", xDecay="100 ms",
            xrest="0.5",
        )
        buf = io.StringIO()
        mcm.export(buf, level=0, namespace="", name_="muscleConcentrationModel2")
        xml = buf.getvalue()
        assert "muscleConcentrationModel2" in xml
        assert 'xRho="0.001"' in xml
        assert 'xDecay="100 ms"' in xml


class TestCellW2D:
    """CellW2D 创建测试。"""

    def test_create(self):
        """属性正确设置。"""
        cell = CellW2D(id="w2d_cell")
        assert cell.id == "w2d_cell"


class TestOutputSynapse:
    """OutputSynapse 创建测试。"""

    def test_create(self):
        """属性正确设置。"""
        syn = OutputSynapse(id="out_syn")
        assert syn.id == "out_syn"
