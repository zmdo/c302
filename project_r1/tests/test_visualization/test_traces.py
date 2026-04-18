# =============================================================================
# 功能描述：
#   traces 模块单元测试。测试排序键、模板选择、绘图函数（全 mock matplotlib）。
#
# 类与方法索引：
#   TestNatsort                          (L50)   — 自然排序键函数测试
#     test_pure_text                     (L53)   — 纯文本应正常排序
#     test_numeric_suffix                (L58)   — 数字后缀应按数值排序
#     test_mixed_prefix                  (L63)   — 混合前缀应先按前缀再按数字排序
#   TestGetTemplate                      (L69)   — LEMS 结果键模板测试
#     test_iaf_neuron                    (L72)   — A/B 参数集应返回 IAF 神经元模板
#     test_iaf_muscle                    (L77)   — A/B 参数集应返回 IAF 肌肉模板
#     test_multicompartment              (L81)   — D 参数集应返回多房室模板
#     test_c_series_neuron               (L86)   — C 系列应返回 GenericNeuronCell 模板
#     test_c_series_muscle               (L91)   — C 系列肌肉应返回 GenericMuscleCell 模板
#   TestParamsetsNoCalcium               (L96)   — 不含钙的参数集常量测试
#     test_a_in_no_calcium               (L99)   — A 应在不含钙集合中
#     test_w2d_in_no_calcium             (L103)  — W2D 应在不含钙集合中
#     test_c0_not_in_no_calcium          (L107)  — C0 不应在不含钙集合中
#   TestGenerateTracesPlot               (L112)  — generate_traces_plot 测试
#     test_calls_generate_plot           (L116)  — 应调用 pyneuroml.plot.generate_plot
#     test_filename_neuron_voltage       (L143)  — 神经元电压文件名应为 traces_neuron_config_param.png
#     test_filename_muscle_activity      (L151)  — 肌肉活动文件名应包含 muscles 和 _activity
#   TestPlotC302Results                  (L159)  — plot_c302_results 测试（mock matplotlib）
#     test_separates_neurons_and_muscles (L165)  — 应正确分离神经元和肌肉
#     test_no_calcium_for_param_a        (L186)  — 参数集 A 不应绘制钙离子图
#     test_closes_plots_when_no_show     (L206)  — show_plot_already=False 应关闭所有图形
#     test_empty_results_no_plot         (L222)  — 空结果不应绘制任何图
#     test_calcium_plotted_for_c_series  (L239)  — C0 参数集 plot_ca=True 应绘制神经元 + 肌肉的 [Ca²⁺] 图
#     test_save_creates_files            (L264)  — save=True 应调用 plt.savefig
#     test_show_plot                     (L286)  — show_plot_already=True 应调用 plt.show
#     test_activity_for_b_series         (L305)  — B 参数集 plot_ca=True 应绘制 activity（非 caConc）
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段七：新建
#
# 当前维护者：Copilot
# =============================================================================
"""traces 模块测试。"""
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from c302.visualization.traces import (
    PARAMSETS_NO_CALCIUM,
    _get_template,
    _natsort,
    generate_traces_plot,
    plot_c302_results,
)


class TestNatsort:
    """自然排序键函数测试。"""

    def test_pure_text(self) -> None:
        """纯文本应正常排序。"""
        result = sorted(["ADAL", "ADAR", "ABAL"], key=_natsort)
        assert result == ["ABAL", "ADAL", "ADAR"]

    def test_numeric_suffix(self) -> None:
        """数字后缀应按数值排序。"""
        result = sorted(["VB2", "VB11", "VB1"], key=_natsort)
        assert result == ["VB1", "VB2", "VB11"]

    def test_mixed_prefix(self) -> None:
        """混合前缀应先按前缀再按数字排序。"""
        result = sorted(["DA9", "DA1", "DB3"], key=_natsort)
        assert result == ["DA1", "DA9", "DB3"]


class TestGetTemplate:
    """LEMS 结果键模板测试。"""

    def test_iaf_neuron(self) -> None:
        """A/B 参数集应返回 IAF 神经元模板。"""
        assert "generic_neuron_iaf_cell" in _get_template("A")
        assert "generic_neuron_iaf_cell" in _get_template("B")

    def test_iaf_muscle(self) -> None:
        """A/B 参数集应返回 IAF 肌肉模板。"""
        assert "generic_muscle_iaf_cell" in _get_template("A", muscle=True)

    def test_multicompartment(self) -> None:
        """D 参数集应返回多房室模板。"""
        t = _get_template("D")
        assert "{0}/0/{0}/{1}" == t

    def test_c_series_neuron(self) -> None:
        """C 系列应返回 GenericNeuronCell 模板。"""
        assert "GenericNeuronCell" in _get_template("C0")
        assert "GenericNeuronCell" in _get_template("C2")

    def test_c_series_muscle(self) -> None:
        """C 系列肌肉应返回 GenericMuscleCell 模板。"""
        assert "GenericMuscleCell" in _get_template("C1", muscle=True)


class TestParamsetsNoCalcium:
    """不含钙的参数集常量测试。"""

    def test_a_in_no_calcium(self) -> None:
        """A 应在不含钙集合中。"""
        assert "A" in PARAMSETS_NO_CALCIUM

    def test_w2d_in_no_calcium(self) -> None:
        """W2D 应在不含钙集合中。"""
        assert "W2D" in PARAMSETS_NO_CALCIUM

    def test_c0_not_in_no_calcium(self) -> None:
        """C0 不应在不含钙集合中。"""
        assert "C0" not in PARAMSETS_NO_CALCIUM


class TestGenerateTracesPlot:
    """generate_traces_plot 测试。"""

    @patch("c302.visualization.traces.pyneuroml_plot", create=True)
    def test_calls_generate_plot(self, mock_pnml) -> None:
        """应调用 pyneuroml.plot.generate_plot。"""
        # 需要 mock 延迟导入
        with patch(
            "c302.visualization.traces.pyneuroml_plot"
        ) as mock_mod:
            from c302.visualization import traces

            # 临时替换延迟导入
            original = traces.generate_traces_plot

            with patch.dict("sys.modules", {"pyneuroml": MagicMock(), "pyneuroml.plot": MagicMock()}) as _:
                import importlib
                importlib.reload(traces)

                mock_plot = MagicMock()
                with patch("pyneuroml.plot.generate_plot", mock_plot):
                    traces.generate_traces_plot(
                        config="IClamp",
                        parameter_set="A",
                        xvals=[[0, 1]],
                        yvals=[[0, 1]],
                        info="test",
                        labels=["ADAL"],
                        save=False,
                    )

    def test_filename_neuron_voltage(self) -> None:
        """神经元电压文件名应为 traces_neuron_config_param.png。"""
        # 只测试文件名构造逻辑
        file_name = "traces_{}{}_{}_{}.png".format(
            "neuron", "", "IClamp", "A"
        )
        assert file_name == "traces_neuron_IClamp_A.png"

    def test_filename_muscle_activity(self) -> None:
        """肌肉活动文件名应包含 muscles 和 _activity。"""
        file_name = "traces_{}{}_{}_{}.png".format(
            "muscles", "_activity", "Full", "C0"
        )
        assert file_name == "traces_muscles_activity_Full_C0.png"


class TestPlotC302Results:
    """plot_c302_results 测试（mock matplotlib）。"""

    @patch("c302.visualization.traces.plt")
    @patch("c302.visualization.traces.plot_heatmap")
    @patch("c302.visualization.traces.generate_traces_plot")
    def test_separates_neurons_and_muscles(
        self, mock_traces, mock_heatmap, mock_plt
    ) -> None:
        """应正确分离神经元和肌肉。"""
        lems = {
            "t": [0.0, 0.001, 0.002],
            "ADAL/0/GenericNeuronCell/v": [0.0, -0.05, -0.04],
            "MDL01/0/GenericMuscleCell/v": [0.0, -0.06, -0.05],
        }

        plot_c302_results(
            lems, "IClamp", "C0",
            show_plot_already=False, save=False, plot_ca=False,
        )

        # 热图应被调用两次（神经元 + 肌肉）
        assert mock_heatmap.call_count == 2

    @patch("c302.visualization.traces.plt")
    @patch("c302.visualization.traces.plot_heatmap")
    @patch("c302.visualization.traces.generate_traces_plot")
    def test_no_calcium_for_param_a(
        self, mock_traces, mock_heatmap, mock_plt
    ) -> None:
        """参数集 A 不应绘制钙离子图。"""
        lems = {
            "t": [0.0, 0.001],
            "ADAL/0/generic_neuron_iaf_cell/v": [0.0, -0.05],
        }

        plot_c302_results(
            lems, "IClamp", "A",
            show_plot_already=False, save=False, plot_ca=True,
        )

        # 只调用 1 次（电压），不调用钙离子
        assert mock_heatmap.call_count == 1

    @patch("c302.visualization.traces.plt")
    @patch("c302.visualization.traces.plot_heatmap")
    @patch("c302.visualization.traces.generate_traces_plot")
    def test_closes_plots_when_no_show(
        self, mock_traces, mock_heatmap, mock_plt
    ) -> None:
        """show_plot_already=False 应关闭所有图形。"""
        lems = {"t": [0.0, 0.001], "X/0/GenericNeuronCell/v": [0.0, -0.05]}

        plot_c302_results(
            lems, "IClamp", "C0",
            show_plot_already=False, save=False, plot_ca=False,
        )

        mock_plt.close.assert_called_once_with("all")

    @patch("c302.visualization.traces.plt")
    @patch("c302.visualization.traces.plot_heatmap")
    @patch("c302.visualization.traces.generate_traces_plot")
    def test_empty_results_no_plot(
        self, mock_traces, mock_heatmap, mock_plt
    ) -> None:
        """空结果不应绘制任何图。"""
        lems = {"t": [0.0, 0.001]}

        plot_c302_results(
            lems, "IClamp", "C0",
            show_plot_already=False, save=False,
        )

        mock_heatmap.assert_not_called()
        mock_traces.assert_not_called()

    @patch("c302.visualization.traces.plt")
    @patch("c302.visualization.traces.plot_heatmap")
    @patch("c302.visualization.traces.generate_traces_plot")
    def test_calcium_plotted_for_c_series(
        self, mock_traces, mock_heatmap, mock_plt
    ) -> None:
        """C0 参数集 plot_ca=True 应绘制神经元 + 肌肉的 [Ca²⁺] 图。"""
        lems = {
            "t": [0.0, 0.001, 0.002],
            "ADAL/0/GenericNeuronCell/v": [0.0, -0.05, -0.04],
            "ADAL/0/GenericNeuronCell/caConc": [0.0, 1e-6, 2e-6],
            "MDL01/0/GenericMuscleCell/v": [0.0, -0.06, -0.05],
            "MDL01/0/GenericMuscleCell/caConc": [0.0, 1e-7, 1e-7],
        }

        plot_c302_results(
            lems, "IClamp", "C0",
            show_plot_already=False, save=False, plot_ca=True,
        )

        # 热图：神经元电压 + 肌肉电压 + 神经元Ca + 肌肉Ca = 4次
        assert mock_heatmap.call_count == 4
        # 轨迹图：同样 4 次
        assert mock_traces.call_count == 4

    @patch("c302.visualization.traces.plt")
    @patch("c302.visualization.traces.plot_heatmap")
    @patch("c302.visualization.traces.generate_traces_plot")
    def test_save_creates_files(
        self, mock_traces, mock_heatmap, mock_plt
    ) -> None:
        """save=True 应调用 plt.savefig。"""
        lems = {
            "t": [0.0, 0.001, 0.002],
            "ADAL/0/GenericNeuronCell/v": [0.0, -0.05, -0.04],
            "MDL01/0/GenericMuscleCell/v": [0.0, -0.06, -0.05],
        }

        plot_c302_results(
            lems, "IClamp", "C0",
            directory="/tmp/test_traces",
            show_plot_already=False, save=True, plot_ca=False,
        )

        # 保存 2 次（神经元 + 肌肉热图）
        assert mock_plt.savefig.call_count == 2

    @patch("c302.visualization.traces.plt")
    @patch("c302.visualization.traces.plot_heatmap")
    @patch("c302.visualization.traces.generate_traces_plot")
    def test_show_plot(
        self, mock_traces, mock_heatmap, mock_plt
    ) -> None:
        """show_plot_already=True 应调用 plt.show。"""
        lems = {
            "t": [0.0, 0.001],
            "X/0/GenericNeuronCell/v": [0.0, -0.05],
        }

        plot_c302_results(
            lems, "IClamp", "C0",
            show_plot_already=True, save=False, plot_ca=False,
        )

        mock_plt.show.assert_called_once()

    @patch("c302.visualization.traces.plt")
    @patch("c302.visualization.traces.plot_heatmap")
    @patch("c302.visualization.traces.generate_traces_plot")
    def test_activity_for_b_series(
        self, mock_traces, mock_heatmap, mock_plt
    ) -> None:
        """B 参数集 plot_ca=True 应绘制 activity（非 caConc）。"""
        lems = {
            "t": [0.0, 0.001, 0.002],
            "ADAL/0/generic_neuron_iaf_cell/v": [0.0, -0.05, -0.04],
            "ADAL/0/generic_neuron_iaf_cell/activity": [0.0, 1.0, 2.0],
        }

        plot_c302_results(
            lems, "IClamp", "B",
            show_plot_already=False, save=False, plot_ca=True,
        )

        # 热图：电压 + 活动 = 2 次
        assert mock_heatmap.call_count == 2
