"""BioParameter 数据类及 split_neuroml_quantity 工具函数的单元测试。"""
import pytest

from c302.parameters.bio import BioParameter, split_neuroml_quantity


class TestSplitNeuromlQuantity:
    """split_neuroml_quantity() 测试。"""

    def test_with_space(self):
        """含空格的标准格式。"""
        mag, unit = split_neuroml_quantity("0.01 nS")
        assert mag == pytest.approx(0.01)
        assert unit == "nS"

    def test_without_space(self):
        """无空格的紧凑格式。"""
        mag, unit = split_neuroml_quantity("-50mV")
        assert mag == pytest.approx(-50.0)
        assert unit == "mV"

    def test_scientific_notation(self):
        """科学计数法。"""
        mag, unit = split_neuroml_quantity("5e-7 S_per_cm2")
        assert mag == pytest.approx(5e-7)
        assert unit == "S_per_cm2"

    def test_compound_unit(self):
        """复合单位。"""
        mag, unit = split_neuroml_quantity("0.000238919 mol_per_m_per_A_per_s")
        assert mag == pytest.approx(0.000238919)
        assert unit == "mol_per_m_per_A_per_s"

    def test_integer(self):
        """纯整数值。"""
        mag, unit = split_neuroml_quantity("5")
        assert mag == pytest.approx(5.0)
        assert unit == ""

    def test_no_space_unit(self):
        """无空格带单位。"""
        mag, unit = split_neuroml_quantity("3pF")
        assert mag == pytest.approx(3.0)
        assert unit == "pF"

    def test_zero(self):
        """零值。"""
        mag, unit = split_neuroml_quantity("0nS")
        assert mag == pytest.approx(0.0)
        assert unit == "nS"

    def test_leading_dot(self):
        """以小数点开头。"""
        mag, unit = split_neuroml_quantity(".1 nS")
        assert mag == pytest.approx(0.1)
        assert unit == "nS"

    def test_per_unit(self):
        """per_ 风格单位。"""
        mag, unit = split_neuroml_quantity("0.025per_ms")
        assert mag == pytest.approx(0.025)
        assert unit == "per_ms"

    def test_negative_integer(self):
        """负整数。"""
        mag, unit = split_neuroml_quantity("-30")
        assert mag == pytest.approx(-30.0)
        assert unit == ""


class TestBioParameter:
    """BioParameter 类测试。"""

    def test_creation(self):
        """创建参数对象。"""
        bp = BioParameter("neuron_iaf_thresh", "-30mV", "BlindGuess", "0.1")
        assert bp.name == "neuron_iaf_thresh"
        assert bp.value == "-30mV"
        assert bp.source == "BlindGuess"
        assert bp.certainty == "0.1"

    def test_str(self):
        """字符串表示。"""
        bp = BioParameter("test_param", "1 nS", "Experimental", "0.8")
        s = str(bp)
        assert "test_param" in s
        assert "1 nS" in s
        assert "Experimental" in s
        assert "0.8" in s

    def test_repr(self):
        """repr 与 str 一致。"""
        bp = BioParameter("test_param", "1 nS", "Experimental", "0.8")
        assert repr(bp) == str(bp)

    def test_x_with_unit(self):
        """提取数值部分（含单位）。"""
        bp = BioParameter("test", "-50mV", "BlindGuess", "0.1")
        assert bp.x() == pytest.approx(-50.0)

    def test_x_with_space(self):
        """提取数值部分（含空格）。"""
        bp = BioParameter("test", "0.01 nS", "BlindGuess", "0.1")
        assert bp.x() == pytest.approx(0.01)

    def test_x_no_unit(self):
        """提取数值部分（无单位）。"""
        bp = BioParameter("test", "5", "BlindGuess", "0.1")
        assert bp.x() == pytest.approx(5.0)

    def test_x_scientific(self):
        """提取科学计数法数值。"""
        bp = BioParameter("test", "5e-7 S_per_cm2", "BlindGuess", "0.1")
        assert bp.x() == pytest.approx(5e-7)

    def test_change_magnitude(self):
        """修改数值，保留单位。"""
        bp = BioParameter("test", "0.01 nS", "BlindGuess", "0.1")
        bp.change_magnitude("0.02")
        assert "nS" in bp.value
        assert bp.x() == pytest.approx(0.02)

    def test_change_magnitude_preserves_unit(self):
        """修改整数值，保留无单位。"""
        bp = BioParameter("test", "5", "BlindGuess", "0.1")
        bp.change_magnitude("10")
        assert bp.x() == pytest.approx(10.0)

    def test_change_magnitude_negative(self):
        """修改为负数。"""
        bp = BioParameter("test", "-50 mV", "BlindGuess", "0.1")
        bp.change_magnitude("-60")
        assert bp.x() == pytest.approx(-60.0)
        assert "mV" in bp.value
