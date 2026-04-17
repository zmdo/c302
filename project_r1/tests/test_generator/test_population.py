# =============================================================================
# 功能描述：
#   种群创建模块的单元测试。覆盖 get_cell_id_string、is_cond_based_cell、
#   以及种群创建的核心逻辑。
#
# 类与方法索引：
#   _FakeParams                          (L39)   — 用于测试的模拟参数对象
#     __init__                           (L42)   — __init__ 函数
#     is_level_D                         (L49)   — is_level_D 函数
#     is_level_C                         (L52)   — is_level_C 函数
#     is_level_A                         (L55)   — is_level_A 函数
#     is_level_B                         (L58)   — is_level_B 函数
#   TestGetCellIdString                  (L62)   — get_cell_id_string 测试
#     test_neuron_non_d_level            (L65)   — 非 D 级神经元应使用 generic_neuron_cell.id
#     test_muscle_non_d_level            (L71)   — 非 D 级肌肉应使用 generic_muscle_cell.id
#     test_neuron_d_level                (L77)   — D 级神经元应使用细胞名本身
#     test_muscle_d_level                (L83)   — D 级肌肉仍使用 generic_muscle_cell.id
#     test_auto_detect_muscle            (L89)   — 体壁肌肉名称应自动检测为肌肉
#   TestIsCondBasedCell                  (L97)   — is_cond_based_cell 测试
#     test_level_a_not_cond_based        (L100)  — A 级不是导电模型
#     test_level_b_not_cond_based        (L104)  — B 级不是导电模型
#     test_level_c_is_cond_based         (L108)  — C 级是导电模型
#     test_level_d_is_cond_based         (L112)  — D 级是导电模型
#     test_level_c0_is_cond_based        (L116)  — C0 级是导电模型
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段四：新建
#
# 当前维护者：Copilot
# =============================================================================
"""population 模块测试。"""
from unittest.mock import MagicMock

import pytest

from c302.generator.population import get_cell_id_string, is_cond_based_cell


class _FakeParams:
    """用于测试的模拟参数对象。"""

    def __init__(self, level: str = "A"):
        self.level = level
        self.generic_neuron_cell = MagicMock()
        self.generic_neuron_cell.id = "generic_iaf_cell"
        self.generic_muscle_cell = MagicMock()
        self.generic_muscle_cell.id = "generic_iaf_muscle"

    def is_level_D(self):
        return self.level.startswith("D")

    def is_level_C(self):
        return self.level.startswith("C")

    def is_level_A(self):
        return self.level.startswith("A")

    def is_level_B(self):
        return self.level.startswith("B")


class TestGetCellIdString:
    """get_cell_id_string 测试。"""

    def test_neuron_non_d_level(self):
        """非 D 级神经元应使用 generic_neuron_cell.id。"""
        params = _FakeParams("A")
        result = get_cell_id_string("ADAL", params)
        assert result == "../ADAL/0/generic_iaf_cell"

    def test_muscle_non_d_level(self):
        """非 D 级肌肉应使用 generic_muscle_cell.id。"""
        params = _FakeParams("A")
        result = get_cell_id_string("MDR01", params, muscle=True)
        assert result == "../MDR01/0/generic_iaf_muscle"

    def test_neuron_d_level(self):
        """D 级神经元应使用细胞名本身。"""
        params = _FakeParams("D")
        result = get_cell_id_string("ADAL", params)
        assert result == "../ADAL/0/ADAL"

    def test_muscle_d_level(self):
        """D 级肌肉仍使用 generic_muscle_cell.id。"""
        params = _FakeParams("D")
        result = get_cell_id_string("MDR01", params, muscle=True)
        assert result == "../MDR01/0/generic_iaf_muscle"

    def test_auto_detect_muscle(self):
        """体壁肌肉名称应自动检测为肌肉。"""
        params = _FakeParams("A")
        # MDR01 在 get_muscle_names() 中，应自动设为 muscle=True
        result = get_cell_id_string("MDR01", params)
        assert result == "../MDR01/0/generic_iaf_muscle"


class TestIsCondBasedCell:
    """is_cond_based_cell 测试。"""

    def test_level_a_not_cond_based(self):
        """A 级不是导电模型。"""
        assert is_cond_based_cell(_FakeParams("A")) is False

    def test_level_b_not_cond_based(self):
        """B 级不是导电模型。"""
        assert is_cond_based_cell(_FakeParams("B")) is False

    def test_level_c_is_cond_based(self):
        """C 级是导电模型。"""
        assert is_cond_based_cell(_FakeParams("C")) is True

    def test_level_d_is_cond_based(self):
        """D 级是导电模型。"""
        assert is_cond_based_cell(_FakeParams("D")) is True

    def test_level_c0_is_cond_based(self):
        """C0 级是导电模型。"""
        assert is_cond_based_cell(_FakeParams("C0")) is True
