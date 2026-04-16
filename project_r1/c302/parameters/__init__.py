# =============================================================================
# 功能描述：
#   参数集注册表，提供按层级名称查找参数配置的工厂函数。
#   支持的层级：A, B, BC1, C, C0, C1, C2, D, D1, W2D。
#
# 类与方法索引：
#   _LEVEL_REGISTRY                       (L27)  — 层级名称到 YAML 映射
#   get_parameter_set                     (L42)  — 按层级加载参数集
#   list_parameter_sets                   (L55)  — 列出所有可用层级
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段三：新建参数集注册表
#
# 当前维护者：Copilot
# =============================================================================
import logging

from c302.parameters.bio import BioParameter
from c302.parameters.loader import ParameterLoader

logger = logging.getLogger(__name__)

# 层级名称到 YAML 文件的映射
_LEVEL_REGISTRY: dict[str, str] = {
    "A": "A",
    "B": "B",
    "BC1": "BC1",
    "C": "C",
    "C0": "C0",
    "C1": "C1",
    "C2": "C2",
    "D": "D",
    "D1": "D1",
    "W2D": "W2D",
}

# 全局加载器实例（带缓存）
_loader = ParameterLoader()


def get_parameter_set(level: str) -> list[BioParameter]:
    """按层级名称加载参数集。

    :param level: 层级名称（如 ``"A"``、``"C0"``、``"W2D"``）
    :return: BioParameter 列表
    :raises KeyError: 未知的层级名称
    """
    level_upper = level.upper()
    if level_upper not in _LEVEL_REGISTRY:
        raise KeyError(
            f"未知的参数层级: {level}，可用: {list(_LEVEL_REGISTRY.keys())}"
        )
    return _loader.load_parameters(_LEVEL_REGISTRY[level_upper])


def list_parameter_sets() -> list[str]:
    """列出所有可用的参数层级名称。

    :return: 层级名称列表
    """
    return list(_LEVEL_REGISTRY.keys())
