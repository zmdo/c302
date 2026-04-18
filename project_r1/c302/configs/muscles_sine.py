# =============================================================================
# 功能描述：
#   正弦波肌肉刺激配置脚本。
#   向 AVBL 施加正弦波电流驱动运动神经元-肌肉网络。
#
# 类与方法索引：
#   setup                                (L28)   — 正弦波驱动肌肉网络配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_MusclesSine.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""MusclesSine 配置脚本。"""
import logging

import neuroml.writers as writers
from neuroml import Input, InputList, SineGenerator

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("MusclesSine")
def setup(
    parameter_set,
    generate_flag=False,
    duration=1000,
    dt=0.05,
    target_directory="examples",
    data_reader=DEFAULT_DATA_READER,
    param_overrides=None,
    config_param_overrides=None,
    verbose=True,
):
    """正弦波驱动肌肉网络配置。

    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    params.set_bioparameter(
        "unphysiological_offset_current", "0pA", "Disabling offset current", "0"
    )
    params.set_bioparameter("chem_exc_syn_decay", "5 ms", "BlindGuess", "0.1")
    params.set_bioparameter("chem_inh_syn_decay", "200 ms", "BlindGuess", "0.1")

    cells = [
        "AS1", "AS10", "AS11", "AS2", "AS3", "AS4", "AS5", "AS6",
        "AS7", "AS8", "AS9",
        "AVFL", "AVFR", "AVKR", "AVL",
        "CEPVL", "CEPVR",
        "DA1", "DA2", "DA3", "DA4", "DA5", "DA6", "DA7", "DA8", "DA9",
        "DB1", "DB2", "DB3", "DB4", "DB5", "DB6", "DB7",
        "DD1", "DD2", "DD3", "DD4", "DD5", "DD6",
        "DVB",
        "HSNL", "HSNR",
        "IL1DL", "IL1DR", "IL1L", "IL1R", "IL1VL", "IL1VR",
        "PDA", "PDB",
        "PVNL", "PVNR",
        "RID", "RIML", "RIMR", "RIVL", "RIVR",
        "RMDDL", "RMDDR", "RMDL", "RMDR", "RMDVL", "RMDVR",
        "RMED", "RMEL", "RMER", "RMEV",
        "RMFL", "RMGL", "RMGR", "RMHL", "RMHR",
        "SMBDL", "SMBDR", "SMBVL", "SMBVR",
        "SMDDL", "SMDDR", "SMDVL", "SMDVR",
        "URADL", "URADR", "URAVL", "URAVR",
        "VA1", "VA10", "VA11", "VA12", "VA2", "VA3", "VA4", "VA5",
        "VA6", "VA7", "VA8", "VA9",
        "VB1", "VB10", "VB11", "VB2", "VB3", "VB4", "VB5", "VB6",
        "VB7", "VB8", "VB9",
        "VC1", "VC2", "VC3", "VC4", "VC5", "VC6",
        "VD1", "VD10", "VD11", "VD12", "VD13", "VD2", "VD3", "VD4",
        "VD5", "VD6", "VD7", "VD8", "VD9",
        "AVAL", "AVAR", "AVBL", "AVBR", "AVDL", "AVDR", "PVCL", "PVCR",
    ]

    cells_to_stimulate = ["AVBL", "AVBR"]
    cells_to_plot = [
        "AVBL", "AVBR", "PVCL", "PVCR",
        "DB1", "DB2", "VB1", "VB2",
        "DD1", "DD2", "VD1", "VD2",
    ]

    muscles_to_include = True
    reference = "c302_%s_MusclesSine" % parameter_set
    nml_doc = None

    if generate_flag:
        nml_doc = generate(
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
            data_reader=data_reader,
        )

        # 正弦波刺激发生器
        sw_input = SineGenerator(
            id="NewSineWaveInput",
            delay="100ms",
            phase="0",
            duration="800ms",
            amplitude="4.5pA",
            period="200ms",
        )
        nml_doc.sine_generators.append(sw_input)

        # 将正弦波刺激添加到 AVBL
        cell = "AVBL"
        input_list = InputList(
            id="Input_%s_%s" % (cell, sw_input.id),
            component=sw_input.id,
            populations="%s" % cell,
        )
        input_list.input.append(
            Input(
                id=0,
                target="../%s/0/GenericNeuronCell" % cell,
                destination="synapses",
            )
        )
        nml_doc.networks[0].input_lists.append(input_list)

        nml_file = target_directory + "/" + reference + ".net.nml"
        writers.NeuroMLWriter.write(nml_doc, nml_file)

    return cells, cells_to_stimulate, params, muscles_to_include, nml_doc
