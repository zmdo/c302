# =============================================================================
# 功能描述：
#   CLI 模块的单元测试。测试参数解析、版本输出、配置列表等功能。
#
# 类与方法索引：
#   TestBuildParser                      (L45)   — 参数解析器构建测试
#     test_parser_has_config             (L48)   — 解析器应包含 --config 参数
#     test_parser_has_params             (L55)   — 解析器应包含 --params 参数
#     test_default_duration              (L61)   — 默认仿真时长应为 500ms
#     test_custom_duration               (L67)   — 应支持自定义仿真时长
#     test_default_dt                    (L73)   — 默认步长应为 0.05ms
#     test_default_simulator             (L79)   — 默认仿真后端应为 jNeuroML
#     test_neuron_simulator              (L85)   — 应支持选择 jNeuroML_NEURON 后端
#     test_invalid_simulator_rejected    (L93)   — 无效的仿真后端应被拒绝
#     test_default_output_dir            (L99)   — 默认输出目录应为 examples
#     test_save_flag                     (L105)  — --save 标志应正确解析
#     test_no_plot_flag                  (L111)  — --no-plot 标志应正确解析
#     test_verbose_flag                  (L117)  — -v 标志应正确解析
#     test_missing_config_exits          (L123)  — 缺少 --config 应导致退出
#     test_missing_params_exits          (L129)  — 缺少 --params 应导致退出
#     test_plot_connectivity_flag        (L135)  — --plot-connectivity 标志应正确解析
#     test_data_reader_option            (L143)  — --data-reader 应支持自定义值
#   TestProcessArgs                      (L152)  — process_args 参数处理测试
#     test_returns_namespace             (L155)  — 应返回解析后的命名空间
#     test_list_configs_exits            (L161)  — --list-configs 应打印配置列表并退出
#   TestMain                             (L168)  — main 入口函数测试
#     test_main_calls_run_c302           (L172)  — main 应调用 run_c302 并传递正确的参数
#     test_main_verbose_sets_debug       (L184)  — -v 应设置 verbose=True
#     test_main_passes_simulator         (L192)  — 应传递选择的仿真后端
#     test_main_passes_output_dir        (L200)  — 应传递输出目录
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段六：新建
#
# 当前维护者：Copilot
# =============================================================================
"""CLI 模块测试。"""
from unittest.mock import patch

import pytest

from c302.cli import build_parser, main, process_args


class TestBuildParser:
    """参数解析器构建测试。"""

    def test_parser_has_config(self) -> None:
        """解析器应包含 --config 参数。"""
        parser = build_parser()
        # 尝试解析最小参数集
        args = parser.parse_args(["-c", "IClamp", "-p", "A"])
        assert args.config == "IClamp"

    def test_parser_has_params(self) -> None:
        """解析器应包含 --params 参数。"""
        parser = build_parser()
        args = parser.parse_args(["-c", "IClamp", "-p", "A"])
        assert args.params == "A"

    def test_default_duration(self) -> None:
        """默认仿真时长应为 500ms。"""
        parser = build_parser()
        args = parser.parse_args(["-c", "IClamp", "-p", "A"])
        assert args.duration == 500.0

    def test_custom_duration(self) -> None:
        """应支持自定义仿真时长。"""
        parser = build_parser()
        args = parser.parse_args(["-c", "IClamp", "-p", "A", "-d", "1000"])
        assert args.duration == 1000.0

    def test_default_dt(self) -> None:
        """默认步长应为 0.05ms。"""
        parser = build_parser()
        args = parser.parse_args(["-c", "IClamp", "-p", "A"])
        assert args.dt == 0.05

    def test_default_simulator(self) -> None:
        """默认仿真后端应为 jNeuroML。"""
        parser = build_parser()
        args = parser.parse_args(["-c", "IClamp", "-p", "A"])
        assert args.simulator == "jNeuroML"

    def test_neuron_simulator(self) -> None:
        """应支持选择 jNeuroML_NEURON 后端。"""
        parser = build_parser()
        args = parser.parse_args(
            ["-c", "IClamp", "-p", "A", "-s", "jNeuroML_NEURON"]
        )
        assert args.simulator == "jNeuroML_NEURON"

    def test_invalid_simulator_rejected(self) -> None:
        """无效的仿真后端应被拒绝。"""
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-c", "IClamp", "-p", "A", "-s", "invalid"])

    def test_default_output_dir(self) -> None:
        """默认输出目录应为 examples。"""
        parser = build_parser()
        args = parser.parse_args(["-c", "IClamp", "-p", "A"])
        assert args.output_dir == "examples"

    def test_save_flag(self) -> None:
        """--save 标志应正确解析。"""
        parser = build_parser()
        args = parser.parse_args(["-c", "IClamp", "-p", "A", "--save"])
        assert args.save is True

    def test_no_plot_flag(self) -> None:
        """--no-plot 标志应正确解析。"""
        parser = build_parser()
        args = parser.parse_args(["-c", "IClamp", "-p", "A", "--no-plot"])
        assert args.no_plot is True

    def test_verbose_flag(self) -> None:
        """-v 标志应正确解析。"""
        parser = build_parser()
        args = parser.parse_args(["-c", "IClamp", "-p", "A", "-v"])
        assert args.verbose is True

    def test_missing_config_exits(self) -> None:
        """缺少 --config 应导致退出。"""
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-p", "A"])

    def test_missing_params_exits(self) -> None:
        """缺少 --params 应导致退出。"""
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-c", "IClamp"])

    def test_plot_connectivity_flag(self) -> None:
        """--plot-connectivity 标志应正确解析。"""
        parser = build_parser()
        args = parser.parse_args(
            ["-c", "IClamp", "-p", "A", "--plot-connectivity"]
        )
        assert args.plot_connectivity is True

    def test_data_reader_option(self) -> None:
        """--data-reader 应支持自定义值。"""
        parser = build_parser()
        args = parser.parse_args(
            ["-c", "FW", "-p", "C2", "--data-reader", "custom.reader"]
        )
        assert args.data_reader == "custom.reader"


class TestProcessArgs:
    """process_args 参数处理测试。"""

    def test_returns_namespace(self) -> None:
        """应返回解析后的命名空间。"""
        args = process_args(["-c", "IClamp", "-p", "A"])
        assert args.config == "IClamp"
        assert args.params == "A"

    def test_list_configs_exits(self) -> None:
        """--list-configs 应打印配置列表并退出。"""
        with pytest.raises(SystemExit) as exc_info:
            process_args(["-c", "IClamp", "-p", "A", "--list-configs"])
        assert exc_info.value.code == 0


class TestMain:
    """main 入口函数测试。"""

    @patch("c302.cli.run_c302")
    def test_main_calls_run_c302(self, mock_run) -> None:
        """main 应调用 run_c302 并传递正确的参数。"""
        main(["-c", "IClamp", "-p", "A", "-d", "100", "--no-plot"])

        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["config"] == "IClamp"
        assert call_kwargs["parameter_set"] == "A"
        assert call_kwargs["duration"] == 100.0
        assert call_kwargs["show_plot_already"] is False

    @patch("c302.cli.run_c302")
    def test_main_verbose_sets_debug(self, mock_run) -> None:
        """-v 应设置 verbose=True。"""
        main(["-c", "IClamp", "-p", "A", "-v", "--no-plot"])

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["verbose"] is True

    @patch("c302.cli.run_c302")
    def test_main_passes_simulator(self, mock_run) -> None:
        """应传递选择的仿真后端。"""
        main(["-c", "Full", "-p", "C", "-s", "jNeuroML_NEURON", "--no-plot"])

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["simulator"] == "jNeuroML_NEURON"

    @patch("c302.cli.run_c302")
    def test_main_passes_output_dir(self, mock_run) -> None:
        """应传递输出目录。"""
        main(["-c", "IClamp", "-p", "A", "-o", "/tmp/output", "--no-plot"])

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["target_directory"] == "/tmp/output"
