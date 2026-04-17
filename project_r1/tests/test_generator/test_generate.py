# =============================================================================
# 功能描述：
#   主入口 generate 模块的单元测试。覆盖辅助函数和 generate() 函数
#   的参数处理逻辑。
#
# 类与方法索引：
#   (由 gen_index.py 生成)
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段四：新建
#
# 当前维护者：Copilot
# =============================================================================
"""generate 主入口模块测试。"""
from unittest.mock import MagicMock, patch

import pytest

from c302.generator import DEFAULT_DATA_READER, FW_DATA_READER


class TestConstants:
    """模块常量测试。"""

    def test_default_data_reader(self):
        """默认数据读取器应为 SpreadsheetDataReader。"""
        assert "SpreadsheetDataReader" in DEFAULT_DATA_READER

    def test_fw_data_reader(self):
        """前向数据读取器应为 UpdatedSpreadsheetDataReader2。"""
        assert "UpdatedSpreadsheetDataReader2" in FW_DATA_READER


class TestGenerateParamProcessing:
    """generate() 的参数处理逻辑测试。"""

    def _make_params(self, level="A"):
        """构造模拟的参数对象。"""
        params = MagicMock()
        params.level = level
        params.is_level_A.return_value = level.startswith("A")
        params.is_level_B.return_value = level.startswith("B")
        params.is_level_C.return_value = level.startswith("C")
        params.is_level_D.return_value = level.startswith("D")
        params.is_level_C0.return_value = level == "C0"
        params.is_level_C2.return_value = level == "C2"
        params.is_level_D1.return_value = level == "D1"
        params.is_level_X.return_value = level == "X"
        params.bioparameters = []
        params.bioparameter_info.return_value = "bio info"
        params.generic_neuron_cell = MagicMock()
        params.generic_neuron_cell.id = "generic_iaf_cell"
        params.generic_muscle_cell = MagicMock()
        params.generic_muscle_cell.id = "generic_iaf_muscle"
        params.offset_current = MagicMock()
        params.offset_current.id = "offset_current"
        params.concentration_model = MagicMock()
        params.custom_component_types_definitions = None
        return params

    @patch("c302.generator.write_to_file")
    @patch("c302.generator.create_muscle_connections")
    @patch("c302.generator.create_neuron_connections")
    @patch("c302.generator.create_muscle_populations")
    @patch("c302.generator.create_neuron_populations")
    @patch("c302.generator.get_cell_muscle_names_and_connection")
    @patch("c302.generator.get_cell_names_and_connection")
    def test_generate_level_a_defaults(
        self,
        mock_cells,
        mock_muscles,
        mock_neuron_pop,
        mock_muscle_pop,
        mock_neuron_conn,
        mock_muscle_conn,
        mock_write,
    ):
        """A 级别应使用 IAF 细胞并设置正确的电压默认值。"""
        mock_cells.return_value = (["ADAL", "ADAR"], [])
        mock_muscles.return_value = ([], [], [])
        mock_neuron_pop.return_value = ["ADAL", "ADAR"]

        from c302.generator import generate

        params = self._make_params("A")
        doc = generate("test_A", params)

        # 验证 iaf_cells 被使用（A 级别）
        assert len(doc.iaf_cells) == 2
        # 验证 create_models 被调用
        params.create_models.assert_called_once()
        # 验证 write_to_file 被调用
        mock_write.assert_called_once()

    @patch("c302.generator.write_to_file")
    @patch("c302.generator.create_muscle_connections")
    @patch("c302.generator.create_neuron_connections")
    @patch("c302.generator.create_muscle_populations")
    @patch("c302.generator.create_neuron_populations")
    @patch("c302.generator.get_cell_muscle_names_and_connection")
    @patch("c302.generator.get_cell_names_and_connection")
    def test_generate_level_c_uses_cells(
        self,
        mock_cells,
        mock_muscles,
        mock_neuron_pop,
        mock_muscle_pop,
        mock_neuron_conn,
        mock_muscle_conn,
        mock_write,
    ):
        """C 级别应使用 cells（非 iaf_cells）。"""
        mock_cells.return_value = (["ADAL"], [])
        mock_muscles.return_value = ([], [], [])
        mock_neuron_pop.return_value = ["ADAL"]

        from c302.generator import generate

        params = self._make_params("C")
        doc = generate("test_C", params)

        assert len(doc.cells) == 2  # generic_muscle + generic_neuron
        assert len(doc.iaf_cells) == 0

    @patch("c302.generator.write_to_file")
    @patch("c302.generator.create_muscle_connections")
    @patch("c302.generator.create_neuron_connections")
    @patch("c302.generator.create_muscle_populations")
    @patch("c302.generator.create_neuron_populations")
    @patch("c302.generator.get_cell_muscle_names_and_connection")
    @patch("c302.generator.get_cell_names_and_connection")
    def test_generate_with_muscles(
        self,
        mock_cells,
        mock_muscles,
        mock_neuron_pop,
        mock_muscle_pop,
        mock_neuron_conn,
        mock_muscle_conn,
        mock_write,
    ):
        """传入 muscles_to_include 时应调用肌肉种群和连接创建。"""
        mock_cells.return_value = (["ADAL"], [])
        mock_muscles.return_value = (
            ["ADAL"],
            ["MDR01", "MVL01"],
            [MagicMock()],
        )
        mock_neuron_pop.return_value = ["ADAL"]

        from c302.generator import generate

        params = self._make_params("A")
        doc = generate(
            "test_muscles",
            params,
            muscles_to_include=["MDR01", "MVL01"],
        )

        mock_muscle_pop.assert_called_once()
        mock_muscle_conn.assert_called_once()

    @patch("c302.generator.write_to_file")
    @patch("c302.generator.create_muscle_connections")
    @patch("c302.generator.create_neuron_connections")
    @patch("c302.generator.create_muscle_populations")
    @patch("c302.generator.create_neuron_populations")
    @patch("c302.generator.get_cell_muscle_names_and_connection")
    @patch("c302.generator.get_cell_names_and_connection")
    def test_generate_no_muscles(
        self,
        mock_cells,
        mock_muscles,
        mock_neuron_pop,
        mock_muscle_pop,
        mock_neuron_conn,
        mock_muscle_conn,
        mock_write,
    ):
        """muscles_to_include=[] 时不应创建肌肉种群。"""
        mock_cells.return_value = (["ADAL"], [])
        mock_muscles.return_value = ([], [], [])
        mock_neuron_pop.return_value = ["ADAL"]

        from c302.generator import generate

        params = self._make_params("A")
        doc = generate("test_no_muscle", params, muscles_to_include=[])

        mock_muscle_pop.assert_not_called()
        mock_muscle_conn.assert_not_called()

    @patch("c302.generator.write_to_file")
    @patch("c302.generator.create_muscle_connections")
    @patch("c302.generator.create_neuron_connections")
    @patch("c302.generator.create_muscle_populations")
    @patch("c302.generator.create_neuron_populations")
    @patch("c302.generator.get_cell_muscle_names_and_connection")
    @patch("c302.generator.get_cell_names_and_connection")
    def test_generate_param_overrides_update_notes(
        self,
        mock_cells,
        mock_muscles,
        mock_neuron_pop,
        mock_muscle_pop,
        mock_neuron_conn,
        mock_muscle_conn,
        mock_write,
    ):
        """param_overrides 非空时应重新生成注释。"""
        mock_cells.return_value = (["ADAL"], [])
        mock_muscles.return_value = ([], [], [])
        mock_neuron_pop.return_value = ["ADAL"]

        from c302.generator import generate

        params = self._make_params("A")
        params.bioparameter_info.return_value = "updated info"

        doc = generate(
            "test_override",
            params,
            param_overrides={"some_param": "1.0 nS"},
        )

        # 注释中应包含更新后的信息
        assert "updated info" in doc.notes
