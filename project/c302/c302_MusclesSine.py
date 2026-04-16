# =============================================================================
# 功能描述：
#   正弦波肌肉刺激配置脚本。
#   向体壁肌肉施加正弦波电流，模拟节律性收缩。
#
# 类与方法索引：
#   setup                                (L19)   — 正弦驱动肌肉配置的 setup 函数
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
    data_reader=c302.DEFAULT_DATA_READER,
    param_overrides={},
    config_param_overrides={},
    verbose=True,
):
    """正弦驱动肌肉配置的 setup 函数。

    配置使用正弦波信号驱动的肌肉网络。
    对运动神经元施加正弦波电流刺激，
    验证肌肉系统对周期性输入的响应。

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
        "unphysiological_offset_current", "0pA", "Disabling offset current", "0"
    )

    # --- 突触衰减参数调整 ---
    # [备选] 以下为手动试验时使用的替代突触参数
    # params.set_bioparameter("exc_syn_conductance", ".20 nS", "BlindGuess", "0.1")
    params.set_bioparameter("chem_exc_syn_decay", "5 ms", "BlindGuess", "0.1")

    # params.set_bioparameter("inh_syn_conductance", ".35 nS", "BlindGuess", "0.1")
    params.set_bioparameter("chem_inh_syn_decay", "200 ms", "BlindGuess", "0.1")

    # params.set_bioparameter("elec_syn_gbase", "0.001 nS", "BlindGuess", "0.1")

    # --- 运动神经元全集（与 c302_Muscles 相同）---
    cells = [
        "AS1",
        "AS10",
        "AS11",
        "AS2",
        "AS3",
        "AS4",
        "AS5",
        "AS6",
        "AS7",
        "AS8",
        "AS9",
        "AVFL",
        "AVFR",
        "AVKR",
        "AVL",
        "CEPVL",
        "CEPVR",
        "DA1",
        "DA2",
        "DA3",
        "DA4",
        "DA5",
        "DA6",
        "DA7",
        "DA8",
        "DA9",
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
        "DVB",
        "HSNL",
        "HSNR",
        "IL1DL",
        "IL1DR",
        "IL1L",
        "IL1R",
        "IL1VL",
        "IL1VR",
        "PDA",
        "PDB",
        "PVNL",
        "PVNR",
        "RID",
        "RIML",
        "RIMR",
        "RIVL",
        "RIVR",
        "RMDDL",
        "RMDDR",
        "RMDL",
        "RMDR",
        "RMDVL",
        "RMDVR",
        "RMED",
        "RMEL",
        "RMER",
        "RMEV",
        "RMFL",
        "RMGL",
        "RMGR",
        "RMHL",
        "RMHR",
        "SMBDL",
        "SMBDR",
        "SMBVL",
        "SMBVR",
        "SMDDL",
        "SMDDR",
        "SMDVL",
        "SMDVR",
        "URADL",
        "URADR",
        "URAVL",
        "URAVR",
        "VA1",
        "VA10",
        "VA11",
        "VA12",
        "VA2",
        "VA3",
        "VA4",
        "VA5",
        "VA6",
        "VA7",
        "VA8",
        "VA9",
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
        "VC1",
        "VC2",
        "VC3",
        "VC4",
        "VC5",
        "VC6",
        "VD1",
        "VD10",
        "VD11",
        "VD12",
        "VD13",
        "VD2",
        "VD3",
        "VD4",
        "VD5",
        "VD6",
        "VD7",
        "VD8",
        "VD9",
    ]

    cells += ["AVAL", "AVAR", "AVBL", "AVBR", "AVDL", "AVDR", "PVCL", "PVCR"]  # 命令中间神经元
    # [备选] 以下为直接包含全部细胞的旧配置
    # cells=None  # implies all cells...

    # [调试] 以下为按概率随机挑选刺激神经元的旧实验代码
    # probability = 0.1
    cells_to_stimulate = []
    """
    for cell in cells:
        #if random.random()<probability:
        #    cells_to_stimulate.append(cell)
        if cell.startswith("xxVB") or cell.startswith("DB"):
            cells_to_stimulate.append(cell)"""
    # [备选] 以下为早期使用过的刺激目标组合
    # cells_to_stimulate = ['DB1', 'VB1']

    # cells_to_stimulate = ['PVCL', 'AVBL']
    # cells_to_stimulate.extend(['DB1', 'VB1'])
    # cells_to_stimulate = ['PVCL','PVCR']
    # cells_to_stimulate = ['PLML','PLMR']
    cells_to_stimulate = ["AVBL", "AVBR"]

    # [备选] 以下为更完整的绘图目标列表
    # cells_to_plot      = ['AS1', 'AS10', 'AVFL', 'DA1','DB1','DB4','DB7','IL1DL','RID', 'RIML','SMBDL', 'SMBDR', 'VB1', 'VB5', 'VB10','VC1', 'VC2']
    # 绘制部分直接受刺激与未受刺激神经元，便于对比响应
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

    reference = "c302_%s_MusclesSine" % parameter_set

    muscles_to_include = True  # True 表示包含所有肌肉并绘图
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

    # --- 正弦波电流发生器：用于代替阶跃电流刺激 ---
    # 从 libNeuroML 导入正弦波输入相关类型
    from neuroml import SineGenerator, InputList, Input
    import neuroml.writers as writers

    # 创建正弦波发生器（周期 200ms、幅值 4.5pA）
    sw_input = SineGenerator(
        id="NewSineWaveInput",
        delay="100ms",
        phase="0",
        duration="800ms",
        amplitude="4.5pA",
        period="200ms",
    )

    nml_doc.sine_generators.append(sw_input)

    # 将正弦波刺激添加到 AVBL 神经元
    cell = "AVBL"

    # 创建 InputList 并绑定到目标神经元的突触端
    input_list = InputList(
        id="Input_%s_%s" % (cell, sw_input.id),
        component=sw_input.id,
        populations="%s" % cell,
    )
    input_list.input.append(
        Input(id=0, target="../%s/0/GenericNeuronCell" % cell, destination="synapses")
    )
    nml_doc.networks[0].input_lists.append(input_list)

    # 覆盖前面已经生成的网络文件...
    nml_file = target_directory + "/" + reference + ".net.nml"
    writers.NeuroMLWriter.write(nml_doc, nml_file)

    c302.print_("(Re)written network file to: " + nml_file)

    return cells, cells_to_stimulate, params, muscles_to_include, nml_doc


if __name__ == "__main__":
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else "A"

    setup(parameter_set, generate=True)
