# =============================================================================
# 功能描述：
#   SpreadsheetDataReader 的单元测试：XLS 解析正确性、连接数据完整性。
#
# 类与方法索引：
#   TestSpreadsheetReadData              (L23)   — read_data 测试
#   TestSpreadsheetReadMuscleData        (L55)   — read_muscle_data 测试
#
# 更新日志：
#   2026-04-17  yi  初始创建
#
# 当前维护者：yi
# =============================================================================
"""SpreadsheetDataReader 的单元测试。"""
import pytest

from c302.readers.base import ConnectionInfo, NEURONS
from c302.readers.spreadsheet import SpreadsheetDataReader


class TestSpreadsheetReadData:
    """read_data 测试（CElegansNeuronTables.xls）。"""

    def test_returns_tuple(self):
        """返回值为 (cells, conns) 元组。"""
        cells, conns = SpreadsheetDataReader.read_data()
        assert isinstance(cells, list)
        assert isinstance(conns, list)

    def test_cells_not_empty(self):
        """应返回非空的细胞列表。"""
        cells, conns = SpreadsheetDataReader.read_data()
        assert len(cells) > 0

    def test_conns_not_empty(self):
        """应返回非空的连接列表。"""
        cells, conns = SpreadsheetDataReader.read_data()
        assert len(conns) > 0

    def test_conn_type(self):
        """每个连接应为 ConnectionInfo 实例。"""
        cells, conns = SpreadsheetDataReader.read_data()
        assert all(isinstance(c, ConnectionInfo) for c in conns)

    def test_include_nonconnected_cells(self):
        """include_nonconnected_cells=True 应包含 CANL/CANR/VC6。"""
        cells, _ = SpreadsheetDataReader.read_data(include_nonconnected_cells=True)
        assert "CANL" in cells
        assert "CANR" in cells
        assert "VC6" in cells

    def test_neuron_connect_mode(self):
        """neuron_connect=True 使用 NeuronConnectFormatted.xlsx。"""
        cells, conns = SpreadsheetDataReader.read_data(neuron_connect=True)
        assert len(cells) > 0
        assert len(conns) > 0
        # NeuronConnectFormatted 只有 Generic_GJ 或 Chemical_Synapse
        synclasses = {c.synclass for c in conns}
        assert synclasses <= {"Generic_GJ", "Chemical_Synapse"}


class TestSpreadsheetReadMuscleData:
    """read_muscle_data 测试。"""

    def test_returns_triple(self):
        """返回值为 (neurons, muscles, conns) 三元组。"""
        neurons, muscles, conns = SpreadsheetDataReader.read_muscle_data()
        assert isinstance(neurons, list)
        assert isinstance(muscles, list)
        assert isinstance(conns, list)

    def test_neurons_not_empty(self):
        """运动神经元列表不为空。"""
        neurons, _, _ = SpreadsheetDataReader.read_muscle_data()
        assert len(neurons) > 0

    def test_muscles_not_empty(self):
        """肌肉列表不为空。"""
        _, muscles, _ = SpreadsheetDataReader.read_muscle_data()
        assert len(muscles) > 0

    def test_conns_all_send(self):
        """肌肉连接的突触类型均为 Send。"""
        _, _, conns = SpreadsheetDataReader.read_muscle_data()
        assert all(c.syntype == "Send" for c in conns)

    def test_synclass_no_comma(self):
        """synclass 字段不含逗号。"""
        _, _, conns = SpreadsheetDataReader.read_muscle_data()
        for c in conns:
            assert "," not in c.synclass
