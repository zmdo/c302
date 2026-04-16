# =============================================================================
# 功能描述：
#   读取器注册表的单元测试。
#
# 类与方法索引：
#   TestReaderRegistry                   (L20)   — 注册表功能测试
#
# 更新日志：
#   2026-04-17  yi  初始创建
#
# 当前维护者：yi
# =============================================================================
"""读取器注册表的单元测试。"""
import pytest

from c302.readers import get_reader, list_readers, register_reader
from c302.readers.base import BaseDataReader


class TestReaderRegistry:
    """注册表功能测试。"""

    def test_spreadsheet_registered(self):
        """SpreadsheetDataReader 应已注册。"""
        # 导入 spreadsheet 模块以触发注册
        import c302.readers.spreadsheet  # noqa: F401

        reader = get_reader("SpreadsheetDataReader")
        assert issubclass(reader, BaseDataReader)

    def test_csv_readers_registered(self):
        """CSV 读取器应已注册。"""
        import c302.readers.csv_reader  # noqa: F401

        assert "UpdatedSpreadsheetDataReader" in list_readers()
        assert "UpdatedSpreadsheetDataReader2" in list_readers()

    def test_unknown_reader_raises(self):
        """获取不存在的读取器应抛出 KeyError。"""
        with pytest.raises(KeyError):
            get_reader("NonExistentReader")

    def test_list_readers(self):
        """列表应包含已注册的读取器。"""
        import c302.readers.spreadsheet  # noqa: F401

        readers = list_readers()
        assert "SpreadsheetDataReader" in readers
