# =============================================================================
# 功能描述：
#   全运动神经元振荡器配置脚本。
#   包含 DB/DD/VB/VD/DA/VA 全系列运动神经元 + PVC/AVB 命令神经元。
#
# 类与方法索引：
#   setup                                (L25)   — 全运动神经元振荡器配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_OscillatorM.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""OscillatorM 配置脚本。"""
import logging

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("OscillatorM")
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
    """全运动神经元振荡器配置。

    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    params.set_bioparameter(
        "unphysiological_offset_current", "1.5pA", "Testing Osc", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_del", "500 ms", "Testing Osc", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_dur", "1200 ms", "Testing Osc", "0"
    )
    params.set_bioparameter(
        "neuron_to_neuron_elec_syn_gbase", "0.0001 nS", "BlindGuess", "0.1"
    )

    cells = [
        "DB1", "DB2", "DB3", "DB4", "DB5", "DB6", "DB7",
        "DD1", "DD2", "DD3", "DD4", "DD5", "DD6",
        "VB1", "VB2", "VB3", "VB4", "VB5", "VB6", "VB7",
        "VB8", "VB9", "VB10", "VB11",
        "VD1", "VD2", "VD3", "VD4", "VD5", "VD6", "VD7",
        "VD8", "VD9", "VD10", "VD11", "VD12", "VD13",
        "DA1", "DA2", "DA3", "DA4", "DA5", "DA6", "DA7", "DA8", "DA9",
        "VA1", "VA2", "VA3", "VA4", "VA5", "VA6", "VA7",
        "VA8", "VA9", "VA10", "VA11", "VA12",
        "PVCL", "PVCR", "AVBL", "AVBR",
    ]

    cells_to_stimulate = ["VB1", "VB2"]
    muscles_to_include = []

    reference = "c302_%s_OscillatorM" % parameter_set
    nml_doc = None

    if generate_flag:
        nml_doc = generate(
            reference,
            params,
            cells=cells,
            cells_to_plot=cells,
            cells_to_stimulate=cells_to_stimulate,
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            param_overrides=param_overrides,
            data_reader=data_reader,
        )

    return cells, cells_to_stimulate, params, muscles_to_include, nml_doc
