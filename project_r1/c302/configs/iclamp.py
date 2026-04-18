# =============================================================================
# 功能描述：
#   电流钳（IClamp）单细胞刺激配置脚本。
#   对 ADAL / PVCL 神经元和 MDR01 肌肉施加递增阶跃电流。
#
# 类与方法索引：
#   setup                                (L28)   — 电流钳测试配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_IClamp.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""IClamp 配置脚本。"""
import logging

import neuroml.writers as writers

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.generator.stimulation import add_new_input
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("IClamp")
def setup(
    parameter_set,
    generate_flag=False,
    duration=None,
    dt=0.05,
    target_directory="examples",
    data_reader=DEFAULT_DATA_READER,
    param_overrides=None,
    config_param_overrides=None,
    verbose=True,
):
    """电流钳测试配置。

    :param parameter_set: 参数层级
    :param generate_flag: 是否生成 NeuroML 文件
    :param duration: 仿真时长（ms）
    :param dt: 时间步长（ms）
    :param target_directory: 输出目录
    :param data_reader: 数据读取器
    :param param_overrides: 参数覆盖字典
    :param config_param_overrides: 配置级参数覆盖
    :param verbose: 详细输出
    :return: ``(cells, cells_total, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    # 递增电流幅值序列，每级持续 1s
    stim_amplitudes = ["1pA", "2pA", "3pA", "4pA", "5pA", "6pA"]
    if duration is None:
        duration = len(stim_amplitudes) * 1000

    my_cells = ["ADAL", "PVCL"]
    muscles_to_include = ["MDR01"]
    cells_total = my_cells + muscles_to_include

    reference = "c302_%s_IClamp" % parameter_set
    nml_doc = None

    if generate_flag:
        nml_doc = generate(
            reference,
            params,
            cells=my_cells,
            cells_to_stimulate=[],
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            param_overrides=param_overrides,
            data_reader=data_reader,
        )

        # 逐级施加递增电流
        for i in range(len(stim_amplitudes)):
            start = "%sms" % (i * 1000 + 100)
            for c in cells_total:
                add_new_input(nml_doc, c, start, "800ms", stim_amplitudes[i], params)

        # 覆盖写出网络文件
        nml_file = target_directory + "/" + reference + ".net.nml"
        writers.NeuroMLWriter.write(nml_doc, nml_file)

    return my_cells, cells_total, params, muscles_to_include, nml_doc
