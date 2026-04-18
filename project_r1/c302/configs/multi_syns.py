# =============================================================================
# 功能描述：
#   多突触连接测试配置脚本。
#   选取 URYDL、SMDDR 等 6 个神经元，验证多种突触连接类型。
#
# 类与方法索引：
#   setup                                (L28)   — 多突触连接测试配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_MultiSyns.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""MultiSyns 配置脚本。"""
import logging

import neuroml.writers as writers

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.generator.stimulation import add_new_input
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("MultiSyns")
def setup(
    parameter_set,
    generate_flag=False,
    duration=1000,
    dt=0.1,
    target_directory="examples",
    data_reader=DEFAULT_DATA_READER,
    param_overrides=None,
    config_param_overrides=None,
    verbose=True,
):
    """多突触连接测试配置。

    原脚本仅有 __main__ 执行块，已重构为 setup() 函数。

    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    cells = ["URYDL", "SMDDR", "ADAL", "RIML", "IL2VL", "RIPL"]
    cells_to_stimulate = []

    reference = "c302_%s_MultiSyns" % parameter_set
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
            data_reader=data_reader,
        )

        # 分时段阶跃电流
        stim_amplitude = "0.35nA"
        add_new_input(nml_doc, "URYDL", "100ms", "200ms", stim_amplitude, params)
        add_new_input(nml_doc, "ADAL", "400ms", "200ms", stim_amplitude, params)
        add_new_input(nml_doc, "IL2VL", "700ms", "200ms", stim_amplitude, params)

        nml_file = target_directory + "/" + reference + ".net.nml"
        writers.NeuroMLWriter.write(nml_doc, nml_file)

    return cells, cells_to_stimulate, params, [], nml_doc
