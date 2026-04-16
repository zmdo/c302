# =============================================================================
# 功能描述：
#   目标肌肉配置脚本。
#   选取少量运动神经元和肌肉细胞，验证目标肌肉激活。
#
# 类与方法索引：
#   setup                                (L20)   — 目标肌肉测试配置的 setup 函数
#
# 更新日志：
#   2026-04-16  Copilot  计划2 阶段八收尾：补记汇总校验与最终勘误完成
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
    duration=3000,
    dt=0.05,
    target_directory="examples",
    data_reader=c302.DEFAULT_DATA_READER,
    param_overrides={},
    config_param_overrides={},
    verbose=True,
):
    """目标肌肉测试配置的 setup 函数。

    配置目标肌肉的单元测试。
    仅包含少量神经元和肌肉，用于验证特定肌肉的响应。

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
        "unphysiological_offset_current", "15pA", "Testing IClamp", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_del", "1 ms", "Testing IClamp", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_dur", "20 ms", "Testing IClamp", "0"
    )

    duration = 300

    my_cells = ["AVKR"]
    my_cells = ["RMHR"]  # 覆盖上行：最终选用 RMHR 运动神经元
    muscles_to_include = None  # None 表示包含所有肌肉

    cells = my_cells

    reference = "c302_%s_TargetMuscle" % parameter_set

    nml_doc = None

    if generate:
        nml_doc = c302.generate(
            reference,
            params,
            cells=cells,
            cells_to_stimulate=cells,
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            param_overrides=param_overrides,
            verbose=verbose,
            data_reader=data_reader,
            print_connections=True,
        )

    return cells, cells, params, muscles_to_include, nml_doc


if __name__ == "__main__":
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else "A"

    setup(parameter_set, generate=True)
