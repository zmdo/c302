# =============================================================================
# 功能描述：
#   仿真编排模块。提供 run_c302() 函数，串联配置加载 → 网络生成 →
#   LEMS 仿真 → 结果绘图的完整流程。
#
# 类与方法索引：
#   run_c302                             (L29)   — 仿真编排主函数：配置加载 → 网络生成 → LEMS 仿真 → 结果绘图
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段六：新建
#
# 当前维护者：Copilot
# =============================================================================
"""仿真编排模块。"""
import logging
import os
from pathlib import Path

from pyneuroml import pynml

from c302.configs import get_config

logger = logging.getLogger(__name__)

# 支持的仿真后端
SIMULATORS = ("jNeuroML", "jNeuroML_NEURON")


def run_c302(
    config: str,
    parameter_set: str,
    duration: float,
    dt: float,
    simulator: str = "jNeuroML",
    *,
    data_reader: str = "cect.readers.SpreadsheetDataReader",
    target_directory: str = "examples",
    save: bool = False,
    show_plot_already: bool = True,
    verbose: bool = False,
    plot_ca: bool = True,
    plot_connectivity: bool = False,
    param_overrides: dict | None = None,
    config_param_overrides: dict | None = None,
    save_fig_to: str | None = None,
) -> tuple[list, list, object, object]:
    """仿真编排主函数：配置加载 → 网络生成 → LEMS 仿真 → 结果绘图。

    :param config: 配置名称（如 "IClamp", "Full"）
    :param parameter_set: 参数层级（"A"/"B"/"C"/"C0"/"C1"/"C2"/"D"/"D1"/"W2D"）
    :param duration: 仿真时长（毫秒）
    :param dt: 仿真时间步长（毫秒）
    :param simulator: 仿真后端，"jNeuroML" 或 "jNeuroML_NEURON"
    :param data_reader: 数据读取器模块路径
    :param target_directory: 输出目录
    :param save: 是否保存图片
    :param show_plot_already: 是否立即显示图形窗口
    :param verbose: 是否输出详细日志
    :param plot_ca: 是否绘制钙浓度/活性图
    :param plot_connectivity: 是否绘制连接矩阵
    :param param_overrides: 生物参数覆盖字典
    :param config_param_overrides: 配置级参数覆盖字典
    :param save_fig_to: 图片保存目录覆盖
    :return: (cells, cells_to_stimulate, params, muscles_to_include) 四元组
    :raises ValueError: simulator 不在支持列表中
    """
    if simulator not in SIMULATORS:
        raise ValueError(
            f"不支持的仿真后端: {simulator}，可选: {SIMULATORS}"
        )

    if param_overrides is None:
        param_overrides = {}
    if config_param_overrides is None:
        config_param_overrides = {}

    logger.info(
        "生成 c302_%s_%s 并运行 %sms (dt=%sms) 于 %s",
        parameter_set, config, duration, dt, simulator,
    )

    # ── 步骤 1：加载配置并生成 NeuroML 网络 ──
    setup_func = get_config(config)

    # 确保输出目录存在
    os.makedirs(target_directory, exist_ok=True)

    # 调用配置的 setup 函数生成网络
    cells, cells_to_stimulate, params, muscles_to_include, nml_doc = setup_func(
        parameter_set,
        generate_flag=True,
        data_reader=data_reader,
        duration=duration,
        dt=dt,
        target_directory=target_directory,
        verbose=verbose,
        param_overrides=param_overrides,
        config_param_overrides=config_param_overrides,
    )

    # ── 步骤 2：运行 LEMS 仿真 ──
    lems_file = f"LEMS_c302_{parameter_set}_{config}.xml"
    lems_path = os.path.join(target_directory, lems_file)

    # jNeuroML 工具在当前目录下工作，需要临时切换
    orig_dir = os.getcwd()
    os.chdir(target_directory)

    # 确保图像保存目录存在
    fig_dir = save_fig_to or "summary"
    image_dir = os.path.join(fig_dir, "images")
    os.makedirs(image_dir, exist_ok=True)

    try:
        if simulator == "jNeuroML":
            # 使用纯 Java jNeuroML 仿真后端
            results = pynml.run_lems_with_jneuroml(
                lems_file, nogui=True, load_saved_data=True, verbose=verbose,
            )
        else:
            # 使用 NEURON 仿真后端（更快，支持更多模型类型）
            results = pynml.run_lems_with_jneuroml_neuron(
                lems_file, nogui=True, load_saved_data=True, verbose=verbose,
            )

        logger.info("仿真完成: %s", lems_file)

        # ── 步骤 3：绘制结果 ──
        try:
            from c302.visualization.traces import plot_c302_results

            plot_c302_results(
                results,
                config,
                parameter_set,
                directory=image_dir,
                save=save,
                show_plot_already=show_plot_already,
                data_reader=data_reader,
                plot_ca=plot_ca,
            )
        except ImportError:
            # 可视化模块可能未安装 matplotlib
            logger.warning("可视化模块不可用，跳过绘图")

        # ── 步骤 4（可选）：生成连接矩阵 ──
        if plot_connectivity and nml_doc is not None:
            try:
                from c302.visualization.connectivity import generate_conn_matrix

                generate_conn_matrix(nml_doc, save_fig_dir=image_dir)
            except ImportError:
                logger.warning("连接矩阵可视化不可用，跳过")

    finally:
        # 始终恢复工作目录
        os.chdir(orig_dir)

    return cells, cells_to_stimulate, params, muscles_to_include
