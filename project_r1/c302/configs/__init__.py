# =============================================================================
# 功能描述：
#   配置脚本注册表，提供配置注册装饰器和按名称查找功能。
#   每个配置脚本使用 @register_config 装饰器注册自身的 setup() 函数。
#
# 类与方法索引：
#   register_config                      (L27)   — 配置注册装饰器
#   get_config                           (L41)   — 按名称获取配置 setup 函数
#   list_configs                         (L58)   — 列出所有已注册的配置名称
#   _auto_import                         (L67)   — 自动导入所有配置模块以触发注册
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：新建
#   2026-04-19  Copilot  计划5阶段九：_auto_import 改为 pkgutil.iter_modules 扫描
#
# 当前维护者：Copilot
# =============================================================================
"""配置脚本注册表。"""
import logging
from typing import Callable

logger = logging.getLogger(__name__)

_CONFIG_REGISTRY: dict[str, Callable] = {}


def register_config(name: str) -> Callable:
    """配置注册装饰器。

    :param name: 配置名称（如 "IClamp", "Full"）
    :return: 装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        _CONFIG_REGISTRY[name] = func
        return func

    return decorator


def get_config(name: str) -> Callable:
    """按名称获取配置 setup 函数。

    :param name: 配置名称
    :return: setup 函数
    :raises KeyError: 配置名称不存在
    """
    if name not in _CONFIG_REGISTRY:
        # 尝试触发自动导入
        _auto_import()
        if name not in _CONFIG_REGISTRY:
            raise KeyError(
                f"未知的配置: {name}，可用: {list(_CONFIG_REGISTRY.keys())}"
            )
    return _CONFIG_REGISTRY[name]


def list_configs() -> list[str]:
    """列出所有已注册的配置名称。

    :return: 配置名称列表
    """
    _auto_import()
    return list(_CONFIG_REGISTRY.keys())


def _auto_import() -> None:
    """自动导入所有配置模块以触发注册。

    使用 pkgutil.iter_modules 扫描本包下所有子模块，
    避免硬编码模块列表。
    """
    import importlib
    import pkgutil

    # 扫描 c302.configs 包下所有子模块
    for finder, name, ispkg in pkgutil.iter_modules(__path__, __name__ + "."):
        try:
            importlib.import_module(name)
        except ImportError:
            pass
