# =============================================================================
# 功能描述：
#   readers/base.py 的单元测试：ConnectionInfo 数据类、常量加载、
#   细胞类型判断函数、名称规范化函数。
#
# 类与方法索引：
#   TestConnectionInfo                   (L26)   — ConnectionInfo 数据类测试
#   TestConnectionInfoOrdering           (L76)   — ConnectionInfo 排序测试
#   TestNeuronsConstant                  (L90)   — NEURONS 常量测试
#   TestMusclesConstant                  (L104)  — MUSCLES 常量测试
#   TestConvertToPreferredMuscleName     (L118)  — 肌肉名称转换测试
#   TestIsMuscle                         (L139)  — is_muscle 判断测试
#   TestIsBodyWallMuscle                 (L153)  — is_body_wall_muscle 判断测试
#   TestIsNeuron                         (L167)  — is_neuron 判断测试
#   TestRemoveLeadingIndexZero           (L181)  — 前导零去除测试
#   TestCheckNeurons                     (L195)  — check_neurons 三路比对测试
#
# 更新日志：
#   2026-04-17  yi  初始创建
#
# 当前维护者：yi
# =============================================================================
"""readers/base.py 的单元测试。"""
import pytest

from c302.readers.base import (
    MUSCLES,
    NEURONS,
    BaseDataReader,
    ConnectionInfo,
    analyse_connections,
    check_neurons,
    convert_to_preferred_muscle_name,
    is_body_wall_muscle,
    is_muscle,
    is_neuron,
    remove_leading_index_zero,
)


class TestConnectionInfo:
    """ConnectionInfo 数据类测试。"""

    def test_create(self):
        """创建连接记录。"""
        ci = ConnectionInfo("AVAL", "AVAR", 3, "Send", "Acetylcholine")
        assert ci.pre_cell == "AVAL"
        assert ci.post_cell == "AVAR"
        assert ci.number == 3
        assert ci.syntype == "Send"
        assert ci.synclass == "Acetylcholine"

    def test_str(self):
        """格式化输出。"""
        ci = ConnectionInfo("AVAL", "AVAR", 3, "Send", "Acetylcholine")
        s = str(ci)
        assert "AVAL" in s
        assert "AVAR" in s
        assert "3" in s

    def test_short(self):
        """简短输出。"""
        ci = ConnectionInfo("AVAL", "AVAR", 3, "Send", "Acetylcholine")
        s = ci.short()
        assert "AVAL" in s
        assert "Send" in s

    def test_eq(self):
        """相等比较。"""
        ci1 = ConnectionInfo("AVAL", "AVAR", 3, "Send", "Acetylcholine")
        ci2 = ConnectionInfo("AVAL", "AVAR", 3, "Send", "Acetylcholine")
        assert ci1 == ci2

    def test_neq(self):
        """不等比较。"""
        ci1 = ConnectionInfo("AVAL", "AVAR", 3, "Send", "Acetylcholine")
        ci2 = ConnectionInfo("AVAL", "AVAR", 5, "Send", "Acetylcholine")
        assert ci1 != ci2

    def test_repr(self):
        """repr 输出。"""
        ci = ConnectionInfo("AVAL", "AVAR", 3, "Send", "Acetylcholine")
        assert repr(ci) == str(ci)


class TestConnectionInfoOrdering:
    """ConnectionInfo 排序测试。"""

    def test_lt(self):
        """小于比较。"""
        ci1 = ConnectionInfo("AVAL", "AVAR", 3, "Send", "Acetylcholine")
        ci2 = ConnectionInfo("PVCL", "PVCR", 1, "Send", "Acetylcholine")
        assert ci1 < ci2

    def test_sorting(self):
        """列表排序。"""
        ci1 = ConnectionInfo("PVCL", "PVCR", 1, "Send", "Acetylcholine")
        ci2 = ConnectionInfo("AVAL", "AVAR", 3, "Send", "Acetylcholine")
        result = sorted([ci1, ci2])
        assert result[0].pre_cell == "AVAL"


class TestNeuronsConstant:
    """NEURONS 常量测试。"""

    def test_count(self):
        """应有 302 个神经元。"""
        assert len(NEURONS) == 302

    def test_known_neurons(self):
        """包含已知关键神经元。"""
        assert "AVAL" in NEURONS
        assert "AVAR" in NEURONS
        assert "PVCL" in NEURONS

    def test_no_duplicates(self):
        """无重复名称。"""
        assert len(NEURONS) == len(set(NEURONS))


class TestMusclesConstant:
    """MUSCLES 常量测试。"""

    def test_count(self):
        """应有 97 个肌肉名称。"""
        assert len(MUSCLES) == 97

    def test_known_muscles(self):
        """包含已知肌肉。"""
        assert "MDL01" in MUSCLES
        assert "MVR24" in MUSCLES
        assert "MVULVA" in MUSCLES

    def test_no_duplicates(self):
        """无重复名称。"""
        assert len(MUSCLES) == len(set(MUSCLES))


class TestConvertToPreferredMuscleName:
    """肌肉名称转换测试。"""

    def test_bwm_vl(self):
        assert convert_to_preferred_muscle_name("BWM-VL01") == "MVL01"

    def test_bwm_vr(self):
        assert convert_to_preferred_muscle_name("BWM-VR24") == "MVR24"

    def test_bwm_dl(self):
        assert convert_to_preferred_muscle_name("BWM-DL05") == "MDL05"

    def test_bwm_dr(self):
        assert convert_to_preferred_muscle_name("BWM-DR12") == "MDR12"

    def test_legacy(self):
        assert convert_to_preferred_muscle_name("LegacyBodyWallMuscles") == "BWM"

    def test_unknown(self):
        result = convert_to_preferred_muscle_name("UNKNOWN")
        assert result == "UNKNOWN???"


class TestIsMuscle:
    """is_muscle 判断测试。"""

    def test_body_wall_muscle(self):
        assert is_muscle("BWM-DL01") is True

    def test_pharyngeal_muscle(self):
        assert is_muscle("pm1") is True

    def test_neuron(self):
        assert is_muscle("AVAL") is False

    def test_vbwm_prefix(self):
        assert is_muscle("vBWML01") is True


class TestIsBodyWallMuscle:
    """is_body_wall_muscle 判断测试。"""

    def test_bwm_d(self):
        assert is_body_wall_muscle("BWM-DL01") is True

    def test_pharyngeal_not_body_wall(self):
        assert is_body_wall_muscle("pm1") is False

    def test_neuron(self):
        assert is_body_wall_muscle("AVAL") is False


class TestIsNeuron:
    """is_neuron 判断测试。"""

    def test_neuron(self):
        assert is_neuron("AVAL") is True

    def test_body_wall_muscle(self):
        assert is_neuron("BWM-DL01") is False

    def test_pharyngeal_is_neuron(self):
        """咽部肌肉不是体壁肌肉，所以 is_neuron 返回 True。"""
        assert is_neuron("pm1") is True


class TestRemoveLeadingIndexZero:
    """前导零去除测试。"""

    def test_with_leading_zero(self):
        assert remove_leading_index_zero("VB01") == "VB1"

    def test_without_leading_zero(self):
        assert remove_leading_index_zero("VB1") == "VB1"

    def test_two_digit_no_zero(self):
        assert remove_leading_index_zero("VB11") == "VB11"

    def test_muscle_unchanged(self):
        """体壁肌肉不受影响。"""
        assert remove_leading_index_zero("BWM-DL01") == "BWM-DL01"


class TestCheckNeurons:
    """check_neurons 三路比对测试。"""

    def test_all_preferred(self):
        """全部是标准神经元。"""
        cells = ["AVAL", "AVAR"]
        preferred, not_in, missing = check_neurons(cells)
        assert preferred == ["AVAL", "AVAR"]
        assert not_in == []
        assert "AVAL" not in missing
        assert "AVAR" not in missing

    def test_with_non_neuron(self):
        """包含非神经元。"""
        cells = ["AVAL", "BWM-DL01"]
        preferred, not_in, missing = check_neurons(cells)
        assert "BWM-DL01" in not_in

    def test_missing_preferred(self):
        """少数标准神经元缺失。"""
        cells = ["AVAL"]
        preferred, not_in, missing = check_neurons(cells)
        assert len(missing) == 301  # 302 - 1
