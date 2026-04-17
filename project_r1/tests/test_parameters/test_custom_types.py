# =============================================================================
# 功能描述：
#   自定义组件类型（custom_types.py）单元测试。
#   测试 IafActivityCell 和 GradedSynapse2 的创建和 XML export。
#
# 类与方法索引：
#   TestIafActivityCell                  (L18)  — IafActivityCell 测试
#   TestGradedSynapse2                   (L46)  — GradedSynapse2 测试
#
# 更新日志：
#   2026-04-18  Copilot  计划4阶段二：自定义组件类型测试
#
# 当前维护者：Copilot
# =============================================================================
"""自定义组件类型单元测试。"""
import io

from c302.parameters.custom_types import GradedSynapse2, IafActivityCell


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
