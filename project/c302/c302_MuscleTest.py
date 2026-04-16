# =============================================================================
# 功能描述：
#   肌肉测试配置脚本。
#   选取运动神经元和肌肉细胞，施加指定电流脉冲，验证肌肉驱动。
#
# 类与方法索引：
#   setup                                (L26)   — 肌肉单元测试配置的 setup 函数
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


def setup(
    parameter_set,
    generate=False,
    duration=2000,
    dt=0.05,
    target_directory="examples",
    data_reader=c302.DEFAULT_DATA_READER,
    param_overrides={},
    verbose=True,
    config_param_overrides={},
):
    """肌肉单元测试配置的 setup 函数。

    配置神经元到肌肉连接的单元测试。
    选取部分运动神经元和对应肌肉，验证神经肌肉接头功能。

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

    params.set_bioparameter(
        "unphysiological_offset_current", "0pA", "Testing TapWithdrawal", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_del", "0 ms", "Testing TapWithdrawal", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_dur", "2000 ms", "Testing TapWithdrawal", "0"
    )

    """
    VA_motors = ["VA%s" % c for c in range_incl(1, 12)]
    VB_motors = ["VB%s" % c for c in range_incl(1, 11)]
    DA_motors = ["DA%s" % c for c in range_incl(1, 9)]
    DB_motors = ["DB%s" % c for c in range_incl(1, 7)]
    DD_motors = ["DD%s" % c for c in range_incl(1, 6)]
    VD_motors = ["VD%s" % c for c in range_incl(1, 13)]
    AS_motors = ["AS%s" % c for c in range_incl(1, 11)]"""

    cells = []

    muscles_to_include = True  # True 表示包含所有肌肉

    if config_param_overrides.has_key("muscles_to_include"):  # 允许外部覆盖
        muscles_to_include = config_param_overrides["muscles_to_include"]

    cells_to_stimulate = []

    cells_to_plot = list(cells)
    reference = "c302_%s_MuscleTest" % parameter_set

    conns_to_include = []
    if config_param_overrides.has_key("conns_to_include"):  # 允许外部限定连接子集
        conns_to_include = config_param_overrides["conns_to_include"]

    conns_to_exclude = ["^.+-.+$"]  # 默认排除包含 '-' 的连接名
    if config_param_overrides.has_key("conns_to_exclude"):
        conns_to_exclude = config_param_overrides["conns_to_exclude"]

    conn_polarity_override = {}
    if config_param_overrides.has_key("conn_polarity_override"):
        conn_polarity_override.update(config_param_overrides["conn_polarity_override"])

    conn_number_override = {}
    if config_param_overrides.has_key("conn_number_override"):
        conn_number_override.update(config_param_overrides["conn_number_override"])

    param_overrides = {
        "ca_conc_decay_time_muscle": "60 ms",
        "ca_conc_rho_muscle": "0.002138919 mol_per_m_per_A_per_s",
    }

    # end = "%sms" % (int(duration) - 100)

    # --- 手动定义的肌肉刺激列表: (cell, start, dur, amp) ---
    input_list = []

    # [备选] 以下为早期试验使用的肌肉刺激组合
    # input_list.append(('MDL02', '0ms', '250ms', '3pA'))
    # input_list.append(('MDL03', '0ms', '250ms', '3pA'))
    # input_list.append(('MDR02', '0ms', '250ms', '3pA'))
    # input_list.append(('MDR03', '0ms', '250ms', '3pA'))

    # 腹侧右侧肌肉 MVR10-15：幅值呈山形分布 (1,2,3,3,2,1 pA)
    input_list.append(("MVR10", "0ms", "250ms", "1pA"))
    input_list.append(("MVR11", "0ms", "250ms", "2pA"))
    input_list.append(("MVR12", "0ms", "250ms", "3pA"))
    input_list.append(("MVR13", "0ms", "250ms", "3pA"))
    input_list.append(("MVR14", "0ms", "250ms", "2pA"))
    input_list.append(("MVR15", "0ms", "250ms", "1pA"))

    # 腹侧左侧肌肉 MVL10-15：同样山形幅值
    input_list.append(("MVL10", "0ms", "250ms", "1pA"))
    input_list.append(("MVL11", "0ms", "250ms", "2pA"))
    input_list.append(("MVL12", "0ms", "250ms", "3pA"))
    input_list.append(("MVL13", "0ms", "250ms", "3pA"))
    input_list.append(("MVL14", "0ms", "250ms", "2pA"))
    input_list.append(("MVL15", "0ms", "250ms", "1pA"))

    # 背侧肌肉 MDL/MDR 21-22
    input_list.append(("MDL21", "0ms", "250ms", "3pA"))
    input_list.append(("MDL22", "0ms", "250ms", "3pA"))
    input_list.append(("MDR21", "0ms", "250ms", "3pA"))
    input_list.append(("MDR22", "0ms", "250ms", "3pA"))

    # 循环生成波浪状肌肉刺激：5 轮× 24 块肌肉，背侧/腹侧交替
    for stim_num in range(5):
        for muscle_num in range(24):
            # 背侧左右肌肉编号（MDL01-MDL24/MDR01-MDR24）
            mdlx = "MDL0%s" % (muscle_num + 1)
            mdrx = "MDR0%s" % (muscle_num + 1)

            mvlx = "MVL0%s" % (muscle_num + 1)
            mvrx = "MVR0%s" % (muscle_num + 1)

            if muscle_num >= 9:  # 编号 ≥10 时不需要前导零
                mdlx = "MDL%s" % (muscle_num + 1)
                mdrx = "MDR%s" % (muscle_num + 1)

                mvlx = "MVL%s" % (muscle_num + 1)
                if muscle_num != 23:
                    mvrx = "MVR%s" % (muscle_num + 1)

            # 背侧肌肉刺激起始时间：每轮 1s + 每块延迟 50ms（波浪传播）
            startd = "%sms" % (stim_num * 1000 + muscle_num * 50)
            # 腹侧肌肉刺激起始时间：比背侧晚 500ms（反相收缩）
            startv = "%sms" % ((stim_num * 1000 + 500) + muscle_num * 50)
            dur = "250ms"
            amp = "3pA"

            input_list.append((mdlx, startd, dur, amp))
            input_list.append((mdrx, startd, dur, amp))

            input_list.append((mvlx, startv, dur, amp))
            input_list.append((mvrx, startv, dur, amp))

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

        if "input" in config_param_overrides:
            input_list = config_param_overrides["input"]

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
    setup_kwargs = dict()
    if len(sys.argv) == 3:
        setup_kwargs["data_reader"] = sys.argv[2]

    # setup(parameter_set, generate=True, data_reader=data_reader)
