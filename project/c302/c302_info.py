# =============================================================================
# 功能描述：
#   c302 网络文档生成工具。
#   从 NeuroML 文档中解析连接信息，通过 owmeta 查询细胞类型、
#   神经递质和受体数据，生成 Markdown 格式的神经元/肌肉汇总表。
#
# 类与方法索引：
#   generate_c302_info                   (L20)   — 从 NeuroML 文档生成神经元和肌肉的汇总信息表
#   _info_set                            (L139)  — 将集合排序后用逗号连接为字符串
#
# 更新日志：
#   2026-04-16  Copilot  计划2 阶段八收尾：补记汇总校验与最终勘误完成
#   2026-04-16  Copilot  添加中文 docstring 和行内注释
#
# 当前维护者：Copilot
# =============================================================================
import c302


def generate_c302_info(nml_doc, verbose=False):
    """从 NeuroML 文档生成神经元和肌肉的汇总信息表。

    解析网络中所有连续投射和电投射，通过 owmeta 查询细胞类型、
    神经递质和受体信息，生成 Markdown 格式汇总文件。

    :param nml_doc: NeuroML 文档对象
    :param verbose: 是否输出详细日志
    """
    net = nml_doc.networks[0]

    cc_exc_conns = {}   # 兴奋性化学突触连接 {pre: {post: weight}}
    cc_inh_conns = {}   # 抑制性化学突触连接
    all_cells = []      # 所有参与连接的细胞名称

    for cp in net.continuous_projections:
        if cp.presynaptic_population not in cc_exc_conns.keys():
            cc_exc_conns[cp.presynaptic_population] = {}
        if cp.presynaptic_population not in cc_inh_conns.keys():
            cc_inh_conns[cp.presynaptic_population] = {}

        if cp.presynaptic_population not in all_cells:
            all_cells.append(cp.presynaptic_population)
        if cp.postsynaptic_population not in all_cells:
            all_cells.append(cp.postsynaptic_population)

        for c in cp.continuous_connection_instance_ws:
            if "inh" in c.post_component:
                cc_inh_conns[cp.presynaptic_population][cp.postsynaptic_population] = (
                    float(c.weight)
                )
            else:
                cc_exc_conns[cp.presynaptic_population][cp.postsynaptic_population] = (
                    float(c.weight)
                )

    gj_conns = {}  # 电突触（缝隙连接） {pre: {post: weight}}
    for ep in net.electrical_projections:
        if ep.presynaptic_population not in gj_conns.keys():
            gj_conns[ep.presynaptic_population] = {}

        if ep.presynaptic_population not in all_cells:
            all_cells.append(ep.presynaptic_population)
        if ep.postsynaptic_population not in all_cells:
            all_cells.append(ep.postsynaptic_population)

        for e in ep.electrical_connection_instance_ws:
            gj_conns[ep.presynaptic_population][ep.postsynaptic_population] = float(
                e.weight
            )

    all_cells = sorted(all_cells)

    try:
        # 尝试使用 PyOpenWorm 查询细胞信息
        from PyOpenWorm import (
            connect as pyow_connect,
            __version__ as pyow_version,
        )

        pow_conn = pyow_connect("./pyopenworm.conf")
        all_neuron_info, all_muscle_info = c302._get_cell_info(pow_conn, all_cells)
        ver_info = "PyOpenWorm v%s" % pyow_version
    except Exception as e:
        c302.print_("Unable to connect to PyOpenWorm database: %s" % e)
        # 回退到 owmeta 查询
        from owmeta_core.bundle import Bundle

        from owmeta_core import __version__ as owc_version
        from owmeta import __version__ as owmeta_version

        ver_info = "owmeta v%s (owmeta core v%s)" % (owmeta_version, owc_version)

        with Bundle("openworm/owmeta-data", version=6) as bnd:
            all_neuron_info, all_muscle_info = c302._get_cell_info(bnd, all_cells)

    all_neurons = []
    all_muscles = []
    for c in all_cells:
        if c302.is_muscle(c):
            all_muscles.append(c)
        else:
            all_neurons.append(c)

    info = "# Information on neuron and muscles\n"
    info += "## Generated using %s\n" % ver_info

    info += "### Neurons (%i)\n" % (len(all_neuron_info))
    info += "<table>\n"
    for n in all_neuron_info:
        info += "<tr>\n"
        ni = all_neuron_info[n]
        # [调试] 可取消注释以检查单个神经元信息元组的结构
        # print(ni)
        info += (
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>Colour: %s</td>"
            % (n, _info_set(ni[1]), _info_set(ni[2]), _info_set(ni[3]), ni[4], ni[5])
        )
        info += "</tr>\n"
    info += "</table>\n"

    info += "### Muscles (%i)\n" % (len(all_muscle_info))
    info += "<table>\n"
    for n in all_muscle_info:
        info += "<tr>\n"
        ni = all_muscle_info[n]
        info += (
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>Colour: %s</td>"
            % (n, _info_set(ni[1]), _info_set(ni[2]), _info_set(ni[3]), ni[4], ni[5])
        )
        info += "</tr>\n"
    info += "</table>\n"

    with open("examples/summary/summary.md", "w") as f2:
        # [备选] 以下为同时写出 HTML 包装页的旧写法，当前仅输出 Markdown 摘要
        # f2.write('<html><body>%s</body></html>'%info)
        f2.write("%s" % info)


def _info_set(s):
    """将集合排序后用逗号连接为字符串。

    :param s: 可迭代对象
    :return: 逗号分隔的排序字符串
    """
    s = sorted(s)
    return ", ".join(["%s" % i for i in s])


if __name__ == "__main__":
    from neuroml.loaders import read_neuroml2_file

    config = "c302_C0_Full.net.nml"

    nml_doc = read_neuroml2_file("examples/%s" % config)

    generate_c302_info(nml_doc)
