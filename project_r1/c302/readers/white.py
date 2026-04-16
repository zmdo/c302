# =============================================================================
# 功能描述：
#   通过 cect 库读取 White et al. 1986 连接组数据的适配器读取器。
#   合并了原代码中 White_whole、White_A、White_L4 三个独立模块，
#   通过参数化选择不同数据集。
#
# 类与方法索引：
#   WhiteDataReader                      (L29)   — cect White 连接组数据读取器
#     read_data                          (L54)   — 读取神经元连接数据
#     read_muscle_data                   (L67)   — 读取神经肌肉连接数据
#
# 更新日志：
#   2026-04-17  yi  初始创建：合并 White_whole + White_A + White_L4
#
# 当前维护者：yi
# =============================================================================
"""White et al. 1986 连接组数据读取器（通过 cect 库）。"""
import importlib
import logging

from c302.readers import register_reader
from c302.readers.base import BaseDataReader, ConnectionInfo

logger = logging.getLogger(__name__)

# cect 读取器模块路径
_CECT_MODULE_MAP = {
    "White_whole": "cect.readers.White_whole",
    "White_A": "cect.readers.White_A",
    "White_L4": "cect.readers.White_L4",
}


def _get_cect_instance(dataset: str):
    """动态导入 cect 读取器并获取实例。

    :param dataset: 数据集名称
    :return: cect ConnectomeDataset 实例
    """
    module_name = _CECT_MODULE_MAP[dataset]
    module = importlib.import_module(module_name)
    return module.get_instance()


def _convert_conns(conns) -> list[ConnectionInfo]:
    """将 cect ConnectionInfo 转换为本项目的 ConnectionInfo。

    :param conns: cect 连接列表
    :return: 本项目 ConnectionInfo 列表
    """
    return [
        ConnectionInfo(c.pre_cell, c.post_cell, c.number, c.syntype, c.synclass)
        for c in conns
    ]


def _make_white_reader(dataset: str) -> type[BaseDataReader]:
    """为指定数据集创建 White 读取器类。

    :param dataset: 数据集名称
    :return: 读取器类
    """

    class _WhiteReader(BaseDataReader):
        __doc__ = "White et al. 1986 %s 连接组读取器。" % dataset

        @staticmethod
        def read_data(
            include_nonconnected_cells: bool = False,
        ) -> tuple[list[str], list[ConnectionInfo]]:
            """从 cect 读取神经元连接数据。

            :param include_nonconnected_cells: cect 不使用此参数
            :return: ``(cells, conns)``
            """
            instance = _get_cect_instance(dataset)
            # cect read_data() 不接受参数
            cells, conns = instance.read_data()
            return cells, _convert_conns(conns)

        @staticmethod
        def read_muscle_data() -> tuple[list[str], list[str], list[ConnectionInfo]]:
            """从 cect 读取神经肌肉连接数据。

            :return: ``(neurons, muscles, conns)``
            """
            instance = _get_cect_instance(dataset)
            neurons, muscles, conns = instance.read_muscle_data()
            return neurons, muscles, _convert_conns(conns)

    _WhiteReader.__name__ = "White%sReader" % dataset.replace("_", "").title()
    _WhiteReader.__qualname__ = _WhiteReader.__name__
    return _WhiteReader


# 创建并注册三个 White 读取器
WhiteWholeReader = _make_white_reader("White_whole")
WhiteAReader = _make_white_reader("White_A")
WhiteL4Reader = _make_white_reader("White_L4")

register_reader("White_whole", WhiteWholeReader)
register_reader("White_A", WhiteAReader)
register_reader("White_L4", WhiteL4Reader)
