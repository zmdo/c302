# =============================================================================
# 功能描述：
#   全 302 神经元网络配置脚本。
#   使用数据读取器获取全部细胞名称，施加 PLM 触觉刺激。
#
# 类与方法索引：
#   setup                                (L25)   — 全 302 神经元网络配置
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段五：从 c302_Full.py 重写
#
# 当前维护者：Copilot
# =============================================================================
"""Full 配置脚本。"""
import logging

from c302.configs import register_config
from c302.generator import DEFAULT_DATA_READER, generate, get_cell_names_and_connection
from c302.parameters import get_parameter_set

logger = logging.getLogger(__name__)


@register_config("Full")
def setup(
    parameter_set,
    generate_flag=False,
    duration=500,
    dt=0.05,
    target_directory="examples",
    data_reader=DEFAULT_DATA_READER,
    param_overrides=None,
    config_param_overrides=None,
    verbose=True,
):
    """全 302 神经元网络配置。

    :return: ``(cell_names, cells_to_stimulate, params, muscles, nml_doc)``
    """
    if param_overrides is None:
        param_overrides = {}

    params = get_parameter_set(parameter_set)

    muscles_to_include = True

    cells_to_stimulate = ["PLML", "PLMR"]
    cells_to_plot = [
        "AVBL", "AVBR", "PVCL", "PVCR",
        "DB1", "DB2", "VB1", "VB2",
        "DD1", "DD2", "VD1", "VD2",
    ]

    params.set_bioparameter(
        "unphysiological_offset_current", "5pA", "Testing Full net", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_del", "50 ms", "Testing Full net", "0"
    )
    params.set_bioparameter(
        "unphysiological_offset_current_dur", "900 ms", "Testing Full net", "0"
    )

    reference = "c302_%s_Full" % parameter_set
    cell_names, conns = get_cell_names_and_connection(data_reader)

    nml_doc = None

    if generate_flag:
        nml_doc = generate(
            reference,
            params,
            cells_to_plot=cells_to_plot,
            cells_to_stimulate=cells_to_stimulate,
            muscles_to_include=muscles_to_include,
            duration=duration,
            dt=dt,
            vmin=-72 if parameter_set == "A" else -52,
            vmax=-48 if parameter_set == "A" else -28,
            target_directory=target_directory,
            param_overrides=param_overrides,
            data_reader=data_reader,
        )

    return cell_names, cells_to_stimulate, params, muscles_to_include, nml_doc
