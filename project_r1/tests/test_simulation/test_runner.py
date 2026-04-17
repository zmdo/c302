# =============================================================================
# 功能描述：
#   仿真编排 runner 模块的单元测试。测试 run_c302() 的参数校验、
#   配置加载、仿真调用和绘图流程（全部 mock，不执行真实仿真）。
#
# 类与方法索引：
#   TestSimulators                       (L35)   — 仿真后端常量测试
#     test_supported_simulators          (L38)   — 应包含两种仿真后端
#     test_simulators_is_tuple           (L43)   — 应为不可变元组
#   TestRunC302Validation                (L48)   — run_c302 参数校验测试
#     test_invalid_simulator_raises      (L51)   — 传入不支持的仿真后端应抛出 ValueError
#   TestRunC302Workflow                  (L63)   — run_c302 工作流程测试（全 mock）
#     test_calls_setup_with_generate_flag (L68)   — 应以 generate_flag=True 调用配置 setup 函数
#     test_calls_jneuroml_simulator      (L94)   — simulator='jNeuroML' 应调用 run_lems_with_jneuroml
#     test_calls_neuron_simulator        (L117)  — simulator='jNeuroML_NEURON' 应调用 run_lems_with_jneuroml_neuron
#     test_returns_four_tuple            (L140)  — 应返回 (cells, cells_to_stimulate, params, muscles) 四元组
#     test_restores_cwd_on_success       (L168)  — 仿真成功后应恢复原始工作目录
#     test_restores_cwd_on_failure       (L195)  — 仿真失败后也应恢复原始工作目录
#     test_passes_param_overrides        (L224)  — param_overrides 应传递给 setup 函数
#     test_creates_target_directory      (L249)  — 应自动创建输出目录
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段六：新建
#
# 当前维护者：Copilot
# =============================================================================
"""仿真编排 runner 模块测试。"""
from unittest.mock import MagicMock, patch

import pytest

from c302.simulation.runner import SIMULATORS, run_c302


class TestSimulators:
    """仿真后端常量测试。"""

    def test_supported_simulators(self) -> None:
        """应包含两种仿真后端。"""
        assert "jNeuroML" in SIMULATORS
        assert "jNeuroML_NEURON" in SIMULATORS

    def test_simulators_is_tuple(self) -> None:
        """应为不可变元组。"""
        assert isinstance(SIMULATORS, tuple)


class TestRunC302Validation:
    """run_c302 参数校验测试。"""

    def test_invalid_simulator_raises(self) -> None:
        """传入不支持的仿真后端应抛出 ValueError。"""
        with pytest.raises(ValueError, match="不支持的仿真后端"):
            run_c302(
                config="IClamp",
                parameter_set="A",
                duration=100,
                dt=0.05,
                simulator="invalid_backend",
            )


class TestRunC302Workflow:
    """run_c302 工作流程测试（全 mock）。"""

    @patch("c302.simulation.runner.pynml")
    @patch("c302.simulation.runner.get_config")
    def test_calls_setup_with_generate_flag(
        self, mock_get_config, mock_pynml
    ) -> None:
        """应以 generate_flag=True 调用配置 setup 函数。"""
        # 构造 mock setup 函数
        mock_setup = MagicMock(
            return_value=(["ADAL"], ["ADAL"], MagicMock(), [], None)
        )
        mock_get_config.return_value = mock_setup
        mock_pynml.run_lems_with_jneuroml.return_value = {}

        run_c302(
            config="IClamp",
            parameter_set="A",
            duration=100,
            dt=0.05,
            show_plot_already=False,
        )

        # 验证 setup 被调用，且 generate_flag=True
        mock_setup.assert_called_once()
        call_kwargs = mock_setup.call_args
        assert call_kwargs[1]["generate_flag"] is True

    @patch("c302.simulation.runner.pynml")
    @patch("c302.simulation.runner.get_config")
    def test_calls_jneuroml_simulator(
        self, mock_get_config, mock_pynml
    ) -> None:
        """simulator='jNeuroML' 应调用 run_lems_with_jneuroml。"""
        mock_setup = MagicMock(
            return_value=([], [], MagicMock(), [], None)
        )
        mock_get_config.return_value = mock_setup
        mock_pynml.run_lems_with_jneuroml.return_value = {}

        run_c302(
            config="IClamp",
            parameter_set="A",
            duration=100,
            dt=0.05,
            simulator="jNeuroML",
            show_plot_already=False,
        )

        mock_pynml.run_lems_with_jneuroml.assert_called_once()

    @patch("c302.simulation.runner.pynml")
    @patch("c302.simulation.runner.get_config")
    def test_calls_neuron_simulator(
        self, mock_get_config, mock_pynml
    ) -> None:
        """simulator='jNeuroML_NEURON' 应调用 run_lems_with_jneuroml_neuron。"""
        mock_setup = MagicMock(
            return_value=([], [], MagicMock(), [], None)
        )
        mock_get_config.return_value = mock_setup
        mock_pynml.run_lems_with_jneuroml_neuron.return_value = {}

        run_c302(
            config="IClamp",
            parameter_set="A",
            duration=100,
            dt=0.05,
            simulator="jNeuroML_NEURON",
            show_plot_already=False,
        )

        mock_pynml.run_lems_with_jneuroml_neuron.assert_called_once()

    @patch("c302.simulation.runner.pynml")
    @patch("c302.simulation.runner.get_config")
    def test_returns_four_tuple(
        self, mock_get_config, mock_pynml
    ) -> None:
        """应返回 (cells, cells_to_stimulate, params, muscles) 四元组。"""
        mock_params = MagicMock()
        mock_setup = MagicMock(
            return_value=(["ADAL"], ["ADAL"], mock_params, True, None)
        )
        mock_get_config.return_value = mock_setup
        mock_pynml.run_lems_with_jneuroml.return_value = {}

        result = run_c302(
            config="IClamp",
            parameter_set="A",
            duration=100,
            dt=0.05,
            show_plot_already=False,
        )

        # 应返回四元组
        assert len(result) == 4
        assert result[0] == ["ADAL"]
        assert result[1] == ["ADAL"]
        assert result[2] is mock_params
        assert result[3] is True

    @patch("c302.simulation.runner.pynml")
    @patch("c302.simulation.runner.get_config")
    def test_restores_cwd_on_success(
        self, mock_get_config, mock_pynml, tmp_path
    ) -> None:
        """仿真成功后应恢复原始工作目录。"""
        import os

        orig_cwd = os.getcwd()
        mock_setup = MagicMock(
            return_value=([], [], MagicMock(), [], None)
        )
        mock_get_config.return_value = mock_setup
        mock_pynml.run_lems_with_jneuroml.return_value = {}

        run_c302(
            config="IClamp",
            parameter_set="A",
            duration=100,
            dt=0.05,
            target_directory=str(tmp_path),
            show_plot_already=False,
        )

        # 工作目录应已恢复
        assert os.getcwd() == orig_cwd

    @patch("c302.simulation.runner.pynml")
    @patch("c302.simulation.runner.get_config")
    def test_restores_cwd_on_failure(
        self, mock_get_config, mock_pynml, tmp_path
    ) -> None:
        """仿真失败后也应恢复原始工作目录。"""
        import os

        orig_cwd = os.getcwd()
        mock_setup = MagicMock(
            return_value=([], [], MagicMock(), [], None)
        )
        mock_get_config.return_value = mock_setup
        # 仿真抛出异常
        mock_pynml.run_lems_with_jneuroml.side_effect = RuntimeError("sim failed")

        with pytest.raises(RuntimeError):
            run_c302(
                config="IClamp",
                parameter_set="A",
                duration=100,
                dt=0.05,
                target_directory=str(tmp_path),
                show_plot_already=False,
            )

        # 工作目录应仍被恢复
        assert os.getcwd() == orig_cwd

    @patch("c302.simulation.runner.pynml")
    @patch("c302.simulation.runner.get_config")
    def test_passes_param_overrides(
        self, mock_get_config, mock_pynml
    ) -> None:
        """param_overrides 应传递给 setup 函数。"""
        mock_setup = MagicMock(
            return_value=([], [], MagicMock(), [], None)
        )
        mock_get_config.return_value = mock_setup
        mock_pynml.run_lems_with_jneuroml.return_value = {}

        overrides = {"cell_diameter": "10"}
        run_c302(
            config="IClamp",
            parameter_set="A",
            duration=100,
            dt=0.05,
            param_overrides=overrides,
            show_plot_already=False,
        )

        call_kwargs = mock_setup.call_args[1]
        assert call_kwargs["param_overrides"] == overrides

    @patch("c302.simulation.runner.pynml")
    @patch("c302.simulation.runner.get_config")
    def test_creates_target_directory(
        self, mock_get_config, mock_pynml, tmp_path
    ) -> None:
        """应自动创建输出目录。"""
        target = str(tmp_path / "output" / "nested")
        mock_setup = MagicMock(
            return_value=([], [], MagicMock(), [], None)
        )
        mock_get_config.return_value = mock_setup
        mock_pynml.run_lems_with_jneuroml.return_value = {}

        run_c302(
            config="IClamp",
            parameter_set="A",
            duration=100,
            dt=0.05,
            target_directory=target,
            show_plot_already=False,
        )

        assert (tmp_path / "output" / "nested").is_dir()
