# =============================================================================
# 功能描述：
#   社交决策回路配置脚本。
#   选取 RMGR、ASHR、ASKR、AWBR、IL2R 等感觉/中间神经元，
#   模拟线虫群聚/独居行为的决策过程。
#
# 类与方法索引：
#   setup                                (L24)   — 社交决策回路配置的 setup 函数
#
# 更新日志：
#   2026-04-16  Copilot  计划2 阶段八收尾：补记汇总校验与最终勘误完成
#   2026-04-16  Copilot  添加中文 docstring 和行内注释
#
# 当前维护者：Copilot
# =============================================================================
import c302

import neuroml.writers as writers

import sys
import importlib


def setup(
    parameter_set,
    generate=False,
    duration=2500,
    dt=0.05,
    target_directory="examples",
    data_reader=c302.DEFAULT_DATA_READER,
    param_overrides={},
    config_param_overrides={},
    verbose=True,
):
    """社交决策回路配置的 setup 函数。

    配置社交决策回路（群聚/独居行为）。
    选取 RMGR、ASHR、ASKR、AWBR、IL2R 等感觉和中间神经元，
    模拟线虫对社交信号的决策过程。

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

    # 社交回路关键神经元：RMG(枢纽)、ASH/ASK/AWB(感觉)、IL2/RMH/URX
    cells = ["RMGR", "ASHR", "ASKR", "AWBR", "IL2R", "RMHR", "URXR"]
    cells_to_stimulate = []

    reference = "c302_%s_Social" % parameter_set

    nml_doc = None

    if generate:
        nml_doc = c302.generate(
            reference,
            params,
            cells=cells,
            cells_to_stimulate=cells_to_stimulate,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            param_overrides=param_overrides,
            verbose=verbose,
            data_reader=data_reader,
        )

    # 依次向各感觉/中间神经元施加阶跃电流，间隔 300ms
    stim_amplitude = "5pA"
    c302.add_new_input(nml_doc, "RMGR", "100ms", "200ms", stim_amplitude, params)
    c302.add_new_input(nml_doc, "ASHR", "400ms", "200ms", stim_amplitude, params)
    c302.add_new_input(nml_doc, "ASKR", "700ms", "200ms", stim_amplitude, params)
    c302.add_new_input(nml_doc, "AWBR", "1000ms", "200ms", stim_amplitude, params)
    c302.add_new_input(nml_doc, "IL2R", "1300ms", "200ms", stim_amplitude, params)
    c302.add_new_input(nml_doc, "RMHR", "1600ms", "200ms", stim_amplitude, params)
    c302.add_new_input(nml_doc, "URXR", "1900ms", "200ms", stim_amplitude, params)

    nml_file = target_directory + "/" + reference + ".net.nml"
    writers.NeuroMLWriter.write(
        nml_doc, nml_file
    )  # 覆盖前面生成的网络文件...

    c302.print_("(Re)written network file to: " + nml_file)

    return cells, cells_to_stimulate, params, [], nml_doc


if __name__ == "__main__":
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else "A"

    setup(parameter_set, generate=True)
