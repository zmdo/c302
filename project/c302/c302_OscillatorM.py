# =============================================================================
# 功能描述：
#   含肌肉的振荡器配置脚本。
#   在神经振荡器基础上增加体壁肌肉，验证肌肉驱动的节律性运动。
#
# 类与方法索引：
#   setup                                (L20)   — 振荡驱动肌肉配置的 setup 函数
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
    """振荡驱动肌肉配置的 setup 函数。

    配置振荡回路驱动的肌肉网络。
    在振荡回路基础上添加运动神经元到肌肉的连接，
    验证节律性运动输出。

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
        "unphysiological_offset_current", "1.5pA", "Testing Osc", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_del", "500 ms", "Testing Osc", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_dur", "1200 ms", "Testing Osc", "0"
    )

    # [备选] 以下为较高初始膜电位的旧试验配置
    # params.set_bioparameter("initial_memb_pot", "-62 mV", "Testing Osc", "0")

    # [备选] 以下为手动试验时使用的替代突触参数
    # params.set_bioparameter("chem_exc_syn_gbase", ".2 nS", "BlindGuess", "0.1")
    # params.set_bioparameter("chem_exc_syn_decay", "5 ms", "BlindGuess", "0.1")

    # params.set_bioparameter("chem_inh_syn_gbase", ".2 nS", "BlindGuess", "0.1")
    # params.set_bioparameter("chem_inh_syn_decay", "30 ms", "BlindGuess", "0.1")
    # params.set_bioparameter("inh_syn_erev", "-90 mV", "BlindGuess", "0.1")

    params.set_bioparameter(
        "neuron_to_neuron_elec_syn_gbase", "0.0001 nS", "BlindGuess", "0.1"
    )

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
        "VB2",
        "VB3",
        "VB4",
        "VB5",
        "VB6",
        "VB7",
        "VB8",
        "VB9",
        "VB10",
        "VB11",
        "VD1",
        "VD2",
        "VD3",
        "VD4",
        "VD5",
        "VD6",
        "VD7",
        "VD8",
        "VD9",
        "VD10",
        "VD11",
        "VD12",
        "VD13",
    ]

    # DA 系列：背侧 A 类运动神经元
    cells += ["DA1", "DA2", "DA3", "DA4", "DA5", "DA6", "DA7", "DA8", "DA9"]
    # VA 系列：腹侧 A 类运动神经元
    cells += [
        "VA1",
        "VA2",
        "VA3",
        "VA4",
        "VA5",
        "VA6",
        "VA7",
        "VA8",
        "VA9",
        "VA10",
        "VA11",
        "VA12",
    ]

    # [备选] 以下为更小范围的振荡器子集配置
    # cells = ['DB2', 'VB2', 'DD2', 'VD2', 'DB3', 'VB3', 'DD3', 'VD3', 'DB4', 'VB4', 'DD4', 'VD4']
    # cells = ['DB3', 'VB3', 'DD3', 'VD3']
    # cells += ['DA2', 'VA2','DA3','VA3']
    # cells = ['DB3', 'VB3', 'DB4', 'VB4']

    # [备选] 以下为其他命令中间神经元组合与全量细胞配置
    # cells+=['AVBL','PVCL','AVBR','PVCR']
    # cells+=[]
    cells += ["PVCL", "PVCR", "AVBL", "AVBR"]  # 命令中间神经元
    # cells+=['AVAL','AVAR']
    # cells+=['AVBL','AVBR']
    # cells=None  # implies all cells...

    # [备选] 以下为旧的刺激目标选择方案
    # cells = ['AVBR', 'VB2', 'VD3', 'DB3', 'DD2']
    # cells = ['VB2', 'VD3']

    # cells_to_stimulate = ['PVCL','PVCR']
    # cells_to_stimulate = ['PLML','PLMR']
    cells_to_stimulate = ["AVBR"]
    cells_to_stimulate = ["VB1", "VB2"]  # 最终选用：VB1/VB2 腹侧运动神经元
    # cells_to_stimulate = ['AVAL']

    # [备选] 以下为手工指定的绘图目标列表
    # cells_to_plot      = ['AVBL','PVCL', 'PVCR', 'DB1','DB2','DB3', 'DB4','DD1','DD2','DD3', 'DD4','DB4','VB1','VB2', 'VB3', 'VB4','VD1','VD2', 'VD3', 'VD4']
    # 绘制直接受刺激与未受刺激神经元，便于对比响应
    cells_to_plot = cells

    reference = "c302_%s_OscillatorM" % parameter_set

    muscles_to_include = None  # None 表示包含所有肌肉
    muscles_to_include = []  # 覆盖：实际不含肌肉（仅纯神经元振荡）

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
