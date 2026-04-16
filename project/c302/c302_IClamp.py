# =============================================================================
# 功能描述：
#   电流钳（IClamp）单细胞刺激配置脚本。
#   对 ADAL 神经元施加阶跃电流，用于验证单个神经元响应。
#
# 类与方法索引：
#   setup                                (L21)   — 电流钳测试配置的 setup 函数
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
    duration=None,
    dt=0.05,
    target_directory="examples",
    data_reader=c302.DEFAULT_DATA_READER,
    param_overrides={},
    config_param_overrides={},
    verbose=True,
):
    """电流钳测试配置的 setup 函数。

    配置单个或少量神经元的电流钳注入测试。
    用于验证单细胞模型在不同参数层级下的响应特性。

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
    reference = "c302_%s_IClamp" % parameter_set
    c302.print_("Setting up %s" % reference)

    ParameterisedModel = getattr(
        importlib.import_module("c302.parameters_%s" % parameter_set),
        "ParameterisedModel",
    )
    params = ParameterisedModel()

    # 递增电流幅值序列，每级持续 1s
    stim_amplitudes = ["1pA", "2pA", "3pA", "4pA", "5pA", "6pA"]
    if duration is None:
        duration = (len(stim_amplitudes)) * 1000  # 总时长 = 级数 × 1000ms

    my_cells = ["ADAL", "PVCL"]
    muscles_to_include = ["MDR01"]

    cells = my_cells
    cells_total = my_cells + muscles_to_include

    nml_doc = None

    if generate:
        c302.print_("Generating %s" % reference)

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

        # 逐级施加递增电流：每 1000ms 切换到下一级幅值
        for i in range(len(stim_amplitudes)):
            start = "%sms" % (i * 1000 + 100)  # 每级起始 = i*1000+100
            for c in cells_total:
                c302.add_new_input(
                    nml_doc, c, start, "800ms", stim_amplitudes[i], params
                )

        nml_file = target_directory + "/" + reference + ".net.nml"
        writers.NeuroMLWriter.write(
            nml_doc, nml_file
        )  # 覆盖前面生成的网络文件...

        c302.print_("(Re)written network file to: " + nml_file)

    return cells, cells_total, params, muscles_to_include, nml_doc


if __name__ == "__main__":
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else "A"

    setup(parameter_set, generate=True)
