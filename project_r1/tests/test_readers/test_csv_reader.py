# =============================================================================
# 功能描述：
#   CsvDataReader / CsvDataReaderModified 的单元测试。
#
# 类与方法索引：
#   TestCsvReadData                      (L23)   — CsvDataReader.read_data 测试
#   TestCsvReadMuscleData                (L57)   — CsvDataReader.read_muscle_data 测试
#   TestCsvModifiedReader                (L79)   — CsvDataReaderModified 测试
#   TestHelperFunctions                  (L95)   — CSV 模块辅助函数测试
#
# 更新日志：
#   2026-04-17  yi  初始创建
#
# 当前维护者：yi
# =============================================================================
"""CsvDataReader 的单元测试。"""
import pytest

from c302.readers.base import ConnectionInfo
from c302.readers.csv_reader import (
    CsvDataReader,
    CsvDataReaderModified,
    _get_old_muscle_name,
    _get_synclass,
    _get_syntype,
    _is_neuron_csv,
)


class TestCsvReadData:
    """CsvDataReader.read_data 测试。"""

    def test_returns_tuple(self):
        """返回 (cells, conns) 元组。"""
        cells, conns = CsvDataReader.read_data()
        assert isinstance(cells, list)
        assert isinstance(conns, list)

    def test_cells_not_empty(self):
        """应返回非空的细胞列表。"""
        cells, _ = CsvDataReader.read_data()
        assert len(cells) > 0

    def test_all_neurons(self):
        """read_data 应只返回神经元（大写字母开头）。"""
        cells, _ = CsvDataReader.read_data()
        for c in cells:
            assert c[0].isupper(), f"{c} 不是以大写字母开头"

    def test_include_nonconnected(self):
        """应包含 CANL/CANR。"""
        cells, _ = CsvDataReader.read_data(include_nonconnected_cells=True)
        assert "CANL" in cells
        assert "CANR" in cells

    def test_conn_type(self):
        """每个连接应为 ConnectionInfo 实例。"""
        _, conns = CsvDataReader.read_data()
        assert all(isinstance(c, ConnectionInfo) for c in conns)


class TestCsvReadMuscleData:
    """CsvDataReader.read_muscle_data 测试。"""

    def test_returns_triple(self):
        """返回 (neurons, muscles, conns) 三元组。"""
        neurons, muscles, conns = CsvDataReader.read_muscle_data()
        assert isinstance(neurons, list)
        assert isinstance(muscles, list)
        assert isinstance(conns, list)

    def test_muscles_standard_names(self):
        """肌肉名称应为标准格式（M** 开头）。"""
        _, muscles, _ = CsvDataReader.read_muscle_data()
        for m in muscles:
            assert m.startswith(("M", "BWM")), f"非标准肌肉名: {m}"

    def test_conns_not_empty(self):
        """应有神经肌肉连接。"""
        _, _, conns = CsvDataReader.read_muscle_data()
        assert len(conns) > 0


class TestCsvModifiedReader:
    """CsvDataReaderModified 测试。"""

    def test_read_data(self):
        """修正版 CSV 也能正常读取。"""
        cells, conns = CsvDataReaderModified.read_data()
        assert len(cells) > 0
        assert len(conns) > 0

    def test_read_muscle_data(self):
        """修正版 CSV 肌肉数据。"""
        neurons, muscles, conns = CsvDataReaderModified.read_muscle_data()
        assert len(neurons) > 0


class TestHelperFunctions:
    """CSV 模块辅助函数测试。"""

    def test_is_neuron_csv_uppercase(self):
        assert _is_neuron_csv("AVAL") is True

    def test_is_neuron_csv_lowercase(self):
        assert _is_neuron_csv("vBWML01") is False

    def test_get_syntype_electrical(self):
        assert _get_syntype("electrical") == "GapJunction"

    def test_get_syntype_chemical(self):
        assert _get_syntype("chemical") == "Send"

    def test_get_syntype_unknown(self):
        with pytest.raises(NotImplementedError):
            _get_syntype("unknown")

    def test_get_synclass_gap(self):
        assert _get_synclass("AVAL", "GapJunction") == "Generic_GJ"

    def test_get_synclass_gaba(self):
        assert _get_synclass("DD1", "Send") == "GABA"

    def test_get_synclass_ach(self):
        assert _get_synclass("AVAL", "Send") == "Acetylcholine"

    def test_get_old_muscle_name_vbwml(self):
        assert _get_old_muscle_name("vBWML05") == "MVL05"

    def test_get_old_muscle_name_dbwmr(self):
        assert _get_old_muscle_name("dBWMR23") == "MDR23"

    def test_get_old_muscle_name_padding(self):
        """小于 10 的索引应补零。"""
        assert _get_old_muscle_name("vBWML3") == "MVL03"
