# =============================================================================
# 功能描述：
#   连接矩阵图绘制模块。重写自原 c302_utils.py 的
#   generate_conn_matrix() / _show_conn_matrix() 函数。
#   从 NeuroML 文档解析投射信息，构建连接矩阵并可视化。
#
# 类与方法索引：
#   _is_muscle_nml                       (L46)   — 判断细胞名称是否为肌肉（兼容 NeuroML 和电子表格命名）
#   _load_cell_info                      (L75)   — 从缓存 JSON 加载细胞分类信息
#   _show_conn_matrix                    (L108)  — 渲染单张连接矩阵热图
#   generate_conn_matrix                 (L188)  — 从 NeuroML 文档生成全套连接矩阵图
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段七：新建
#
# 当前维护者：Copilot
# =============================================================================
"""连接矩阵图绘制。"""

from __future__ import annotations

import json
import logging
from collections import OrderedDict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from c302.readers.base import is_muscle as _reader_is_muscle
from c302.utils.helpers import get_connectome_dir

logger = logging.getLogger(__name__)

# 默认图形尺寸
DEFAULT_FIGSIZE = (6.4, 4.8)

# NeuroML 网络中使用的肌肉名称前缀
_NML_MUSCLE_PREFIXES = ("MV", "MD", "pm", "vm", "um", "BWM")

# 模块级缓存：加载后的 muscle/neuron 名称集合
_cached_muscle_names: set[str] | None = None
_cached_neuron_names: set[str] | None = None


def _is_muscle_nml(cell: str) -> bool:
    """判断细胞名称是否为肌肉（兼容 NeuroML 和电子表格命名）。

    :param cell: 细胞名称
    :return: True 表示肌肉
    """
    global _cached_muscle_names, _cached_neuron_names

    # 首次调用时加载缓存
    if _cached_muscle_names is None:
        cache_path = get_connectome_dir() / "owmeta_cache.json"
        if cache_path.exists():
            with open(cache_path, encoding="utf-8") as f:
                cached = json.load(f)
            _cached_muscle_names = set(cached.get("muscle_info", {}).keys())
            _cached_neuron_names = set(cached.get("neuron_info", {}).keys())
        else:
            _cached_muscle_names = set()
            _cached_neuron_names = set()

    # 优先按缓存判定
    if cell in _cached_muscle_names:
        return True
    if cell in _cached_neuron_names:
        return False
    # 回退到前缀匹配
    return cell.startswith(_NML_MUSCLE_PREFIXES) or _reader_is_muscle(cell)


def _load_cell_info(cells: list[str]) -> tuple[OrderedDict, OrderedDict]:
    """从缓存 JSON 加载细胞分类信息。

    分类逻辑：先查缓存 JSON 中的 muscle_info / neuron_info 字段判定类别，
    再回退到 ``is_muscle()`` 做前缀匹配。

    :param cells: 细胞名称列表
    :return: (神经元信息有序字典, 肌肉信息有序字典)
    """
    cache_path = get_connectome_dir() / "owmeta_cache.json"
    with open(cache_path, encoding="utf-8") as f:
        cached = json.load(f)

    muscle_info_cache = cached.get("muscle_info", {})
    neuron_info_cache = cached.get("neuron_info", {})

    all_neuron_info: OrderedDict = OrderedDict()
    all_muscle_info: OrderedDict = OrderedDict()

    for cell in cells:
        # 优先按缓存中的分类判定
        if cell in muscle_info_cache:
            all_muscle_info[cell] = muscle_info_cache[cell]
        elif cell in neuron_info_cache:
            all_neuron_info[cell] = neuron_info_cache[cell]
        elif _is_muscle_nml(cell):
            all_muscle_info[cell] = (cell, (), (), (), cell, "0 0.6 0")
        else:
            all_neuron_info[cell] = (cell, (), (), (), cell, ".5 0 0")

    return all_neuron_info, all_muscle_info


def _show_conn_matrix(
    data: np.ndarray,
    title_suffix: str,
    all_info_pre: OrderedDict,
    all_info_post: OrderedDict,
    net_id: str,
    *,
    save_figure_to: str | None = None,
    verbose: bool = True,
    figsize: tuple[float, float] = DEFAULT_FIGSIZE,
    colormap: str | None = None,
) -> None:
    """渲染单张连接矩阵热图。

    :param data: 连接权重矩阵
    :param title_suffix: 标题后缀描述
    :param all_info_pre: 突触前细胞信息有序字典
    :param all_info_post: 突触后细胞信息有序字典
    :param net_id: 网络 ID
    :param save_figure_to: 保存路径（None 则不保存）
    :param verbose: 是否输出详细日志
    :param figsize: 图形尺寸
    :param colormap: 色图名称（None 使用 gist_stern_r）
    """
    # 计算最大值
    if data.shape[0] > 0 and data.shape[1] > 0 and np.amax(data) > 0:
        maxn = int(np.amax(data))
    else:
        maxn = 0

    logger.debug("矩阵 shape=%s, max=%d: %s", data.shape, maxn, title_suffix)

    # 全零矩阵则跳过
    if maxn == 0:
        logger.debug("无连接，跳过绘图")
        return

    fig, ax = plt.subplots(figsize=figsize)
    title = "{}: {}".format(net_id, title_suffix)
    plt.title(title)
    fig.canvas.manager.set_window_title(title)

    # 选择色图
    cmap = plt.colormaps[colormap or "gist_stern_r"]
    plt.imshow(data, cmap=cmap, interpolation="nearest", norm=None)

    ax = plt.gca()
    # 小网络显示网格线
    if data.shape[0] < 40:
        ax.grid(which="minor", color="grey", linestyle="-", linewidth=0.3)

    # X/Y 刻度
    xt = np.arange(data.shape[1])
    ax.set_xticks(xt)
    ax.set_xticks(xt[:-1] + 0.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]))
    ax.set_yticks(np.arange(data.shape[0]) + 0.5, minor=True)

    # 标签
    ax.set_yticklabels([all_info_pre[k][4] for k in all_info_pre])
    ax.set_xticklabels([all_info_post[k][4] for k in all_info_post])
    ax.set_ylabel("presynaptic")
    ax.set_xlabel("postsynaptic")

    # 自适应字号
    tick_size = 10 if data.shape[0] < 20 else (8 if data.shape[0] < 40 else 6)
    ax.tick_params(axis="y", labelsize=tick_size)
    ax.tick_params(axis="x", labelsize=tick_size)
    fig.autofmt_xdate()

    # 整数色条
    cbar = plt.colorbar(ticks=range(maxn + 1))
    cbar.set_ticklabels(range(maxn + 1))

    # 保存
    if save_figure_to:
        logger.info("保存连接矩阵图: %s", save_figure_to)
        plt.savefig(save_figure_to, bbox_inches="tight")


def generate_conn_matrix(
    nml_doc: object,
    *,
    save_fig_dir: str | None = None,
    verbose: bool = False,
    figsize: tuple[float, float] = DEFAULT_FIGSIZE,
    colormap: str | None = None,
) -> None:
    """从 NeuroML 文档生成全套连接矩阵图。

    解析化学突触（兴奋性 + 抑制性）和电突触（间隙连接），
    分别为神经元→神经元、神经元→肌肉、肌肉→肌肉构建矩阵并绘图。

    :param nml_doc: NeuroML 文档对象（含 networks 属性）
    :param save_fig_dir: 图片保存目录（None 则不保存）
    :param verbose: 是否输出详细日志
    :param figsize: 图形尺寸
    :param colormap: 色图名称
    """
    net = nml_doc.networks[0]

    # ---- 解析化学突触 ----
    cc_exc_conns: dict[str, dict[str, float]] = {}
    cc_inh_conns: dict[str, dict[str, float]] = {}
    all_cells: list[str] = []

    for cp in net.continuous_projections:
        pre = cp.presynaptic_population
        post = cp.postsynaptic_population
        cc_exc_conns.setdefault(pre, {})
        cc_inh_conns.setdefault(pre, {})

        # 收集所有细胞
        if pre not in all_cells:
            all_cells.append(pre)
        if post not in all_cells:
            all_cells.append(post)

        for c in cp.continuous_connection_instance_ws:
            if "inh" in c.post_component:
                cc_inh_conns[pre][post] = float(c.weight)
            else:
                cc_exc_conns[pre][post] = float(c.weight)

    # ---- 解析电突触 ----
    gj_conns: dict[str, dict[str, float]] = {}
    for ep in net.electrical_projections:
        pre = ep.presynaptic_population
        post = ep.postsynaptic_population
        gj_conns.setdefault(pre, {})

        if pre not in all_cells:
            all_cells.append(pre)
        if post not in all_cells:
            all_cells.append(post)

        for e in ep.electrical_connection_instance_ws:
            gj_conns[pre][post] = float(e.weight)

    # ---- 分离神经元与肌肉 ----
    all_cells.sort()
    all_neurons = [c for c in all_cells if not _is_muscle_nml(c)]
    all_muscles = [c for c in all_cells if _is_muscle_nml(c)]

    # 加载细胞注释信息
    all_neuron_info, all_muscle_info = _load_cell_info(all_cells)

    # ---- 构建化学突触矩阵 ----
    data_exc_n = np.zeros((len(all_neurons), len(all_neurons)))
    data_exc_m = np.zeros((len(all_neurons), len(all_muscles)))
    data_inh_n = np.zeros((len(all_neurons), len(all_neurons)))
    data_inh_m = np.zeros((len(all_neurons), len(all_muscles)))

    for pre in cc_exc_conns:
        for post, weight in cc_exc_conns[pre].items():
            if post in all_neurons:
                data_exc_n[all_neurons.index(pre), all_neurons.index(post)] = weight
            else:
                data_exc_m[all_neurons.index(pre), all_muscles.index(post)] = weight

    for pre in cc_inh_conns:
        for post, weight in cc_inh_conns[pre].items():
            if post in all_neurons:
                data_inh_n[all_neurons.index(pre), all_neurons.index(post)] = weight
            else:
                data_inh_m[all_neurons.index(pre), all_muscles.index(post)] = weight

    # ---- 绘制化学突触矩阵 ----
    def _save_path(suffix: str) -> str | None:
        if save_fig_dir:
            return "{}/{}_{}.png".format(save_fig_dir, net.id, suffix)
        return None

    _show_conn_matrix(
        data_exc_n, "Excitatory (non GABA) conns to neurons",
        all_neuron_info, all_neuron_info, net.id,
        save_figure_to=_save_path("exc_to_neurons"),
        verbose=verbose, figsize=figsize, colormap=colormap,
    )
    _show_conn_matrix(
        data_exc_m, "Excitatory (non GABA) conns to muscles",
        all_neuron_info, all_muscle_info, net.id,
        save_figure_to=_save_path("exc_to_muscles"),
        verbose=verbose, figsize=figsize, colormap=colormap,
    )
    _show_conn_matrix(
        data_inh_n, "Inhibitory (GABA) conns to neurons",
        all_neuron_info, all_neuron_info, net.id,
        save_figure_to=_save_path("inh_to_neurons"),
        verbose=verbose, figsize=figsize, colormap=colormap,
    )
    _show_conn_matrix(
        data_inh_m, "Inhibitory (GABA) conns to muscles",
        all_neuron_info, all_muscle_info, net.id,
        save_figure_to=_save_path("inh_to_muscles"),
        verbose=verbose, figsize=figsize, colormap=colormap,
    )

    # ---- 构建间隙连接矩阵 ----
    data_n = np.zeros((len(all_neurons), len(all_neurons)))
    data_n_m = np.zeros((len(all_neurons), len(all_muscles)))
    data_m_m = np.zeros((len(all_muscles), len(all_muscles)))
    neuron_muscle = False
    muscle_muscle = False

    for pre in gj_conns:
        for post, weight in gj_conns[pre].items():
            if pre in all_neurons and post in all_neurons:
                data_n[all_neurons.index(pre), all_neurons.index(post)] = weight
            elif pre in all_neurons and post in all_muscles:
                data_n_m[all_neurons.index(pre), all_muscles.index(post)] = weight
                neuron_muscle = True
            elif pre in all_muscles and post in all_neurons:
                data_n_m[all_muscles.index(pre), all_neurons.index(post)] = weight
                neuron_muscle = True
            elif pre in all_muscles and post in all_muscles:
                data_m_m[all_muscles.index(pre), all_muscles.index(post)] = weight
                muscle_muscle = True

    # ---- 绘制间隙连接矩阵 ----
    _show_conn_matrix(
        data_n, "Electrical (gap junction) conns to neurons",
        all_neuron_info, all_neuron_info, net.id,
        save_figure_to=_save_path("elec_neurons_neurons"),
        verbose=verbose, figsize=figsize, colormap=colormap,
    )

    if neuron_muscle:
        _show_conn_matrix(
            data_n_m, "Electrical (gap junction) conns between neurons and muscles",
            all_neuron_info, all_muscle_info, net.id,
            save_figure_to=_save_path("elec_neurons_muscles"),
            verbose=verbose, figsize=figsize, colormap=colormap,
        )

    if muscle_muscle:
        _show_conn_matrix(
            data_m_m, "Electrical (gap junction) conns between muscles",
            all_muscle_info, all_muscle_info, net.id,
            save_figure_to=_save_path("elec_muscles_muscles"),
            verbose=verbose, figsize=figsize, colormap=colormap,
        )
