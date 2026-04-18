# =============================================================================
# 功能描述：
#   电压轨迹图与活动曲线绘制模块。重写自原 c302_utils.py 的
#   plot_c302_results() / generate_traces_plot() 函数。
#
# 类与方法索引：
#   _is_muscle_nml                       (L45)   — 判断细胞名称是否为肌肉（兼容 NeuroML 和电子表格命名）
#   _natsort                             (L54)   — 自然排序键函数，使 ``VB2`` 排在 ``VB11`` 之前
#   _get_template                        (L64)   — 根据参数集返回 LEMS 结果键模板
#   generate_traces_plot                 (L85)   — 绘制单组电压 / 活动曲线图
#   plot_c302_results                    (L137)  — 从 LEMS 仿真结果生成全套可视化图（热图 + 轨迹图）
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段七：新建
#
# 当前维护者：Copilot
# =============================================================================
"""电压轨迹图与活动曲线绘制。"""

from __future__ import annotations

import logging
import os
import re
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from c302.readers.base import is_muscle as _reader_is_muscle
from c302.visualization.heatmap import plot_heatmap

if TYPE_CHECKING:
    from pyneuroml import plot as pyneuroml_plot  # pragma: no cover

logger = logging.getLogger(__name__)

# 不含钙离子活性的参数集
PARAMSETS_NO_CALCIUM = ("A", "W2D")

# NeuroML 网络中使用的肌肉名称前缀（与 readers 中的电子表格前缀不同）
_NML_MUSCLE_PREFIXES = ("MV", "MD", "pm", "vm", "um", "BWM")


def _is_muscle_nml(cell: str) -> bool:
    """判断细胞名称是否为肌肉（兼容 NeuroML 和电子表格命名）。

    :param cell: 细胞名称
    :return: True 表示肌肉
    """
    return cell.startswith(_NML_MUSCLE_PREFIXES) or _reader_is_muscle(cell)


def _natsort(s: str) -> list:
    """自然排序键函数，使 ``VB2`` 排在 ``VB11`` 之前。

    :param s: 待排序字符串
    :return: 按自然顺序拆分的列表
    """
    # 将字符串拆分为数字和非数字片段
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def _get_template(parameter_set: str, *, muscle: bool = False) -> str:
    """根据参数集返回 LEMS 结果键模板。

    :param parameter_set: 参数集名称（如 "A", "C0", "D"）
    :param muscle: True 时返回肌肉模板
    :return: 格式化字符串模板（含 {0} 和 {1} 占位符）
    """
    # IAF 模型
    if parameter_set.startswith("A") or parameter_set.startswith("B"):
        if muscle:
            return "{0}/0/generic_muscle_iaf_cell/{1}"
        return "{0}/0/generic_neuron_iaf_cell/{1}"
    # 多房室模型
    if parameter_set.startswith("D"):
        return "{0}/0/{0}/{1}"
    # 默认 — C 系列
    if muscle:
        return "{0}/0/GenericMuscleCell/{1}"
    return "{0}/0/GenericNeuronCell/{1}"


def generate_traces_plot(
    config: str,
    parameter_set: str,
    xvals: list[list[float]],
    yvals: list[list[float]],
    info: str,
    labels: list[str],
    *,
    save: bool = True,
    save_fig_path: str = "",
    voltage: bool = True,
    muscles: bool = False,
) -> None:
    """绘制单组电压 / 活动曲线图。

    :param config: 配置名称
    :param parameter_set: 参数集名称
    :param xvals: 每条曲线的时间序列
    :param yvals: 每条曲线的值序列
    :param info: 图标题
    :param labels: 曲线标签
    :param save: 是否保存图片
    :param save_fig_path: 保存路径模板（含 %s 占位符）
    :param voltage: True 表示电压图，False 表示活动图
    :param muscles: True 表示肌肉，False 表示神经元
    """
    from pyneuroml import plot as pyneuroml_plot  # 延迟导入

    # 构造文件名
    file_name = "traces_{}{}_{}_{}.png".format(
        "muscles" if muscles else "neuron",
        "" if voltage else "_activity",
        config,
        parameter_set,
    )

    # 调用 pyneuroml 绘图
    pyneuroml_plot.generate_plot(
        xvals,
        yvals,
        info,
        labels=labels,
        xaxis="Time (ms)",
        yaxis="Membrane potential (mV)" if voltage else "Activity",
        show_plot_already=False,
        save_figure_to=(None if not save else save_fig_path % file_name),
        cols_in_legend_box=8,
        legend_position="bottom center",
        title_above_plot=True,
    )


def plot_c302_results(
    lems_results: dict,
    config: str,
    parameter_set: str,
    *,
    directory: str = "./",
    save: bool = True,
    show_plot_already: bool = True,
    plot_ca: bool = True,
) -> None:
    """从 LEMS 仿真结果生成全套可视化图（热图 + 轨迹图）。

    最多生成 8 张图：神经元电压（热图 + 轨迹）、肌肉电压（热图 + 轨迹）、
    神经元活动/[Ca²⁺]（热图 + 轨迹）、肌肉活动/[Ca²⁺]（热图 + 轨迹）。

    :param lems_results: LEMS 仿真结果字典（键为路径，值为时间序列）
    :param config: 配置名称
    :param parameter_set: 参数集名称
    :param directory: 图片保存目录
    :param save: 是否保存图片
    :param show_plot_already: 是否立即显示图形窗口
    :param plot_ca: 是否绘制钙离子 / 活动图
    """
    params = {"legend.fontsize": 8, "font.size": 10}
    plt.rcParams.update(params)

    # 规范化保存路径
    if not directory.endswith("/"):
        directory += "/"
    save_fig_path = directory + "%s"

    # 分离细胞和肌肉
    cells: list[str] = []
    muscles: list[str] = []
    times = [t * 1000 for t in lems_results["t"]]
    for key in lems_results:
        if key != "t" and key.endswith("/v"):
            cell_name = key.split("/")[0]
            if _is_muscle_nml(cell_name):
                muscles.append(cell_name)
            else:
                cells.append(cell_name)

    # 自然排序后翻转（与原始行为一致）
    cells.sort(key=_natsort)
    cells.reverse()

    dt = lems_results["t"][1]

    # ---- 段落一：神经元电压 ----
    template = _get_template(parameter_set, muscle=False)
    if cells:
        logger.debug("绘制 %d 个神经元电压", len(cells))
        xvals, yvals, labels = [], [], []
        volts_n = None

        for cell in cells:
            v = lems_results[template.format(cell, "v")]
            xvals.append(times)
            labels.append(cell)
            row = [[vv * 1000 for vv in v]]
            if volts_n is None:
                volts_n = np.array(row)
            else:
                volts_n = np.append(volts_n, row, axis=0)
            yvals.append(volts_n[-1])

        info = "Membrane potentials of {} neuron(s) ({} {})".format(
            len(cells), config, parameter_set
        )
        plot_heatmap(volts_n, info, cells, dt)
        if save:
            f = save_fig_path % ("neurons_{}_{}.png".format(parameter_set, config))
            logger.debug("保存图片: %s", os.path.abspath(f))
            plt.savefig(f, bbox_inches="tight")

        generate_traces_plot(
            config, parameter_set, xvals, yvals, info, labels,
            save=save, save_fig_path=save_fig_path, voltage=True, muscles=False,
        )

    # ---- 段落二：肌肉电压 ----
    muscles.sort(key=_natsort)
    muscles.reverse()
    template_m = _get_template(parameter_set, muscle=True)

    if muscles:
        logger.debug("绘制 %d 块肌肉电压", len(muscles))
        xvals, yvals, labels = [], [], []
        mvolts_n = None

        for muscle in muscles:
            mv = lems_results[template_m.format(muscle, "v")]
            xvals.append(times)
            labels.append(muscle)
            row = [[vv * 1000 for vv in mv]]
            if mvolts_n is None:
                mvolts_n = np.array(row)
            else:
                mvolts_n = np.append(mvolts_n, row, axis=0)
            yvals.append(mvolts_n[-1])

        info = "Membrane potentials of {} muscle(s) ({} {})".format(
            len(muscles), config, parameter_set
        )
        plot_heatmap(mvolts_n, info, muscles, dt)
        if save:
            f = save_fig_path % ("muscles_{}_{}.png".format(parameter_set, config))
            logger.debug("保存图片: %s", os.path.abspath(f))
            plt.savefig(f, bbox_inches="tight")

        generate_traces_plot(
            config, parameter_set, xvals, yvals, info, labels,
            save=save, save_fig_path=save_fig_path, voltage=True, muscles=True,
        )

    # ---- 段落三：神经元活动 / [Ca²⁺] ----
    if plot_ca and parameter_set not in PARAMSETS_NO_CALCIUM and cells:
        logger.debug("绘制神经元活动 ([Ca²⁺])")
        variable = "caConc" if (
            parameter_set.startswith("C") or parameter_set.startswith("D")
        ) else "activity"
        description = "[Ca2+]" if variable == "caConc" else "Activity"

        xvals, yvals, labels = [], [], []
        activities_n = None

        info = "{} of {} neurons ({} {})".format(
            description, len(cells), config, parameter_set
        )
        for cell in cells:
            a = lems_results[template.format(cell, variable)]
            xvals.append(times)
            yvals.append(a)
            labels.append(cell)
            if activities_n is None:
                activities_n = np.array([a])
            else:
                activities_n = np.append(activities_n, [a], axis=0)

        plot_heatmap(activities_n, info, cells, dt)
        if save:
            f = save_fig_path % ("neuron_activity_{}_{}.png".format(
                parameter_set, config))
            logger.debug("保存图片: %s", os.path.abspath(f))
            plt.savefig(f, bbox_inches="tight")

        generate_traces_plot(
            config, parameter_set, xvals, yvals, info, labels,
            save=save, save_fig_path=save_fig_path, voltage=False, muscles=False,
        )

    # ---- 段落四：肌肉活动 / [Ca²⁺] ----
    if plot_ca and parameter_set not in PARAMSETS_NO_CALCIUM and muscles:
        logger.debug("绘制肌肉活动 ([Ca²⁺])")
        variable = "caConc" if (
            parameter_set.startswith("C") or parameter_set.startswith("D")
        ) else "activity"
        description = "[Ca2+]" if variable == "caConc" else "Activity"

        xvals, yvals, labels = [], [], []
        activities_n = None

        info = "{} of {} muscles ({} {})".format(
            description, len(muscles), config, parameter_set
        )
        for m in muscles:
            a = lems_results[template_m.format(m, variable)]
            xvals.append(times)
            yvals.append(a)
            labels.append(m)
            if activities_n is None:
                activities_n = np.array([a])
            else:
                activities_n = np.append(activities_n, [a], axis=0)

        plot_heatmap(activities_n, info, muscles, dt)
        if save:
            f = save_fig_path % ("muscle_activity_{}_{}.png".format(
                parameter_set, config))
            logger.debug("保存图片: %s", os.path.abspath(f))
            plt.savefig(f, bbox_inches="tight")

        generate_traces_plot(
            config, parameter_set, xvals, yvals, info, labels,
            save=save, save_fig_path=save_fig_path, voltage=False, muscles=True,
        )

    # 显示或关闭
    if show_plot_already:
        plt.show()
    else:
        plt.close("all")
