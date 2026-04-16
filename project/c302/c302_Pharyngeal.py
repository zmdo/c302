# =============================================================================
# 功能描述：
#   咽部神经系统配置脚本。
#   选取 I1–I6、M1–M5、MI、MC、NSM 等咽部神经元，构建咽泵回路。
#
# 类与方法索引：
#   setup                                (L20)   — 咽部摄食回路配置的 setup 函数
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
    duration=500,
    dt=0.01,
    target_directory="examples",
    data_reader=c302.DEFAULT_DATA_READER,
    param_overrides={},
    config_param_overrides={},
    verbose=True,
):
    """咽部摄食回路配置的 setup 函数。

    配置咽部神经系统的摄食回路。
    选取 I1-I6、M1-M5、MC、MI、NSM 等 20 个咽部神经元，
    验证摄食泵送节律。

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
        "unphysiological_offset_current", "2.2pA", "Testing Pharyngeal", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_del", "50ms", "Testing Pharyngeal", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_dur", "200ms", "Testing Pharyngeal", "0"
    )

    # --- 咽部神经元：M 系列（肌肉运动）、I 系列（中间）、MI/NSM/MC ---
    cells = [
        "M1",
        "M2L",
        "M2R",
        "M3L",
        "M3R",
        "M4",
        "M5",
        "I1L",
        "I1R",
        "I2L",
        "I2R",
        "I3",
        "I4",
        "I5",
        "I6",
        "MI",
        "NSML",
        "NSMR",
        "MCL",
        "MCR",
    ]
    # 刺激子集：从 20 个咽部神经元中选取 10 个
    cells_to_stimulate = [
        "M1",
        "M3R",
        "M4",
        "M5",
        "I1L",
        "I4",
        "I5",
        "I6",
        "MCL",
        "MCR",
    ]

    reference = "c302_%s_Pharyngeal" % parameter_set

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

    return cells, cells_to_stimulate, params, [], nml_doc


if __name__ == "__main__":
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else "A"

    setup(parameter_set, generate=True)
