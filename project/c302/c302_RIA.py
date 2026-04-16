# =============================================================================
# 功能描述：
#   RIA 中间神经元配置脚本。
#   选取 RIAL/RIAR 及连接神经元，验证 RIA 中间层信号处理。
#
# 类与方法索引：
#   setup                                (L20)   — RIA 单细胞测试配置的 setup 函数
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
    duration=1000,
    dt=0.05,
    target_directory="examples",
    data_reader=c302.DEFAULT_DATA_READER,
    param_overrides={},
    verbose=True,
):
    """RIA 单细胞测试配置的 setup 函数。

    配置 RIA 中间神经元的单细胞测试。
    仅包含 RIAL/RIAR 两个细胞，用于验证单细胞模型响应。

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

    # RIA 左/右 + SMD 辅助神经元（用于验证 RIA 信号传播）
    my_cells = ["RIAL", "RIAR", "SMDDL", "SMDVL"]
    muscles_to_include = []

    cells = my_cells
    cells_total = my_cells + muscles_to_include

    reference = "c302_%s_RIA" % parameter_set
    nml_doc = None

    if generate:
        nml_doc = c302.generate(
            reference,
            params,
            cells=cells,
            cells_to_stimulate=muscles_to_include,
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            param_overrides=param_overrides,
            verbose=verbose,
            data_reader=data_reader,
        )

        # 两阶段刺激：100ms 刺激 SMDDL，400ms 刺激 SMDVL
        start1 = "100ms"
        dur1 = "100ms"
        stim_amplitude1 = "4pA"
        start2 = "400ms"
        dur2 = "100ms"
        stim_amplitude2 = "4pA"

        c302.add_new_input(nml_doc, "SMDDL", start1, dur1, stim_amplitude1, params)
        c302.add_new_input(nml_doc, "SMDVL", start2, dur2, stim_amplitude2, params)

        nml_file = target_directory + "/" + reference + ".net.nml"
        writers.NeuroMLWriter.write(
            nml_doc, nml_file
        )  # 覆盖前面生成的网络文件...

        c302.print_("(Re)written network file to: " + nml_file)

    return cells, cells_total, params, muscles_to_include, nml_doc


if __name__ == "__main__":
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else "D1"

    setup(parameter_set, generate=True)
