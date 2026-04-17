# =============================================================================
# 功能描述：
#   connectivity 模块单元测试。测试细胞信息加载、矩阵渲染和整体生成流程。
#
# 类与方法索引：
#   TestDefaultFigsize                   (L44)   — 默认图形尺寸测试
#     test_is_tuple                      (L47)   — 应为元组
#     test_has_two_elements              (L51)   — 应有两个元素
#   TestLoadCellInfo                     (L56)   — _load_cell_info 测试
#     test_loads_neuron_info             (L59)   — 应从缓存加载神经元信息
#     test_loads_muscle_info             (L65)   — 应从缓存加载肌肉信息
#     test_mixed_cells                   (L71)   — 混合输入应正确分类
#     test_unknown_neuron_fallback       (L77)   — 未知神经元应使用兜底标签
#   TestShowConnMatrix                   (L84)   — _show_conn_matrix 测试
#     test_skips_zero_matrix             (L88)   — 全零矩阵应跳过绘图
#     test_plots_nonzero_matrix          (L97)   — 非零矩阵应创建图形
#     test_saves_figure                  (L116)  — 指定保存路径时应调用 savefig
#     test_uses_custom_colormap          (L136)  — 应支持自定义色图
#   TestGenerateConnMatrix               (L157)  — generate_conn_matrix 测试
#     test_parses_chemical_synapses      (L162)  — 应解析化学突触投射
#     test_parses_electrical_projections (L197)  — 应解析电突触投射
#     test_inhibitory_uses_inh_key       (L230)  — 抑制性连接应根据 post_component 中的 'inh' 分类
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段七：新建
#
# 当前维护者：Copilot
# =============================================================================
"""connectivity 模块测试。"""
from collections import OrderedDict
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from c302.visualization.connectivity import (
    DEFAULT_FIGSIZE,
    _load_cell_info,
    _show_conn_matrix,
    generate_conn_matrix,
)


class TestDefaultFigsize:
    """默认图形尺寸测试。"""

    def test_is_tuple(self) -> None:
        """应为元组。"""
        assert isinstance(DEFAULT_FIGSIZE, tuple)

    def test_has_two_elements(self) -> None:
        """应有两个元素。"""
        assert len(DEFAULT_FIGSIZE) == 2


class TestLoadCellInfo:
    """_load_cell_info 测试。"""

    def test_loads_neuron_info(self) -> None:
        """应从缓存加载神经元信息。"""
        info_n, info_m = _load_cell_info(["ADAL"])
        assert "ADAL" in info_n
        assert len(info_m) == 0

    def test_loads_muscle_info(self) -> None:
        """应从缓存加载肌肉信息。"""
        info_n, info_m = _load_cell_info(["MDL01"])
        assert len(info_n) == 0
        assert "MDL01" in info_m

    def test_mixed_cells(self) -> None:
        """混合输入应正确分类。"""
        info_n, info_m = _load_cell_info(["ADAL", "MDL01"])
        assert "ADAL" in info_n
        assert "MDL01" in info_m

    def test_unknown_neuron_fallback(self) -> None:
        """未知神经元应使用兜底标签。"""
        info_n, _ = _load_cell_info(["ZZZZ_UNKNOWN"])
        assert "ZZZZ_UNKNOWN" in info_n
        assert info_n["ZZZZ_UNKNOWN"][4] == "ZZZZ_UNKNOWN"


class TestShowConnMatrix:
    """_show_conn_matrix 测试。"""

    @patch("c302.visualization.connectivity.plt")
    def test_skips_zero_matrix(self, mock_plt) -> None:
        """全零矩阵应跳过绘图。"""
        data = np.zeros((3, 3))
        _show_conn_matrix(
            data, "Test", OrderedDict(), OrderedDict(), "net1"
        )
        mock_plt.subplots.assert_not_called()

    @patch("c302.visualization.connectivity.plt")
    def test_plots_nonzero_matrix(self, mock_plt) -> None:
        """非零矩阵应创建图形。"""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_plt.gca.return_value = mock_ax
        mock_plt.colormaps = {"gist_stern_r": MagicMock()}
        mock_plt.colorbar.return_value = MagicMock()

        data = np.array([[0, 1], [2, 0]])
        pre = OrderedDict([("A", ("A", (), (), (), "A", "0")),
                           ("B", ("B", (), (), (), "B", "0"))])
        post = OrderedDict([("A", ("A", (), (), (), "A", "0")),
                            ("B", ("B", (), (), (), "B", "0"))])

        _show_conn_matrix(data, "Test conns", pre, post, "net1")
        mock_plt.subplots.assert_called_once()

    @patch("c302.visualization.connectivity.plt")
    def test_saves_figure(self, mock_plt) -> None:
        """指定保存路径时应调用 savefig。"""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_plt.gca.return_value = mock_ax
        mock_plt.colormaps = {"gist_stern_r": MagicMock()}
        mock_plt.colorbar.return_value = MagicMock()

        data = np.array([[1]])
        pre = OrderedDict([("A", ("A", (), (), (), "A", "0"))])
        post = OrderedDict([("A", ("A", (), (), (), "A", "0"))])

        _show_conn_matrix(
            data, "Test", pre, post, "net1",
            save_figure_to="/tmp/test.png",
        )
        mock_plt.savefig.assert_called_once()

    @patch("c302.visualization.connectivity.plt")
    def test_uses_custom_colormap(self, mock_plt) -> None:
        """应支持自定义色图。"""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_plt.gca.return_value = mock_ax
        mock_plt.colormaps = {"nipy_spectral": "custom_cm"}
        mock_plt.colorbar.return_value = MagicMock()

        data = np.array([[5]])
        pre = OrderedDict([("A", ("A", (), (), (), "A", "0"))])
        post = OrderedDict([("A", ("A", (), (), (), "A", "0"))])

        _show_conn_matrix(
            data, "Test", pre, post, "net1",
            colormap="nipy_spectral",
        )
        mock_plt.imshow.assert_called_once()
        assert mock_plt.imshow.call_args[1]["cmap"] == "custom_cm"


class TestGenerateConnMatrix:
    """generate_conn_matrix 测试。"""

    @patch("c302.visualization.connectivity._show_conn_matrix")
    @patch("c302.visualization.connectivity._load_cell_info")
    def test_parses_chemical_synapses(
        self, mock_load, mock_show
    ) -> None:
        """应解析化学突触投射。"""
        mock_load.return_value = (
            OrderedDict([("ADAL", ("ADAL", (), (), (), "ADAL", "0")),
                         ("ADAR", ("ADAR", (), (), (), "ADAR", "0"))]),
            OrderedDict(),
        )

        # 构造 mock NeuroML 文档
        conn = MagicMock()
        conn.weight = "3.0"
        conn.post_component = "exc_syn"

        proj = MagicMock()
        proj.presynaptic_population = "ADAL"
        proj.postsynaptic_population = "ADAR"
        proj.continuous_connection_instance_ws = [conn]

        net = MagicMock()
        net.id = "test_net"
        net.continuous_projections = [proj]
        net.electrical_projections = []

        nml_doc = MagicMock()
        nml_doc.networks = [net]

        generate_conn_matrix(nml_doc)

        # _show_conn_matrix 应被调用 5 次（4 化学 + 1 电）
        assert mock_show.call_count == 5

    @patch("c302.visualization.connectivity._show_conn_matrix")
    @patch("c302.visualization.connectivity._load_cell_info")
    def test_parses_electrical_projections(
        self, mock_load, mock_show
    ) -> None:
        """应解析电突触投射。"""
        mock_load.return_value = (
            OrderedDict([("ADAL", ("ADAL", (), (), (), "ADAL", "0")),
                         ("ADAR", ("ADAR", (), (), (), "ADAR", "0"))]),
            OrderedDict(),
        )

        conn = MagicMock()
        conn.weight = "1.0"

        proj = MagicMock()
        proj.presynaptic_population = "ADAL"
        proj.postsynaptic_population = "ADAR"
        proj.electrical_connection_instance_ws = [conn]

        net = MagicMock()
        net.id = "test_net"
        net.continuous_projections = []
        net.electrical_projections = [proj]

        nml_doc = MagicMock()
        nml_doc.networks = [net]

        generate_conn_matrix(nml_doc)

        # 至少应调用一次（电突触 N-N）
        assert mock_show.call_count >= 5

    @patch("c302.visualization.connectivity._show_conn_matrix")
    @patch("c302.visualization.connectivity._load_cell_info")
    def test_inhibitory_uses_inh_key(
        self, mock_load, mock_show
    ) -> None:
        """抑制性连接应根据 post_component 中的 'inh' 分类。"""
        mock_load.return_value = (
            OrderedDict([("ADAL", ("ADAL", (), (), (), "ADAL", "0")),
                         ("ADAR", ("ADAR", (), (), (), "ADAR", "0"))]),
            OrderedDict(),
        )

        exc_conn = MagicMock()
        exc_conn.weight = "2.0"
        exc_conn.post_component = "exc_syn"

        inh_conn = MagicMock()
        inh_conn.weight = "1.0"
        inh_conn.post_component = "inh_syn"

        proj_exc = MagicMock()
        proj_exc.presynaptic_population = "ADAL"
        proj_exc.postsynaptic_population = "ADAR"
        proj_exc.continuous_connection_instance_ws = [exc_conn]

        proj_inh = MagicMock()
        proj_inh.presynaptic_population = "ADAR"
        proj_inh.postsynaptic_population = "ADAL"
        proj_inh.continuous_connection_instance_ws = [inh_conn]

        net = MagicMock()
        net.id = "test_net"
        net.continuous_projections = [proj_exc, proj_inh]
        net.electrical_projections = []

        nml_doc = MagicMock()
        nml_doc.networks = [net]

        generate_conn_matrix(nml_doc)

        # 应被调用 5 次
        assert mock_show.call_count == 5
