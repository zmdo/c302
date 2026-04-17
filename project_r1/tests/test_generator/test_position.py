# =============================================================================
# 功能描述：
#   3D 位置计算模块的单元测试。覆盖细胞位置加载、肌肉坐标计算、
#   肌肉名称判断和名称列表生成。
#
# 类与方法索引：
#   (由 gen_index.py 生成)
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段四：新建
#
# 当前维护者：Copilot
# =============================================================================
"""position 模块测试。"""
import pytest

from c302.generator.position import (
    DB_SOMA_POS,
    VB_SOMA_POS,
    get_cell_position,
    get_muscle_names,
    get_muscle_position,
    is_body_wall_muscle,
)


class TestGetCellPosition:
    """get_cell_position 测试。"""

    def test_returns_tuple_of_three_floats(self):
        """应返回三元组 (x, y, z)。"""
        pos = get_cell_position("ADAL")
        assert isinstance(pos, tuple)
        assert len(pos) == 3
        assert all(isinstance(v, float) for v in pos)

    def test_different_cells_have_different_positions(self):
        """不同细胞的 soma 位置应不同。"""
        pos1 = get_cell_position("ADAL")
        pos2 = get_cell_position("ADAR")
        # 至少有一个坐标不同（左右对称细胞 x 或 z 通常相反）
        assert pos1 != pos2

    def test_nonexistent_cell_raises(self):
        """不存在的细胞文件应抛出异常。"""
        with pytest.raises(Exception):
            get_cell_position("NONEXISTENT_CELL_XYZ")


class TestGetMusclePosition:
    """get_muscle_position 测试。"""

    def test_standard_muscle_mdl01(self):
        """MDL01 应返回 (80, -270, 80)。"""
        x, y, z = get_muscle_position("MDL01")
        assert x == 80.0  # L → 正 x
        assert y == -270.0  # -300 + 30*1
        assert z == 80.0  # D → 正 z

    def test_standard_muscle_mvr12(self):
        """MVR12 应返回 (-80, 60, -80)。"""
        x, y, z = get_muscle_position("MVR12")
        assert x == -80.0  # R → 负 x
        assert y == 60.0  # -300 + 30*12
        assert z == -80.0  # V → 负 z

    def test_special_muscle_manal(self):
        """MANAL 返回原点。"""
        assert get_muscle_position("MANAL") == (0.0, 0.0, 0.0)

    def test_special_muscle_mvulva(self):
        """MVULVA 返回原点。"""
        assert get_muscle_position("MVULVA") == (0.0, 0.0, 0.0)

    def test_alternate_format_vl10(self):
        """无 M 前缀格式 VL10 也应正常解析。"""
        x, y, z = get_muscle_position("VL10")
        assert x == 80.0  # L → 正 x
        assert y == 0.0  # -300 + 30*10
        assert z == -80.0  # V → 负 z

    def test_unrecognized_raises(self):
        """无法识别的肌肉名称应抛出 ValueError。"""
        with pytest.raises(ValueError, match="无法识别"):
            get_muscle_position("TOTALLY_UNKNOWN")


class TestIsBodyWallMuscle:
    """is_body_wall_muscle 测试。"""

    def test_standard_muscles(self):
        """标准体壁肌肉名称应返回 True。"""
        assert is_body_wall_muscle("MDR01") is True
        assert is_body_wall_muscle("MVL24") is True

    def test_neurons_are_not_muscles(self):
        """神经元名称应返回 False。"""
        assert is_body_wall_muscle("ADAL") is False
        assert is_body_wall_muscle("VB1") is False

    def test_special_muscles_not_matching_pattern(self):
        """MANAL/MVULVA 不匹配体壁肌肉正则。"""
        assert is_body_wall_muscle("MANAL") is False
        assert is_body_wall_muscle("MVULVA") is False


class TestGetMuscleNames:
    """get_muscle_names 测试。"""

    def test_returns_96_names(self):
        """应返回 96 个肌肉名称。"""
        names = get_muscle_names()
        assert len(names) == 96

    def test_quadrant_distribution(self):
        """每个象限应有 24 个肌肉。"""
        names = get_muscle_names()
        for prefix in ("MDR", "MVR", "MVL", "MDL"):
            count = sum(1 for n in names if n.startswith(prefix))
            assert count == 24, f"{prefix} count = {count}"

    def test_padding(self):
        """1-9 应补零，10-24 不补零。"""
        names = get_muscle_names()
        assert "MDR01" in names
        assert "MDR09" in names
        assert "MDR10" in names
        assert "MDR24" in names

    def test_no_duplicates(self):
        """不应有重复名称。"""
        names = get_muscle_names()
        assert len(names) == len(set(names))


class TestSomaPositionDicts:
    """VB/DB soma 位置字典测试。"""

    def test_vb_has_11_entries(self):
        """VB_SOMA_POS 应有 11 个条目。"""
        assert len(VB_SOMA_POS) == 11

    def test_db_has_7_entries(self):
        """DB_SOMA_POS 应有 7 个条目。"""
        assert len(DB_SOMA_POS) == 7

    def test_values_are_floats_in_range(self):
        """所有位置值应在 [0, 1] 范围内。"""
        for v in VB_SOMA_POS.values():
            assert 0.0 <= v <= 1.0
        for v in DB_SOMA_POS.values():
            assert 0.0 <= v <= 1.0
