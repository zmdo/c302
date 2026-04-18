# =============================================================================
# 功能描述：
#   刺激注入模块。提供脉冲刺激（PulseGenerator）和正弦波刺激（SineGenerator）
#   的创建，以及将刺激绑定到 NeuroML 网络 InputList 的功能。
#
# 类与方法索引：
#   get_next_stim_id                     (L32)   — 为指定细胞生成下一个不重复的刺激 ID
#   append_input_to_nml_input_list       (L49)   — 将刺激输入追加到 NeuroML 网络的 InputList 中
#   add_new_input                        (L71)   — 为指定细胞创建脉冲刺激输入
#   add_new_sinusoidal_input             (L91)   — 为指定细胞创建正弦波刺激输入
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段四：从 __init__.py 提取重写
#
# 当前维护者：Copilot
# =============================================================================
"""刺激注入模块。"""
import logging

from neuroml import Input, InputList, PulseGenerator, SineGenerator

from c302.generator.population import get_cell_id_string
from c302.generator.position import (
    DB_SOMA_POS,
    VB_SOMA_POS,
    is_body_wall_muscle,
)

logger = logging.getLogger(__name__)


def get_next_stim_id(nml_doc, cell: str) -> str:
    """为指定细胞生成下一个不重复的刺激 ID。

    遍历已有 ``pulse_generators``，计数以 ``stim_{cell}`` 开头的数量，
    返回 ``stim_{cell}_{n+1}`` 格式的新 ID。

    :param nml_doc: NeuroML 文档对象
    :param cell: 细胞名称
    :return: 新的刺激 ID 字符串
    """
    i = 1
    for stim in nml_doc.pulse_generators:
        if stim.id.startswith("stim_%s" % cell):
            i += 1
    return "stim_%s_%s" % (cell, i)


def append_input_to_nml_input_list(stim, nml_doc, cell: str, params) -> None:
    """将刺激输入追加到 NeuroML 网络的 InputList 中。

    创建 ``InputList`` 并添加一个 ``Input`` 条目，绑定到指定细胞的
    突触目标端点。

    :param stim: 刺激生成器对象
    :param nml_doc: NeuroML 文档对象
    :param cell: 目标细胞名称
    :param params: 参数模型对象
    """
    target = get_cell_id_string(cell, params, muscle=is_body_wall_muscle(cell))

    input_list = InputList(
        id="Input_%s_%s" % (cell, stim.id),
        component=stim.id,
        populations="%s" % cell,
    )
    input_list.input.append(Input(id=0, target=target, destination="synapses"))
    nml_doc.networks[0].input_lists.append(input_list)


def add_new_input(
    nml_doc, cell: str, delay: str, duration: str, amplitude: str, params
) -> None:
    """为指定细胞创建脉冲刺激输入。

    :param nml_doc: NeuroML 文档对象
    :param cell: 目标细胞名称
    :param delay: 延迟时间（含单位）
    :param duration: 持续时间（含单位）
    :param amplitude: 幅度（含单位）
    :param params: 参数模型对象
    """
    stim_id = get_next_stim_id(nml_doc, cell)
    stim = PulseGenerator(
        id=stim_id, delay=delay, duration=duration, amplitude=amplitude
    )
    nml_doc.pulse_generators.append(stim)
    append_input_to_nml_input_list(stim, nml_doc, cell, params)


def add_new_sinusoidal_input(
    nml_doc,
    cell: str,
    delay: str,
    duration: str,
    amplitude: str,
    period: str,
    params,
) -> None:
    """为指定细胞创建正弦波刺激输入。

    根据运动神经元（VB/DB）的 soma 位置自动计算相位偏移，
    VB 系列的幅度取反以产生反相振荡。

    :param nml_doc: NeuroML 文档对象
    :param cell: 目标细胞名称
    :param delay: 延迟时间
    :param duration: 持续时间
    :param amplitude: 幅度
    :param period: 周期
    :param params: 参数模型对象
    """
    stim_id = get_next_stim_id(nml_doc, cell)

    # 从预定义字典获取 soma 位置作为相位基础
    if cell.startswith("VB"):
        phase = VB_SOMA_POS[cell]
    else:
        phase = DB_SOMA_POS[cell]
    # 转换为相位偏移
    phase = phase * -0.886
    logger.info("CELL %s PHASE: %s", cell, phase)

    # VB 系列幅度取反（反相振荡）
    if cell.startswith("VB"):
        if amplitude.startswith("-"):
            amplitude = amplitude[1:]
        else:
            amplitude = "-" + amplitude

    stim = SineGenerator(
        id=stim_id,
        delay=delay,
        phase=phase,
        duration=duration,
        amplitude=amplitude,
        period=period,
    )
    nml_doc.sine_generators.append(stim)
    append_input_to_nml_input_list(stim, nml_doc, cell, params)
