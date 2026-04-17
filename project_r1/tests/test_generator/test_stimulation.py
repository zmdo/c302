# =============================================================================
# 功能描述：
#   刺激注入模块的单元测试。覆盖脉冲刺激 ID 生成、InputList 追加、
#   脉冲和正弦波刺激创建。
#
# 类与方法索引：
#   (由 gen_index.py 生成)
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段四：新建
#
# 当前维护者：Copilot
# =============================================================================
"""stimulation 模块测试。"""
from unittest.mock import MagicMock

import pytest

from c302.generator.stimulation import (
    add_new_input,
    add_new_sinusoidal_input,
    get_next_stim_id,
)


def _make_nml_doc(existing_stims=None):
    """创建模拟的 NeuroML 文档对象。"""
    doc = MagicMock()
    doc.pulse_generators = []
    doc.sine_generators = []
    net = MagicMock()
    net.input_lists = []
    doc.networks = [net]
    if existing_stims:
        for sid in existing_stims:
            stim = MagicMock()
            stim.id = sid
            doc.pulse_generators.append(stim)
    return doc


def _make_params(level="A"):
    """创建模拟的参数对象。"""
    params = MagicMock()
    params.generic_neuron_cell.id = "generic_iaf_cell"
    params.generic_muscle_cell.id = "generic_iaf_muscle"
    params.is_level_D.return_value = level.startswith("D")
    return params


class TestGetNextStimId:
    """get_next_stim_id 测试。"""

    def test_first_stim(self):
        """无已有刺激时应返回 stim_CELL_1。"""
        doc = _make_nml_doc()
        result = get_next_stim_id(doc, "ADAL")
        assert result == "stim_ADAL_1"

    def test_increments_correctly(self):
        """已有一个刺激时应返回 stim_CELL_2。"""
        doc = _make_nml_doc(["stim_ADAL_1"])
        result = get_next_stim_id(doc, "ADAL")
        assert result == "stim_ADAL_2"

    def test_different_cells_independent(self):
        """不同细胞的刺激计数应独立。"""
        doc = _make_nml_doc(["stim_ADAL_1", "stim_ADAL_2"])
        result = get_next_stim_id(doc, "ADAR")
        assert result == "stim_ADAR_1"


class TestAddNewInput:
    """add_new_input 测试。"""

    def test_creates_pulse_generator(self):
        """应创建 PulseGenerator 并添加到文档。"""
        doc = _make_nml_doc()
        params = _make_params()
        add_new_input(doc, "ADAL", "0ms", "500ms", "5pA", params)
        assert len(doc.pulse_generators) == 1
        assert doc.pulse_generators[0].id == "stim_ADAL_1"
        assert doc.pulse_generators[0].delay == "0ms"
        assert doc.pulse_generators[0].duration == "500ms"
        assert doc.pulse_generators[0].amplitude == "5pA"

    def test_creates_input_list(self):
        """应创建 InputList 并追加到网络。"""
        doc = _make_nml_doc()
        params = _make_params()
        add_new_input(doc, "ADAL", "0ms", "500ms", "5pA", params)
        assert len(doc.networks[0].input_lists) == 1

    def test_multiple_stims_increment_id(self):
        """多次添加应递增 ID。"""
        doc = _make_nml_doc()
        params = _make_params()
        add_new_input(doc, "ADAL", "0ms", "500ms", "5pA", params)
        add_new_input(doc, "ADAL", "100ms", "400ms", "3pA", params)
        assert len(doc.pulse_generators) == 2
        assert doc.pulse_generators[1].id == "stim_ADAL_2"


class TestAddNewSinusoidalInput:
    """add_new_sinusoidal_input 测试。"""

    def test_creates_sine_generator_for_db(self):
        """DB 系列应正常创建 SineGenerator。"""
        doc = _make_nml_doc()
        params = _make_params()
        add_new_sinusoidal_input(doc, "DB1", "0ms", "500ms", "5pA", "200ms", params)
        assert len(doc.sine_generators) == 1
        sine = doc.sine_generators[0]
        assert sine.id == "stim_DB1_1"
        assert sine.amplitude == "5pA"  # DB 不取反

    def test_vb_inverts_amplitude(self):
        """VB 系列幅度应取反。"""
        doc = _make_nml_doc()
        params = _make_params()
        add_new_sinusoidal_input(doc, "VB1", "0ms", "500ms", "5pA", "200ms", params)
        sine = doc.sine_generators[0]
        assert sine.amplitude == "-5pA"  # VB 取反

    def test_vb_negative_amplitude_becomes_positive(self):
        """VB 系列的负幅度应变正。"""
        doc = _make_nml_doc()
        params = _make_params()
        add_new_sinusoidal_input(doc, "VB1", "0ms", "500ms", "-5pA", "200ms", params)
        sine = doc.sine_generators[0]
        assert sine.amplitude == "5pA"

    def test_phase_is_computed(self):
        """相位应基于 soma 位置计算。"""
        doc = _make_nml_doc()
        params = _make_params()
        add_new_sinusoidal_input(doc, "DB1", "0ms", "500ms", "5pA", "200ms", params)
        sine = doc.sine_generators[0]
        # DB1 位置 = 0.24，相位 = 0.24 * -0.886
        expected_phase = 0.24 * -0.886
        assert sine.phase == pytest.approx(expected_phase)
