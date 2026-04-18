# =============================================================================
# 功能描述：
#   heatmap 模块单元测试。测试 plot_heatmap 函数的绘图逻辑。
#
# 类与方法索引：
#   TestDownscale                        (L29)   — 下采样常量测试
#     test_downscale_is_ten              (L32)   — 下采样倍数应为 10
#   TestPlotHeatmap                      (L37)   — plot_heatmap 函数测试
#     test_creates_figure                (L41)   — 应创建子图
#     test_heightened_for_many_cells     (L56)   — 超过 24 个细胞应使用加高图形
#     test_uses_jet_colormap             (L76)   — 应使用 jet 色图
#     test_sets_title                    (L93)   — 应设置标题
#     test_downsamples_data              (L108)  — 应对数据进行 10 倍下采样
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段七：新建
#
# 当前维护者：Copilot
# =============================================================================
"""heatmap 模块测试。"""
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from c302.visualization.heatmap import _DOWNSCALE, plot_heatmap


class TestDownscale:
    """下采样常量测试。"""

    def test_downscale_is_ten(self) -> None:
        """下采样倍数应为 10。"""
        assert _DOWNSCALE == 10


class TestPlotHeatmap:
    """plot_heatmap 函数测试。"""

    @patch("c302.visualization.heatmap.plt")
    def test_creates_figure(self, mock_plt) -> None:
        """应创建子图。"""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_plt.colormaps = {"jet": MagicMock()}
        mock_ax.pcolormesh.return_value = MagicMock()
        mock_ax.get_xticklabels.return_value = []

        data = np.random.rand(5, 100)
        plot_heatmap(data, "Test", ["A", "B", "C", "D", "E"], 0.001)

        mock_plt.subplots.assert_called_once()

    @patch("c302.visualization.heatmap.plt")
    def test_heightened_for_many_cells(self, mock_plt) -> None:
        """超过 24 个细胞应使用加高图形。"""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_plt.colormaps = {"jet": MagicMock()}
        mock_ax.pcolormesh.return_value = MagicMock()
        mock_ax.get_xticklabels.return_value = []

        # 30 个细胞
        labels = [f"cell_{i}" for i in range(30)]
        data = np.random.rand(30, 100)
        plot_heatmap(data, "Test", labels, 0.001)

        # 应传递 figsize 和 gridspec_kw
        call_kwargs = mock_plt.subplots.call_args[1]
        assert "figsize" in call_kwargs
        assert "gridspec_kw" in call_kwargs

    @patch("c302.visualization.heatmap.plt")
    def test_uses_jet_colormap(self, mock_plt) -> None:
        """应使用 jet 色图。"""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_plt.colormaps = {"jet": "jet_cmap"}
        mock_ax.pcolormesh.return_value = MagicMock()
        mock_ax.get_xticklabels.return_value = []

        data = np.random.rand(3, 100)
        plot_heatmap(data, "Test", ["A", "B", "C"], 0.001)

        # pcolormesh 应使用 jet 色图
        call_kwargs = mock_ax.pcolormesh.call_args
        assert call_kwargs[1]["cmap"] == "jet_cmap"

    @patch("c302.visualization.heatmap.plt")
    def test_sets_title(self, mock_plt) -> None:
        """应设置标题。"""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_plt.colormaps = {"jet": MagicMock()}
        mock_ax.pcolormesh.return_value = MagicMock()
        mock_ax.get_xticklabels.return_value = []

        data = np.random.rand(2, 50)
        plot_heatmap(data, "My Title", ["X", "Y"], 0.001)

        mock_plt.title.assert_called_once_with("My Title")

    @patch("c302.visualization.heatmap.plt")
    def test_downsamples_data(self, mock_plt) -> None:
        """应对数据进行 10 倍下采样。"""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_plt.colormaps = {"jet": MagicMock()}
        mock_ax.pcolormesh.return_value = MagicMock()
        mock_ax.get_xticklabels.return_value = []

        data = np.random.rand(2, 100)
        plot_heatmap(data, "Test", ["A", "B"], 0.001)

        # pcolormesh 应接收下采样后的数据
        passed_data = mock_ax.pcolormesh.call_args[0][0]
        assert passed_data.shape == (2, 10)  # 100 / 10 = 10
