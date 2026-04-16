# =============================================================================
# 功能描述：
#   突触连接测试配置脚本。
#   选取 URYDL、SMDDR、IL2VL 等少量神经元，测试突触生成。
#
# 类与方法索引：
#   setup                                (L20)   — 突触连接测试配置的 setup 函数
#
# 更新日志：
#   2026-04-16  Copilot  添加中文 docstring 和行内注释
#
# 当前维护者：Copilot
# =============================================================================
import c302
import sys
import neuroml.writers as writers
import importlib


def setup(
    parameter_set,
    generate=False,
    duration=500,
    dt=0.05,
    target_directory="examples",
    data_reader=c302.DEFAULT_DATA_READER,
    param_overrides={},
    config_param_overrides={},
    verbose=True,
):
    """突触连接测试配置的 setup 函数。

    配置少量神经元对的突触连接测试。
    选取 URYDL/SMDDR/VB11 等细胞，验证各类突触模型的功能。

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

    stim_amplitudes = ["1pA", "5pA"]
    duration = (len(stim_amplitudes)) * 1800

    params.set_bioparameter(
        "unphysiological_offset_current_del", "50 ms", "Testing IClamp", "0"
    )

    # --- 测试 4 种突触类型：兴奋性/抑制性化学突触、间隙连接、神经肌肉接头 ---
    exc_pre = "URYDL"       # 兴奋性突触·突触前
    exc_post = "SMDDR"      # 兴奋性突触·突触后
    inh_pre = "VD12"        # 抑制性突触·突触前
    inh_post = "VB11"       # 抑制性突触·突触后
    gap_1 = "AIZL"          # 间隙连接·细胞 1
    gap_2 = "ASHL"          # 间隙连接·细胞 2
    moto_pre = "AS2"        # 神经肌肉接头·运动神经元
    muscle_post = "MDL07"   # 神经肌肉接头·肌肉细胞

    cells = [exc_pre, exc_post, inh_pre, inh_post, moto_pre]
    cells_to_stimulate_extra = [exc_pre, inh_pre, moto_pre]
    muscles_to_include = [muscle_post]

    if parameter_set != "A":  # 参数 A 无间隙连接模型，仅 B 以上层级添加
        cells.append(gap_1)
        cells.append(gap_2)
        cells_to_stimulate_extra.append(gap_1)

    reference = "c302_%s_Syns" % parameter_set

    nml_doc = None

    if generate:
        nml_doc = c302.generate(
            reference,
            params,
            cells=cells,
            cells_to_stimulate=[],
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            param_overrides=param_overrides,
            verbose=verbose,
            data_reader=data_reader,
        )

    # 逐级递增电流：每 1400ms 切换到下一级幅值
    for i in range(len(stim_amplitudes)):
        start = "%sms" % (i * 1400 + 500)  # 起始 = i*1400+500
        for c in cells_to_stimulate_extra:
            c302.add_new_input(nml_doc, c, start, "800ms", stim_amplitudes[i], params)

    nml_file = target_directory + "/" + reference + ".net.nml"
    writers.NeuroMLWriter.write(
        nml_doc, nml_file
    )  # Write over network file written above...

    c302.print_("(Re)written network file to: " + nml_file)

    return cells, cells_to_stimulate_extra, params, [], nml_doc


if __name__ == "__main__":
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else "A"

    setup(parameter_set, generate=True)
