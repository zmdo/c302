# =============================================================================
# 功能描述：
#   咽部神经系统配置脚本。
#   选取 I1–I6、M1–M5、MI、MC、NSM 等 20 个咽部神经元。
#
# 类与方法索引：
#   setup                                (L25)   — 咽部摄食回路配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_Pharyngeal.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""Pharyngeal 配置脚本。"""
import logging

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("Pharyngeal")
def setup(
    parameter_set,
    generate_flag=False,
    duration=500,
    dt=0.01,
    target_directory="examples",
    data_reader=DEFAULT_DATA_READER,
    param_overrides=None,
    config_param_overrides=None,
    verbose=True,
):
    """咽部摄食回路配置。

    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    params.set_bioparameter(
        "unphysiological_offset_current", "2.2pA", "Testing Pharyngeal", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_del", "50ms", "Testing Pharyngeal", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_dur", "200ms", "Testing Pharyngeal", "0"
    )

    cells = [
        "M1", "M2L", "M2R", "M3L", "M3R", "M4", "M5",
        "I1L", "I1R", "I2L", "I2R", "I3", "I4", "I5", "I6",
        "MI", "NSML", "NSMR", "MCL", "MCR",
    ]
    cells_to_stimulate = [
        "M1", "M3R", "M4", "M5", "I1L", "I4", "I5", "I6", "MCL", "MCR",
    ]

    reference = "c302_%s_Pharyngeal" % parameter_set
    nml_doc = None

    if generate_flag:
        nml_doc = generate(
            reference,
            params,
            cells=cells,
            cells_to_stimulate=cells_to_stimulate,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            param_overrides=param_overrides,
            data_reader=data_reader,
        )

    return cells, cells_to_stimulate, params, [], nml_doc
