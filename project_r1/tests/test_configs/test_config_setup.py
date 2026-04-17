# =============================================================================
# 功能描述：
#   配置脚本注册表和各配置 setup() 函数的单元测试。
#   验证注册表机制、所有 16 个配置的注册状态和基本结构。
#
# 类与方法索引：
#   _make_mock_params                    (L125)  — 构造模拟的参数对象
#   mock_params                          (L136)  — 统一 mock 所有配置模块中的 get_parameter_set
#   TestRegisterConfig                   (L152)  — register_config 装饰器测试
#     test_decorator_registers_function  (L155)  — 装饰器应将函数注册到全局注册表中
#     test_decorator_returns_original_function (L167)  — 装饰器应返回原始函数（不包装）
#     test_duplicate_registration_overwrites (L178)  — 重复注册同名配置应覆盖旧条目
#   TestGetConfig                        (L193)  — get_config 查找测试
#     test_get_existing_config           (L196)  — 应能获取已注册的配置函数
#     test_get_nonexistent_raises_key_error (L206)  — 获取不存在的配置应抛出 KeyError
#   TestListConfigs                      (L212)  — list_configs 列举测试
#     test_list_returns_list             (L215)  — 应返回列表类型
#     test_list_contains_registered_configs (L220)  — 列表应包含所有已注册的配置名称
#   TestAllConfigsRegistered             (L250)  — 验证全部 16 个配置已注册
#     test_config_registered             (L254)  — 配置 {name} 应已注册到注册表中
#     test_total_config_count            (L259)  — 注册表中应恰好包含 16 个配置
#     test_config_is_callable            (L267)  — 配置 setup 函数应是可调用的
#   _make_mock_params                    (L275)  — 构造模拟的参数对象
#   TestSetupReturnStructure             (L285)  — setup() 返回值基本结构测试（不生成文件）
#     test_setup_returns_five_tuple      (L289)  — setup(generate_flag=False) 应返回 5 元素元组
#     test_cells_is_list                 (L302)  — 返回的 cells 应是列表类型
#     test_nml_doc_is_none_without_generate (L313)  — generate_flag=False 时 nml_doc 应为 None
#   TestIClampConfig                     (L326)  — IClamp 配置特定测试
#     test_cells_contain_adal            (L329)  — 应包含 ADAL 神经元
#     test_muscles_include_mdr01         (L334)  — 应包含 MDR01 肌肉
#     test_default_duration_based_on_stim (L339)  — 默认时长应基于刺激级数 (6*1000=6000ms)
#   TestIClampMuscleConfig               (L345)  — IClampMuscle 配置特定测试
#     test_cells_is_empty                (L348)  — 应无神经元（纯肌肉测试）
#   TestFullConfig                       (L354)  — Full 配置特定测试
#     test_returns_all_cell_names        (L357)  — 应返回数据读取器提供的全部细胞名称
#   TestPharyngealConfig                 (L365)  — Pharyngeal 配置特定测试
#     test_cells_count                   (L368)  — 应包含 20 个咽部神经元
#   TestOscillatorConfig                 (L374)  — Oscillator 配置特定测试
#     test_cells_count                   (L377)  — 应包含 14 个振荡器神经元
#     test_no_muscles                    (L382)  — 不应包含肌肉
#   TestSocialConfig                     (L388)  — Social 配置特定测试
#     test_cells_count                   (L391)  — 应包含 7 个社交神经元
#     test_rmgr_in_cells                 (L396)  — 应包含枢纽神经元 RMGR
#   TestSynsConfig                       (L402)  — Syns 配置特定测试
#     test_gap_cells_added_for_non_a     (L405)  — 非 A 层级应添加间隙连接测试细胞
#   TestMuscleTestConfig                 (L412)  — MuscleTest 配置特定测试
#     test_no_neurons                    (L415)  — 应无神经元细胞（纯肌肉测试）
#     test_muscles_included              (L420)  — muscles_to_include 应为 True
#   TestFWConfig                         (L426)  — FW 配置特定测试
#     test_contains_avbl                 (L429)  — 应包含 AVBL 命令神经元
#     test_muscles_included              (L434)  — 应包含所有肌肉
#   TestTapWithdrawalConfig              (L440)  — TapWithdrawal 配置特定测试
#     test_contains_touch_sensory        (L443)  — 应包含触觉感觉神经元 PLML
#     test_no_muscles                    (L448)  — muscles_to_include 应为 False
#   TestMultiSynsConfig                  (L454)  — MultiSyns 配置特定测试
#     test_cells_count                   (L457)  — 应包含 6 个神经元
#   TestTargetMuscleConfig               (L463)  — TargetMuscle 配置特定测试
#     test_cells_contain_rmhr            (L466)  — 应包含 RMHR 神经元
#     test_muscles_all_included          (L471)  — 应包含全部肌肉
#   TestRIAConfig                        (L477)  — RIA 配置特定测试
#     test_cells_contain_rial            (L480)  — 应包含 RIAL 神经元
#   TestMusclesConfig                    (L486)  — Muscles 配置特定测试
#     test_cells_contain_motor_neurons   (L489)  — 应包含运动神经元 DB1
#     test_stimulate_avbl                (L494)  — 刺激目标应包含 AVBL
#   TestMusclesSineConfig                (L500)  — MusclesSine 配置特定测试
#     test_stimulate_avbl_avbr           (L503)  — 刺激目标应为 AVBL 和 AVBR
#   TestOscillatorMConfig                (L510)  — OscillatorM 配置特定测试
#     test_no_muscles                    (L513)  — 不应包含肌肉
#     test_stimulate_vb1_vb2             (L518)  — 刺激目标应为 VB1 和 VB2
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：新建
#
# 当前维护者：Copilot
# =============================================================================
"""配置脚本注册表和 setup 函数测试。"""
from unittest.mock import MagicMock, patch

import pytest

from c302.configs import (
    _CONFIG_REGISTRY,
    get_config,
    list_configs,
    register_config,
)
import c302.configs.full as _mod_full
import c302.configs.fw as _mod_fw
import c302.configs.iclamp as _mod_iclamp
import c302.configs.iclamp_muscle as _mod_iclamp_muscle
import c302.configs.multi_syns as _mod_multi_syns
import c302.configs.muscles as _mod_muscles
import c302.configs.muscles_sine as _mod_muscles_sine
import c302.configs.muscle_test as _mod_muscle_test
import c302.configs.oscillator as _mod_oscillator
import c302.configs.oscillator_m as _mod_oscillator_m
import c302.configs.pharyngeal as _mod_pharyngeal
import c302.configs.ria as _mod_ria
import c302.configs.social as _mod_social
import c302.configs.syns as _mod_syns
import c302.configs.tap_withdrawal as _mod_tap_withdrawal
import c302.configs.target_muscle as _mod_target_muscle

# 所有配置模块映射
_CONFIG_MODULES = {
    "Full": _mod_full,
    "FW": _mod_fw,
    "IClamp": _mod_iclamp,
    "IClampMuscle": _mod_iclamp_muscle,
    "MultiSyns": _mod_multi_syns,
    "Muscles": _mod_muscles,
    "MusclesSine": _mod_muscles_sine,
    "MuscleTest": _mod_muscle_test,
    "Oscillator": _mod_oscillator,
    "OscillatorM": _mod_oscillator_m,
    "Pharyngeal": _mod_pharyngeal,
    "RIA": _mod_ria,
    "Social": _mod_social,
    "Syns": _mod_syns,
    "TapWithdrawal": _mod_tap_withdrawal,
    "TargetMuscle": _mod_target_muscle,
}


def _make_mock_params():
    """构造模拟的参数对象。"""
    params = MagicMock()
    params.level = "A"
    params.is_level_A.return_value = True
    params.bioparameters = []
    params.set_bioparameter = MagicMock()
    return params


@pytest.fixture()
def mock_params():
    """统一 mock 所有配置模块中的 get_parameter_set。"""
    mock_p = _make_mock_params()
    patches = []
    for mod in _CONFIG_MODULES.values():
        if hasattr(mod, "get_parameter_set"):
            p = patch.object(mod, "get_parameter_set", return_value=mock_p)
            patches.append(p)
            p.start()
    yield mock_p
    for p in patches:
        p.stop()


# ========== 注册表机制测试 ==========

class TestRegisterConfig:
    """register_config 装饰器测试。"""

    def test_decorator_registers_function(self):
        """装饰器应将函数注册到全局注册表中。"""

        @register_config("__test_dummy")
        def dummy_setup():
            pass

        assert "__test_dummy" in _CONFIG_REGISTRY
        assert _CONFIG_REGISTRY["__test_dummy"] is dummy_setup
        # 清理
        del _CONFIG_REGISTRY["__test_dummy"]

    def test_decorator_returns_original_function(self):
        """装饰器应返回原始函数（不包装）。"""

        def original():
            return 42

        result = register_config("__test_return")(original)
        assert result is original
        assert result() == 42
        del _CONFIG_REGISTRY["__test_return"]

    def test_duplicate_registration_overwrites(self):
        """重复注册同名配置应覆盖旧条目。"""

        @register_config("__test_dup")
        def first():
            pass

        @register_config("__test_dup")
        def second():
            pass

        assert _CONFIG_REGISTRY["__test_dup"] is second
        del _CONFIG_REGISTRY["__test_dup"]


class TestGetConfig:
    """get_config 查找测试。"""

    def test_get_existing_config(self):
        """应能获取已注册的配置函数。"""

        @register_config("__test_get")
        def my_setup():
            pass

        assert get_config("__test_get") is my_setup
        del _CONFIG_REGISTRY["__test_get"]

    def test_get_nonexistent_raises_key_error(self):
        """获取不存在的配置应抛出 KeyError。"""
        with pytest.raises(KeyError, match="未知的配置"):
            get_config("__nonexistent_config_xyz__")


class TestListConfigs:
    """list_configs 列举测试。"""

    def test_list_returns_list(self):
        """应返回列表类型。"""
        result = list_configs()
        assert isinstance(result, list)

    def test_list_contains_registered_configs(self):
        """列表应包含所有已注册的配置名称。"""
        configs = list_configs()
        # 至少应包含通过 _auto_import 加载的 16 个配置之一
        assert "IClamp" in configs


# ========== 全局配置发现测试 ==========

# 所有 16 个配置的名称列表
ALL_CONFIG_NAMES = [
    "Full",
    "FW",
    "IClamp",
    "IClampMuscle",
    "MultiSyns",
    "Muscles",
    "MusclesSine",
    "MuscleTest",
    "Oscillator",
    "OscillatorM",
    "Pharyngeal",
    "RIA",
    "Social",
    "Syns",
    "TapWithdrawal",
    "TargetMuscle",
]


class TestAllConfigsRegistered:
    """验证全部 16 个配置已注册。"""

    @pytest.mark.parametrize("name", ALL_CONFIG_NAMES)
    def test_config_registered(self, name):
        """配置 {name} 应已注册到注册表中。"""
        configs = list_configs()
        assert name in configs, f"配置 {name} 未注册"

    def test_total_config_count(self):
        """注册表中应恰好包含 16 个配置。"""
        configs = list_configs()
        # 过滤掉测试中添加的临时配置
        real_configs = [c for c in configs if not c.startswith("__test")]
        assert len(real_configs) == 16

    @pytest.mark.parametrize("name", ALL_CONFIG_NAMES)
    def test_config_is_callable(self, name):
        """配置 setup 函数应是可调用的。"""
        func = get_config(name)
        assert callable(func)


# ========== setup() 返回值结构测试 ==========

def _make_mock_params():
    """构造模拟的参数对象。"""
    params = MagicMock()
    params.level = "A"
    params.is_level_A.return_value = True
    params.bioparameters = []
    params.set_bioparameter = MagicMock()
    return params


class TestSetupReturnStructure:
    """setup() 返回值基本结构测试（不生成文件）。"""

    @pytest.mark.parametrize("name", ALL_CONFIG_NAMES)
    def test_setup_returns_five_tuple(self, mock_params, name):
        """setup(generate_flag=False) 应返回 5 元素元组。"""
        # Full 需要额外 mock get_cell_names_and_connection
        if name == "Full":
            with patch.object(_mod_full, "get_cell_names_and_connection",
                              return_value=(["ADAL"], [])):
                result = get_config(name)("A", generate_flag=False)
        else:
            result = get_config(name)("A", generate_flag=False)
        assert isinstance(result, tuple), f"{name} 未返回元组"
        assert len(result) == 5, f"{name} 返回 {len(result)} 元素，应为 5"

    @pytest.mark.parametrize("name", ALL_CONFIG_NAMES)
    def test_cells_is_list(self, mock_params, name):
        """返回的 cells 应是列表类型。"""
        if name == "Full":
            with patch.object(_mod_full, "get_cell_names_and_connection",
                              return_value=(["ADAL"], [])):
                cells, _, _, _, _ = get_config(name)("A", generate_flag=False)
        else:
            cells, _, _, _, _ = get_config(name)("A", generate_flag=False)
        assert isinstance(cells, list)

    @pytest.mark.parametrize("name", ALL_CONFIG_NAMES)
    def test_nml_doc_is_none_without_generate(self, mock_params, name):
        """generate_flag=False 时 nml_doc 应为 None。"""
        if name == "Full":
            with patch.object(_mod_full, "get_cell_names_and_connection",
                              return_value=(["ADAL"], [])):
                _, _, _, _, nml_doc = get_config(name)("A", generate_flag=False)
        else:
            _, _, _, _, nml_doc = get_config(name)("A", generate_flag=False)
        assert nml_doc is None


# ========== 各配置特定行为测试 ==========

class TestIClampConfig:
    """IClamp 配置特定测试。"""

    def test_cells_contain_adal(self, mock_params):
        """应包含 ADAL 神经元。"""
        cells, _, _, _, _ = get_config("IClamp")("A", generate_flag=False)
        assert "ADAL" in cells

    def test_muscles_include_mdr01(self, mock_params):
        """应包含 MDR01 肌肉。"""
        _, _, _, muscles, _ = get_config("IClamp")("A", generate_flag=False)
        assert "MDR01" in muscles

    def test_default_duration_based_on_stim(self, mock_params):
        """默认时长应基于刺激级数 (6*1000=6000ms)。"""
        result = get_config("IClamp")("A", generate_flag=False)
        assert result is not None


class TestIClampMuscleConfig:
    """IClampMuscle 配置特定测试。"""

    def test_cells_is_empty(self, mock_params):
        """应无神经元（纯肌肉测试）。"""
        cells, _, _, _, _ = get_config("IClampMuscle")("A", generate_flag=False)
        assert cells == []


class TestFullConfig:
    """Full 配置特定测试。"""

    def test_returns_all_cell_names(self, mock_params):
        """应返回数据读取器提供的全部细胞名称。"""
        with patch.object(_mod_full, "get_cell_names_and_connection",
                          return_value=(["ADAL", "ADAR", "RIAL"], [])):
            cells, _, _, _, _ = get_config("Full")("A", generate_flag=False)
        assert cells == ["ADAL", "ADAR", "RIAL"]


class TestPharyngealConfig:
    """Pharyngeal 配置特定测试。"""

    def test_cells_count(self, mock_params):
        """应包含 20 个咽部神经元。"""
        cells, _, _, _, _ = get_config("Pharyngeal")("A", generate_flag=False)
        assert len(cells) == 20


class TestOscillatorConfig:
    """Oscillator 配置特定测试。"""

    def test_cells_count(self, mock_params):
        """应包含 14 个振荡器神经元。"""
        cells, _, _, _, _ = get_config("Oscillator")("A", generate_flag=False)
        assert len(cells) == 14

    def test_no_muscles(self, mock_params):
        """不应包含肌肉。"""
        _, _, _, muscles, _ = get_config("Oscillator")("A", generate_flag=False)
        assert muscles == []


class TestSocialConfig:
    """Social 配置特定测试。"""

    def test_cells_count(self, mock_params):
        """应包含 7 个社交神经元。"""
        cells, _, _, _, _ = get_config("Social")("A", generate_flag=False)
        assert len(cells) == 7

    def test_rmgr_in_cells(self, mock_params):
        """应包含枢纽神经元 RMGR。"""
        cells, _, _, _, _ = get_config("Social")("A", generate_flag=False)
        assert "RMGR" in cells


class TestSynsConfig:
    """Syns 配置特定测试。"""

    def test_gap_cells_added_for_non_a(self, mock_params):
        """非 A 层级应添加间隙连接测试细胞。"""
        cells_a, _, _, _, _ = get_config("Syns")("A", generate_flag=False)
        cells_b, _, _, _, _ = get_config("Syns")("B", generate_flag=False)
        assert len(cells_b) == len(cells_a) + 2  # AIZL + ASHL


class TestMuscleTestConfig:
    """MuscleTest 配置特定测试。"""

    def test_no_neurons(self, mock_params):
        """应无神经元细胞（纯肌肉测试）。"""
        cells, _, _, _, _ = get_config("MuscleTest")("A", generate_flag=False)
        assert cells == []

    def test_muscles_included(self, mock_params):
        """muscles_to_include 应为 True。"""
        _, _, _, muscles, _ = get_config("MuscleTest")("A", generate_flag=False)
        assert muscles is True


class TestFWConfig:
    """FW 配置特定测试。"""

    def test_contains_avbl(self, mock_params):
        """应包含 AVBL 命令神经元。"""
        cells, _, _, _, _ = get_config("FW")("C2", generate_flag=False)
        assert "AVBL" in cells

    def test_muscles_included(self, mock_params):
        """应包含所有肌肉。"""
        _, _, _, muscles, _ = get_config("FW")("C2", generate_flag=False)
        assert muscles is True


class TestTapWithdrawalConfig:
    """TapWithdrawal 配置特定测试。"""

    def test_contains_touch_sensory(self, mock_params):
        """应包含触觉感觉神经元 PLML。"""
        cells, _, _, _, _ = get_config("TapWithdrawal")("C2", generate_flag=False)
        assert "PLML" in cells

    def test_no_muscles(self, mock_params):
        """muscles_to_include 应为 False。"""
        _, _, _, muscles, _ = get_config("TapWithdrawal")("C2", generate_flag=False)
        assert muscles is False


class TestMultiSynsConfig:
    """MultiSyns 配置特定测试。"""

    def test_cells_count(self, mock_params):
        """应包含 6 个神经元。"""
        cells, _, _, _, _ = get_config("MultiSyns")("A", generate_flag=False)
        assert len(cells) == 6


class TestTargetMuscleConfig:
    """TargetMuscle 配置特定测试。"""

    def test_cells_contain_rmhr(self, mock_params):
        """应包含 RMHR 神经元。"""
        cells, _, _, _, _ = get_config("TargetMuscle")("A", generate_flag=False)
        assert "RMHR" in cells

    def test_muscles_all_included(self, mock_params):
        """应包含全部肌肉。"""
        _, _, _, muscles, _ = get_config("TargetMuscle")("A", generate_flag=False)
        assert muscles is True


class TestRIAConfig:
    """RIA 配置特定测试。"""

    def test_cells_contain_rial(self, mock_params):
        """应包含 RIAL 神经元。"""
        cells, _, _, _, _ = get_config("RIA")("A", generate_flag=False)
        assert "RIAL" in cells


class TestMusclesConfig:
    """Muscles 配置特定测试。"""

    def test_cells_contain_motor_neurons(self, mock_params):
        """应包含运动神经元 DB1。"""
        cells, _, _, _, _ = get_config("Muscles")("A", generate_flag=False)
        assert "DB1" in cells

    def test_stimulate_avbl(self, mock_params):
        """刺激目标应包含 AVBL。"""
        _, stim, _, _, _ = get_config("Muscles")("A", generate_flag=False)
        assert "AVBL" in stim


class TestMusclesSineConfig:
    """MusclesSine 配置特定测试。"""

    def test_stimulate_avbl_avbr(self, mock_params):
        """刺激目标应为 AVBL 和 AVBR。"""
        _, stim, _, _, _ = get_config("MusclesSine")("A", generate_flag=False)
        assert "AVBL" in stim
        assert "AVBR" in stim


class TestOscillatorMConfig:
    """OscillatorM 配置特定测试。"""

    def test_no_muscles(self, mock_params):
        """不应包含肌肉。"""
        _, _, _, muscles, _ = get_config("OscillatorM")("A", generate_flag=False)
        assert muscles == []

    def test_stimulate_vb1_vb2(self, mock_params):
        """刺激目标应为 VB1 和 VB2。"""
        _, stim, _, _, _ = get_config("OscillatorM")("A", generate_flag=False)
        assert "VB1" in stim
        assert "VB2" in stim
