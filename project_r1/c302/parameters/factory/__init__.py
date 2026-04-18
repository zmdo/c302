# =============================================================================
# 功能描述：
#   参数工厂入口模块，提供 create_model() 工厂函数。
#   根据层级名称创建对应的参数化模型实例。
#   所有 10 个层级均已迁移到新子模块。
#
# 类与方法索引：
#   create_model                         (L46)   — 根据层级名称创建参数化模型实例
#
# 更新日志：
#   2026-04-19  Copilot  计划5阶段二：从 factory.py 拆分为子包
#   2026-04-19  Copilot  计划5阶段三-六：完成全部 10 层级迁移
#
# 当前维护者：Copilot
# =============================================================================
"""参数工厂入口。"""
import logging

from c302.parameters.model import c302ModelPrototype

# -- 向后兼容：重新导出被测试/外部引用的符号 --
from c302.parameters.custom_types import (  # noqa: F401
    GradedSynapse2,
    IafActivityCell,
)
from c302.parameters.factory.base import _ModelBase, _GradedSynapse2Mixin  # noqa: F401
from c302.parameters.factory.iaf import (  # noqa: F401
    _BC1Model,
    _IafActivityModel,
    _IafModel,
)
from c302.parameters.factory.hh import (  # noqa: F401
    _HHC0Model,
    _HHC1Model,
    _HHModel,
)
from c302.parameters.factory.hh_multi import (  # noqa: F401
    _HHGradedModel,
    _HHMultiCompModel,
)
from c302.parameters.factory.special import _C2Model, _W2DModel  # noqa: F401

logger = logging.getLogger(__name__)


def create_model(level: str) -> c302ModelPrototype:
    """根据层级名称创建参数化模型实例。

    :param level: 层级名称（如 ``"A"``、``"C0"``、``"D1"``）
    :return: 已加载参数的 c302ModelPrototype 实例
    :raises KeyError: 未知的层级名称
    """
    _LEVEL_TO_CLASS: dict[str, type] = {
        "A": _IafModel,
        "B": _IafActivityModel,
        "BC1": _BC1Model,
        "C": _HHModel,
        "C0": _HHC0Model,
        "C1": _HHC1Model,
        "C2": _C2Model,
        "D": _HHMultiCompModel,
        "D1": _HHGradedModel,
        "W2D": _W2DModel,
    }

    level_upper = level.upper()
    cls = _LEVEL_TO_CLASS.get(level_upper)
    if cls is None:
        raise KeyError(
            f"未知的模型层级: {level}，可用: {sorted(_LEVEL_TO_CLASS.keys())}"
        )
    logger.info("创建 %s 层级模型: %s", level_upper, cls.__name__)
    return cls(level_upper)
