# =============================================================================
# 功能描述：
#   WhiteDataReader.White_whole 读取器的临时适配器模块。
#   将 White_whole 类的 read_data/read_muscle_data 方法暴露为模块级别名，
#   以供比较 notebook 使用。数据源：White et al. 1986 完整成虫连接组（whole）。
#
# 类与方法索引：
#   main1                                (L29)   — 读取 White_whole 连接组数据并打印统计摘要
#
# 更新日志：
#   2026-04-16  zmdo  添加中文注释（计划1 阶段二）
#
# 当前维护者：zmdo
# =============================================================================
# 临时适配器模块，用于在比较 notebook 中使用 WhiteDataReader 的实际读取器类。
# 后续应整理为更规范的形式。
# 数据源：White et al. 1986 完整成虫神经元连接组（whole）

from c302.WhiteDataReader import White_whole

from c302.ConnectomeReader import analyse_connections

# 将 White_whole 类的 read_data/read_muscle_data 方法暴露为模块级别名，
# 与其他数据读取器保持相同接口
read_data = White_whole.read_data
read_muscle_data = White_whole.read_muscle_data


def main1():
    """读取 White_whole 连接组数据并打印统计摘要。"""
    cells, neuron_conns = read_data(include_nonconnected_cells=True)
    neurons2muscles, muscles, muscle_conns = read_muscle_data()
    analyse_connections(cells, neuron_conns, neurons2muscles, muscles, muscle_conns)


if __name__ == "__main__":
    main1()
