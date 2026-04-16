# =============================================================================
# 功能描述：
#   NeuroML 2 几何工具集。
#   提供从细胞形态学数据中提取片段 ID、计算三维坐标的功能，
#   用于将 Population/Instance 放置于正确的空间位置。
#
# 类与方法索引：
#   getSegmentIds                        (L21)   — 提取细胞形态学中所有片段的 ID 列表
#   get3DPosition                        (L34)   — 计算细胞指定片段上某点的三维坐标
#   fract                                (L65)   — 在两点之间进行线性插值
#
# 更新日志：
#   2026-04-16  Copilot  添加中文 docstring 和行内注释
#
# 当前维护者：Copilot
# =============================================================================

from c302.ConnectomeReader import analyse_connections


def getSegmentIds(cell):
    """提取细胞形态学中所有片段的 ID 列表。

    :param cell: NeuroML Cell 对象
    :return: 片段 ID 列表
    """
    seg_ids = []
    for segment in cell.morphology.segments:
        seg_ids.append(segment.id)

    return seg_ids


def get3DPosition(cell, segment_index, fraction_along):
    """计算细胞指定片段上某点的三维坐标。

    根据 ``fraction_along`` 在片段的近端（proximal）和远端（distal）之间
    进行线性插值。若近端缺失，则使用父片段的远端作为起点。

    :param cell: NeuroML Cell 对象
    :param segment_index: 片段索引
    :param fraction_along: 沿片段的分数位置（0.0=近端，1.0=远端）
    :return: ``(x, y, z)`` 三维坐标元组
    """
    seg = cell.morphology.segments[segment_index]

    end = seg.distal

    start = seg.proximal
    if start is None:
        # 近端缺失时，使用父片段的远端作为起点
        segs = getSegmentIds(cell)
        seg_index_parent = segs.index(seg.parent.segments)
        start = cell.morphology.segments[seg_index_parent].distal

    fx = fract(start.x, end.x, fraction_along)
    fy = fract(start.y, end.y, fraction_along)
    fz = fract(start.z, end.z, fraction_along)

    # print "(%f, %f, %f) is %f between (%f, %f, %f) and (%f, %f, %f)"%(fx,fy,fz,fraction_along,start.x,start.y,start.z,end.x,end.y,end.z)

    return fx, fy, fz


def fract(a, b, f):
    """在两点之间进行线性插值。

    公式：``a + (b - a) * f``

    :param a: 起始值
    :param b: 终止值
    :param f: 插值分数（0.0=a，1.0=b）
    :return: 插值结果
    """
    return a + (b - a) * f


if __name__ == "__main__":
    from WormNeuroAtlasReader import read_data, read_muscle_data

    cells, neuron_conns = read_data(include_nonconnected_cells=True)
    neurons2muscles, muscles, muscle_conns = read_muscle_data()

    analyse_connections(cells, neuron_conns, neurons2muscles, muscles, muscle_conns)
