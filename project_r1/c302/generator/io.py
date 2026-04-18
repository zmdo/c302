# =============================================================================
# 功能描述：
#   文件写出模块。将生成的 NeuroML 网络和 LEMS 仿真配置文件写入磁盘，
#   可选进行 NeuroML2 schema 验证。使用 Airspeed 模板引擎渲染 LEMS XML。
#
# 类与方法索引：
#   merge_with_template                  (L30)   — 使用 Airspeed 模板引擎将变量字典与 LEMS 模板文件合并
#   write_to_file                        (L42)   — 将生成的 NeuroML 网络和 LEMS 仿真文件写入磁盘
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段四：从 __init__.py 提取重写
#
# 当前维护者：Copilot
# =============================================================================
"""文件写出模块。"""
import logging
import os

import airspeed
import neuroml.writers as writers

from c302.utils.helpers import get_xml_dir

logger = logging.getLogger(__name__)

# LEMS 模板文件名
LEMS_TEMPLATE_FILE = "LEMS_c302_TEMPLATE.xml"


def merge_with_template(model: dict, templfile: str) -> str:
    """使用 Airspeed 模板引擎将变量字典与 LEMS 模板文件合并。

    :param model: 变量字典（传入模板的上下文数据）
    :param templfile: 模板文件路径
    :return: 合并后的 XML 字符串
    """
    with open(templfile) as f:
        templ = airspeed.Template(f.read())
    return templ.merge(model)


def write_to_file(
    nml_doc,
    lems_info: dict,
    reference: str,
    template_path: str = "",
    validate: bool = True,
    target_directory: str = ".",
) -> None:
    """将生成的 NeuroML 网络和 LEMS 仿真文件写入磁盘。

    输出两个文件：
    1. ``{reference}.net.nml`` — NeuroML 网络描述文件
    2. ``LEMS_{reference}.xml`` — LEMS 仿真配置文件（由模板渲染）

    :param nml_doc: NeuroML 文档对象
    :param lems_info: LEMS 模板变量字典
    :param reference: 网络标识字符串
    :param template_path: LEMS 模板文件所在目录
    :param validate: 是否进行 NeuroML2 验证
    :param target_directory: 输出目录
    """
    # 写入 .net.nml 文件
    nml_file = os.path.join(target_directory, "%s.net.nml" % reference)
    logger.info("Writing generated network to: %s", os.path.realpath(nml_file))
    writers.NeuroMLWriter.write(nml_doc, nml_file)

    # 渲染 LEMS 模板并写入
    lems_file_name = os.path.join(target_directory, "LEMS_%s.xml" % reference)
    # 若未指定模板路径，使用 data/xml/ 下的模板
    if not template_path:
        template_path = str(get_xml_dir()) + "/"
    merged = merge_with_template(lems_info, template_path + LEMS_TEMPLATE_FILE)
    with open(lems_file_name, "w") as lems:
        lems.write(merged)

    logger.info("Written LEMS file to: %s", lems_file_name)

    # 可选 NeuroML2 验证
    if validate:
        from neuroml.utils import validate_neuroml2

        try:
            validate_neuroml2(nml_file)
        except Exception as e:
            logger.warning("Problem validating NeuroML: %s", e)
