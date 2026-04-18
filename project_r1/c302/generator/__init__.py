# =============================================================================
# 功能描述：
#   网络生成引擎主入口。generate() 函数协调调用 position、population、
#   connection、stimulation 和 io 子模块，将连接组数据与参数化模型组装为
#   完整的 NeuroML2 网络文档。
#
# 类与方法索引：
#   _load_data_reader                    (L49)   — 动态导入并返回指定名称的数据读取器
#   get_cell_names_and_connection        (L64)   — 读取连接组数据，返回所有细胞名称和突触连接列表
#   get_cell_muscle_names_and_connection (L79)   — 读取神经元-肌肉连接数据
#   generate                             (L113)  — 生成 NeuroML 2 网络文档
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段四：从 __init__.py 提取重写
#
# 当前维护者：Copilot
# =============================================================================
"""网络生成引擎主入口。"""
import logging
import os
import random
import shutil

from lxml import etree
from neuroml import IncludeType, NeuroMLDocument, Network, Property

from c302.generator.connection import (
    create_muscle_connections,
    create_neuron_connections,
    mirror_param,
    set_param,
)
from c302.generator.io import write_to_file
from c302.generator.population import (
    create_muscle_populations,
    create_neuron_populations,
    is_cond_based_cell,
)
from c302.utils.helpers import get_xml_dir, is_regex_string

logger = logging.getLogger(__name__)

# 默认数据读取器
DEFAULT_DATA_READER = "cect.readers.SpreadsheetDataReader"
# 前向运动专用数据读取器
FW_DATA_READER = "cect.readers.UpdatedSpreadsheetDataReader2"


def _load_data_reader(data_reader: str):
    """动态导入并返回指定名称的数据读取器。

    :param data_reader: 读取器模块路径字符串
    :return: 读取器实例或模块
    """
    import importlib

    if "cect" in data_reader:
        dr = importlib.import_module(data_reader)
        return dr.get_instance()
    else:
        return importlib.import_module("c302.%s" % data_reader)


def get_cell_names_and_connection(
    data_reader: str,
) -> tuple[list[str], list]:
    """读取连接组数据，返回所有细胞名称和突触连接列表。

    :param data_reader: 数据读取器模块路径
    :return: ``(cell_names, conns)`` 元组
    """
    cell_names, conns = _load_data_reader(data_reader).read_data(
        include_nonconnected_cells=True
    )
    cell_names.sort()
    return cell_names, conns


def get_cell_muscle_names_and_connection(
    data_reader: str,
) -> tuple[list[str], list[str], list]:
    """读取神经元-肌肉连接数据。

    过滤掉非体壁肌肉（MANAL/MVULVA），仅保留已知的体壁肌肉。

    :param data_reader: 数据读取器模块路径
    :return: ``(mneurons, all_known_muscles, muscle_conns)`` 元组
    """
    from cect.Cells import BODY_WALL_MUSCLE_NAMES

    mneurons, all_muscles, muscle_conns = _load_data_reader(
        data_reader
    ).read_muscle_data()

    # 移除非体壁特殊肌肉
    if "MANAL" in all_muscles:
        all_muscles.remove("MANAL")
    if "MVULVA" in all_muscles:
        all_muscles.remove("MVULVA")

    # 仅保留已知体壁肌肉
    if len(all_muscles) == 0:
        all_known_muscles = BODY_WALL_MUSCLE_NAMES
    else:
        all_known_muscles = [m for m in all_muscles if m in BODY_WALL_MUSCLE_NAMES]

    all_known_muscles = sorted(all_known_muscles)
    logger.info("Using for muscles: %s", all_known_muscles)

    return mneurons, all_known_muscles, muscle_conns


def generate(
    net_id: str,
    params,
    data_reader: str = DEFAULT_DATA_READER,
    cells: list[str] | None = None,
    cells_to_plot: list[str] | None = None,
    cells_to_stimulate: list[str] | None = None,
    muscles_to_include: list[str] | None = None,
    conns_to_include: list | None = None,
    conns_to_exclude: list | None = None,
    conn_number_override: dict | None = None,
    conn_number_scaling: dict | None = None,
    conn_polarity_override: dict | None = None,
    duration: float = 500.0,
    dt: float = 0.01,
    vmin: float | None = None,
    vmax: float | None = None,
    seed: int = 1234,
    param_overrides: dict | None = None,
    target_directory: str = "./",
) -> NeuroMLDocument:
    """生成 NeuroML 2 网络文档。

    主要步骤：
    1. 处理参数覆盖并创建模型组件
    2. 初始化 NeuroML 文档和网络
    3. 创建神经元种群（加载形态、分配坐标、添加偏置电流）
    4. 创建肌肉种群
    5. 创建神经元间连接
    6. 创建神经肌肉连接
    7. 写出文件

    :param net_id: 网络唯一标识
    :param params: 参数化模型对象
    :param data_reader: 数据读取器模块路径
    :param cells: 包含的细胞列表（None 表示全部）
    :param cells_to_plot: 需要绘图的细胞列表
    :param cells_to_stimulate: 需要刺激的细胞列表
    :param muscles_to_include: 包含的肌肉列表（None/True 全部；空列表/False 无）
    :param conns_to_include: 连接白名单
    :param conns_to_exclude: 连接黑名单
    :param conn_number_override: 连接数量覆盖字典
    :param conn_number_scaling: 连接数量缩放字典
    :param conn_polarity_override: 连接极性覆盖字典
    :param duration: 仿真时长（ms）
    :param dt: 时间步长（ms）
    :param vmin: 绘图电压下限（mV）
    :param vmax: 绘图电压上限（mV）
    :param seed: 随机数种子
    :param param_overrides: 参数覆盖字典
    :param target_directory: 输出目录
    :return: ``NeuroMLDocument`` 对象
    """
    if param_overrides is None:
        param_overrides = {}
    if conns_to_include is None:
        conns_to_include = []
    if conns_to_exclude is None:
        conns_to_exclude = []
    if muscles_to_include is None:
        muscles_to_include = []

    # 确定是否跳过验证（某些层级生成的文件不通过标准验证）
    validate = not (
        params.is_level_B()
        or params.is_level_C0()
        or params.is_level_C2()
        or params.is_level_D1()
    )

    # ── 步骤 1：处理参数覆盖 ──
    regex_param_overrides: dict = {"mirrored_elec_conn_params": {}}
    if param_overrides:
        for k, v in param_overrides.items():
            if k == "mirrored_elec_conn_params":
                # 镜像电连接参数
                for mk, mv in v.items():
                    if is_regex_string(mk):
                        regex_param_overrides["mirrored_elec_conn_params"][mk] = mv
                    else:
                        mirror_param(params, mk, mv)
            elif k == "custom_component_type_gate_overrides":
                continue  # 延迟到 XML 处理阶段
            elif is_regex_string(k):
                regex_param_overrides[k] = v
            else:
                set_param(params, k, v)

    # ── 步骤 2：创建所有细胞和突触模型组件 ──
    params.create_models()

    # ── 步骤 3：设置绘图电压范围默认值 ──
    if vmin is None:
        if params.is_level_A() or params.is_level_B():
            vmin = -52.0
        elif params.is_level_C() or params.is_level_D():
            vmin = -60.0
        else:
            vmin = -52.0

    if vmax is None:
        if params.is_level_A() or params.is_level_B():
            vmax = -28.0
        elif params.is_level_C() or params.is_level_D():
            vmax = 25.0
        else:
            vmax = -28.0

    random.seed(seed)

    # 构建信息注释
    info = (
        "\n\nParameters and setting used to generate this network:\n\n"
        + "    Data reader:                    %s\n" % data_reader
        + "    Cells:                          %s\n"
        % (cells if cells is not None else "All cells")
        + "    Cell stimulated:                %s\n"
        % (cells_to_stimulate if cells_to_stimulate is not None else "All neurons")
        + "    Connection numbers overridden:  %s\n"
        % (conn_number_override if conn_number_override is not None else "None")
        + "    Connection numbers scaled:      %s\n"
        % (conn_number_scaling if conn_number_scaling is not None else "None")
        + "    Connection polarities override: %s\n" % conn_polarity_override
        + "    Muscles:                        %s\n"
        % (muscles_to_include if muscles_to_include is not None else "All muscles")
    )

    info_settings = info
    info += "\n%s\n" % (params.bioparameter_info("    "))

    # ── 步骤 4：初始化 NeuroML 文档和网络 ──
    nml_doc = NeuroMLDocument(id=net_id, notes=info)

    # 按层级将细胞模型添加到文档
    if params.is_level_A() or params.is_level_B() or params.level == "BC1":
        nml_doc.iaf_cells.append(params.generic_muscle_cell)
        nml_doc.iaf_cells.append(params.generic_neuron_cell)
    elif params.is_level_C():
        nml_doc.cells.append(params.generic_muscle_cell)
        nml_doc.cells.append(params.generic_neuron_cell)
    elif params.is_level_D():
        nml_doc.cells.append(params.generic_muscle_cell)
    elif params.is_level_X():
        nml_doc.cells.append(params.generic_muscle_cell)
        nml_doc.cells.append(params.generic_neuron_cell)

    net = Network(id=net_id)
    nml_doc.networks.append(net)

    net.properties.append(Property("recommended_duration_ms", duration))
    net.properties.append(Property("recommended_dt_ms", dt))

    # 添加偏置电流生成器
    nml_doc.pulse_generators.append(params.offset_current)

    # 导电模型添加离子浓度模型
    if is_cond_based_cell(params):
        if isinstance(params.concentration_model, list):
            nml_doc.fixed_factor_concentration_models.extend(params.concentration_model)
        else:
            nml_doc.fixed_factor_concentration_models.append(params.concentration_model)

    # ── 步骤 5：处理自定义组件类型 XML ──
    lems_info: dict = {
        "comment": info,
        "reference": net_id,
        "duration": duration,
        "dt": dt,
        "vmin": vmin,
        "vmax": vmax,
        "plots": [],
        "activity_plots": [],
        "muscle_plots": [],
        "muscle_activity_plots": [],
        "to_save": [],
        "activity_to_save": [],
        "muscles_to_save": [],
        "muscles_activity_to_save": [],
        "cells": [],
        "muscles": [],
        "includes": [],
    }

    if params.custom_component_types_definitions:
        ctds = params.custom_component_types_definitions
        if isinstance(ctds, str):
            ctds = [ctds]
        for ctd in ctds:
            if target_directory != "./":
                # 从数据目录拷贝（或修改后写出）XML 定义文件
                def_file = str(get_xml_dir() / ctd) if not os.path.isabs(ctd) else ctd

                if (
                    param_overrides
                    and "custom_component_type_gate_overrides" in param_overrides
                    and param_overrides["custom_component_type_gate_overrides"]
                ):
                    # 使用 lxml 修改 ion channel 参数
                    root = etree.parse(def_file).getroot()
                    for k, v in param_overrides[
                        "custom_component_type_gate_overrides"
                    ].items():
                        channel_id = k.split("__")[0]
                        gate_id = k.split("__")[1]
                        gate_attr = k.split("__")[2]

                        for c1 in root:
                            if (
                                c1.tag != "ionChannel"
                                and c1.attrib.get("id") != channel_id
                            ):
                                continue
                            for c2 in c1:
                                if (
                                    c2.tag != "gateHHtauInf"
                                    and c2.attrib.get("id") != gate_id
                                ):
                                    continue
                                for child in c2:
                                    if child.attrib.get(gate_attr):
                                        child.set(gate_attr, v)
                    etree.ElementTree(root).write(
                        os.path.join(target_directory, ctd), pretty_print=True
                    )
                else:
                    shutil.copy(def_file, target_directory)

            if target_directory == "./" and not os.path.isfile(ctd):
                # 退回到数据目录查找
                ctd = str(get_xml_dir() / ctd)

            lems_info["includes"].append(ctd)
            nml_doc.includes.append(IncludeType(href=ctd))

    # ── 步骤 6：读取连接组数据 ──
    cell_names, conns = get_cell_names_and_connection(data_reader)

    # ── 步骤 7：创建神经元种群 ──
    all_cells = create_neuron_populations(
        net, nml_doc, params, cell_names, cells,
        cells_to_stimulate, cells_to_plot, lems_info,
        target_directory=target_directory,
    )

    logger.info("Loaded %i neuron populations", len(all_cells))

    # ── 步骤 8：创建肌肉种群 ──
    mneurons, all_muscles, muscle_conns = get_cell_muscle_names_and_connection(
        data_reader
    )

    # 规范化 muscles_to_include
    if muscles_to_include is True or muscles_to_include is None:
        muscles_to_include = all_muscles
    elif muscles_to_include is False:
        muscles_to_include = []

    # 验证肌肉名称
    for m in muscles_to_include:
        if m not in all_muscles:
            raise ValueError("%s is not among the known muscles" % m)

    if len(muscles_to_include) > 0:
        create_muscle_populations(
            net, nml_doc, params, all_muscles, muscles_to_include,
            cells_to_stimulate, lems_info,
        )

    # ── 步骤 9：创建连接 ──
    existing_synapses: dict = {}

    # 神经元间连接
    create_neuron_connections(
        net, nml_doc, params, conns, lems_info,
        regex_param_overrides, param_overrides,
        conns_to_include, conns_to_exclude,
        conn_number_override, conn_number_scaling, conn_polarity_override,
        existing_synapses,
    )

    # 神经肌肉连接
    if len(muscles_to_include) > 0:
        create_muscle_connections(
            net, nml_doc, params, muscle_conns, lems_info,
            muscles_to_include,
            regex_param_overrides, param_overrides,
            conns_to_include, conns_to_exclude,
            conn_number_override, conn_number_scaling, conn_polarity_override,
            existing_synapses,
        )

    # ── 步骤 10：如果有参数覆盖，更新注释 ──
    if param_overrides:
        info_new = info_settings + "\n%s\n" % (params.bioparameter_info("    "))
        nml_doc.notes = info_new
        lems_info["comment"] = info_new

    # ── 步骤 11：写出文件 ──
    template_path = str(get_xml_dir()) + "/"
    write_to_file(
        nml_doc, lems_info, net_id,
        template_path=template_path,
        validate=validate,
        target_directory=target_directory,
    )

    return nml_doc
