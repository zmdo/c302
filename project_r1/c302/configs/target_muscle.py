# =============================================================================
# 功能描述：
#   目标肌肉输出配置脚本。
#   选取 RMHR 神经元，包含全部体壁肌肉，时长 300ms。
#
# 类与方法索引：
#   setup                                (L25)   — 目标肌肉输出配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_TargetMuscle.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""TargetMuscle 配置脚本。"""
import logging

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("TargetMuscle")
def setup(
    parameter_set,
    generate_flag=False,
    duration=300,
    dt=0.05,
    target_directory="examples",
    data_reader=DEFAULT_DATA_READER,
    param_overrides=None,
    config_param_overrides=None,
    verbose=True,
):
    """目标肌肉输出配置。

    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    cells = ["RMHR"]
    muscles_to_include = True
    cells_to_stimulate = cells

    reference = "c302_%s_TargetMuscle" % parameter_set
    nml_doc = None

    if generate_flag:
        nml_doc = generate(
            reference,
            params,
            cells=cells,
            cells_to_stimulate=cells_to_stimulate,
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            param_overrides=param_overrides,
            data_reader=data_reader,
        )

    return cells, cells_to_stimulate, params, muscles_to_include, nml_doc
