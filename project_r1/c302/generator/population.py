# =============================================================================
# 功能描述：
#   种群创建模块。负责在 NeuroML 网络中创建神经元和肌肉的 Population，
#   加载形态文件并分配 3D 位置坐标，以及添加偏置电流输入。
#
# 类与方法索引：
#   get_cell_id_string                   (L39)   — 构建 NeuroML 中引用细胞实例的路径字符串
#   is_cond_based_cell                   (L68)   — 判断参数层级是否为导电模型（Level C 或 D 系列）
#   create_neuron_populations            (L77)   — 在网络中创建神经元种群
#   create_muscle_populations            (L231)  — 在网络中创建肌肉种群
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段四：从 __init__.py 提取重写
#
# 当前维护者：Copilot
# =============================================================================
"""种群创建模块。"""
import logging

import neuroml.loaders as loaders
import neuroml.writers as writers
from neuroml import (
    IncludeType,
    Input,
    InputList,
    Instance,
    Location,
    NeuroMLDocument,
    Population,
    Property,
)

from c302.generator.position import get_cell_position, get_muscle_position, get_muscle_names
from c302.utils.helpers import get_morphology_dir, get_random_colour_hex

logger = logging.getLogger(__name__)


def get_cell_id_string(cell: str, params, muscle: bool = False) -> str:
    """构建 NeuroML 中引用细胞实例的路径字符串。

    格式为 ``../{cell}/0/{component_id}``。
    Level D 的神经元使用细胞名本身作为 component ID。

    :param cell: 细胞名称
    :param params: 参数模型对象
    :param muscle: 是否为肌肉细胞
    :return: NeuroML 实例路径字符串
    """
    # 自动检测体壁肌肉
    if cell in get_muscle_names():
        muscle = True

    if not params.is_level_D():
        # 非 D 级：使用通用细胞模型 ID
        if not muscle:
            return "../%s/0/%s" % (cell, params.generic_neuron_cell.id)
        else:
            return "../%s/0/%s" % (cell, params.generic_muscle_cell.id)
    else:
        # D 级：神经元使用细胞名本身作为组件
        if not muscle:
            return "../%s/0/%s" % (cell, cell)
        else:
            return "../%s/0/%s" % (cell, params.generic_muscle_cell.id)


def is_cond_based_cell(params) -> bool:
    """判断参数层级是否为导电模型（Level C 或 D 系列）。

    :param params: 参数模型对象
    :return: True 若为导电模型
    """
    return params.is_level_C() or params.is_level_D()


def create_neuron_populations(
    net,
    nml_doc: NeuroMLDocument,
    params,
    cell_names: list[str],
    cells: list[str] | None,
    cells_to_stimulate: list[str] | None,
    cells_to_plot: list[str] | None,
    lems_info: dict,
    target_directory: str = "./",
) -> dict:
    """在网络中创建神经元种群。

    遍历每个要包含的细胞，创建 Population + Instance，加载形态，
    分配 3D 坐标，添加偏置电流。

    :param net: NeuroML Network 对象
    :param nml_doc: NeuroML 文档对象
    :param params: 参数模型对象
    :param cell_names: 完整的细胞名称列表（来自读取器）
    :param cells: 要包含的细胞列表（None 表示全部）
    :param cells_to_stimulate: 需要刺激的细胞列表（None 表示全部神经元）
    :param cells_to_plot: 需要绘图的细胞列表（None 表示全部）
    :param lems_info: LEMS 信息字典（原地修改）
    :param target_directory: 输出目录
    :return: ``{cell_name: cell_object}`` 字典
    """
    all_cells: dict = {}
    count = 0

    for cell in cell_names:
        # 仅包含用户指定的细胞
        if cells is not None and cell not in cells:
            continue

        inst = Instance(id="0")

        if not params.is_level_D():
            # 非 D 级使用通用神经元组件
            pop0 = Population(
                id=cell,
                component=params.generic_neuron_cell.id,
                type="populationList",
                size="1",
            )
            cell_id = params.generic_neuron_cell.id
        else:
            # D 级使用细胞名本身作为组件（多室模型）
            pop0 = Population(
                id=cell, component=cell, type="populationList", size="1"
            )
            cell_id = cell

        pop0.instances.append(inst)
        net.populations.append(pop0)

        # 加载细胞形态文件
        cell_file = get_morphology_dir() / f"{cell}.cell.nml"
        doc = loaders.NeuroMLLoader.load(str(cell_file))
        all_cells[cell] = doc.cells[0]

        if params.is_level_D():
            # D 级：为每个细胞创建独立的多室模型文件
            new_cell = params.create_neuron_cell(cell, doc.cells[0].morphology)
            nml_cell_doc = NeuroMLDocument(id=cell)
            nml_cell_doc.cells.append(new_cell)
            new_cell_file = "cells/%s_D.cell.nml" % cell
            nml_file = target_directory + "/" + new_cell_file
            logger.info("Writing new cell to: %s", nml_file)
            writers.NeuroMLWriter.write(nml_cell_doc, nml_file)

            nml_doc.includes.append(IncludeType(href=new_cell_file))
            lems_info["includes"].append(new_cell_file)

            inst.location = Location(0, 0, 0)
        else:
            # 非 D 级：从形态文件读取 soma 位置
            location = doc.cells[0].morphology.segments[0].proximal
            inst.location = Location(
                float(location.x), float(location.y), float(location.z)
            )

        # 添加偏置电流输入
        if cells_to_stimulate is None or cell in cells_to_stimulate:
            target = "../%s/0/%s" % (pop0.id, cell_id)
            input_list = InputList(
                id="Input_%s_%s" % (cell, params.offset_current.id),
                component=params.offset_current.id,
                populations="%s" % cell,
            )
            i0 = Input(id=0, target=target, destination="synapses")
            if params.is_level_D():
                i0.segment_id = 0
            input_list.input.append(i0)
            net.input_lists.append(input_list)

        # 添加绘图/保存条目
        if cells_to_plot is None or cell in cells_to_plot:
            # 电压曲线
            plot = {
                "cell": cell,
                "colour": get_random_colour_hex(),
                "quantity": "%s/0/%s/v" % (cell, cell_id),
            }
            lems_info["plots"].append(plot)

            # Level B 的 activity 曲线
            if params.is_level_B():
                plot = {
                    "cell": cell,
                    "colour": get_random_colour_hex(),
                    "quantity": "%s/0/%s/activity" % (cell, cell_id),
                }
                lems_info["activity_plots"].append(plot)

            # 导电模型的 caConc 曲线
            if is_cond_based_cell(params):
                plot = {
                    "cell": cell,
                    "colour": get_random_colour_hex(),
                    "quantity": "%s/0/%s/caConc" % (cell, cell_id),
                }
                lems_info["activity_plots"].append(plot)

        # 电压保存条目
        save = {
            "cell": cell,
            "quantity": "%s/0/%s/v" % (cell, cell_id),
        }
        lems_info["to_save"].append(save)

        # Level B 的 activity 保存
        if params.is_level_B():
            save = {
                "cell": cell,
                "quantity": "%s/0/%s/activity" % (cell, cell_id),
            }
            lems_info["activity_to_save"].append(save)

        # 导电模型的 caConc 保存
        if is_cond_based_cell(params):
            save = {
                "cell": cell,
                "quantity": "%s/0/%s/caConc" % (cell, cell_id),
            }
            lems_info["activity_to_save"].append(save)

        lems_info["cells"].append(cell)
        count += 1

    logger.info("Finished loading %i cells", count)
    return all_cells


def create_muscle_populations(
    net,
    nml_doc: NeuroMLDocument,
    params,
    all_muscles: list[str],
    muscles_to_include: list[str],
    cells_to_stimulate: list[str] | None,
    lems_info: dict,
) -> None:
    """在网络中创建肌肉种群。

    :param net: NeuroML Network 对象
    :param nml_doc: NeuroML 文档对象
    :param params: 参数模型对象
    :param all_muscles: 所有已知肌肉名称
    :param muscles_to_include: 要包含的肌肉列表
    :param cells_to_stimulate: 需要刺激的细胞列表
    :param lems_info: LEMS 信息字典（原地修改）
    """
    muscle_count = 0
    for muscle in muscles_to_include:
        inst = Instance(id="0")

        # 肌肉使用通用肌肉细胞模型
        pop0 = Population(
            id=muscle,
            component=params.generic_muscle_cell.id,
            type="populationList",
            size="1",
        )
        pop0.properties.append(Property("color", "0 .6 0"))
        pop0.instances.append(inst)
        net.populations.append(pop0)

        # 计算肌肉 3D 坐标
        x, y, z = get_muscle_position(muscle)
        inst.location = Location(x, y, z)

        muscle_cell_id = params.generic_muscle_cell.id
        muscle_cell_class = params.generic_muscle_cell.__class__.__name__

        # 电压曲线
        plot = {
            "cell": muscle,
            "colour": get_random_colour_hex(),
            "quantity": "%s/0/%s/v" % (muscle, muscle_cell_id),
        }
        lems_info["muscle_plots"].append(plot)

        # IafActivityCell 的 activity 曲线
        if muscle_cell_class == "IafActivityCell":
            plot = {
                "cell": muscle,
                "colour": get_random_colour_hex(),
                "quantity": "%s/0/%s/activity" % (muscle, muscle_cell_id),
            }
            lems_info["muscle_activity_plots"].append(plot)

        # Cell 类型的 caConc 曲线
        if muscle_cell_class == "Cell":
            plot = {
                "cell": muscle,
                "colour": get_random_colour_hex(),
                "quantity": "%s/0/%s/caConc" % (muscle, muscle_cell_id),
            }
            lems_info["muscle_activity_plots"].append(plot)

        # 电压保存
        save = {
            "cell": muscle,
            "quantity": "%s/0/%s/v" % (muscle, muscle_cell_id),
        }
        lems_info["muscles_to_save"].append(save)

        # IafActivityCell 的 activity 保存
        if muscle_cell_class == "IafActivityCell":
            save = {
                "cell": muscle,
                "quantity": "%s/0/%s/activity" % (muscle, muscle_cell_id),
            }
            lems_info["muscles_activity_to_save"].append(save)

        # Cell 类型的 caConc 保存
        if muscle_cell_class == "Cell":
            save = {
                "cell": muscle,
                "quantity": "%s/0/%s/caConc" % (muscle, muscle_cell_id),
            }
            lems_info["muscles_activity_to_save"].append(save)

        lems_info["muscles"].append(muscle)
        muscle_count += 1

        # 肌肉的偏置电流输入（仅当明确指定时）
        if cells_to_stimulate is not None and muscle in cells_to_stimulate:
            target = "../%s/0/%s" % (pop0.id, muscle_cell_id)
            input_list = InputList(
                id="Input_%s_%s" % (muscle, params.offset_current.id),
                component=params.offset_current.id,
                populations="%s" % pop0.id,
            )
            i0 = Input(id=0, target=target, destination="synapses")
            if params.is_level_D():
                i0.segment_id = 0
            input_list.input.append(i0)
            net.input_lists.append(input_list)

    logger.info("Finished creating %i muscles", muscle_count)
