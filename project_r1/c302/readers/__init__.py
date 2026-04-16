# =============================================================================
# 功能描述：
#   数据读取器注册表和工厂函数，支持按名称动态获取读取器。
#
# 类与方法索引：
#   register_reader                      (L26)   — 注册数据读取器
#   get_reader                           (L36)   — 按名称获取读取器类
#   list_readers                         (L50)   — 列出所有已注册的读取器名称
#
# 更新日志：
#   2026-04-17  yi  初始创建
#
# 当前维护者：yi
# =============================================================================
"""数据读取器注册表和工厂函数。"""
import logging

from c302.readers.base import BaseDataReader

logger = logging.getLogger(__name__)

# 读取器注册表：名称 → 读取器类
_READER_REGISTRY: dict[str, type[BaseDataReader]] = {}


def register_reader(name: str, reader_class: type[BaseDataReader]) -> None:
    """注册数据读取器。

    :param name: 读取器名称
    :param reader_class: 读取器类（必须继承 BaseDataReader）
    """
    _READER_REGISTRY[name] = reader_class
    logger.debug("注册读取器: %s -> %s", name, reader_class.__name__)


def get_reader(name: str) -> type[BaseDataReader]:
    """按名称获取读取器类。

    :param name: 读取器名称
    :return: 读取器类
    :raises KeyError: 读取器名称不存在
    """
    if name not in _READER_REGISTRY:
        raise KeyError(
            "未知的读取器: %s，可用: %s" % (name, list(_READER_REGISTRY.keys()))
        )
    return _READER_REGISTRY[name]


def list_readers() -> list[str]:
    """列出所有已注册的读取器名称。

    :return: 读取器名称列表
    """
    return list(_READER_REGISTRY.keys())
