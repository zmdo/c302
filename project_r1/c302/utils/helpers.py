# =============================================================================
# 功能描述：
#   通用工具函数模块，包含项目路径管理、字符串格式化、正则表达式匹配
#   和随机颜色生成等基础工具。所有函数均无 NeuroML 或仿真域的依赖。
#
# 类与方法索引：
#   get_project_root                 (L24)   — 获取项目根目录（包含 pyproject.toml）
#   get_data_dir                     (L40)   — 获取 data/ 目录路径
#   get_morphology_dir               (L49)   — 获取 data/morphology/ 目录路径
#   get_xml_dir                      (L58)   — 获取 data/xml/ 目录路径
#   get_connectome_dir               (L67)   — 获取 data/connectome/ 目录路径
#   get_parameters_dir               (L76)   — 获取 data/parameters/ 目录路径
#   get_str_from_exponential         (L85)   — 将浮点数格式化为 15 位小数字符串
#   get_random_colour_hex            (L97)   — 生成随机 #RRGGBB 颜色字符串
#   is_regex_string                  (L116)  — 判断字符串是否为正则格式
#   regex_match                      (L126)  — 对正则格式的模式执行匹配
#   elem_in_coll_matches_conn        (L138)  — 检查集合中是否有正则元素匹配连接字符串
#
# 更新日志：
#   2026-04-17  yi  初始创建
#
# 当前维护者：yi
# =============================================================================
import logging
import random
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """获取项目根目录（包含 pyproject.toml 的目录）。

    :return: 项目根目录路径
    :raises FileNotFoundError: 无法找到 pyproject.toml
    """
    # 从当前文件向上逐级查找包含 pyproject.toml 的目录
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise FileNotFoundError("无法找到项目根目录（未找到 pyproject.toml）")


def get_data_dir() -> Path:
    """获取数据目录路径。

    :return: data/ 目录路径
    """
    return get_project_root() / "data"


def get_morphology_dir() -> Path:
    """获取细胞形态文件目录。

    :return: data/morphology/ 目录路径
    """
    return get_data_dir() / "morphology"


def get_xml_dir() -> Path:
    """获取 XML 资源目录。

    :return: data/xml/ 目录路径
    """
    return get_data_dir() / "xml"


def get_connectome_dir() -> Path:
    """获取连接组数据目录。

    :return: data/connectome/ 目录路径
    """
    return get_data_dir() / "connectome"


def get_parameters_dir() -> Path:
    """获取参数文件目录。

    :return: data/parameters/ 目录路径
    """
    return get_data_dir() / "parameters"


def get_str_from_exponential(num: float) -> str:
    """将浮点数格式化为 15 位小数的字符串表示。

    例如 ``1e-05`` 会被格式化为 ``"0.000010000000000"``。

    :param num: 待格式化的数值
    :return: 含 15 位小数的字符串
    """
    return f"{num:.15f}"


def get_random_colour_hex() -> str:
    """生成随机十六进制颜色字符串（``#RRGGBB``），用于绘图颜色分配。

    :return: 颜色字符串，如 ``"#3a7f0c"``
    """
    # 生成三个 0-255 随机整数并格式化为两位十六进制
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"#{r:02x}{g:02x}{b:02x}"


def is_regex_string(pattern: str) -> bool:
    """判断字符串是否为正则表达式格式（同时含 ``^`` 和 ``$``）。

    :param pattern: 待检查字符串
    :return: 是否为正则格式
    """
    return "^" in pattern and "$" in pattern


def regex_match(pattern: str, text: str) -> re.Match | None:
    """当 pattern 为正则表达式时执行匹配。

    仅在 pattern 被 :func:`is_regex_string` 判定为正则格式时才执行
    ``re.match``，否则返回 None。

    :param pattern: 模式字符串
    :param text: 待匹配字符串
    :return: 匹配对象或 None
    """
    # 非正则格式直接返回 None
    if not is_regex_string(pattern):
        return None
    return re.match(pattern, text)


def elem_in_coll_matches_conn(coll: list[str] | set[str], conn: str) -> bool:
    """检查集合中是否有正则元素匹配给定的连接字符串。

    :param coll: 字符串集合（可能含正则模式）
    :param conn: 连接简写字符串
    :return: 是否存在匹配
    """
    for elem in coll:
        # 逐个尝试正则匹配
        if regex_match(elem, conn) is not None:
            return True
    return False
