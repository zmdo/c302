# =============================================================================
# 功能描述：
#   graph 模块单元测试。测试 DOT 文件生成和 XML 解析。
#
# 类与方法索引：
#   nml_root                             (L80)   — 返回解析后的最小 NeuroML XML 根节点
#   TestIsMuscleGraph                    (L85)   — 肌肉判定（图着色版）测试
#     test_mv_is_muscle                  (L88)   — test_mv_is_muscle 函数
#     test_md_is_muscle                  (L91)   — test_md_is_muscle 函数
#     test_neuron_not_muscle             (L94)   — test_neuron_not_muscle 函数
#   TestGetCells                         (L98)   — XML 种群提取测试
#     test_extracts_populations          (L101)  — 应提取所有种群 ID
#     test_count                         (L108)  — 应返回 3 个种群
#   TestGetElecConns                     (L113)  — 电突触边提取测试
#     test_extracts_connections          (L116)  — 应提取电突触边
#     test_deduplicates_reverse          (L123)  — 反向连接应被去重
#   TestGetChemConns                     (L131)  — 化学突触边提取测试
#     test_extracts_excitatory           (L134)  — 应提取兴奋性连接
#     test_extracts_inhibitory           (L140)  — 应提取抑制性连接（红色 tee）
#   TestWriteGraphFile                   (L147)  — DOT 文件写入测试
#     test_creates_dot_file              (L150)  — 应创建 DOT 文件
#     test_muscle_color                  (L163)  — 肌肉节点应使用 darkolivegreen3 颜色
#     test_motor_neuron_color            (L170)  — 运动神经元应使用 slategray1 颜色
#     test_other_neuron_color            (L177)  — 其他神经元应使用 thistle2 颜色
#     test_layout_parameter              (L184)  — 应正确写入布局参数
#   TestFindNmlFiles                     (L192)  — NML 文件搜索测试
#     test_finds_nml_files               (L195)  — 应找到 .nml 文件
#     test_recursive_search              (L203)  — 递归搜索应找到子目录中的文件
#   TestExecuteGraphGenerator            (L212)  — execute_graph_generator 测试
#     test_calls_neato_and_dot           (L215)  — 应调用 neato 和 dot 命令
#   TestGenerateGraph                    (L235)  — generate_graph 端到端测试（mock 外部命令）
#     test_generates_both_layouts        (L238)  — 应生成 dot 和 neato 两种布局
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段七：新建
#
# 当前维护者：Copilot
# =============================================================================
"""graph 模块测试。"""
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from c302.visualization.graph import (
    _is_muscle_graph,
    find_nml_files,
    get_cells,
    get_chem_conns,
    get_elec_conns,
    write_graph_file,
)

# 用于测试的最小 NeuroML XML
_MINIMAL_NML = """\
<neuroml xmlns="http://www.neuroml.org/schema/neuroml2">
  <network id="test_net">
    <population id="ADAL" component="cell" size="1"/>
    <population id="ADAR" component="cell" size="1"/>
    <population id="MDL01" component="cell" size="1"/>
    <electricalProjection id="ep1" presynapticPopulation="ADAL"
        postsynapticPopulation="ADAR">
      <electricalConnectionInstanceW id="0" preCell="../ADAL/0/cell"
          postCell="../ADAR/0/cell" synapse="gj" weight="1.0"/>
    </electricalProjection>
    <continuousProjection id="cp1" presynapticPopulation="ADAL"
        postsynapticPopulation="MDL01">
      <continuousConnectionInstanceW id="0" preCell="../ADAL/0/cell"
          postCell="../MDL01/0/cell" preComponent="pre"
          postComponent="exc_syn" weight="2.0"/>
    </continuousProjection>
    <continuousProjection id="cp2" presynapticPopulation="ADAR"
        postsynapticPopulation="ADAL">
      <continuousConnectionInstanceW id="0" preCell="../ADAR/0/cell"
          postCell="../ADAL/0/cell" preComponent="pre"
          postComponent="inh_syn" weight="1.0"/>
    </continuousProjection>
  </network>
</neuroml>
"""


@pytest.fixture()
def nml_root():
    """返回解析后的最小 NeuroML XML 根节点。"""
    return ET.fromstring(_MINIMAL_NML)


class TestIsMuscleGraph:
    """肌肉判定（图着色版）测试。"""

    def test_mv_is_muscle(self) -> None:
        assert _is_muscle_graph("MVL01") is True

    def test_md_is_muscle(self) -> None:
        assert _is_muscle_graph("MDR01") is True

    def test_neuron_not_muscle(self) -> None:
        assert _is_muscle_graph("ADAL") is False


class TestGetCells:
    """XML 种群提取测试。"""

    def test_extracts_populations(self, nml_root) -> None:
        """应提取所有种群 ID。"""
        cells = get_cells(nml_root)
        assert "ADAL" in cells
        assert "ADAR" in cells
        assert "MDL01" in cells

    def test_count(self, nml_root) -> None:
        """应返回 3 个种群。"""
        assert len(get_cells(nml_root)) == 3


class TestGetElecConns:
    """电突触边提取测试。"""

    def test_extracts_connections(self, nml_root) -> None:
        """应提取电突触边。"""
        conns = get_elec_conns(nml_root)
        assert len(conns) >= 1
        assert "ADAL" in conns[0]
        assert "dashed" in conns[0]

    def test_deduplicates_reverse(self, nml_root) -> None:
        """反向连接应被去重。"""
        conns = get_elec_conns(nml_root)
        # 只有 ADAL→ADAR，不应有 ADAR→ADAL
        for c in conns:
            assert "ADAR -> ADAL" not in c


class TestGetChemConns:
    """化学突触边提取测试。"""

    def test_extracts_excitatory(self, nml_root) -> None:
        """应提取兴奋性连接。"""
        conns = get_chem_conns(nml_root)
        exc = [c for c in conns if "black" in c]
        assert len(exc) >= 1

    def test_extracts_inhibitory(self, nml_root) -> None:
        """应提取抑制性连接（红色 tee）。"""
        conns = get_chem_conns(nml_root)
        inh = [c for c in conns if "red" in c and "tee" in c]
        assert len(inh) >= 1


class TestWriteGraphFile:
    """DOT 文件写入测试。"""

    def test_creates_dot_file(self, tmp_path) -> None:
        """应创建 DOT 文件。"""
        output = str(tmp_path / "test.gv")
        write_graph_file(
            output,
            ["ADAL", "MDL01"],
            ['ADAL -> ADAR [style="dashed"]'],
            ['ADAL -> MDL01 [color="black"]'],
        )
        content = Path(output).read_text()
        assert "digraph exp" in content
        assert "ADAL" in content

    def test_muscle_color(self, tmp_path) -> None:
        """肌肉节点应使用 darkolivegreen3 颜色。"""
        output = str(tmp_path / "test.gv")
        write_graph_file(output, ["MDL01"], [], [])
        content = Path(output).read_text()
        assert "darkolivegreen3" in content

    def test_motor_neuron_color(self, tmp_path) -> None:
        """运动神经元应使用 slategray1 颜色。"""
        output = str(tmp_path / "test.gv")
        write_graph_file(output, ["DA1"], [], [])
        content = Path(output).read_text()
        assert "slategray1" in content

    def test_other_neuron_color(self, tmp_path) -> None:
        """其他神经元应使用 thistle2 颜色。"""
        output = str(tmp_path / "test.gv")
        write_graph_file(output, ["ADAL"], [], [])
        content = Path(output).read_text()
        assert "thistle2" in content

    def test_layout_parameter(self, tmp_path) -> None:
        """应正确写入布局参数。"""
        output = str(tmp_path / "test.gv")
        write_graph_file(output, ["ADAL"], [], [], layout="dot")
        content = Path(output).read_text()
        assert "layout = dot" in content


class TestFindNmlFiles:
    """NML 文件搜索测试。"""

    def test_finds_nml_files(self, tmp_path) -> None:
        """应找到 .nml 文件。"""
        (tmp_path / "test.nml").write_text("<nml/>")
        (tmp_path / "other.txt").write_text("text")
        files = find_nml_files(str(tmp_path))
        assert len(files) == 1
        assert files[0].endswith(".nml")

    def test_recursive_search(self, tmp_path) -> None:
        """递归搜索应找到子目录中的文件。"""
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "nested.nml").write_text("<nml/>")
        files = find_nml_files(str(tmp_path), recursive=True)
        assert len(files) == 1


class TestExecuteGraphGenerator:
    """execute_graph_generator 测试。"""

    def test_calls_neato_and_dot(self, tmp_path) -> None:
        """应调用 neato 和 dot 命令。"""
        from unittest.mock import patch, call
        from c302.visualization.graph import execute_graph_generator

        gv = str(tmp_path / "test.gv")
        fig = str(tmp_path / "test.png")
        # 创建虚拟 gv 文件
        Path(gv).write_text("digraph {}")

        with patch("c302.visualization.graph.subprocess.call") as mock_call, \
             patch("c302.visualization.graph.os.system") as mock_system:
            mock_call.return_value = 0
            execute_graph_generator(gv, fig)
            # neato 调用
            assert mock_call.call_count == 1
            # dot | neato 管线
            assert mock_system.call_count == 1


class TestGenerateGraph:
    """generate_graph 端到端测试（mock 外部命令）。"""

    def test_generates_both_layouts(self, tmp_path, nml_root) -> None:
        """应生成 dot 和 neato 两种布局。"""
        from unittest.mock import patch
        from c302.visualization.graph import generate_graph

        # 写出 NML 文件
        nml_file = str(tmp_path / "test.net.nml")
        tree = ET.ElementTree(nml_root)
        tree.write(nml_file)

        with patch("c302.visualization.graph.subprocess.call") as mock_call, \
             patch("c302.visualization.graph.os.system"):
            mock_call.return_value = 0
            generate_graph(nml_file)

        # 应生成 2 个 gv 文件
        gv_files = list(tmp_path.glob("*.gv"))
        assert len(gv_files) == 2
