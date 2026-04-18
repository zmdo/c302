# =============================================================================
# 功能描述：
#   活动热图绘制模块。重写自原 c302_utils.py 的 plots() 函数，
#   使用 pcolormesh 绘制神经元/肌肉电压或活动热图。
#
# 类与方法索引：
#   plot_heatmap                         (L29)   — 绘制活动热图（pcolormesh）
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段七：新建
#
# 当前维护者：Copilot
# =============================================================================
"""活动热图绘制。"""

from __future__ import annotations

import logging

import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)

# 热图下采样倍数
_DOWNSCALE = 10


def plot_heatmap(
    data: np.ndarray,
    info: str,
    cell_labels: list[str],
    dt: float,
) -> None:
    """绘制活动热图（pcolormesh）。

    对时间轴进行 10 倍下采样后，用 ``jet`` 色图绘制 pcolormesh 热图。
    当细胞数 >24 时自动调高图形高度，>100 时进一步加高。

    :param data: 二维数组，行为细胞、列为时间步
    :param info: 图标题 / 窗口标题
    :param cell_labels: Y 轴细胞名称列表
    :param dt: 仿真步长（秒）
    """
    # 根据细胞数确定图形高度
    n_cells = data.shape[0]
    heightened = n_cells > 24
    matrix_height_in = 10
    if n_cells > 100:
        matrix_height_in = 20

    # 创建子图
    if heightened:
        top_margin = 0.04
        bottom_margin = 0.04
        figure_height = matrix_height_in / (1 - top_margin - bottom_margin)
        fig, ax = plt.subplots(
            figsize=(6, figure_height),
            gridspec_kw={"top": 1 - top_margin, "bottom": bottom_margin},
        )
    else:
        fig, ax = plt.subplots()

    # 下采样
    data_ds = data[:, ::_DOWNSCALE]

    # 绘制热图
    cmap = plt.colormaps["jet"]
    plot0 = ax.pcolormesh(data_ds, cmap=cmap)

    # Y 轴标签
    ax.set_yticks(np.arange(data_ds.shape[0]) + 0.5, minor=False)
    ax.set_yticklabels(cell_labels)
    ax.tick_params(axis="y", labelsize=6)

    fig.colorbar(plot0)
    fig.canvas.manager.set_window_title(info)
    plt.title(info)
    plt.xlabel("Time (ms)")

    # 将 X 轴刻度转换为毫秒
    fig.canvas.draw()
    labels_ms: list[float] = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        if text:
            labels_ms.append(float(text) * dt * _DOWNSCALE * 1000)

    ax.set_xticklabels(labels_ms)
    plt.xlim(0, data_ds.shape[1])
