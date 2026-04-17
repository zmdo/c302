# =============================================================================
# 功能描述：
#   触碰回缩反射配置脚本（开发中）。
#   构建触觉感觉→中间→运动神经元回路，模拟触碰回缩行为。
#
# 类与方法索引：
#   range_incl                           (L28)   — 生成包含终止值的整数范围
#   setup                                (L39)   — 触碰退缩反射配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_TapWithdrawal.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""TapWithdrawal 配置脚本（开发中）。"""
import logging

import neuroml.writers as writers

from c302.configs import register_config
from c302.generator import FW_DATA_READER, generate
from c302.generator.stimulation import add_new_sinusoidal_input
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


def range_incl(start, end):
    """生成包含终止值的整数范围。

    :param start: 起始值（含）
    :param end: 终止值（含）
    :return: range 对象
    """
    return range(start, end + 1)


@register_config("TapWithdrawal")
def setup(
    parameter_set,
    generate_flag=False,
    duration=400,
    dt=0.05,
    target_directory="examples",
    data_reader=FW_DATA_READER,
    param_overrides=None,
    config_param_overrides=None,
    verbose=True,
):
    """触碰退缩反射配置。

    注意：该回路仍在开发中，尚不能产生正确行为。

    :return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    params.set_bioparameter(
        "unphysiological_offset_current", "0pA", "Testing TapWithdrawal", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_del", "0 ms", "Testing TapWithdrawal", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_dur", "2000 ms", "Testing TapWithdrawal", "0"
    )

    # 运动神经元分组
    VA_motors = ["VA%s" % c for c in range_incl(1, 12)]
    VB_motors = ["VB%s" % c for c in range_incl(1, 11)]
    DA_motors = ["DA%s" % c for c in range_incl(1, 9)]
    DB_motors = ["DB%s" % c for c in range_incl(1, 7)]
    DD_motors = ["DD%s" % c for c in range_incl(1, 6)]
    VD_motors = ["VD%s" % c for c in range_incl(1, 13)]

    # 触碰回缩回路核心神经元
    TW_cells = [
        "AVAL", "AVAR",     # 后退命令
        "AVBL", "AVBR",     # 前行命令
        "PVCL", "PVCR",     # 前行输入中间
        "AVDL", "AVDR",     # 后退输入中间
        "DVA",
        "PVDL", "PVDR",     # 身体触觉
        "PLML", "PLMR",     # 尾部触觉
        "AVM", "ALML", "ALMR",  # 前部触觉
    ]

    all_motors = list(
        VA_motors + VB_motors + DA_motors + DB_motors + DD_motors + VD_motors
    )

    muscles_to_include = False
    cells = list(TW_cells + all_motors)
    cells_to_stimulate = []

    reference = "c302_%s_TapWithdrawal" % parameter_set

    # 连接极性覆盖
    conn_polarity_override = {
        # ALM/AVM → 命令神经元
        "ALML-ALML": "inh", "ALML-PVCL": "inh", "ALML-PVCR": "inh",
        "ALML-AVDR": "inh",
        "ALMR-PVCR": "inh",
        "AVM-PVCL": "inh", "AVM-PVCR": "inh",
        "AVM-AVBL": "inh", "AVM-AVBR": "inh",
        "AVM-AVDL": "inh", "AVM-AVDR": "inh",
        # PVD → 命令神经元
        "PVDL-PVDR": "inh", "PVDL-PVCL": "exc", "PVDL-PVCR": "exc",
        "PVDL-AVAL": "inh", "PVDL-AVAR": "inh",
        "PVDL-AVDL": "inh", "PVDL-AVDR": "inh",
        "PVDR-PVDL": "inh", "PVDR-DVA": "exc",
        "PVDR-PVCL": "exc", "PVDR-PVCR": "exc",
        "PVDR-AVAL": "inh", "PVDR-AVAR": "inh", "PVDR-AVDL": "inh",
        # DVA → 命令神经元
        "DVA-PVCL": "inh", "DVA-PVCR": "inh",
        "DVA-AVAL": "inh", "DVA-AVAR": "inh",
        "DVA-AVBL": "inh", "DVA-AVBR": "inh", "DVA-AVDR": "inh",
        # PVC ↔ 命令神经元
        "PVCL-DVA": "exc", "PVCL-PVCL": "inh", "PVCL-PVCR": "inh",
        "PVCL-AVAL": "inh", "PVCL-AVAR": "inh",
        "PVCL-AVBL": "exc", "PVCL-AVBR": "exc",
        "PVCL-AVDL": "inh", "PVCL-AVDR": "inh",
        "PVCR-PVDL": "inh", "PVCR-PVDR": "inh",
        "PVCR-DVA": "exc", "PVCR-PVCL": "inh",
        "PVCR-AVAL": "inh", "PVCR-AVAR": "inh",
        "PVCR-AVBL": "exc", "PVCR-AVBR": "exc",
        "PVCR-AVDL": "inh", "PVCR-AVDR": "inh",
        # AVA → 其他命令
        "AVAL-PVCL": "inh", "AVAL-PVCR": "inh", "AVAL-AVAR": "inh",
        "AVAL-AVBL": "inh", "AVAL-AVDL": "inh", "AVAL-AVDR": "inh",
        "AVAR-PVCL": "inh", "AVAR-PVCR": "inh", "AVAR-AVAL": "inh",
        "AVAR-AVBL": "inh", "AVAR-AVBR": "inh",
        "AVAR-AVDL": "inh", "AVAR-AVDR": "inh",
        # AVB → 其他命令
        "AVBL-DVA": "inh", "AVBL-PVCR": "inh",
        "AVBL-AVAL": "inh", "AVBL-AVAR": "inh",
        "AVBL-AVBR": "inh", "AVBL-AVDR": "inh",
        "AVBR-AVAL": "inh", "AVBR-AVAR": "inh",
        "AVBR-AVBL": "inh", "AVBR-AVDL": "inh",
        # AVD → AVA/AVD
        "AVDL-PVCL": "inh",
        "AVDL-AVAL": "exc", "AVDL-AVAR": "exc", "AVDL-AVDR": "exc",
        "AVDR-PVCR": "inh",
        "AVDR-AVAL": "exc", "AVDR-AVAR": "exc",
        "AVDR-AVBL": "inh", "AVDR-AVDL": "exc",
        # 命令 → DA 运动神经元
        "DA9-DVA": "inh", "DVA-DA2": "inh",
        "PVCL-DA5": "inh", "PVCL-DA8": "inh",
        "PVCR-DA2": "inh", "PVCR-DA4": "inh",
        "PVCR-DA5": "inh", "PVCR-DA7": "inh",
        "AVBL-DA5": "inh", "AVBL-DA7": "inh",
        "AVBR-DA3": "inh", "AVBR-DA4": "inh", "AVBR-DA7": "inh",
        "AVDL-DA1": "inh", "AVDL-DA2": "inh", "AVDL-DA3": "inh",
        "AVDL-DA4": "inh", "AVDL-DA5": "inh", "AVDL-DA8": "inh",
        "AVDR-DA1": "inh", "AVDR-DA2": "inh", "AVDR-DA3": "inh",
        "AVDR-DA4": "inh", "AVDR-DA5": "inh", "AVDR-DA8": "inh",
        # DB → DA 交叉抑制
        "DB1-DA1": "inh", "DB1-DA2": "inh",
        "DB2-DA2": "inh", "DB2-DA3": "inh", "DB2-DA4": "inh",
        "DB3-DA4": "inh", "DB3-DA5": "inh",
        "DB4-DA5": "inh",
        "DB5-DA6": "inh", "DB5-DA7": "inh", "DB5-DA8": "inh",
        "DB6-DA8": "inh", "DB6-DA9": "inh",
        "DB7-DA9": "inh",
        "AVAR-DB2": "inh", "AVAR-DB3": "inh", "AVAL-DB7": "inh",
        # DA → DB 交叉抑制
        "DA1-DB1": "inh", "DA2-DA3": "inh", "DA2-DB1": "inh",
        "DA3-DB3": "inh", "DA4-DB2": "inh",
        "DA5-DB4": "inh", "DA6-DB5": "inh",
        "DA7-DB6": "inh", "DA8-DB7": "inh", "DA9-DB7": "inh",
        # 命令 → VA 运动神经元
        "DVA-VA2": "inh", "DVA-VA6": "inh",
        "DVA-VA8": "inh", "DVA-VA12": "inh",
        "PVCL-VA11": "inh",
        "PVDR-VA9": "inh", "PVDR-VA12": "inh",
        "AVBL-VA2": "inh", "AVBL-VA10": "inh",
        "AVBR-VA3": "inh", "AVBR-VA4": "inh",
        "AVDL-VA3": "inh", "AVDL-VA5": "inh",
        "AVDL-VA10": "inh", "AVDL-VA12": "inh",
        "AVDR-VA2": "inh", "AVDR-VA3": "inh",
        "AVDR-VA5": "inh", "AVDR-VA11": "inh",
        # VB → VA 交叉抑制
        "VB1-VA1": "inh", "VB1-VA2": "inh", "VB1-VA3": "inh", "VB1-VA4": "inh",
        "VB2-VA2": "inh", "VB2-VA3": "inh",
        "VB3-VA4": "inh", "VB3-VA5": "inh",
        "VB4-VA4": "inh", "VB4-VA5": "inh",
        "VB5-VA6": "inh", "VB6-VA7": "inh", "VB6-VA8": "inh",
        "VB7-VA9": "inh", "VB7-VA10": "inh",
        "VB8-VA11": "inh", "VB9-VA11": "inh",
        "VB10-VA11": "inh", "VB11-VA12": "inh",
        "VB11-PVCR": "inh", "VB4-VB5": "inh",
        # VA → VB/AVD 交叉抑制
        "VA2-VB1": "inh", "VA2-VB2": "inh",
        "VA3-VB2": "inh", "VA3-VB3": "inh",
        "VA4-AVDL": "inh", "VA4-VB3": "inh", "VA4-VB4": "inh",
        "VA5-VB4": "inh", "VA6-VB4": "inh", "VA6-VB5": "inh",
        "VA7-VB6": "inh", "VA8-VB6": "inh",
        "VA9-VB7": "inh", "VA9-VB8": "inh",
        "VA10-VB8": "inh", "VA10-VB9": "inh",
        "VA11-VB10": "inh",
        "VA12-PVCL": "inh", "VA12-PVCR": "inh",
        "VA12-DB7": "inh", "VA12-VB11": "inh",
        "AVM-VB3": "inh",
    }

    # 连接数量覆盖 — 间隙连接缩放
    conn_number_override = {
        # PVC ↔ AVA 间隙连接
        "PVCL-AVAL_GJ": 5 * 0.01, "AVAL-PVCL_GJ": 5 * 0.01,
        "PVCL-AVAR_GJ": 10 * 0.01, "AVAR-PVCL_GJ": 10 * 0.01,
        "PVCR-AVAL_GJ": 15 * 0.01, "AVAL-PVCR_GJ": 15 * 0.01,
        "PVCR-AVAR_GJ": 22 * 0.01, "AVAR-PVCR_GJ": 22 * 0.01,
        # PVC ↔ PLM 间隙连接
        "PVCL-PLML_GJ": 4 * 0.01, "PVCR-PLMR_GJ": 8 * 0.01,
        # 命令神经元间
        "AVAR-AVBL_GJ": 3 * 0.01, "AVBL-AVAR_GJ": 3 * 0.01,
        # PVD ↔ AVA
        "PVDL-AVAR_GJ": 4 * 0.01, "AVAR-PVDL_GJ": 4 * 0.01,
        "PVDR-AVAL_GJ": 6 * 0.01, "AVAL-PVDR_GJ": 6 * 0.01,
        # 命令/中间 ↔ 运动神经元
        "AVBL-VA11_GJ": 1 * 0.01, "VA11-AVBL_GJ": 1 * 0.01,
        "AVBR-VA11_GJ": 3 * 0.01, "VA11-AVBR_GJ": 3 * 0.01,
        "PVCR-VA11_GJ": 3 * 0.01, "VA11-PVCR_GJ": 3 * 0.01,
        "DVA-VA11_GJ": 1 * 0.01, "VA11-DVA_GJ": 1 * 0.01,
        "PVCL-VA12_GJ": 18 * 0.01, "VA12-PVCL_GJ": 18 * 0.01,
        "PVCR-VA12_GJ": 8 * 0.01, "VA12-PVCR_GJ": 8 * 0.01,
        "AVAL-VB11_GJ": 2 * 0.01, "VB11-AVAL_GJ": 2 * 0.01,
        "PVCL-DA4_GJ": 1 * 0.01, "DA4-PVCL_GJ": 1 * 0.01,
        "PVCL-DA7_GJ": 1 * 0.01, "DA7-PVCL_GJ": 1 * 0.01,
        "PVCR-DA7_GJ": 3 * 0.01, "DA7-PVCR_GJ": 3 * 0.01,
        "PVCL-DA8_GJ": 17 * 0.01, "DA8-PVCL_GJ": 17 * 0.01,
        "PVCR-DA8_GJ": 1 * 0.01, "DA8-PVCR_GJ": 1 * 0.01,
        "DVA-DA9_GJ": 3 * 0.01, "DA9-DVA_GJ": 3 * 0.01,
        "PVCR-DA9_GJ": 3 * 0.01, "DA9-PVCR_GJ": 3 * 0.01,
        # 运动神经元间
        "DB7-VA10_GJ": 1 * 0.01, "VA10-DB7_GJ": 1 * 0.01,
        "VA4-VB3_GJ": 1 * 0.01, "VB3-VA4_GJ": 1 * 0.01,
        "VA11-VB10_GJ": 3 * 0.01, "VB10-VA11_GJ": 3 * 0.01,
        "VA12-VB11_GJ": 7 * 0.01, "VB11-VA12_GJ": 7 * 0.01,
        "VB11-DA9_GJ": 7 * 0.01, "DA9-VB11_GJ": 7 * 0.01,
    }

    nml_doc = None

    if generate_flag:
        nml_doc = generate(
            reference,
            params,
            cells=cells,
            cells_to_stimulate=cells_to_stimulate,
            conn_polarity_override=conn_polarity_override,
            conn_number_override=conn_number_override,
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            target_directory=target_directory,
            data_reader=data_reader,
            param_overrides=param_overrides,
        )

        # VB/DB 正弦波刺激（周期 150ms）
        for vb in VB_motors:
            add_new_sinusoidal_input(
                nml_doc, cell=vb, delay="0ms",
                duration="1000ms", amplitude="3pA",
                period="150ms", params=params,
            )
        for db in DB_motors:
            add_new_sinusoidal_input(
                nml_doc, cell=db, delay="0ms",
                duration="1000ms", amplitude="3pA",
                period="150ms", params=params,
            )

        nml_file = target_directory + "/" + reference + ".net.nml"
        writers.NeuroMLWriter.write(nml_doc, nml_file)

    return cells, cells_to_stimulate, params, muscles_to_include, nml_doc
