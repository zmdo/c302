# =============================================================================
# 功能描述：
#   突触连接测试配置脚本。
#   选取 URYDL、SMDDR、VB11 等少量神经元，测试 4 种突触类型。
#
# 类与方法索引：
#   setup                                (L28)   — 突触连接测试配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_Syns.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""Syns 配置脚本。"""
import logging

import neuroml.writers as writers

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.generator.stimulation import add_new_input
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("Syns")
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
    """突触连接测试配置。

    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    stim_amplitudes = ["1pA", "5pA"]
    duration = len(stim_amplitudes) * 1800

    params.set_bioparameter(
        "unphysiological_offset_current_del", "50 ms", "Testing IClamp", "0"
    )

    # 测试 4 种突触类型
    exc_pre = "URYDL"       # 兴奋性突触·突触前
    exc_post = "SMDDR"      # 兴奋性突触·突触后
    inh_pre = "VD12"        # 抑制性突触·突触前
    inh_post = "VB11"       # 抑制性突触·突触后
    gap_1 = "AIZL"          # 间隙连接·细胞 1
    gap_2 = "ASHL"          # 间隙连接·细胞 2
    moto_pre = "AS2"        # 神经肌肉接头·运动神经元
    muscle_post = "MDL07"   # 神经肌肉接头·肌肉

    cells = [exc_pre, exc_post, inh_pre, inh_post, moto_pre]
    cells_to_stimulate_extra = [exc_pre, inh_pre, moto_pre]
    muscles_to_include = [muscle_post]

    # 参数 A 无间隙连接模型
    if parameter_set != "A":
        cells.append(gap_1)
        cells.append(gap_2)
        cells_to_stimulate_extra.append(gap_1)

    reference = "c302_%s_Syns" % parameter_set
    nml_doc = None

    if generate_flag:
        nml_doc = generate(
            reference,
            params,
            cells=cells,
            cells_to_stimulate=[],
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            param_overrides=param_overrides,
            data_reader=data_reader,
        )

        # 逐级递增电流
        for i in range(len(stim_amplitudes)):
            start = "%sms" % (i * 1400 + 500)
            for c in cells_to_stimulate_extra:
                add_new_input(nml_doc, c, start, "800ms", stim_amplitudes[i], params)

        nml_file = target_directory + "/" + reference + ".net.nml"
        writers.NeuroMLWriter.write(nml_doc, nml_file)

    return cells, cells_to_stimulate_extra, params, [], nml_doc
