# 临时适配器模块，用于在比较 notebook 中使用 WhiteDataReader 的实际读取器类。
# 后续应整理为更规范的形式。
# 数据源：White et al. 1986 L4 幼虫神经元连接组（L4 larva）

from c302.WhiteDataReader import White_L4

from c302.ConnectomeReader import analyse_connections

# 将 White_L4 类的 read_data/read_muscle_data 方法暴露为模块级别名，
# 与其他数据读取器保持相同接口
read_data = White_L4.read_data
read_muscle_data = White_L4.read_muscle_data


def main1():
    cells, neuron_conns = read_data(include_nonconnected_cells=True)
    neurons2muscles, muscles, muscle_conns = read_muscle_data()
    analyse_connections(cells, neuron_conns, neurons2muscles, muscles, muscle_conns)


if __name__ == "__main__":
    main1()
