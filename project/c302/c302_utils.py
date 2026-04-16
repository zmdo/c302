# =============================================================================
# 功能描述：
#   c302 仿真结果可视化工具集。
#   提供膜电位/活性热图、轨迹叠加图和连接矩阵热图的绘制功能，
#   支持神经元与肌肉分组显示、自动保存 PNG、自然排序等。
#
# 类与方法索引：
#   natsort                              (L32)   — 对字符串进行自然排序的辅助键函数
#   plots                                (L49)   — 将仿真数据矩阵绘制为热图（pcolormesh）
#   generate_traces_plot                 (L138)  — 使用 pyNeuroML 绘制各细胞的膜电位或活性轨迹叠加图
#   plot_c302_results                    (L185)  — c302 仿真结果的主绘图函数
#   _show_conn_matrix                    (L474)  — 内部辅助函数：显示单个连接矩阵热图
#   generate_conn_matrix                 (L564)  — 从 NeuroML 文档生成完整的连接矩阵可视化
#
# 更新日志：
#   2026-04-16  Copilot  计划2 阶段八收尾：补记汇总校验与最终勘误完成
#   2026-04-16  Copilot  添加中文 docstring 和行内注释
#
# 当前维护者：Copilot
# =============================================================================
import sys
import os
import re

import matplotlib.pyplot as plt
import numpy as np
from pyneuroml import plot as pyneuroml_plot

import c302


def natsort(s):
    """对字符串进行自然排序的辅助键函数。

    将字符串按数字和非数字片段拆分，数字部分转为整数，
    使得 ``VB2`` 排在 ``VB11`` 之前（而非字典序的 ``VB11 < VB2``）。

    :param s: 待排序的字符串
    :return: 可用于 ``sorted(key=...)`` 的混合类型列表
    """
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


default_figsize = (6.4, 4.8)  # matplotlib 默认图形尺寸（英寸）

paramsets_no_calcium = ["A", "W2D"]  # 无钙动力学的参数集，跳过 [Ca2+] 绘图


def plots(a_n, info, cells, dt):
    """将仿真数据矩阵绘制为热图（pcolormesh）。

    当细胞数量超过 24 个时自动增大图形高度以保证标签可读。
    X 轴为时间（ms），Y 轴为各细胞名称。

    :param a_n: 二维 numpy 数组，行为细胞、列为时间步
    :param info: 图表标题字符串
    :param cells: 细胞名称列表（与矩阵行对应）
    :param dt: 仿真时间步长（秒）
    """
    c302.print_("Generating plots for: %s" % info)

    heightened = False
    matrix_height_in = None

    if len(cells) > 24:  # 细胞数较多时增大图形高度以保证标签可读
        matrix_height_in = 10
        heightened = True
    if len(cells) > 100:
        matrix_height_in = 20
    if heightened:
        # [备选] 以下为按刻度字体精确估算矩阵高度的旧方案（当前改用固定高度）
        # fontsize_pt = plt.rcParams['ytick.labelsize']
        # dpi = 72.27

        # 计算矩阵高度（点 / 英寸）
        ##matrix_height_pt = fontsize_pt * a_n.shape[0]
        ##matrix_height_in = float(matrix_height_pt) / dpi
        # matrix_height_in = 10

        # 根据上下边距反推最终图形高度
        top_margin = 0.04  # in percentage of the figure height
        bottom_margin = 0.04  # in percentage of the figure height
        figure_height = matrix_height_in / (1 - top_margin - bottom_margin)

        fig, ax = plt.subplots(
            figsize=(6, figure_height),
            gridspec_kw=dict(top=1 - top_margin, bottom=bottom_margin),
        )
    else:
        fig, ax = plt.subplots()

    # [备选] 旧版使用 figure()+gca() 初始化坐标轴
    # fig = plt.figure()
    # ax = fig.gca()
    downscale = 10  # 降采样倍率，减少渲染点数

    a_n_ = a_n[:, ::downscale]  # 对时间轴降采样

    cmap = plt.colormaps["jet"]
    plot0 = ax.pcolormesh(a_n_, cmap=cmap)
    ax.set_yticks(np.arange(a_n_.shape[0]) + 0.5, minor=False)
    ax.set_yticklabels(cells)
    ax.tick_params(axis="y", labelsize=6)
    # [备选] 可旋转 Y 轴标签以提升极密集热图的可读性
    # plt.setp(ax.get_yticklabels(), rotation=45)

    fig.colorbar(plot0)

    fig.canvas.manager.set_window_title(info)
    plt.title(info)
    plt.xlabel("Time (ms)")

    fig.canvas.draw()

    labels = []  # 将刻度标签从采样索引转换为毫秒单位
    for label in ax.get_xticklabels():
        if len(label.get_text()) > 0:
            labels.append(float(str((label.get_text()))) * dt * downscale * 1000)
        # [调试] 以下输出用于定位刻度文本解析失败的异常值
        # except:
        #     print "Error value on forming axis values, value: ", label.get_text(), ", length: ",len(label.get_text())

    # [备选] 旧版使用列表推导式一次性重建 X 轴标签
    # labels = [float(label.get_text())*dt*downscale*1000 for item in ax.get_xticklabels()]
    ax.set_xticklabels(labels)
    # [调试] 可取消注释以检查标签重建后的 X 轴范围
    # print labels
    # print plt.xlim()
    plt.xlim(0, a_n_.shape[1])
    # print plt.xlim()


# [调试] 旧版 cProfile 性能分析入口（当前未启用）
# def plots_prof(a_n, info, cells, dt):
#    cProfile.run("real_plots(a_n, info, cells, dt)")


def generate_traces_plot(
    config,
    parameter_set,
    xvals,
    yvals,
    info,
    labels,
    save,
    save_fig_path,
    voltage,
    muscles,
):
    """使用 pyNeuroML 绘制各细胞的膜电位或活性轨迹叠加图。

    :param config: 配置名称（如 ``Full``、``Syns``）
    :param parameter_set: 参数集名称（如 ``A``、``C1``）
    :param xvals: 时间序列列表（每个细胞一条）
    :param yvals: 电压/活性值列表
    :param info: 图表标题
    :param labels: 曲线标签列表
    :param save: 是否保存为 PNG 文件
    :param save_fig_path: 保存路径模板
    :param voltage: ``True`` 绘制膜电位，``False`` 绘制活性/钙浓度
    :param muscles: ``True`` 表示绘制肌肉数据
    """
    file_name = "traces_%s%s_%s_%s.png" % (
        ("muscles" if muscles else "neuron"),
        ("" if voltage else "_activity"),
        config,
        parameter_set,
    )

    pyneuroml_plot.generate_plot(
        xvals,
        yvals,
        info,
        labels=labels,
        xaxis="Time (ms)",
        yaxis="Membrane potential (mV)" if voltage else "Activity",
        show_plot_already=False,
        save_figure_to=(None if not save else save_fig_path % (file_name)),
        cols_in_legend_box=8,
        legend_position="bottom center",
        title_above_plot=True,
    )


def plot_c302_results(
    lems_results,
    config,
    parameter_set,
    directory="./",
    save=True,
    show_plot_already=True,
    data_reader=c302.DEFAULT_DATA_READER,
    plot_ca=True,
):
    """c302 仿真结果的主绘图函数。

    从 LEMS 仿真结果字典中提取神经元和肌肉数据，依次生成：
    1. 神经元膜电位热图和轨迹图
    2. 肌肉膜电位热图和轨迹图
    3. 神经元活性/钙浓度热图和轨迹图（可选）
    4. 肌肉活性/钙浓度热图和轨迹图（可选）

    :param lems_results: LEMS 仿真结果字典，键为变量路径，值为时间序列
    :param config: 配置名称
    :param parameter_set: 参数集名称
    :param directory: 图片保存目录
    :param save: 是否保存图片
    :param show_plot_already: 是否立即显示图形窗口
    :param data_reader: 数据读取器名称
    :param plot_ca: 是否绘制活性/钙浓度图
    """
    params = {"legend.fontsize": 8, "font.size": 10}
    plt.rcParams.update(params)

    if not directory.endswith("/"):
        directory += "/"
    save_fig_path = directory + "%s"

    # [调试] 可取消注释以检查 LEMS 结果中实际加载的变量键
    # c302.print_("Reloaded data: %s"%lems_results.keys())
    cells = []
    muscles = []
    times = [t * 1000 for t in lems_results["t"]]

    # 扫描结果键名，拆分出神经元和肌肉两类绘图目标
    for cm in lems_results.keys():
        if not cm == "t" and cm.endswith("/v"):
            cell_name_part = cm.split("/")[0]
            if c302.is_muscle(cell_name_part):
                muscles.append(cell_name_part)
            else:
                cells.append(cell_name_part)

    # 热图按自然排序后逆序显示，以维持既有图像的上下顺序
    cells.sort(key=natsort)
    cells.reverse()

    c302.print_("All cells: %s" % cells)
    dt = lems_results["t"][1]

    # ── 第 1 段：绘制神经元膜电位 ──────────────────────────

    if len(cells) > 0:
        c302.print_("Plotting neuron voltages")

        # 不同参数集对应不同的 NeuroML 路径模板
        template = "{0}/0/GenericNeuronCell/{1}"
        if parameter_set.startswith("A") or parameter_set.startswith("B"):
            template = "{0}/0/generic_neuron_iaf_cell/{1}"  # IAF 模型
        if parameter_set.startswith("D"):
            template = "{0}/0/{0}/{1}"  # 多室模型

        xvals = []
        yvals = []
        labels = []

        # 逐个提取神经元膜电位，并同时构造热图矩阵与轨迹图输入
        for cell in cells:
            v = lems_results[template.format(cell, "v")]

            xvals.append(times)
            labels.append(cell)

            if cell == cells[0]:
                volts_n = np.array([[vv * 1000 for vv in v]])
            else:
                volts_n = np.append(volts_n, [[vv * 1000 for vv in v]], axis=0)
            yvals.append(volts_n[-1])

        info = "Membrane potentials of %i neuron(s) (%s %s)" % (
            len(cells),
            config,
            parameter_set,
        )

        # [备选] 旧版曾将绘图任务压入队列后统一执行
        # tasks.append((volts_n, info, cells, dt))
        plots(volts_n, info, cells, dt)

        if save:
            f = save_fig_path % ("neurons_%s_%s.png" % (parameter_set, config))
            c302.print_("Saving figure to: %s" % os.path.abspath(f))
            plt.savefig(f, bbox_inches="tight")

        generate_traces_plot(
            config,
            parameter_set,
            xvals,
            yvals,
            info,
            labels,
            save=save,
            save_fig_path=save_fig_path,
            voltage=True,
            muscles=False,
        )

    # ── 第 2 段：绘制肌肉膜电位 ──────────────────────────

    muscles.sort(key=natsort)
    muscles.reverse()

    xvals = []
    yvals = []
    labels = []

    if len(muscles) > 0:
        c302.print_("Plotting muscle voltages")

        template_m = "{0}/0/GenericMuscleCell/{1}"
        if parameter_set.startswith("A") or parameter_set.startswith("B"):
            template_m = "{0}/0/generic_muscle_iaf_cell/{1}"

        # 逐个提取肌肉膜电位，并构造热图矩阵与轨迹图输入
        for muscle in muscles:
            mv = lems_results[template_m.format(muscle, "v")]

            xvals.append(times)
            labels.append(muscle)

            if muscle == muscles[0]:
                mvolts_n = np.array([[vv * 1000 for vv in mv]])
            else:
                mvolts_n = np.append(mvolts_n, [[vv * 1000 for vv in mv]], axis=0)
            yvals.append(mvolts_n[-1])

        info = "Membrane potentials of %i muscle(s) (%s %s)" % (
            len(muscles),
            config,
            parameter_set,
        )

        plots(mvolts_n, info, muscles, dt)

        if save:
            f = save_fig_path % ("muscles_%s_%s.png" % (parameter_set, config))
            c302.print_("Saving figure to: %s" % os.path.abspath(f))
            plt.savefig(f, bbox_inches="tight")

        generate_traces_plot(
            config,
            parameter_set,
            xvals,
            yvals,
            info,
            labels,
            save=save,
            save_fig_path=save_fig_path,
            voltage=True,
            muscles=True,
        )

    # ── 第 3 段：绘制神经元活性 / [Ca2+] ────────────────────

    if plot_ca and parameter_set not in paramsets_no_calcium and len(cells) > 0:
        c302.print_("Plotting neuron activities ([Ca2+])")
        variable = "activity"
        description = "Activity"

        # Level C/D 使用 ``caConc``，其余参数集使用 ``activity`` 字段
        if parameter_set.startswith("C") or parameter_set.startswith("D"):
            variable = "caConc"
            description = "[Ca2+]"

        xvals = []
        yvals = []
        labels = []

        info = "%s of %i neurons (%s %s)" % (
            description,
            len(cells),
            config,
            parameter_set,
        )

        # 逐个提取神经元活性或钙浓度，构造热图矩阵与轨迹图输入
        for cell in cells:
            a = lems_results[template.format(cell, variable)]

            xvals.append(times)
            yvals.append(a)
            labels.append(cell)

            if cell == cells[0]:
                activities_n = np.array([a])
            else:
                activities_n = np.append(activities_n, [a], axis=0)

        plots(activities_n, info, cells, dt)

        if save:
            f = save_fig_path % ("neuron_activity_%s_%s.png" % (parameter_set, config))
            c302.print_("Saving figure to: %s" % os.path.abspath(f))
            plt.savefig(f, bbox_inches="tight")

        generate_traces_plot(
            config,
            parameter_set,
            xvals,
            yvals,
            info,
            labels,
            save=save,
            save_fig_path=save_fig_path,
            voltage=False,
            muscles=False,
        )

    # ── 第 4 段：绘制肌肉活性 / [Ca2+] ─────────────────────

    if plot_ca and parameter_set not in paramsets_no_calcium and len(muscles) > 0:
        c302.print_("Plotting muscle activities ([Ca2+])")
        variable = "activity"
        description = "Activity"

        # Level C/D 使用 ``caConc``，其余参数集使用 ``activity`` 字段
        if parameter_set.startswith("C") or parameter_set.startswith("D"):
            variable = "caConc"
            description = "[Ca2+]"

        xvals = []
        yvals = []
        labels = []

        info = "%s of %i muscles (%s %s)" % (
            description,
            len(muscles),
            config,
            parameter_set,
        )

        # 逐个提取肌肉活性或钙浓度，构造热图矩阵与轨迹图输入
        for m in muscles:
            a = lems_results[template_m.format(m, variable)]

            xvals.append(times)
            yvals.append(a)
            labels.append(m)

            if m == muscles[0]:
                activities_n = np.array([a])
            else:
                activities_n = np.append(activities_n, [a], axis=0)

        plots(activities_n, info, muscles, dt)

        if save:
            f = save_fig_path % ("muscle_activity_%s_%s.png" % (parameter_set, config))
            c302.print_("Saving figure to: %s" % os.path.abspath(f))
            plt.savefig(f, bbox_inches="tight")

        generate_traces_plot(
            config,
            parameter_set,
            xvals,
            yvals,
            info,
            labels,
            save=save,
            save_fig_path=save_fig_path,
            voltage=False,
            muscles=True,
        )

    if show_plot_already:
        try:
            plt.show()
        except KeyboardInterrupt:
            c302.print_("Interrupt received, stopping...")
    else:
        plt.close("all")


def _show_conn_matrix(
    data,
    t,
    all_info_pre,
    all_info_post,
    type,
    save_figure_to=False,
    verbose=True,
    figsize=default_figsize,
    colormap=None,
):
    """内部辅助函数：显示单个连接矩阵热图。

    当矩阵数据全为零时直接返回。否则使用 imshow 绘制热图，
    突触前细胞为 Y 轴、突触后细胞为 X 轴。

    :param data: 二维 numpy 连接权重矩阵
    :param t: 图表副标题
    :param all_info_pre: 突触前细胞信息有序字典
    :param all_info_post: 突触后细胞信息有序字典
    :param type: 网络 ID（用于图表主标题）
    :param save_figure_to: 保存路径，``False`` 表示不保存
    :param verbose: 是否输出详细日志
    :param figsize: 图形尺寸元组
    :param colormap: matplotlib 色彩映射名称
    """
    if data.shape[0] > 0 and data.shape[1] > 0 and np.amax(data) > 0:
        # [备选] 旧版尝试使用对数色标增强稀疏矩阵的对比度
        ##norm = matplotlib.colors.LogNorm(vmin=1, vmax=np.amax(data))
        maxn = int(np.amax(data))
    else:
        ##norm = None
        maxn = 0

    c302.print_(
        "Plotting data of size %s, max %s: %s" % (str(data.shape), maxn, t), verbose
    )

    if maxn == 0:
        c302.print_("No connections!!", verbose)
        return

    fig, ax = plt.subplots(figsize=figsize)
    title = "%s: %s" % (type, t)
    plt.title(title)
    fig.canvas.manager.set_window_title(title)

    # [备选] 可切换为其他 matplotlib 预置色图
    # cm = matplotlib.cm.get_cmap('gist_stern_r')
    if colormap is None:
        cmap = plt.colormaps["gist_stern_r"]
    else:
        # cmap = plt.colormaps['gist_earth']
        # cmap = plt.colormaps['nipy_spectral']
        cmap = plt.colormaps[colormap]

    im = plt.imshow(data, cmap=cmap, interpolation="nearest", norm=None)

    ax = plt.gca()
    # 基于次刻度绘制网格线（细胞数 < 40 时显示）
    if data.shape[0] < 40:
        ax.grid(which="minor", color="grey", linestyle="-", linewidth=0.3)

    xt = np.arange(data.shape[1]) + 0
    ax.set_xticks(xt)
    ax.set_xticks(xt[:-1] + 0.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]) + 0)
    ax.set_yticks(np.arange(data.shape[0]) + 0.5, minor=True)

    # Y 轴显示突触前细胞，X 轴显示突触后细胞
    ax.set_yticklabels([all_info_pre[k][4] for k in all_info_pre])
    ax.set_xticklabels([all_info_post[k][4] for k in all_info_post])
    ax.set_ylabel("presynaptic")
    tick_size = 10 if data.shape[0] < 20 else (8 if data.shape[0] < 40 else 6)
    ax.tick_params(axis="y", labelsize=tick_size)
    ax.set_xlabel("postsynaptic")
    ax.tick_params(axis="x", labelsize=tick_size)
    fig.autofmt_xdate()

    # [备选] 旧版使用 pcolor 绘制热图
    # heatmap = ax.pcolor(data, cmap='gist_stern')
    cbar = plt.colorbar(im, ticks=range(maxn + 1))
    cbar.set_ticklabels(range(maxn + 1))
    if save_figure_to:
        c302.print_("Saving connectivity figure to: %s" % save_figure_to)
        plt.savefig(save_figure_to, bbox_inches="tight")
    else:
        c302.print_("Not saving figure", verbose)


def generate_conn_matrix(
    nml_doc,
    save_fig_dir=None,
    verbose=False,
    figsize=default_figsize,
    order_by_type=False,
    colormap=None,
):
    """从 NeuroML 文档生成完整的连接矩阵可视化。

    解析网络中的所有连续投射（化学突触）和电投射（缝隙连接），
    按兴奋性/抑制性和神经元/肌肉四象限分别绘制热图。

    :param nml_doc: NeuroML 文档对象
    :param save_fig_dir: 图片保存目录，``None`` 表示不保存
    :param verbose: 是否输出详细日志
    :param figsize: 图形尺寸元组
    :param order_by_type: 是否按细胞类型排序（保留未实现）
    :param colormap: matplotlib 色彩映射名称
    """
    net = nml_doc.networks[0]

    cc_exc_conns = {}   # 兴奋性化学突触连接字典 {pre: {post: weight}}
    cc_inh_conns = {}   # 抑制性化学突触连接字典
    all_cells = []      # 所有参与连接的细胞名称

    for cp in net.continuous_projections:
        if cp.presynaptic_population not in cc_exc_conns.keys():
            cc_exc_conns[cp.presynaptic_population] = {}
        if cp.presynaptic_population not in cc_inh_conns.keys():
            cc_inh_conns[cp.presynaptic_population] = {}

        if cp.presynaptic_population not in all_cells:
            all_cells.append(cp.presynaptic_population)
        if cp.postsynaptic_population not in all_cells:
            all_cells.append(cp.postsynaptic_population)

        for c in cp.continuous_connection_instance_ws:
            if "inh" in c.post_component:
                cc_inh_conns[cp.presynaptic_population][cp.postsynaptic_population] = (
                    float(c.weight)
                )
            else:
                cc_exc_conns[cp.presynaptic_population][cp.postsynaptic_population] = (
                    float(c.weight)
                )

    gj_conns = {}  # 电突触（缝隙连接）字典 {pre: {post: weight}}
    for ep in net.electrical_projections:
        if ep.presynaptic_population not in gj_conns.keys():
            gj_conns[ep.presynaptic_population] = {}

        if ep.presynaptic_population not in all_cells:
            all_cells.append(ep.presynaptic_population)
        if ep.postsynaptic_population not in all_cells:
            all_cells.append(ep.postsynaptic_population)

        for e in ep.electrical_connection_instance_ws:
            gj_conns[ep.presynaptic_population][ep.postsynaptic_population] = float(
                e.weight
            )

    all_cells = sorted(all_cells)

    all_neurons = []
    all_muscles = []
    for c in all_cells:
        if c302.is_muscle(c):
            all_muscles.append(c)
        else:
            all_neurons.append(c)

    try:
        from owmeta_core.bundle import Bundle

        with Bundle("openworm/owmeta-data", version=6) as bnd:
            all_neuron_info, all_muscle_info = c302._get_cell_info(bnd, all_cells)
    except Exception as e:
        # [调试] 可取消注释以输出完整 traceback，定位 owmeta 连接失败原因
        # traceback.print_exc()
        c302.print_(
            "Unable to connect to the owmeta bundle: %s\n Proceeding anyway..." % e
        )
        all_neuron_info, all_muscle_info = c302._get_cell_info(None, all_cells)

    """
    if order_by_type:
        ordered_all_neuron_info = {}
        order = ['(Se)','(InSe)','(In)','(Mo)']

        for o in order:
            for c in all_neuron_info:
                print('Checking: %s'%str(all_neuron_info[c]))
                if o in all_neuron_info[c][4]:
                    print('Adding: %s'%str(all_neuron_info[c]))
                    ordered_all_neuron_info[c] = all_neuron_info[c]


        print('Swapping %s with %s'%(all_neuron_info,ordered_all_neuron_info))
        all_neuron_info = ordered_all_neuron_info"""

    # 构建四象限连接权重矩阵：兴奋/抑制 × 神经元/肌肉
    data_exc_n = np.zeros((len(all_neurons), len(all_neurons)))  # 兴奋→神经元
    data_exc_m = np.zeros((len(all_neurons), len(all_muscles)))  # 兴奋→肌肉

    data_inh_n = np.zeros((len(all_neurons), len(all_neurons)))  # 抑制→神经元
    data_inh_m = np.zeros((len(all_neurons), len(all_muscles)))  # 抑制→肌肉

    for pre in cc_exc_conns.keys():
        for post in cc_exc_conns[pre].keys():
            c302.print_(
                "Exc Conn %s -> %s: %s" % (pre, post, cc_exc_conns[pre][post]), verbose
            )
            if post in all_neurons:
                data_exc_n[all_neurons.index(pre), all_neurons.index(post)] = (
                    cc_exc_conns[pre][post]
                )
            else:
                data_exc_m[all_neurons.index(pre), all_muscles.index(post)] = (
                    cc_exc_conns[pre][post]
                )
            if pre in all_muscles:
                raise Exception("Unexpected...")

    for pre in cc_inh_conns.keys():
        for post in cc_inh_conns[pre].keys():
            c302.print_(
                "Inh Conn %s -> %s: %s" % (pre, post, cc_inh_conns[pre][post]), verbose
            )
            if post in all_neurons:
                data_inh_n[all_neurons.index(pre), all_neurons.index(post)] = (
                    cc_inh_conns[pre][post]
                )
            else:
                data_inh_m[all_neurons.index(pre), all_muscles.index(post)] = (
                    cc_inh_conns[pre][post]
                )
            if pre in all_muscles:
                raise Exception("Unexpected...")

    _show_conn_matrix(
        data_exc_n,
        "Excitatory (non GABA) conns to neurons",
        all_neuron_info,
        all_neuron_info,
        net.id,
        save_figure_to="%s/%s_exc_to_neurons.png" % (save_fig_dir, net.id)
        if save_fig_dir
        else None,
        verbose=verbose,
        figsize=figsize,
        colormap=colormap,
    )

    _show_conn_matrix(
        data_exc_m,
        "Excitatory (non GABA) conns to muscles",
        all_neuron_info,
        all_muscle_info,
        net.id,
        save_figure_to="%s/%s_exc_to_muscles.png" % (save_fig_dir, net.id)
        if save_fig_dir
        else None,
        verbose=verbose,
        figsize=figsize,
        colormap=colormap,
    )

    _show_conn_matrix(
        data_inh_n,
        "Inhibitory (GABA) conns to neurons",
        all_neuron_info,
        all_neuron_info,
        net.id,
        save_figure_to="%s/%s_inh_to_neurons.png" % (save_fig_dir, net.id)
        if save_fig_dir
        else None,
        verbose=verbose,
        figsize=figsize,
        colormap=colormap,
    )

    _show_conn_matrix(
        data_inh_m,
        "Inhibitory (GABA) conns to muscles",
        all_neuron_info,
        all_muscle_info,
        net.id,
        save_figure_to="%s/%s_inh_to_muscles.png" % (save_fig_dir, net.id)
        if save_fig_dir
        else None,
        verbose=verbose,
        figsize=figsize,
        colormap=colormap,
    )

    data_n = np.zeros((len(all_neurons), len(all_neurons)))
    data_n_m = np.zeros((len(all_neurons), len(all_muscles)))
    data_m_m = np.zeros((len(all_muscles), len(all_muscles)))

    neuron_muscle = False
    muscle_muscle = False

    for pre in gj_conns.keys():
        for post in gj_conns[pre].keys():
            c302.print_(
                "Elect Conn %s -> %s: %s" % (pre, post, gj_conns[pre][post]), verbose
            )

            if pre in all_neurons and post in all_neurons:
                data_n[all_neurons.index(pre), all_neurons.index(post)] = gj_conns[pre][
                    post
                ]
            elif (
                pre in all_neurons
                and post in all_muscles
                or pre in all_muscles
                and post in all_neurons
            ):
                if pre in all_neurons:
                    data_n_m[all_neurons.index(pre), all_muscles.index(post)] = (
                        gj_conns[pre][post]
                    )
                else:
                    data_n_m[all_muscles.index(pre), all_neurons.index(post)] = (
                        gj_conns[pre][post]
                    )
                neuron_muscle = True
            elif pre in all_muscles and post in all_muscles:
                muscle_muscle = True
                data_m_m[all_muscles.index(pre), all_muscles.index(post)] = gj_conns[
                    pre
                ][post]
            else:
                raise Exception("Unexpected...")

    _show_conn_matrix(
        data_n,
        "Electrical (gap junction) conns to neurons",
        all_neuron_info,
        all_neuron_info,
        net.id,
        save_figure_to="%s/%s_elec_neurons_neurons.png" % (save_fig_dir, net.id)
        if save_fig_dir
        else None,
        verbose=verbose,
        figsize=figsize,
        colormap=colormap,
    )

    if neuron_muscle:
        _show_conn_matrix(
            data_n_m,
            "Electrical (gap junction) conns between neurons and muscles",
            all_neuron_info,
            all_muscle_info,
            net.id,
            save_figure_to="%s/%s_elec_neurons_muscles.png" % (save_fig_dir, net.id)
            if save_fig_dir
            else None,
            verbose=verbose,
            figsize=figsize,
            colormap=colormap,
        )

    if muscle_muscle:
        _show_conn_matrix(
            data_m_m,
            "Electrical (gap junction) conns between muscles",
            all_muscle_info,
            all_muscle_info,
            net.id,
            save_figure_to="%s/%s_elec_muscles_muscles.png" % (save_fig_dir, net.id)
            if save_fig_dir
            else None,
            verbose=verbose,
            figsize=figsize,
            colormap=colormap,
        )

    # [备选] 旧版曾单独绘制“电突触到肌肉”子图，现已由组合矩阵覆盖
    # _show_conn_matrix(data_m, 'Electrical (gap junction) conns to muscles',all_neuron_info,all_muscle_info, net.id)


if __name__ == "__main__":
    from neuroml.loaders import read_neuroml2_file

    configs = ["c302_C0_Syns.net.nml", "c302_C0_Social.net.nml"]
    #
    configs = ["c302_C0_Syns.net.nml"]
    configs = ["c302_C0_Oscillator.net.nml"]
    configs = ["c302_C0_Muscles.net.nml"]
    configs = [
        "c302_C0_Syns.net.nml",
        "c302_C0_Social.net.nml",
        "c302_C0_Muscles.net.nml",
        "c302_C0_Pharyngeal.net.nml",
        "c302_C0_Oscillator.net.nml",
        "c302_C0_Full.net.nml",
    ]

    figsize = (6.4, 4.8)
    colormap = None

    if "-phar" in sys.argv:
        configs = ["c302_C0_Pharyngeal.net.nml"]

    elif "-osc" in sys.argv:
        configs = ["c302_C1_Oscillator.net.nml"]

    elif "-soc" in sys.argv:
        configs = ["c302_C1_Social.net.nml"]

    elif "-musc" in sys.argv:
        configs = ["c302_C1_Muscles.net.nml"]
        figsize = (10, 10)

    elif "-full" in sys.argv:
        configs = ["c302_C1_Full.net.nml"]
        figsize = (12, 12)
        colormap = "nipy_spectral"

    for c in configs:
        nml_doc = read_neuroml2_file("examples/%s" % c)

        generate_conn_matrix(
            nml_doc,
            save_fig_dir="./examples/summary/images",
            figsize=figsize,
            colormap=colormap,
        )

    if "-nogui" not in sys.argv:
        plt.show()
