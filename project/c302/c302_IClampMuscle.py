# =============================================================================
# 功能描述：
#   肌肉电流钳刺激配置脚本。
#   对 MDL08 肌肉细胞施加阶跃电流，验证肌肉模型响应。
#
# 类与方法索引：
#   setup                                (L20)   — 肌肉电流钳配置的 setup 函数
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
    duration=2000,
    dt=0.05,
    target_directory="examples",
    data_reader=c302.DEFAULT_DATA_READER,
    param_overrides={},
    verbose=True,
):
    """肌肉电流钳配置的 setup 函数。

    配置肌肉细胞的电流钳注入测试。
    用于验证肌肉模型在刺激下的膜电位响应。

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

    my_cells = []
    muscles_to_include = ["MDR01"]  # 目标肌肉：背侧右第 1 行肌肉

    cells = my_cells
    cells_total = my_cells + muscles_to_include

    reference = "c302_%s_IClampMuscle" % parameter_set
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

    return cells, cells_total, params, muscles_to_include, nml_doc


if __name__ == "__main__":
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else "A"

    setup(parameter_set, generate=True)
