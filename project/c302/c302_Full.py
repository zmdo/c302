# =============================================================================
# 功能描述：
#   全连接组（302 神经元）配置脚本。
#   随机选取部分神经元施加脉冲刺激，用于整体网络行为验证。
#
# 类与方法索引：
#   setup                                (L20)   — 全连接组配置（302 神经元）的 setup 函数
#
# 更新日志：
#   2026-04-16  Copilot  添加中文 docstring 和行内注释
#
# 当前维护者：Copilot
# =============================================================================
import c302
import sys

import importlib


def setup(
    parameter_set,
    generate=False,
    duration=1000,
    dt=0.05,
    target_directory="examples",
    muscles_to_include=None,  # None 表示包含全部肌肉
    data_reader=c302.DEFAULT_DATA_READER,
    param_overrides={},
    config_param_overrides={},
    verbose=True,
):
    """全连接组配置（302 神经元）的 setup 函数。

    配置 c302 全连接组网络，包含 302 个神经元。
    随机选取部分神经元施加脉冲刺激，用于整体网络行为验证。

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

    # 随机选取的神经元集合（含感觉、中间和咽部神经元）
    cells_to_stimulate = [
        "ADAL",
        "ADAR",
        "M1",
        "M2L",
        "M3L",
        "M3R",
        "M4",
        "I1R",
        "I2L",
        "I5",
        "I6",
        "MI",
        "NSMR",
        "MCL",
        "ASEL",
        "AVEL",
        "AWAR",
        "DB1",
        "DVC",
        "RIAR",
        "RMDDL",
    ]
    cells_to_stimulate = ["PVCL", "PVCR"]
    cells_to_stimulate = ["PLML", "PLMR"]  # 最终选用：PLM 触觉感觉神经元
    # [备选] 以下为旧的刺激目标配置
    # cells_to_stimulate = ['AVBL','AVBR']

    # 绘图目标：混合刺激/非刺激神经元以对比响应
    cells_to_plot = ["ADAL", "ADAR", "PVDR", "BDUR", "I1R", "I2L"]
    cells_to_plot = [
        "AVBL",
        "AVBR",
        "PVCL",
        "PVCR",
        "DB1",
        "DB2",
        "VB1",
        "VB2",
        "DD1",
        "DD2",
        "VD1",
        "VD2",
    ]

    params.set_bioparameter(
        "unphysiological_offset_current", "5pA", "Testing Full net", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_del", "50 ms", "Testing Full net", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_dur", "900 ms", "Testing Full net", "0"
    )

    reference = "c302_%s_Full" % parameter_set

    cell_names, conns = c302.get_cell_names_and_connection(data_reader)

    nml_doc = None

    if generate:
        nml_doc = c302.generate(
            reference,
            params,
            cells_to_plot=cells_to_plot,
            cells_to_stimulate=cells_to_stimulate,
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            vmin=-72 if parameter_set == "A" else -52,
            vmax=-48 if parameter_set == "A" else -28,
            target_directory=target_directory,
            param_overrides=param_overrides,
            verbose=verbose,
            data_reader=data_reader,
        )

    return cell_names, cells_to_stimulate, params, muscles_to_include, nml_doc


if __name__ == "__main__":
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else "A"

    setup(parameter_set, generate=True)
