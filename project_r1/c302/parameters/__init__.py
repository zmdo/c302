# =============================================================================
# 功能描述：
#   参数集注册表，提供按层级名称查找参数配置的工厂函数。
#   get_parameter_set 返回 c302ModelPrototype 实例（已加载 YAML 参数、
#   具备 create_models / get_*_syn 等能力），可直接传递给 generate()。
#   支持的层级：A, B, C, C0, C1, D, D1（可扩展 BC1, C2, W2D）。
#
# 类与方法索引：
#   get_parameter_set                    (L34)   — 按层级名称创建参数化模型实例
#   list_parameter_sets                  (L56)   — 列出所有可用的参数层级名称
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段三：新建参数集注册表
#   2026-04-18  Copilot  计划3阶段八：改为返回 c302ModelPrototype 实例
#
# 当前维护者：Copilot
# =============================================================================
"""参数集注册表。"""
import logging

from c302.parameters.model import c302ModelPrototype

logger = logging.getLogger(__name__)

# 所有已知层级（含 factory 尚未实现的）
_LEVEL_REGISTRY: set[str] = {
    "A", "B", "C", "C0", "C1", "D", "D1",
}

# 尚未迁移的层级（YAML 存在但 factory 未实现）
_PENDING_LEVELS: set[str] = {"BC1", "C2", "W2D"}


def get_parameter_set(level: str) -> c302ModelPrototype:
    """按层级名称创建参数化模型实例。

    返回的对象已加载 YAML 参数，并具备 ``create_models()`` /
    ``get_exc_syn()`` / ``get_inh_syn()`` / ``get_elec_syn()`` 等方法，
    可直接传递给 ``generate()``。

    :param level: 层级名称（如 ``"A"``、``"C0"``、``"D1"``）
    :return: c302ModelPrototype 实例
    :raises KeyError: 未知的层级名称
    """
    level_upper = level.upper()
    if level_upper not in _LEVEL_REGISTRY:
        raise KeyError(
            f"未知的参数层级: {level}，可用: {sorted(_LEVEL_REGISTRY)}"
        )
    # 延迟导入避免循环依赖
    from c302.parameters.factory import create_model

    return create_model(level_upper)


def list_parameter_sets() -> list[str]:
    """列出所有可用的参数层级名称。

    :return: 层级名称列表
    """
    return sorted(_LEVEL_REGISTRY)
