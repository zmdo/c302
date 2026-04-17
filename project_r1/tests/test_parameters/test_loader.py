# =============================================================================
# 功能描述：
#   ParameterLoader 和参数集注册表的单元测试。
#   验证 YAML 加载、继承、缓存及所有 10 个层级参数的正确性。
#
# 类与方法索引：
#   TestParameterLoader                  (L48)   — ParameterLoader 加载与继承测试
#     setup_method                       (L51)   — 每个测试使用新加载器（无缓存干扰）
#     test_load_raw_returns_dict         (L55)   — load_raw 返回 YAML 字典
#     test_load_raw_cache                (L63)   — 同一层级只读取一次（缓存）
#     test_load_parameters_returns_bioparameters (L69)   — load_parameters 返回 BioParameter 列表
#     test_load_level_a_count            (L75)   — Level A 应有 28 个参数
#     test_load_level_b_inherits_a       (L80)   — Level B 继承 A，结果参数 27 个
#     test_load_level_bc1_count          (L91)   — Level BC1 应有 29 个参数
#     test_load_level_c_count            (L96)   — Level C 应有 35 个参数
#     test_load_level_c_preserves_typo   (L101)  — Level C 保留原始 'Bli ndGuess' 拼写错误
#     test_load_level_c0_count           (L107)  — Level C0 应有 38 个参数
#     test_load_level_c1_inherits_c      (L112)  — Level C1 继承 C，移除 10 个化学突触参数并覆盖 14 个
#     test_load_level_c2_count           (L124)  — Level C2 应有 62 个参数
#     test_load_level_c2_muscle_specific (L129)  — Level C2 拥有肌肉专有参数
#     test_load_level_d_count            (L137)  — Level D 应有 36 个参数
#     test_load_level_d_has_resistivity  (L142)  — Level D 包含 resistivity 参数
#     test_load_level_d1_count           (L148)  — Level D1 应有 41 个参数
#     test_load_level_d1_lower_resistivity (L153)  — Level D1 的 resistivity 低于 D
#     test_load_level_w2d_count          (L159)  — Level W2D 应有 7 个参数
#     test_load_level_w2d_minimal        (L164)  — Level W2D 只含最少参数集
#     test_inheritance_overrides         (L171)  — B 继承 A 后覆盖 neuron_iaf_tau1
#     test_inheritance_removals_wildcard (L177)  — B 继承 A，通配符移除 elec_syn_* 中 gbase 以外的参数
#   TestParameterSetRegistry             (L188)  — 参数集注册表测试
#     test_list_parameter_sets           (L191)  — 列出所有已实现的层级
#     test_get_parameter_set             (L202)  — 按名称获取参数集，返回 c302ModelPrototype 实例
#     test_get_parameter_set_case_insensitive (L210)  — 大小写不敏感
#     test_get_parameter_set_unknown     (L215)  — 未知层级抛出 KeyError
#     test_all_levels_loadable           (L220)  — 所有注册层级都可加载
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段三：新建加载器单元测试
#
# 当前维护者：Copilot
# =============================================================================
import pytest

from c302.parameters.bio import BioParameter
from c302.parameters.loader import ParameterLoader
from c302.parameters import get_parameter_set, list_parameter_sets


class TestParameterLoader:
    """ParameterLoader 加载与继承测试。"""

    def setup_method(self):
        """每个测试使用新加载器（无缓存干扰）。"""
        self.loader = ParameterLoader()

    def test_load_raw_returns_dict(self):
        """load_raw 返回 YAML 字典。"""
        data = self.loader.load_raw("A")
        assert isinstance(data, dict)
        assert "level" in data
        assert "parameters" in data
        assert data["level"] == "A"

    def test_load_raw_cache(self):
        """同一层级只读取一次（缓存）。"""
        d1 = self.loader.load_raw("A")
        d2 = self.loader.load_raw("A")
        assert d1 is d2

    def test_load_parameters_returns_bioparameters(self):
        """load_parameters 返回 BioParameter 列表。"""
        params = self.loader.load_parameters("A")
        assert isinstance(params, list)
        assert all(isinstance(p, BioParameter) for p in params)

    def test_load_level_a_count(self):
        """Level A 应有 28 个参数。"""
        params = self.loader.load_parameters("A")
        assert len(params) == 28

    def test_load_level_b_inherits_a(self):
        """Level B 继承 A，结果参数 27 个。"""
        params = self.loader.load_parameters("B")
        names = [p.name for p in params]
        # A(28) + 2 new tau1 - 3 event-only removals(erev/rise/decay) = 27
        assert len(params) == 27
        # 验证移除的参数不在列表中
        assert "elec_syn_erev" not in names
        assert "elec_syn_rise" not in names
        assert "elec_syn_decay" not in names

    def test_load_level_bc1_count(self):
        """Level BC1 应有 29 个参数。"""
        params = self.loader.load_parameters("BC1")
        assert len(params) == 29

    def test_load_level_c_count(self):
        """Level C 应有 35 个参数。"""
        params = self.loader.load_parameters("C")
        assert len(params) == 35

    def test_load_level_c_preserves_typo(self):
        """Level C 保留原始 'Bli ndGuess' 拼写错误。"""
        params = self.loader.load_parameters("C")
        chem_exc_rise = next(p for p in params if p.name == "chem_exc_syn_rise")
        assert "Bli ndGuess" in chem_exc_rise.source

    def test_load_level_c0_count(self):
        """Level C0 应有 38 个参数。"""
        params = self.loader.load_parameters("C0")
        assert len(params) == 38

    def test_load_level_c1_inherits_c(self):
        """Level C1 继承 C，移除 10 个化学突触参数并覆盖 14 个。"""
        params = self.loader.load_parameters("C1")
        names = [p.name for p in params]
        # C(35) + 12 new overrides + 2 gbase replaces - 10 chem_syn removals = 37
        assert len(params) == 37
        # 验证突触参数已被移除
        assert "chem_exc_syn_erev" not in names
        assert "chem_exc_syn_rise" not in names
        # 验证 GradedSynapse 参数存在
        assert "neuron_to_neuron_exc_syn_conductance" in names

    def test_load_level_c2_count(self):
        """Level C2 应有 62 个参数。"""
        params = self.loader.load_parameters("C2")
        assert len(params) == 62

    def test_load_level_c2_muscle_specific(self):
        """Level C2 拥有肌肉专有参数。"""
        params = self.loader.load_parameters("C2")
        names = [p.name for p in params]
        assert "muscle_initial_memb_pot" in names
        assert "muscle_specific_capacitance" in names
        assert "muscle_leak_erev" in names

    def test_load_level_d_count(self):
        """Level D 应有 36 个参数。"""
        params = self.loader.load_parameters("D")
        assert len(params) == 36

    def test_load_level_d_has_resistivity(self):
        """Level D 包含 resistivity 参数。"""
        params = self.loader.load_parameters("D")
        res = next(p for p in params if p.name == "resistivity")
        assert "12 kohm_cm" in res.value

    def test_load_level_d1_count(self):
        """Level D1 应有 41 个参数。"""
        params = self.loader.load_parameters("D1")
        assert len(params) == 41

    def test_load_level_d1_lower_resistivity(self):
        """Level D1 的 resistivity 低于 D。"""
        params = self.loader.load_parameters("D1")
        res = next(p for p in params if p.name == "resistivity")
        assert "3 kohm_cm" in res.value

    def test_load_level_w2d_count(self):
        """Level W2D 应有 7 个参数。"""
        params = self.loader.load_parameters("W2D")
        assert len(params) == 7

    def test_load_level_w2d_minimal(self):
        """Level W2D 只含最少参数集。"""
        params = self.loader.load_parameters("W2D")
        names = {p.name for p in params}
        assert "initial_memb_pot" in names
        assert "neuron_to_neuron_elec_syn_gbase" in names

    def test_inheritance_overrides(self):
        """B 继承 A 后覆盖 neuron_iaf_tau1。"""
        params = self.loader.load_parameters("B")
        gbase = next(p for p in params if p.name == "neuron_iaf_tau1")
        assert gbase.value == "50ms"

    def test_inheritance_removals_wildcard(self):
        """B 继承 A，通配符移除 elec_syn_* 中 gbase 以外的参数。"""
        params_a = self.loader.load_parameters("A")
        params_b = self.loader.load_parameters("B")
        a_names = {p.name for p in params_a}
        b_names = {p.name for p in params_b}
        # A 中有 elec_syn_erev 等，B 中不应有
        assert "elec_syn_erev" in a_names
        assert "elec_syn_erev" not in b_names


class TestParameterSetRegistry:
    """参数集注册表测试。"""

    def test_list_parameter_sets(self):
        """列出所有已实现的层级。"""
        levels = list_parameter_sets()
        assert len(levels) == 10
        assert "A" in levels
        assert "BC1" in levels
        assert "C0" in levels
        assert "C2" in levels
        assert "D1" in levels
        assert "W2D" in levels

    def test_get_parameter_set(self):
        """按名称获取参数集，返回 c302ModelPrototype 实例。"""
        params = get_parameter_set("A")
        # 现在返回 c302ModelPrototype 实例
        assert hasattr(params, "bioparameters")
        assert len(params.bioparameters) == 28
        assert params.level == "A"

    def test_get_parameter_set_case_insensitive(self):
        """大小写不敏感。"""
        params = get_parameter_set("a")
        assert len(params.bioparameters) == 28

    def test_get_parameter_set_unknown(self):
        """未知层级抛出 KeyError。"""
        with pytest.raises(KeyError, match="未知的参数层级"):
            get_parameter_set("Z")

    def test_all_levels_loadable(self):
        """所有注册层级都可加载。"""
        for level in list_parameter_sets():
            params = get_parameter_set(level)
            assert len(params.bioparameters) > 0, f"Level {level} has no parameters"
