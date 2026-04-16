# =============================================================================
# 功能描述：
#   ParameterisedModelPrototype 和 c302ModelPrototype 的单元测试。
#   覆盖参数管理、层级判断、连接参数查找等场景。
#
# 类与方法索引：
#   TestParameterisedModelPrototype      (L47)   — ParameterisedModelPrototype 参数管理测试
#     test_init_empty                    (L50)   — 初始化时参数列表为空
#     test_add_bioparameter_new          (L55)   — 添加新参数
#     test_add_bioparameter_update       (L63)   — 同名参数就地更新
#     test_add_bioparameter_obj          (L72)   — 直接注册 BioParameter 对象
#     test_add_bioparameter_obj_replace  (L80)   — 同名 BioParameter 对象替换旧对象
#     test_get_bioparameter_found        (L89)   — 按名称找到参数
#     test_get_bioparameter_not_found    (L97)   — 按名称未找到返回 None
#     test_get_bioparameter_warn         (L103)  — 未找到时打印警告
#     test_set_bioparameter_exists       (L111)  — 更新已有参数
#     test_set_bioparameter_missing      (L119)  — 更新不存在的参数静默忽略
#     test_bioparameter_info             (L125)  — 格式化参数摘要
#     test_multiple_params               (L135)  — 管理多个参数
#   TestC302ModelPrototype               (L144)  — c302ModelPrototype 层级判断和连接参数测试
#     test_default_level                 (L147)  — 默认层级未设置
#     test_is_level_a                    (L153)  — Level A 判断
#     test_is_level_b                    (L161)  — Level B 判断（包含 BC1）
#     test_is_level_c_variants           (L167)  — C 系列层级判断
#     test_is_level_d                    (L178)  — D 系列层级判断
#     test_get_conn_param_default        (L187)  — 连接参数使用默认模板
#     test_get_conn_param_specific       (L199)  — 连接参数使用精确匹配
#     test_get_conn_param_missing        (L212)  — 连接参数均不存在返回 None
#     test_is_nonneuroml_conn            (L222)  — 非 NeuroML 突触判断
#     test_nonneuroml_custom_type_id     (L228)  — NonNeuroMLCustomType 存储 ID
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段三：新建模型层单元测试
#
# 当前维护者：Copilot
# =============================================================================
import pytest

from c302.parameters.bio import BioParameter
from c302.parameters.model import (
    NonNeuroMLCustomType,
    ParameterisedModelPrototype,
    c302ModelPrototype,
)


class TestParameterisedModelPrototype:
    """ParameterisedModelPrototype 参数管理测试。"""

    def test_init_empty(self):
        """初始化时参数列表为空。"""
        m = ParameterisedModelPrototype()
        assert m.bioparameters == []

    def test_add_bioparameter_new(self):
        """添加新参数。"""
        m = ParameterisedModelPrototype()
        m.add_bioparameter("test", "1 nS", "BlindGuess", "0.1")
        assert len(m.bioparameters) == 1
        assert m.bioparameters[0].name == "test"
        assert m.bioparameters[0].value == "1 nS"

    def test_add_bioparameter_update(self):
        """同名参数就地更新。"""
        m = ParameterisedModelPrototype()
        m.add_bioparameter("test", "1 nS", "BlindGuess", "0.1")
        m.add_bioparameter("test", "2 nS", "Updated", "0.5")
        assert len(m.bioparameters) == 1
        assert m.bioparameters[0].value == "2 nS"
        assert m.bioparameters[0].source == "Updated"

    def test_add_bioparameter_obj(self):
        """直接注册 BioParameter 对象。"""
        m = ParameterisedModelPrototype()
        bp = BioParameter("test", "1 nS", "BlindGuess", "0.1")
        m.add_bioparameter_obj(bp)
        assert len(m.bioparameters) == 1
        assert m.bioparameters[0] is bp

    def test_add_bioparameter_obj_replace(self):
        """同名 BioParameter 对象替换旧对象。"""
        m = ParameterisedModelPrototype()
        m.add_bioparameter("test", "1 nS", "BlindGuess", "0.1")
        bp_new = BioParameter("test", "2 nS", "Updated", "0.5")
        m.add_bioparameter_obj(bp_new)
        assert len(m.bioparameters) == 1
        assert m.bioparameters[0] is bp_new

    def test_get_bioparameter_found(self):
        """按名称找到参数。"""
        m = ParameterisedModelPrototype()
        m.add_bioparameter("test", "1 nS", "BlindGuess", "0.1")
        bp = m.get_bioparameter("test")
        assert bp is not None
        assert bp.name == "test"

    def test_get_bioparameter_not_found(self):
        """按名称未找到返回 None。"""
        m = ParameterisedModelPrototype()
        bp = m.get_bioparameter("missing")
        assert bp is None

    def test_get_bioparameter_warn(self, capsys):
        """未找到时打印警告。"""
        m = ParameterisedModelPrototype()
        bp = m.get_bioparameter("missing", warn_if_missing=True)
        assert bp is None
        captured = capsys.readouterr()
        assert "Cannot find bioparameter" in captured.out

    def test_set_bioparameter_exists(self):
        """更新已有参数。"""
        m = ParameterisedModelPrototype()
        m.add_bioparameter("test", "1 nS", "BlindGuess", "0.1")
        m.set_bioparameter("test", "2 nS", "Updated", "0.5")
        bp = m.get_bioparameter("test")
        assert bp.value == "2 nS"

    def test_set_bioparameter_missing(self):
        """更新不存在的参数静默忽略。"""
        m = ParameterisedModelPrototype()
        m.set_bioparameter("missing", "1 nS", "BlindGuess", "0.1")
        assert len(m.bioparameters) == 0

    def test_bioparameter_info(self):
        """格式化参数摘要。"""
        m = ParameterisedModelPrototype()
        m.add_bioparameter("b_param", "1 nS", "BlindGuess", "0.1")
        m.add_bioparameter("a_param", "2 nS", "BlindGuess", "0.1")
        info = m.bioparameter_info()
        assert "Known BioParameters" in info
        # 按字母序 a_param 在 b_param 之前
        assert info.index("a_param") < info.index("b_param")

    def test_multiple_params(self):
        """管理多个参数。"""
        m = ParameterisedModelPrototype()
        m.add_bioparameter("p1", "1 nS", "S1", "0.1")
        m.add_bioparameter("p2", "2 mV", "S2", "0.2")
        m.add_bioparameter("p3", "3 ms", "S3", "0.3")
        assert len(m.bioparameters) == 3


class TestC302ModelPrototype:
    """c302ModelPrototype 层级判断和连接参数测试。"""

    def test_default_level(self):
        """默认层级未设置。"""
        m = c302ModelPrototype()
        assert m.level == "Level not yet set"
        assert m.generic_neuron_cell is None

    def test_is_level_a(self):
        """Level A 判断。"""
        m = c302ModelPrototype()
        m.level = "A"
        assert m.is_level_A()
        assert not m.is_level_B()
        assert not m.is_level_C()

    def test_is_level_b(self):
        """Level B 判断（包含 BC1）。"""
        m = c302ModelPrototype()
        m.level = "BC1"
        assert m.is_level_B()

    def test_is_level_c_variants(self):
        """C 系列层级判断。"""
        m = c302ModelPrototype()
        for level in ["C", "C0", "C1", "C2"]:
            m.level = level
            assert m.is_level_C(), f"{level} should be C"
        m.level = "C0"
        assert m.is_level_C0()
        m.level = "C2"
        assert m.is_level_C2()

    def test_is_level_d(self):
        """D 系列层级判断。"""
        m = c302ModelPrototype()
        m.level = "D"
        assert m.is_level_D()
        m.level = "D1"
        assert m.is_level_D()
        assert m.is_level_D1()

    def test_get_conn_param_default(self):
        """连接参数使用默认模板。"""
        m = c302ModelPrototype()
        m.add_bioparameter("neuron_to_neuron_elec_syn_gbase", "0.01 nS", "S", "0.1")
        val = m.get_conn_param(
            "ADAL", "ADAR",
            "%s_to_%s_%s", "neuron_to_neuron_%s",
            "elec_syn_gbase",
        )
        assert val == "0.01 nS"
        assert not m.found_specific_param

    def test_get_conn_param_specific(self):
        """连接参数使用精确匹配。"""
        m = c302ModelPrototype()
        m.add_bioparameter("neuron_to_neuron_elec_syn_gbase", "0.01 nS", "S", "0.1")
        m.add_bioparameter("ADAL_to_ADAR_elec_syn_gbase", "0.05 nS", "S", "0.1")
        val = m.get_conn_param(
            "ADAL", "ADAR",
            "%s_to_%s_%s", "neuron_to_neuron_%s",
            "elec_syn_gbase",
        )
        assert val == "0.05 nS"
        assert m.found_specific_param

    def test_get_conn_param_missing(self):
        """连接参数均不存在返回 None。"""
        m = c302ModelPrototype()
        val = m.get_conn_param(
            "ADAL", "ADAR",
            "%s_to_%s_%s", "neuron_to_neuron_%s",
            "elec_syn_gbase",
        )
        assert val is None

    def test_is_nonneuroml_conn(self):
        """非 NeuroML 突触判断。"""
        m = c302ModelPrototype()
        custom = NonNeuroMLCustomType("test")
        assert m.is_nonneuroml_conn(custom)

    def test_nonneuroml_custom_type_id(self):
        """NonNeuroMLCustomType 存储 ID。"""
        t = NonNeuroMLCustomType("output_syn")
        assert t.id == "output_syn"
