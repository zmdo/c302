# =============================================================================
# 功能描述：
#   前向运动（Forward Locomotion）配置脚本。
#   使用 FW_DATA_READER，大量参数覆盖和波浪肌肉刺激。
#
# 类与方法索引：
#   range_incl                           (L28)   — 生成包含终止值的整数范围
#   setup                                (L39)   — 前向运动配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_FW.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""FW 配置脚本。"""
import logging

import neuroml.writers as writers

from c302.configs import register_config
from c302.generator import FW_DATA_READER, generate
from c302.generator.stimulation import add_new_input
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


def range_incl(start, end):
    """生成包含终止值的整数范围。

    :param start: 起始值（含）
    :param end: 终止值（含）
    :return: range 对象
    """
    return range(start, end + 1)


@register_config("FW")
def setup(
    parameter_set,
    generate_flag=False,
    duration=2000,
    dt=0.05,
    target_directory="examples",
    data_reader=FW_DATA_READER,
    param_overrides=None,
    config_param_overrides=None,
    verbose=True,
):
    """前向运动配置。

    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}
    if config_param_overrides is None:
        config_param_overrides = {}

    params = get_parameter_set(parameter_set)

    # 运动神经元分组
    VB_motors = ["VB%s" % c for c in range_incl(1, 11)]
    DB_motors = ["DB%s" % c for c in range_incl(1, 7)]
    DD_motors = ["DD%s" % c for c in range_incl(1, 6)]
    VD_motors = ["VD%s" % c for c in range_incl(1, 13)]

    cells = list(["AVBL", "AVBR"] + DB_motors + VD_motors + VB_motors + DD_motors)
    muscles_to_include = True
    cells_to_stimulate = []

    reference = "c302_%s_FW" % parameter_set

    conns_to_exclude = ["VB2-VB4_GJ", "VB4-VB2_GJ"]

    # DB→DD / VB→VD 交叉抑制
    conn_polarity_override = {
        r"^DB\d+-DD\d+$": "inh",
        r"^VB\d+-VD\d+$": "inh",
    }
    conn_number_override = {"^.+-.+$": 1}

    # 手动定义肌肉刺激列表
    input_list = []

    # 腹侧肌肉: 山形幅值
    input_list.append(("MVR10", "0ms", "150ms", "1pA"))
    input_list.append(("MVR11", "0ms", "150ms", "2pA"))
    input_list.append(("MVR12", "0ms", "150ms", "3pA"))
    input_list.append(("MVR13", "0ms", "150ms", "3pA"))
    input_list.append(("MVR14", "0ms", "150ms", "2pA"))
    input_list.append(("MVR15", "0ms", "150ms", "1pA"))
    input_list.append(("MVL10", "0ms", "150ms", "1pA"))
    input_list.append(("MVL11", "0ms", "150ms", "2pA"))
    input_list.append(("MVL12", "0ms", "150ms", "3pA"))
    input_list.append(("MVL13", "0ms", "150ms", "3pA"))
    input_list.append(("MVL14", "0ms", "150ms", "2pA"))
    input_list.append(("MVL15", "0ms", "150ms", "1pA"))

    input_list.append(("MDL21", "0ms", "250ms", "3pA"))
    input_list.append(("MDL22", "0ms", "250ms", "3pA"))
    input_list.append(("MDR21", "0ms", "250ms", "3pA"))
    input_list.append(("MDR22", "0ms", "250ms", "3pA"))

    amp = "4pA"
    dur = "250ms"

    # 波浪状肌肉刺激: 15 轮 × 7 块
    for stim_num in range(15):
        for muscle_num in range(7):
            mdlx = "MDL0%s" % (muscle_num + 1)
            mdrx = "MDR0%s" % (muscle_num + 1)
            mvlx = "MVL0%s" % (muscle_num + 1)
            mvrx = "MVR0%s" % (muscle_num + 1)

            if muscle_num >= 9:
                mdlx = "MDL%s" % (muscle_num + 1)
                mdrx = "MDR%s" % (muscle_num + 1)
                mvlx = "MVL%s" % (muscle_num + 1)
                mvrx = "MVR%s" % (muscle_num + 1)

            startd = "%sms" % (stim_num * 800 + muscle_num * 30)
            startv = "%sms" % ((stim_num * 800 + 400) + muscle_num * 30)

            input_list.append((mdlx, startd, dur, amp))
            input_list.append((mdrx, startd, dur, amp))
            if muscle_num != 6:
                input_list.append((mvlx, startv, dur, amp))
                input_list.append((mvrx, startv, dur, amp))

    d_v_delay = 400
    start = 190
    motor_dur = "250ms"

    # AVB 持续背景电流
    input_list.append(("AVBL", "0ms", "1e9ms", "15pA"))
    input_list.append(("AVBR", "0ms", "1e9ms", "15pA"))
    # DB1/VB1 交替脉冲
    input_list.append(("DB1", "%sms" % start, motor_dur, "3pA"))
    input_list.append(("VB1", "%sms" % (start + d_v_delay), motor_dur, "3pA"))

    i = start + 2 * d_v_delay
    j = start + 3 * d_v_delay
    for pulse_num in range(1, 15):
        input_list.append(("DB1", "%sms" % i, motor_dur, "3pA"))
        input_list.append(("VB1", "%sms" % j, motor_dur, "3pA"))
        i += d_v_delay * 2
        j += d_v_delay * 2

    config_param_overrides["input"] = input_list

    # 参数覆盖: 突触权重/间隙连接精细调控
    param_overrides_fw = {
        "mirrored_elec_conn_params": {
            r"^AVB._to_DB\d+\_GJ$_elec_syn_gbase": "0.001 nS",
            r"^AVB._to_VB\d+\_GJ$_elec_syn_gbase": "0.001 nS",
            r"^DB\d+_to_DB\d+\_GJ$_elec_syn_gbase": "0.001 nS",
            r"^VB\d+_to_VB\d+\_GJ$_elec_syn_gbase": "0.001 nS",
            r"^DB\d+_to_VB\d+\_GJ$_elec_syn_gbase": "0 nS",
            r"^DB\d+_to_DD\d+\_GJ$_elec_syn_gbase": "0 nS",
            r"^VB\d+_to_VD\d+\_GJ$_elec_syn_gbase": "0 nS",
            "DD1_to_MVL08_elec_syn_gbase": "0 nS",
            "VD2_to_MDL09_elec_syn_gbase": "0 nS",
        },
        # VB 同类突触参数
        r"^VB\d+_to_VB\d+$_exc_syn_conductance": "18 nS",
        r"^VB\d+_to_VB\d+$_exc_syn_ar": "0.19 per_s",
        r"^VB\d+_to_VB\d+$_exc_syn_ad": "73 per_s",
        r"^VB\d+_to_VB\d+$_exc_syn_beta": "2.81 per_mV",
        r"^VB\d+_to_VB\d+$_exc_syn_vth": "-22 mV",
        r"^VB\d+_to_VB\d+$_exc_syn_erev": "10 mV",
        # DB 同类突触参数
        r"^DB\d+_to_DB\d+$_exc_syn_conductance": "20 nS",
        r"^DB\d+_to_DB\d+$_exc_syn_ar": "0.08 per_s",
        r"^DB\d+_to_DB\d+$_exc_syn_ad": "18 per_s",
        r"^DB\d+_to_DB\d+$_exc_syn_beta": "0.21 per_mV",
        r"^DB\d+_to_DB\d+$_exc_syn_vth": "-10 mV",
        r"^DB\d+_to_DB\d+$_exc_syn_erev": "10 mV",
        "initial_memb_pot": "-50 mV",
        "AVBR_to_DB4_exc_syn_conductance": "0 nS",
        "AVBL_to_VB2_exc_syn_conductance": "0 nS",
        "AVBR_to_VD3_exc_syn_conductance": "0 nS",
        "DD1_to_VB2_inh_syn_conductance": "0 nS",
        # 神经肌肉接头参数
        "neuron_to_muscle_exc_syn_conductance": "0.5 nS",
        r"^DB\d+_to_MDL\d+$_exc_syn_conductance": "0.4 nS",
        r"^DB\d+_to_MDR\d+$_exc_syn_conductance": "0.4 nS",
        r"^VB\d+_to_MVL\d+$_exc_syn_conductance": "0.6 nS",
        r"^VB\d+_to_MVR\d+$_exc_syn_conductance": "0.6 nS",
        "neuron_to_muscle_exc_syn_vth": "37 mV",
        "neuron_to_muscle_inh_syn_conductance": "0.6 nS",
        "neuron_to_neuron_inh_syn_conductance": "0.2 nS",
        "AVBR_to_MVL16_exc_syn_conductance": "0 nS",
        "ca_conc_decay_time_muscle": "60.8 ms",
        "ca_conc_rho_muscle": "0.002338919 mol_per_m_per_A_per_s",
    }

    nml_doc = None

    if generate_flag:
        nml_doc = generate(
            reference,
            params,
            cells=cells,
            cells_to_stimulate=cells_to_stimulate,
            conns_to_exclude=conns_to_exclude,
            conn_polarity_override=conn_polarity_override,
            conn_number_override=conn_number_override,
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            data_reader=data_reader,
            param_overrides=param_overrides_fw,
        )

        for stim_input in input_list:
            cell, start_ms, dur_ms, current = stim_input
            add_new_input(nml_doc, cell, start_ms, dur_ms, current, params)

        nml_file = target_directory + "/" + reference + ".net.nml"
        writers.NeuroMLWriter.write(nml_doc, nml_file)

    return cells, cells_to_stimulate, params, muscles_to_include, nml_doc
