# =============================================================================
# 功能描述：
#   c302 公共 API 导出。提供包版本号和核心模块的便捷访问入口。
#
# 类与方法索引：
#   (由 gen_index.py 生成)
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段六：新建公共 API 导出
#
# 当前维护者：Copilot
# =============================================================================
"""C. elegans 302 neuron NeuroML 2 network generation framework."""
from c302.__version__ import __version__

# 默认数据读取器常量（供配置脚本引用）
DEFAULT_DATA_READER = "cect.readers.SpreadsheetDataReader"
FW_DATA_READER = "cect.readers.UpdatedSpreadsheetDataReader2"

__all__ = [
    "__version__",
    "DEFAULT_DATA_READER",
    "FW_DATA_READER",
]
