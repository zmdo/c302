# =============================================================================
# 功能描述：
#   正向运动（Forward locomotion）配置脚本。
#   选取 DB/VB 类运动神经元及中间神经元，构建正向运动回路。
#
# 类与方法索引：
#   range_incl                           (L27)   — 生成包含终止值的整数范围
#   setup                                (L39)   — 前行运动回路配置的 setup 函数
#
# 更新日志：
#   2026-04-16  Copilot  计划2 阶段八收尾：补记汇总校验与最终勘误完成
#   2026-04-16  Copilot  添加中文 docstring 和行内注释
#
# 当前维护者：Copilot
# =============================================================================
import sys
import os
import importlib

sys.path.insert(0, os.path.abspath("."))

import c302

import neuroml.writers as writers


def range_incl(start, end):
    """生成包含终止值的整数范围。

    等效于 ``range(start, end + 1)``。

    :param start: 起始值（含）
    :param end: 终止值（含）
    :return: range 对象
    """
    return range(start, end + 1)


def setup(
    parameter_set,
    generate=False,
    duration=2000,
    dt=0.05,
    target_directory="examples",
    data_reader=c302.FW_DATA_READER,
    param_overrides={},
    verbose=True,
    config_param_overrides={},
):
    """前行运动回路配置的 setup 函数。

    配置 c302 前行（Forward）运动回路。
    选取 AVB、DB、VB 等前行运动相关神经元，
    通过参数覆盖调节突触连接权重以产生前行波。

    :param parameter_set: 参数层级（``A``/``B``/``C``/``C0``/``C1``/``C2``/``D``/``D1``/``W2D``）
    :param generate: 是否生成 NeuroML 文件
    :param duration: 仿真时长（毫秒）
    :param dt: 仿真时间步长（毫秒）
    :param target_directory: 输出目录
    :param data_reader: 数据读取器名称
    :param param_overrides: 生物参数覆盖字典
    :param config_param_overrides: 配置级参数覆盖字典
    :param verbose: 是否输出详细日志
    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)`` 五元组
    """
    ParameterisedModel = getattr(
        importlib.import_module("c302.parameters_%s" % parameter_set),
        "ParameterisedModel",
    )
    params = ParameterisedModel()

    """
    VA_motors = ["VA%s" % c for c in range_incl(1, 12)]
    DA_motors = ["DA%s" % c for c in range_incl(1, 9)]
    AS_motors = ["AS%s" % c for c in range_incl(1, 11)]"""

    # --- 前行运动神经元分组 ---
    VB_motors = ["VB%s" % c for c in range_incl(1, 11)]   # 腹侧 B 类（11 个）
    DB_motors = ["DB%s" % c for c in range_incl(1, 7)]     # 背侧 B 类（7 个）
    DD_motors = ["DD%s" % c for c in range_incl(1, 6)]     # 背侧 D 类抑制（6 个）
    VD_motors = ["VD%s" % c for c in range_incl(1, 13)]   # 腹侧 D 类抑制（13 个）

    # AVB 命令神经元 + 各类运动神经元
    cells = list(["AVBL", "AVBR"] + DB_motors + VD_motors + VB_motors + DD_motors)

    muscles_to_include = True  # True 表示包含所有肌肉

    cells_to_stimulate = []

    cells_to_plot = list(cells)
    reference = "c302_%s_FW" % parameter_set

    conns_to_include = []
    conns_to_exclude = [
        "VB2-VB4_GJ",
        "VB4-VB2_GJ",
    ]
    # --- 连接极性覆盖：DB→DD / VB→VD 均设为抑制性 ---
    conn_polarity_override = {
        r"^DB\d+-DD\d+$": "inh",    # 背侧 B→D 交叉抑制
        r"^VB\d+-VD\d+$": "inh",    # 腹侧 B→D 交叉抑制
    }
    conn_number_override = {
        "^.+-.+$": 1,  # 所有连接均归一化为 1 个突触
    }

    # --- 手动定义肌肉刺激，随后通过循环追加 ---
    input_list = []

    """dur = '250ms'
    amp = '3pA'
    for muscle_num in range(24):
        mdlx = 'MDL0%s' % (muscle_num + 1)
        mdrx = 'MDR0%s' % (muscle_num + 1)
        #mvlx = 'MVL0%s' % (muscle_num + 1)
        #mvrx = 'MVR0%s' % (muscle_num + 1)
        
        if muscle_num >= 9:
            mdlx = 'MDL%s' % (muscle_num + 1)
            mdrx = 'MDR%s' % (muscle_num + 1)
            #mvlx = 'MVL%s' % (muscle_num + 1)
            #mvrx = 'MVR%s' % (muscle_num + 1)

        
        startd = '%sms' % (muscle_num * 10)
        #startv = '%sms' % ((stim_num * 800 + 400) + muscle_num * 30)
        
        input_list.append((mdlx, startd, dur, amp))
        input_list.append((mdrx, startd, dur, amp))"""

    # 腹侧右侧肌肉 MVR10-15：山形幅值 (1,2,3,3,2,1 pA)
    input_list.append(("MVR10", "0ms", "150ms", "1pA"))
    input_list.append(("MVR11", "0ms", "150ms", "2pA"))
    input_list.append(("MVR12", "0ms", "150ms", "3pA"))
    input_list.append(("MVR13", "0ms", "150ms", "3pA"))
    input_list.append(("MVR14", "0ms", "150ms", "2pA"))
    input_list.append(("MVR15", "0ms", "150ms", "1pA"))

    # 腹侧左侧肌肉 MVL10-15
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

    # 循环生成波浪状肌肉刺激：15 轮× 7 块肌肉，背侧/腹侧交替
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

            # 背侧肌肉起始时间 = 轮次*800ms + 肌肉序号*30ms
            startd = "%sms" % (stim_num * 800 + muscle_num * 30)
            # 腹侧肌肉比背侧晚 400ms
            startv = "%sms" % ((stim_num * 800 + 400) + muscle_num * 30)

            input_list.append((mdlx, startd, dur, amp))
            input_list.append((mdrx, startd, dur, amp))
            if muscle_num != 6:
                input_list.append((mvlx, startv, dur, amp))
                input_list.append((mvrx, startv, dur, amp))

    d_v_delay = 400  # 背-腹侧交替延迟（ms）

    start = 190  # 运动神经元刺激起始时间
    motor_dur = "250ms"

    # AVB 持续高幅值背景电流（全程驱动）
    input_list.append(("AVBL", "0ms", "1e9ms", "15pA"))
    input_list.append(("AVBR", "0ms", "1e9ms", "15pA"))
    # DB1/VB1 交替脉冲，间隔 d_v_delay
    input_list.append(("DB1", "%sms" % (start), motor_dur, "3pA"))
    input_list.append(("VB1", "%sms" % (start + d_v_delay), motor_dur, "3pA"))

    # 循环生成 DB1/VB1 交替脉冲序列（14 对）
    i = start + 2 * d_v_delay
    j = start + 3 * d_v_delay
    for pulse_num in range(1, 15):
        input_list.append(("DB1", "%sms" % i, motor_dur, "3pA"))
        input_list.append(("VB1", "%sms" % j, motor_dur, "3pA"))
        i += d_v_delay * 2
        j += d_v_delay * 2

    # [备选] 以下为短时 AVB 背景电流配置，已由上方长时输入列表替代
    # input_list = []
    # input_list.append(('AVBL', '0ms', '1900ms', '15pA'))
    # input_list.append(('AVBR', '0ms', '1900ms', '15pA'))

    config_param_overrides["input"] = input_list

    # --- 参数覆盖：突触权重/间隙连接精细调控 ---
    param_overrides = {
        # -- 间隙连接电导（镜像对称）--
        "mirrored_elec_conn_params": {
            r"^AVB._to_DB\d+\_GJ$_elec_syn_gbase": "0.001 nS",
            r"^AVB._to_VB\d+\_GJ$_elec_syn_gbase": "0.001 nS",
            r"^DB\d+_to_DB\d+\_GJ$_elec_syn_gbase": "0.001 nS",
            # [备选] 以下为曾尝试的缝隙连接门控参数
            #'^DB\d+_to_DB\d+\_GJ$_elec_syn_p_gbase': '0.08 nS',
            #'^DB\d+_to_DB\d+\_GJ$_elec_syn_sigma': '0.2 per_mV',
            #'^DB\d+_to_DB\d+\_GJ$_elec_syn_mu': '-20 mV',
            r"^VB\d+_to_VB\d+\_GJ$_elec_syn_gbase": "0.001 nS",
            #'^VB\d+_to_VB\d+\_GJ$_elec_syn_p_gbase': '0.1 nS',
            #'^VB\d+_to_VB\d+\_GJ$_elec_syn_sigma': '0.3 per_mV',
            #'^VB\d+_to_VB\d+\_GJ$_elec_syn_mu': '-30 mV',
            #'VB2_to_VB4_elec_syn_gbase': '0 nS',
            r"^DB\d+_to_VB\d+\_GJ$_elec_syn_gbase": "0 nS",
            r"^DB\d+_to_DD\d+\_GJ$_elec_syn_gbase": "0 nS",
            r"^VB\d+_to_VD\d+\_GJ$_elec_syn_gbase": "0 nS",
            #'^VD\d+_to_DD\d+\_GJ$_elec_syn_gbase': '0 nS',
            "DD1_to_MVL08_elec_syn_gbase": "0 nS",
            "VD2_to_MDL09_elec_syn_gbase": "0 nS",
        },
        # -- VB 同类突触参数 --
        r"^VB\d+_to_VB\d+$_exc_syn_conductance": "18 nS",
        r"^VB\d+_to_VB\d+$_exc_syn_ar": "0.19 per_s",
        r"^VB\d+_to_VB\d+$_exc_syn_ad": "73 per_s",
        r"^VB\d+_to_VB\d+$_exc_syn_beta": "2.81 per_mV",
        r"^VB\d+_to_VB\d+$_exc_syn_vth": "-22 mV",
        r"^VB\d+_to_VB\d+$_exc_syn_erev": "10 mV",
        # -- DB 同类突触参数 --
        r"^DB\d+_to_DB\d+$_exc_syn_conductance": "20 nS",
        r"^DB\d+_to_DB\d+$_exc_syn_ar": "0.08 per_s",
        r"^DB\d+_to_DB\d+$_exc_syn_ad": "18 per_s",
        r"^DB\d+_to_DB\d+$_exc_syn_beta": "0.21 per_mV",
        r"^DB\d+_to_DB\d+$_exc_syn_vth": "-10 mV",
        r"^DB\d+_to_DB\d+$_exc_syn_erev": "10 mV",
        "initial_memb_pot": "-50 mV",
        "AVBR_to_DB4_exc_syn_conductance": "0 nS",
        #'VB4_to_VB5_exc_syn_conductance': '0 nS',
        "AVBL_to_VB2_exc_syn_conductance": "0 nS",
        "AVBR_to_VD3_exc_syn_conductance": "0 nS",
        # [备选] 以下为整体关闭部分化学突触的旧参数组合
        #'^DB\d+_to_DD\d+$_exc_syn_conductance': '0 nS',
        #'^DD\d+_to_DB\d+$_inh_syn_conductance': '0 nS',
        #'^VB\d+_to_VD\d+$_exc_syn_conductance': '0 nS',
        #'^VD\d+_to_VB\d+$_inh_syn_conductance': '0 nS',
        "DD1_to_VB2_inh_syn_conductance": "0 nS",
        # -- 神经肌肉接头参数 --
        "neuron_to_muscle_exc_syn_conductance": "0.5 nS",
        r"^DB\d+_to_MDL\d+$_exc_syn_conductance": "0.4 nS",
        r"^DB\d+_to_MDR\d+$_exc_syn_conductance": "0.4 nS",
        r"^VB\d+_to_MVL\d+$_exc_syn_conductance": "0.6 nS",
        r"^VB\d+_to_MVR\d+$_exc_syn_conductance": "0.6 nS",
        "neuron_to_muscle_exc_syn_vth": "37 mV",
        "neuron_to_muscle_inh_syn_conductance": "0.6 nS",
        "neuron_to_neuron_inh_syn_conductance": "0.2 nS",
        # [备选] 以下为单条连接的手动覆盖方案
        #'DB2_to_MDL11_exc_syn_conductance': '1 nS',
        "AVBR_to_MVL16_exc_syn_conductance": "0 nS",
        "ca_conc_decay_time_muscle": "60.8 ms",
        "ca_conc_rho_muscle": "0.002338919 mol_per_m_per_A_per_s",
    }

    nml_doc = None
    if generate:
        nml_doc = c302.generate(
            reference,
            params,
            cells=cells,
            cells_to_plot=cells_to_plot,
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
            verbose=verbose,
        )

        # [废弃] 以下为旧版从配置覆盖字典回读 input 列表的兼容逻辑
        # if config_param_overrides.has_key('input'):
        #    input_list = config_param_overrides['input']

        for stim_input in input_list:
            cell, start, dur, current = stim_input
            c302.add_new_input(nml_doc, cell, start, dur, current, params)

        nml_file = target_directory + "/" + reference + ".net.nml"
        writers.NeuroMLWriter.write(
            nml_doc, nml_file
        )  # 覆盖前面生成的网络文件...

        c302.print_("(Re)written network file to: " + nml_file)

    return cells, cells_to_stimulate, params, muscles_to_include, nml_doc


if __name__ == "__main__":
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else "C2"
    data_reader = sys.argv[2] if len(sys.argv) == 3 else c302.FW_DATA_READER

    setup(parameter_set, generate=True, data_reader=data_reader)
