# =============================================================================
# 功能描述：
#   WhiteDataReader 的单元测试：cect 适配器调用正确性。
#   这些测试依赖 cect 库安装，不可用时自动跳过。
#
# 类与方法索引：
#   TestWhiteWholeReader                 (L26)   — White_whole 读取器测试
#   TestWhiteAReader                     (L46)   — White_A 读取器测试
#   TestWhiteL4Reader                    (L60)   — White_L4 读取器测试
#
# 更新日志：
#   2026-04-17  yi  初始创建
#
# 当前维护者：yi
# =============================================================================
"""WhiteDataReader 的单元测试。"""
import pytest

from c302.readers.base import ConnectionInfo

# 尝试导入 cect，不可用时跳过全部测试
cect = pytest.importorskip("cect")

from c302.readers.white import WhiteWholeReader, WhiteAReader, WhiteL4Reader


class TestWhiteWholeReader:
    """White_whole 读取器测试。"""

    def test_read_data(self):
        """返回非空的细胞和连接列表。"""
        cells, conns = WhiteWholeReader.read_data()
        assert len(cells) > 0
        assert len(conns) > 0

    def test_conn_type(self):
        """连接类型应为本项目的 ConnectionInfo。"""
        _, conns = WhiteWholeReader.read_data()
        assert all(isinstance(c, ConnectionInfo) for c in conns)

    def test_read_muscle_data(self):
        """返回神经元、肌肉和连接列表。"""
        neurons, muscles, conns = WhiteWholeReader.read_muscle_data()
        assert isinstance(neurons, list)
        assert isinstance(muscles, list)


class TestWhiteAReader:
    """White_A 读取器测试。"""

    def test_read_data(self):
        cells, conns = WhiteAReader.read_data()
        assert len(cells) > 0

    def test_read_muscle_data(self):
        neurons, muscles, conns = WhiteAReader.read_muscle_data()
        assert isinstance(neurons, list)


class TestWhiteL4Reader:
    """White_L4 读取器测试。"""

    def test_read_data(self):
        cells, conns = WhiteL4Reader.read_data()
        assert len(cells) > 0

    def test_read_muscle_data(self):
        neurons, muscles, conns = WhiteL4Reader.read_muscle_data()
        assert isinstance(neurons, list)
