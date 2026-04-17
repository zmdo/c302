# =============================================================================
# 功能描述：
#   运动神经元 + 肌肉网络配置脚本。
#   选取约 130 个运动和命令神经元，包含全部体壁肌肉。
#
# 类与方法索引：
#   setup                                (L25)   — 运动神经元 + 肌肉网络配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_Muscles.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""Muscles 配置脚本。"""
import logging

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("Muscles")
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
    """运动神经元 + 肌肉网络配置。

    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    params.set_bioparameter(
        "chem_exc_syn_decay", "3ms", "BlindGuess", "0.1"
    )
    params.set_bioparameter(
        "chem_inh_syn_decay", "30ms", "BlindGuess", "0.1"
    )

    cells = [
        "AVBL", "AVBR",
        "DB1", "DB2", "DB3", "DB4", "DB5", "DB6", "DB7",
        "VB1", "VB2", "VB3", "VB4", "VB5", "VB6", "VB7",
        "VB8", "VB9", "VB10", "VB11",
        "DD1", "DD2", "DD3", "DD4", "DD5", "DD6",
        "VD1", "VD2", "VD3", "VD4", "VD5", "VD6", "VD7",
        "VD8", "VD9", "VD10", "VD11", "VD12", "VD13",
        "DA1", "DA2", "DA3", "DA4", "DA5", "DA6", "DA7", "DA8", "DA9",
        "VA1", "VA2", "VA3", "VA4", "VA5", "VA6", "VA7",
        "VA8", "VA9", "VA10", "VA11", "VA12",
        "AS1", "AS2", "AS3", "AS4", "AS5", "AS6", "AS7",
        "AS8", "AS9", "AS10", "AS11",
        "AVAL", "AVAR",
        "PVCL", "PVCR",
        "AVDL", "AVDR",
        "DVA",
        "PVDL", "PVDR",
        "PLML", "PLMR",
        "AVM", "ALML", "ALMR",
        "RID",
    ]

    muscles_to_include = True
    cells_to_stimulate = ["AVBL", "AVBR"]

    reference = "c302_%s_Muscles" % parameter_set
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
