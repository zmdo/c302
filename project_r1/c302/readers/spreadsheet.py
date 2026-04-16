# =============================================================================
# 功能描述：
#   从 CElegansNeuronTables.xls / NeuronConnectFormatted.xlsx 电子表格读取
#   线虫神经元连接数据的数据读取器。继承 BaseDataReader 抽象基类。
#
# 类与方法索引：
#   SpreadsheetDataReader                (L30)   — XLS 格式连接组数据读取器
#     read_data                          (L44)   — 从 XLS 文件读取神经元连接数据
#     read_muscle_data                   (L114)  — 从 XLS 第 1 工作表读取神经肌肉连接数据
#
# 更新日志：
#   2026-04-17  yi  初始创建：从 SpreadsheetDataReader.py 重写
#
# 当前维护者：yi
# =============================================================================
"""CElegansNeuronTables.xls 电子表格连接组数据读取器。"""
import logging

from xlrd import open_workbook

from c302.readers import register_reader
from c302.readers.base import BaseDataReader, ConnectionInfo
from c302.utils.helpers import get_data_dir

logger = logging.getLogger(__name__)

# 数据文件目录
_DATA_DIR = get_data_dir() / "connectome"


class SpreadsheetDataReader(BaseDataReader):
    """XLS 格式连接组数据读取器。

    支持两种 XLS 数据源：

    - ``CElegansNeuronTables.xls``（默认）：含神经元+肌肉连接
    - ``NeuronConnectFormatted.xlsx``（``neuron_connect=True``）：仅神经元间连接
    """

    @staticmethod
    def read_data(
        include_nonconnected_cells: bool = False,
        neuron_connect: bool = False,
    ) -> tuple[list[str], list[ConnectionInfo]]:
        """从 XLS 文件读取神经元连接数据。

        :param include_nonconnected_cells: 是否包含已知无连接的神经元
        :param neuron_connect: True 使用 NeuronConnectFormatted.xlsx
        :return: ``(cells, conns)``
        """
        if neuron_connect:
            return SpreadsheetDataReader._read_neuron_connect()
        return SpreadsheetDataReader._read_ce_tables(include_nonconnected_cells)

    @staticmethod
    def _read_neuron_connect() -> tuple[list[str], list[ConnectionInfo]]:
        """从 NeuronConnectFormatted.xlsx 读取。

        :return: ``(cells, conns)``
        """
        conns: list[ConnectionInfo] = []
        cells: list[str] = []
        filename = str(_DATA_DIR / "NeuronConnectFormatted.xls")
        rb = open_workbook(filename)
        logger.info("Opened Excel file: %s", filename)

        # 列：0=pre 1=post 2=syntype 3=num
        for row in range(1, rb.sheet_by_index(0).nrows):
            pre = str(rb.sheet_by_index(0).cell(row, 0).value)
            post = str(rb.sheet_by_index(0).cell(row, 1).value)
            syntype = rb.sheet_by_index(0).cell(row, 2).value
            num = int(rb.sheet_by_index(0).cell(row, 3).value)
            # 包含 'EJ' 则为缝隙连接（电突触），否则为化学突触
            synclass = "Generic_GJ" if "EJ" in syntype else "Chemical_Synapse"

            conns.append(ConnectionInfo(pre, post, num, syntype, synclass))
            if pre not in cells:
                cells.append(pre)
            if post not in cells:
                cells.append(post)

        return cells, conns

    @staticmethod
    def _read_ce_tables(
        include_nonconnected_cells: bool,
    ) -> tuple[list[str], list[ConnectionInfo]]:
        """从 CElegansNeuronTables.xls 读取。

        :param include_nonconnected_cells: 是否包含已知无连接的神经元
        :return: ``(cells, conns)``
        """
        conns: list[ConnectionInfo] = []
        cells: list[str] = []
        filename = str(_DATA_DIR / "CElegansNeuronTables.xls")
        rb = open_workbook(filename)
        logger.info("Opened Excel file: %s", filename)

        # CANL/CANR/VC6 在数据文件中没有连接记录
        known_nonconnected_cells = ["CANL", "CANR", "VC6"]

        # 列：0=pre 1=post 2=syntype 3=num 4=synclass
        for row in range(1, rb.sheet_by_index(0).nrows):
            pre = str(rb.sheet_by_index(0).cell(row, 0).value)
            post = str(rb.sheet_by_index(0).cell(row, 1).value)
            syntype = rb.sheet_by_index(0).cell(row, 2).value
            num = int(rb.sheet_by_index(0).cell(row, 3).value)
            synclass = rb.sheet_by_index(0).cell(row, 4).value

            conns.append(ConnectionInfo(pre, post, num, syntype, synclass))
            if pre not in cells:
                cells.append(pre)
            if post not in cells:
                cells.append(post)

        if include_nonconnected_cells:
            for c in known_nonconnected_cells:
                cells.append(c)

        return cells, conns

    @staticmethod
    def read_muscle_data() -> tuple[list[str], list[str], list[ConnectionInfo]]:
        """从 CElegansNeuronTables.xls 第 1 工作表读取神经肌肉连接数据。

        :return: ``(neurons, muscles, conns)``
        """
        conns: list[ConnectionInfo] = []
        neurons: list[str] = []
        muscles: list[str] = []
        filename = str(_DATA_DIR / "CElegansNeuronTables.xls")
        rb = open_workbook(filename)
        logger.info("Opened Excel file: %s", filename)

        sheet = rb.sheet_by_index(1)

        for row in range(1, sheet.nrows):
            pre = str(sheet.cell(row, 0).value)
            post = str(sheet.cell(row, 1).value)
            syntype = "Send"  # 肌肉连接均为化学突触
            num = int(sheet.cell(row, 2).value)
            # 逗号→plus，空格→下划线
            synclass = sheet.cell(row, 3).value.replace(",", "plus").replace(" ", "_")

            conns.append(ConnectionInfo(pre, post, num, syntype, synclass))
            if pre not in neurons:
                neurons.append(pre)
            if post not in muscles:
                muscles.append(post)

        return neurons, muscles, conns


# 注册到读取器注册表
register_reader("SpreadsheetDataReader", SpreadsheetDataReader)
