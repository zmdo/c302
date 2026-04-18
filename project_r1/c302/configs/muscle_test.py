# =============================================================================
# 功能描述：
#   肌肉波浪刺激测试配置脚本。
#   对体壁肌肉施加波浪状阶跃电流，验证肌肉响应。
#
# 类与方法索引：
#   setup                                (L28)   — 肌肉波浪刺激测试配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_MuscleTest.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""MuscleTest 配置脚本。"""
import logging

import neuroml.writers as writers

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.generator.stimulation import add_new_input
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("MuscleTest")
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
    """肌肉波浪刺激测试配置。

    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}
    if config_param_overrides is None:
        config_param_overrides = {}

    params = get_parameter_set(parameter_set)

    params.set_bioparameter(
        "unphysiological_offset_current", "0pA", "Testing TapWithdrawal", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_del", "0 ms", "Testing TapWithdrawal", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_dur", "2000 ms", "Testing TapWithdrawal", "0"
    )

    cells = []
    muscles_to_include = True

    # 允许外部覆盖
    if "muscles_to_include" in config_param_overrides:
        muscles_to_include = config_param_overrides["muscles_to_include"]

    cells_to_stimulate = []

    conns_to_include = []
    if "conns_to_include" in config_param_overrides:
        conns_to_include = config_param_overrides["conns_to_include"]

    conns_to_exclude = ["^.+-.+$"]
    if "conns_to_exclude" in config_param_overrides:
        conns_to_exclude = config_param_overrides["conns_to_exclude"]

    conn_polarity_override = {}
    if "conn_polarity_override" in config_param_overrides:
        conn_polarity_override.update(config_param_overrides["conn_polarity_override"])

    conn_number_override = {}
    if "conn_number_override" in config_param_overrides:
        conn_number_override.update(config_param_overrides["conn_number_override"])

    param_overrides = {
        "ca_conc_decay_time_muscle": "60 ms",
        "ca_conc_rho_muscle": "0.002138919 mol_per_m_per_A_per_s",
    }

    reference = "c302_%s_MuscleTest" % parameter_set

    # 手动定义肌肉刺激列表
    input_list = []

    # 腹侧右/左侧肌肉：幅值呈山形分布
    input_list.append(("MVR10", "0ms", "250ms", "1pA"))
    input_list.append(("MVR11", "0ms", "250ms", "2pA"))
    input_list.append(("MVR12", "0ms", "250ms", "3pA"))
    input_list.append(("MVR13", "0ms", "250ms", "3pA"))
    input_list.append(("MVR14", "0ms", "250ms", "2pA"))
    input_list.append(("MVR15", "0ms", "250ms", "1pA"))
    input_list.append(("MVL10", "0ms", "250ms", "1pA"))
    input_list.append(("MVL11", "0ms", "250ms", "2pA"))
    input_list.append(("MVL12", "0ms", "250ms", "3pA"))
    input_list.append(("MVL13", "0ms", "250ms", "3pA"))
    input_list.append(("MVL14", "0ms", "250ms", "2pA"))
    input_list.append(("MVL15", "0ms", "250ms", "1pA"))

    # 背侧肌肉
    input_list.append(("MDL21", "0ms", "250ms", "3pA"))
    input_list.append(("MDL22", "0ms", "250ms", "3pA"))
    input_list.append(("MDR21", "0ms", "250ms", "3pA"))
    input_list.append(("MDR22", "0ms", "250ms", "3pA"))

    # 波浪状肌肉刺激: 5 轮 × 24 块, 背侧/腹侧交替
    for stim_num in range(5):
        for muscle_num in range(24):
            mdlx = "MDL0%s" % (muscle_num + 1)
            mdrx = "MDR0%s" % (muscle_num + 1)
            mvlx = "MVL0%s" % (muscle_num + 1)
            mvrx = "MVR0%s" % (muscle_num + 1)

            if muscle_num >= 9:
                mdlx = "MDL%s" % (muscle_num + 1)
                mdrx = "MDR%s" % (muscle_num + 1)
                mvlx = "MVL%s" % (muscle_num + 1)
                if muscle_num != 23:
                    mvrx = "MVR%s" % (muscle_num + 1)

            # 背侧起始: 每轮 1s + 每块延迟 50ms
            startd = "%sms" % (stim_num * 1000 + muscle_num * 50)
            # 腹侧起始: 比背侧晚 500ms（反相收缩）
            startv = "%sms" % ((stim_num * 1000 + 500) + muscle_num * 50)
            dur = "250ms"
            amp = "3pA"

            input_list.append((mdlx, startd, dur, amp))
            input_list.append((mdrx, startd, dur, amp))
            input_list.append((mvlx, startv, dur, amp))
            input_list.append((mvrx, startv, dur, amp))

    nml_doc = None

    if generate_flag:
        nml_doc = generate(
            reference,
            params,
            cells=cells,
            cells_to_plot=list(cells),
            cells_to_stimulate=cells_to_stimulate,
            conns_to_include=conns_to_include,
            conns_to_exclude=conns_to_exclude,
            conn_polarity_override=conn_polarity_override,
            conn_number_override=conn_number_override,
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            data_reader=data_reader,
            param_overrides=param_overrides,
        )

        if "input" in config_param_overrides:
            input_list = config_param_overrides["input"]

        for stim_input in input_list:
            cell, start, dur, current = stim_input
            add_new_input(nml_doc, cell, start, dur, current, params)

        nml_file = target_directory + "/" + reference + ".net.nml"
        writers.NeuroMLWriter.write(nml_doc, nml_file)

    return cells, cells_to_stimulate, params, muscles_to_include, nml_doc
