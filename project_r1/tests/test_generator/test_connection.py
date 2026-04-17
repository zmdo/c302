# =============================================================================
# 功能描述：
#   连接创建模块的单元测试。覆盖 get_projection_id、set_param、mirror_param、
#   连接数量处理和投射创建逻辑。
#
# 类与方法索引：
#   _FakeConn                            (L53)   — 模拟连接对象
#     __init__                           (L56)   — __init__ 函数
#   _FakeParams                          (L64)   — 模拟参数模型对象
#     __init__                           (L67)   — __init__ 函数
#     get_bioparameter                   (L70)   — get_bioparameter 函数
#     set_bioparameter                   (L76)   — set_bioparameter 函数
#     add_bioparameter                   (L83)   — add_bioparameter 函数
#   TestGetProjectionId                  (L87)   — get_projection_id 测试
#     test_standard_format               (L90)   — 应返回 NC_pre_post_synclass 格式
#     test_gap_junction                  (L95)   — 电突触也使用相同格式
#   TestSetParam                         (L101)  — set_param 测试
#     test_add_new_param                 (L104)  — 不存在的参数应被添加
#     test_update_existing_param         (L110)  — 已存在的参数应被更新
#     test_same_value_no_update          (L117)  — 相同值不应触发更新
#   TestMirrorParam                      (L126)  — mirror_param 测试
#     test_creates_both_directions       (L129)  — 应同时创建正向和反向参数
#   TestApplyNumberProcessing            (L142)  — _apply_number_processing 测试
#     test_no_modifications              (L145)  — 无覆盖/缩放时应返回原始数量
#     test_number_override               (L152)  — 连接数量覆盖应替换原始值
#     test_number_scaling                (L161)  — 连接数量缩放应使用原始 conn.number
#     test_global_power_scaling          (L170)  — 全局幂缩放应正确计算
#     test_regex_override                (L180)  — 正则模式覆盖应匹配
#   TestEnsureSilentSynapse              (L190)  — _ensure_silent_synapse 测试
#     test_adds_silent_synapse_when_empty (L193)  — 空文档应添加 SilentSynapse
#     test_no_duplicate_when_exists      (L201)  — 已有 SilentSynapse 时不应重复添加
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段四：新建
#
# 当前维护者：Copilot
# =============================================================================
"""connection 模块测试。"""
from unittest.mock import MagicMock, patch

import pytest

from c302.generator.connection import (
    _apply_number_processing,
    _ensure_silent_synapse,
    get_projection_id,
    mirror_param,
    set_param,
)
from c302.parameters.bio import BioParameter


class _FakeConn:
    """模拟连接对象。"""

    def __init__(self, pre="AVAL", post="AVBR", number=5, synclass="Acetylcholine", syntype="Send"):
        self.pre_cell = pre
        self.post_cell = post
        self.number = number
        self.synclass = synclass
        self.syntype = syntype


class _FakeParams:
    """模拟参数模型对象。"""

    def __init__(self):
        self.bioparameters = []

    def get_bioparameter(self, name, warn_if_missing=False):
        for bp in self.bioparameters:
            if bp.name == name:
                return bp
        return None

    def set_bioparameter(self, name, value, source, certainty):
        for bp in self.bioparameters:
            if bp.name == name:
                bp.value = value
                bp.source = source
                bp.certainty = certainty

    def add_bioparameter(self, name, value, source, certainty):
        self.bioparameters.append(BioParameter(name, value, source, certainty))


class TestGetProjectionId:
    """get_projection_id 测试。"""

    def test_standard_format(self):
        """应返回 NC_pre_post_synclass 格式。"""
        result = get_projection_id("AVAL", "AVBR", "Acetylcholine", "Send")
        assert result == "NC_AVAL_AVBR_Acetylcholine"

    def test_gap_junction(self):
        """电突触也使用相同格式。"""
        result = get_projection_id("AVAL", "AVBR", "Generic_GJ", "GapJunction")
        assert result == "NC_AVAL_AVBR_Generic_GJ"


class TestSetParam:
    """set_param 测试。"""

    def test_add_new_param(self):
        """不存在的参数应被添加。"""
        params = _FakeParams()
        set_param(params, "test_param", "1.0 nS")
        assert params.get_bioparameter("test_param").value == "1.0 nS"

    def test_update_existing_param(self):
        """已存在的参数应被更新。"""
        params = _FakeParams()
        params.add_bioparameter("test_param", "1.0 nS", "orig", "0.5")
        set_param(params, "test_param", "2.0 nS")
        assert params.get_bioparameter("test_param").value == "2.0 nS"

    def test_same_value_no_update(self):
        """相同值不应触发更新。"""
        params = _FakeParams()
        params.add_bioparameter("test_param", "1.0 nS", "orig", "0.5")
        set_param(params, "test_param", "1.0 nS")
        # 来源应保持原始
        assert params.get_bioparameter("test_param").source == "orig"


class TestMirrorParam:
    """mirror_param 测试。"""

    def test_creates_both_directions(self):
        """应同时创建正向和反向参数。"""
        params = _FakeParams()
        mirror_param(params, "AVAL_to_AVBR_elec_syn_gbase", "10 nS")
        # 正向
        assert params.get_bioparameter("AVAL_to_AVBR_elec_syn_gbase") is not None
        # 反向
        assert params.get_bioparameter("AVBR_to_AVAL_elec_syn_gbase") is not None
        # 值相同
        assert params.get_bioparameter("AVAL_to_AVBR_elec_syn_gbase").value == "10 nS"
        assert params.get_bioparameter("AVBR_to_AVAL_elec_syn_gbase").value == "10 nS"


class TestApplyNumberProcessing:
    """_apply_number_processing 测试。"""

    def test_no_modifications(self):
        """无覆盖/缩放时应返回原始数量。"""
        conn = _FakeConn(number=10)
        params = _FakeParams()
        result = _apply_number_processing(conn, params, "AVAL-AVBR", None, None)
        assert result == 10

    def test_number_override(self):
        """连接数量覆盖应替换原始值。"""
        conn = _FakeConn(number=10)
        params = _FakeParams()
        result = _apply_number_processing(
            conn, params, "AVAL-AVBR", {"AVAL-AVBR": 5.0}, None
        )
        assert result == 5.0

    def test_number_scaling(self):
        """连接数量缩放应使用原始 conn.number。"""
        conn = _FakeConn(number=10)
        params = _FakeParams()
        result = _apply_number_processing(
            conn, params, "AVAL-AVBR", None, {"AVAL-AVBR": 2.0}
        )
        assert result == 20.0

    def test_global_power_scaling(self):
        """全局幂缩放应正确计算。"""
        conn = _FakeConn(number=4)
        params = _FakeParams()
        params.add_bioparameter(
            "global_connectivity_power_scaling", "0.5", "test", "1"
        )
        result = _apply_number_processing(conn, params, "AVAL-AVBR", None, None)
        assert result == pytest.approx(2.0)  # 4^0.5 = 2

    def test_regex_override(self):
        """正则模式覆盖应匹配。"""
        conn = _FakeConn(number=10)
        params = _FakeParams()
        result = _apply_number_processing(
            conn, params, "AVAL-AVBR", {"^AVAL-.*$": 3.0}, None
        )
        assert result == 3.0


class TestEnsureSilentSynapse:
    """_ensure_silent_synapse 测试。"""

    def test_adds_silent_synapse_when_empty(self):
        """空文档应添加 SilentSynapse。"""
        nml_doc = MagicMock()
        nml_doc.silent_synapses = []
        _ensure_silent_synapse(nml_doc)
        assert len(nml_doc.silent_synapses) == 1
        assert nml_doc.silent_synapses[0].id == "silent"

    def test_no_duplicate_when_exists(self):
        """已有 SilentSynapse 时不应重复添加。"""
        nml_doc = MagicMock()
        existing = MagicMock()
        existing.id = "silent"
        nml_doc.silent_synapses = [existing]
        _ensure_silent_synapse(nml_doc)
        assert len(nml_doc.silent_synapses) == 1
