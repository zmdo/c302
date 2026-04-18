# =============================================================================
# 功能描述：
#   肌肉电流钳刺激配置脚本。
#   对 MDR01 肌肉细胞施加偏置电流。
#
# 类与方法索引：
#   setup                                (L25)   — 肌肉电流钳测试配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_IClampMuscle.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""IClampMuscle 配置脚本。"""
import logging

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("IClampMuscle")
def setup(
    parameter_set,
    generate_flag=False,
    duration=2000,
    dt=0.05,
    target_directory="examples",
    data_reader=DEFAULT_DATA_READER,
    param_overrides=None,
    config_param_overrides=None,
    verbose=True,
):
    """肌肉电流钳测试配置。

    :return: ``(cells, cells_total, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    my_cells = []
    muscles_to_include = ["MDR01"]
    cells_total = my_cells + muscles_to_include

    reference = "c302_%s_IClampMuscle" % parameter_set
    nml_doc = None

    if generate_flag:
        nml_doc = generate(
            reference,
            params,
            cells=my_cells,
            cells_to_stimulate=muscles_to_include,
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            param_overrides=param_overrides,
            data_reader=data_reader,
        )

    return my_cells, cells_total, params, muscles_to_include, nml_doc
