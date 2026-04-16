# =============================================================================
# 功能描述：
#   从 CSV 格式的连接组边列表文件读取线虫神经元连接数据。
#   合并了原代码中 UpdatedSpreadsheetDataReader 和 UpdatedSpreadsheetDataReader2
#   两个模块，通过参数化差异（文件名）实现统一的读取器类。
#
# 类与方法索引：
#   _is_neuron_csv                       (L33)   — CSV 格式中判断细胞是否为神经元
#   _get_body_wall_muscle_prefixes_csv   (L43)   — CSV 格式体壁肌肉前缀
#   _is_body_wall_muscle_csv             (L51)   — CSV 格式判断是否体壁肌肉
#   _get_old_muscle_name                 (L60)   — 将 vBWM/dBWM 格式转换为标准 MVL/MDR 格式
#   _get_syntype                         (L79)   — 将 CSV 突触类型映射为标准形式
#   _get_synclass                        (L94)   — 根据细胞名称和突触类型推断神经递质
#   _parse_row                           (L112)  — 解析 CSV 单行数据
#   CsvDataReader                        (L127)  — CSV 格式连接组数据读取器
#     read_data                          (L143)  — 从 CSV 读取神经元连接数据
#     read_muscle_data                   (L179)  — 从 CSV 读取神经肌肉连接数据
#
# 更新日志：
#   2026-04-17  yi  初始创建：合并 UpdatedSpreadsheetDataReader + V2
#
# 当前维护者：yi
# =============================================================================
"""CSV 格式连接组边列表数据读取器。"""
import csv
import logging

from c302.readers import register_reader
from c302.readers.base import BaseDataReader, ConnectionInfo, remove_leading_index_zero
from c302.utils.helpers import get_data_dir

logger = logging.getLogger(__name__)

# 数据文件目录
_DATA_DIR = get_data_dir() / "connectome"


def _is_neuron_csv(cell: str) -> bool:
    """CSV 格式中判断细胞是否为神经元。

    CSV 中神经元名以大写字母开头，肌肉以小写前缀开头。

    :param cell: 细胞名称
    :return: True 表示为神经元
    """
    return cell[0].isupper()


def _get_body_wall_muscle_prefixes_csv() -> list[str]:
    """CSV 格式体壁肌肉前缀。

    :return: 前缀列表
    """
    return ["dBWM", "vBWM"]


def _is_body_wall_muscle_csv(cell: str) -> bool:
    """CSV 格式判断是否为体壁肌肉。

    :param cell: 细胞名称
    :return: True 表示为体壁肌肉
    """
    return cell.startswith(tuple(_get_body_wall_muscle_prefixes_csv()))


def _get_old_muscle_name(muscle: str) -> str | None:
    """将 ``vBWML05`` / ``dBWMR23`` 格式转换为标准 ``MVL05`` / ``MDR23`` 格式。

    :param muscle: 原始肌肉名称
    :return: 标准名称，无法识别时返回 None
    """
    index = int(muscle[5:])
    if index < 10:
        index = "0%s" % index
    if muscle.startswith("vBWML"):
        return "MVL%s" % index
    elif muscle.startswith("vBWMR"):
        return "MVR%s" % index
    elif muscle.startswith("dBWML"):
        return "MDL%s" % index
    elif muscle.startswith("dBWMR"):
        return "MDR%s" % index
    return None


def _get_syntype(syntype: str) -> str:
    """将 CSV 中的突触类型字符串映射为标准形式。

    :param syntype: CSV 中的突触类型，如 ``"electrical"`` 或 ``"chemical"``
    :return: 标准化突触类型字符串
    :raises NotImplementedError: 无法解析的突触类型
    """
    if syntype == "electrical":
        return "GapJunction"
    elif syntype == "chemical":
        return "Send"
    else:
        raise NotImplementedError("Cannot parse syntype '%s'" % syntype)


def _get_synclass(cell: str, syntype: str) -> str:
    """根据突触前细胞名称和突触类型推断神经递质分类。

    :param cell: 突触前细胞名称
    :param syntype: 标准化后的突触类型
    :return: 神经递质分类
    """
    # 缝隙连接统一为 Generic_GJ
    if syntype == "GapJunction":
        return "Generic_GJ"
    # DD/VD 类运动神经元发出 GABA，其余使用乙酰胆碱
    if cell.startswith("DD") or cell.startswith("VD"):
        return "GABA"
    return "Acetylcholine"


def _parse_row(row: dict[str, str]) -> tuple[str, str, int, str, str]:
    """解析 CSV 中的单行数据。

    :param row: csv.DictReader 返回的字典行
    :return: ``(pre, post, num, syntype, synclass)``
    """
    pre = str.strip(row["Source"])
    post = str.strip(row["Target"])
    num = int(row["Weight"])
    syntype = _get_syntype(str.strip(row["Type"]))
    synclass = _get_synclass(pre, syntype)
    return pre, post, num, syntype, synclass


class CsvDataReader(BaseDataReader):
    """CSV 格式连接组数据读取器。

    通过 ``csv_filename`` 参数区分不同数据源：

    - ``"herm_full_edgelist.csv"``：原始 OpenWorm 连接组数据
    - ``"herm_full_edgelist_MODIFIED.csv"``：手工修正版
    """

    # 数据文件名
    csv_filename: str = "herm_full_edgelist.csv"

    # 已知无连接的神经元
    known_nonconnected_cells: list[str] = ["CANL", "CANR"]

    @staticmethod
    def read_data(
        include_nonconnected_cells: bool = False,
    ) -> tuple[list[str], list[ConnectionInfo]]:
        """从 CSV 读取神经元连接数据。

        :param include_nonconnected_cells: 是否包含已知无连接的神经元
        :return: ``(cells, conns)``
        """
        conns: list[ConnectionInfo] = []
        cells: list[str] = []
        filename = str(_DATA_DIR / CsvDataReader.csv_filename)

        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            logger.info("Opened file: %s", filename)

            for row in reader:
                pre, post, num, syntype, synclass = _parse_row(row)

                # 跳过非神经元行
                if not _is_neuron_csv(pre) or not _is_neuron_csv(post):
                    continue

                # 规范化编号前导零
                pre = remove_leading_index_zero(pre)
                post = remove_leading_index_zero(post)

                conns.append(ConnectionInfo(pre, post, num, syntype, synclass))
                if pre not in cells:
                    cells.append(pre)
                if post not in cells:
                    cells.append(post)

            if include_nonconnected_cells:
                for c in CsvDataReader.known_nonconnected_cells:
                    if c not in cells:
                        cells.append(c)

        return cells, conns

    @staticmethod
    def read_muscle_data() -> tuple[list[str], list[str], list[ConnectionInfo]]:
        """从 CSV 读取神经肌肉连接数据。

        :return: ``(neurons, muscles, conns)``
        """
        neurons: list[str] = []
        muscles: list[str] = []
        conns: list[ConnectionInfo] = []
        filename = str(_DATA_DIR / CsvDataReader.csv_filename)

        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            logger.info("Opened file: %s", filename)

            for row in reader:
                pre, post, num, syntype, synclass = _parse_row(row)

                # 过滤：pre 必须是神经元或体壁肌肉，post 必须是体壁肌肉
                if not (
                    _is_neuron_csv(pre) or _is_body_wall_muscle_csv(pre)
                ) or not _is_body_wall_muscle_csv(post):
                    continue

                # 规范化名称
                if _is_neuron_csv(pre):
                    pre = remove_leading_index_zero(pre)
                else:
                    old_name = _get_old_muscle_name(pre)
                    if old_name:
                        pre = old_name
                old_post = _get_old_muscle_name(post)
                if old_post:
                    post = old_post

                conns.append(ConnectionInfo(pre, post, num, syntype, synclass))
                if _is_neuron_csv(pre) and pre not in neurons:
                    neurons.append(pre)
                elif _is_body_wall_muscle_csv(pre) and pre not in muscles:
                    muscles.append(pre)
                if post not in muscles:
                    muscles.append(post)

        return neurons, muscles, conns


class CsvDataReaderModified(CsvDataReader):
    """使用手工修正版 CSV 的读取器。

    数据文件：``herm_full_edgelist_MODIFIED.csv``
    """

    csv_filename: str = "herm_full_edgelist_MODIFIED.csv"


# 注册到读取器注册表
register_reader("UpdatedSpreadsheetDataReader", CsvDataReader)
register_reader("UpdatedSpreadsheetDataReader2", CsvDataReaderModified)
