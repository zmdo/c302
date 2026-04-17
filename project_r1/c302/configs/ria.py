# =============================================================================
# 功能描述：
#   RIA 中间神经元配置脚本。
#   选取 RIAL/RIAR 及 SMD 辅助神经元，两阶段脉冲刺激。
#
# 类与方法索引：
#   setup                                (L28)   — RIA 单细胞测试配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_RIA.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""RIA 配置脚本。"""
import logging

import neuroml.writers as writers

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.generator.stimulation import add_new_input
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("RIA")
def setup(
    parameter_set,
    generate_flag=False,
    duration=1000,
    dt=0.05,
    target_directory="examples",
    data_reader=DEFAULT_DATA_READER,
    param_overrides=None,
    config_param_overrides=None,
    verbose=True,
):
    """RIA 单细胞测试配置。

    :return: ``(cells, cells_total, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    my_cells = ["RIAL", "RIAR", "SMDDL", "SMDVL"]
    muscles_to_include = []
    cells_total = my_cells + muscles_to_include

    reference = "c302_%s_RIA" % parameter_set
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

        # 两阶段刺激
        add_new_input(nml_doc, "SMDDL", "100ms", "100ms", "4pA", params)
        add_new_input(nml_doc, "SMDVL", "400ms", "100ms", "4pA", params)

        nml_file = target_directory + "/" + reference + ".net.nml"
        writers.NeuroMLWriter.write(nml_doc, nml_file)

    return my_cells, cells_total, params, muscles_to_include, nml_doc
