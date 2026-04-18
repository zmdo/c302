# =============================================================================
# 功能描述：
#   社交决策回路配置脚本。
#   选取 RMGR、ASHR、ASKR、AWBR、IL2R 等感觉/中间神经元。
#
# 类与方法索引：
#   setup                                (L28)   — 社交决策回路配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_Social.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""Social 配置脚本。"""
import logging

import neuroml.writers as writers

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.generator.stimulation import add_new_input
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("Social")
def setup(
    parameter_set,
    generate_flag=False,
    duration=2500,
    dt=0.05,
    target_directory="examples",
    data_reader=DEFAULT_DATA_READER,
    param_overrides=None,
    config_param_overrides=None,
    verbose=True,
):
    """社交决策回路配置。

    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    cells = ["RMGR", "ASHR", "ASKR", "AWBR", "IL2R", "RMHR", "URXR"]
    cells_to_stimulate = []

    reference = "c302_%s_Social" % parameter_set
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

        # 依次施加阶跃电流，间隔 300ms
        stim_amplitude = "5pA"
        add_new_input(nml_doc, "RMGR", "100ms", "200ms", stim_amplitude, params)
        add_new_input(nml_doc, "ASHR", "400ms", "200ms", stim_amplitude, params)
        add_new_input(nml_doc, "ASKR", "700ms", "200ms", stim_amplitude, params)
        add_new_input(nml_doc, "AWBR", "1000ms", "200ms", stim_amplitude, params)
        add_new_input(nml_doc, "IL2R", "1300ms", "200ms", stim_amplitude, params)
        add_new_input(nml_doc, "RMHR", "1600ms", "200ms", stim_amplitude, params)
        add_new_input(nml_doc, "URXR", "1900ms", "200ms", stim_amplitude, params)

        nml_file = target_directory + "/" + reference + ".net.nml"
        writers.NeuroMLWriter.write(nml_doc, nml_file)

    return cells, cells_to_stimulate, params, [], nml_doc
