# =============================================================================
# 功能描述：
#   神经振荡器配置脚本。
#   选取 DB/VB 类运动神经元构建振荡回路，验证节律性活动。
#
# 类与方法索引：
#   setup                                (L20)   — 振荡回路配置的 setup 函数
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
    duration=1000,
    dt=0.05,
    target_directory="examples",
    data_reader=c302.DEFAULT_DATA_READER,
    param_overrides={},
    config_param_overrides={},
    verbose=True,
):
    """振荡回路配置的 setup 函数。

    配置 AVB/DB/VB 等神经元构成的振荡回路。
    通过交互抑制和兴奋产生节律性振荡活动。

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

    params.set_bioparameter("unphysiological_offset_current", "4pA", "Testing Osc", "0")
    params.set_bioparameter(
        "unphysiological_offset_current_del", "100 ms", "Testing Osc", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_dur", "800 ms", "Testing Osc", "0"
    )

    # --- 突触参数调整：拉长抑制衰减 / 降低抑制反转电位 ---
    # [备选] 以下为手动试验时使用的替代突触参数
    # params.set_bioparameter("chem_exc_syn_gbase", ".02 nS", "BlindGuess", "0.1")
    params.set_bioparameter("chem_exc_syn_decay", "5 ms", "BlindGuess", "0.1")

    # params.set_bioparameter("chem_inh_syn_gbase", ".02 nS", "BlindGuess", "0.1")
    params.set_bioparameter("chem_inh_syn_decay", "30 ms", "BlindGuess", "0.1")
    params.set_bioparameter("inh_syn_erev", "-90 mV", "BlindGuess", "0.1")

    # params.set_bioparameter("elec_syn_gbase", "0.001 nS", "BlindGuess", "0.1")

    # --- 运动神经元全集：DB/DD(背侧) + VB/VD(腹侧) ---
    cells = [
        "DB1",
        "DB2",
        "DB3",
        "DB4",
        "DB5",
        "DB6",
        "DB7",
        "DD1",
        "DD2",
        "DD3",
        "DD4",
        "DD5",
        "DD6",
        "VB1",
        "VB10",
        "VB11",
        "VB2",
        "VB3",
        "VB4",
        "VB5",
        "VB6",
        "VB7",
        "VB8",
        "VB9",
        "VD1",
        "VD10",
        "VD11",
        "VD2",
        "VD3",
        "VD4",
        "VD5",
        "VD6",
        "VD7",
        "VD8",
        "VD9",
    ]

    cells = ["DB3", "VB3", "DD3", "VD3", "DB4", "VB4", "DD4", "VD4"]

    # 覆盖为精简子集：DB2-3/VB2-3/DD2-3/VD2-3 + DA2-3/VA2-3
    cells = ["DB2", "VB2", "DD2", "VD2", "DB3", "VB3", "DD3", "VD3"]
    cells += ["DA2", "VA2", "DA3", "VA3"]
    # [备选] 以下为更小范围的振荡器子集配置
    # cells = ['DB3', 'VB3', 'DB4', 'VB4']

    # [备选] 以下为其他命令中间神经元组合与全量细胞配置
    # cells+=['AVBL','PVCL','AVBR','PVCR']
    # cells+=[]
    # cells+=['PVCL', 'PVCR','AVBL','AVBR']
    # cells+=['PLML', 'PLMR','AVAL','AVAR']
    cells += ["AVBL", "AVBR"]  # 添加命令中间神经元作为振荡驱动源
    # cells=None  # implies all cells...

    # [备选] 以下为旧的刺激目标选择方案
    # cells_to_stimulate = ['PVCL','PVCR']
    # cells_to_stimulate = ['PLML','PLMR']
    cells_to_stimulate = ["AVBL", "AVBR"]
    # cells_to_stimulate = ['AVBL']

    # [备选] 以下为手工指定的绘图目标列表
    # cells_to_plot      = ['AVBL','PVCL', 'PVCR', 'DB1','DB2','DB3', 'DB4','DD1','DD2','DD3', 'DD4','DB4','VB1','VB2', 'VB3', 'VB4','VD1','VD2', 'VD3', 'VD4']
    # 绘制直接受刺激与未受刺激神经元，便于对比响应
    cells_to_plot = cells

    reference = "c302_%s_Oscillator" % parameter_set

    muscles_to_include = []

    nml_doc = None

    if generate:
        nml_doc = c302.generate(
            reference,
            params,
            cells=cells,
            cells_to_plot=cells_to_plot,
            cells_to_stimulate=cells_to_stimulate,
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            param_overrides=param_overrides,
            verbose=verbose,
            data_reader=data_reader,
        )

    return cells, cells_to_stimulate, params, muscles_to_include, nml_doc


if __name__ == "__main__":
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else "A"

    setup(parameter_set, generate=True)
