# =============================================================================
# 功能描述：
#   振荡器回路配置脚本。
#   选取 DB/VB/DD/VD 2-3 + DA/VA 2-3 及 AVBL/R 共 14 个神经元。
#
# 类与方法索引：
#   setup                                (L25)   — 振荡器回路配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_Oscillator.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""Oscillator 配置脚本。"""
import logging

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("Oscillator")
def setup(
    parameter_set,
    generate_flag=False,
    duration=500,
    dt=0.05,
    target_directory="examples",
    data_reader=DEFAULT_DATA_READER,
    param_overrides=None,
    config_param_overrides=None,
    verbose=True,
):
    """振荡器回路配置。

    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    params.set_bioparameter(
        "inh_syn_erev", "-90mV", "BlindGuess", "0.1"
    )
    params.set_bioparameter(
        "unphysiological_offset_current", "3pA", "Testing Oscillator", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_del", "50 ms", "Testing Oscillator", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_dur", "200 ms", "Testing Oscillator", "0"
    )

    cells = [
        "DB2", "DB3",
        "VB2", "VB3",
        "DD2", "DD3",
        "VD2", "VD3",
        "DA2", "DA3",
        "VA2", "VA3",
        "AVBL", "AVBR",
    ]
    muscles_to_include = []
    cells_to_stimulate = ["AVBL", "AVBR"]

    reference = "c302_%s_Oscillator" % parameter_set
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
