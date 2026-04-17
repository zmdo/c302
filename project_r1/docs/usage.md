# 使用文档

c302 是 C. elegans 302 神经元 NeuroML 2 网络的建模框架。本文档介绍如何使用 c302 生成、仿真和可视化神经网络模型。

## 安装

```bash
pip install -e .
```

## 快速开始

### 使用配置脚本生成网络

```python
from c302.configs import get_config

setup = get_config("IClamp")
cells, cells_total, params, muscles, nml_doc = setup(
    "A",
    generate_flag=True,
    target_directory="./output",
)
print(f"生成了 {len(cells)} 个神经元")
```

### 使用生成器 API

```python
from c302.parameters import get_parameter_set
from c302.generator import generate

params = get_parameter_set("C")
nml_doc, cells, cells_total, conns, muscles = generate(
    net_id="c302_C_IClamp",
    params=params,
    data_reader="SpreadsheetDataReader",
    cells=["ADAL", "ADAR"],
    cells_to_stimulate=["ADAL"],
    duration=500.0,
    dt=0.01,
    target_directory="./output",
)
```

## 参数集

可用参数集：

| 级别 | 模型类型 | 说明 |
|------|---------|------|
| A    | IAF     | 积分-放电模型，最简单 |
| B    | IAF+Activity | 带活动性的 IAF，GapJunction 电突触 |
| C    | HH      | Hodgkin-Huxley 导电模型（ca_boyle 通道） |
| C0   | HH      | HH 模型（ca_simple 通道，GradedSynapse2） |
| C1   | HH      | HH 模型（ca_boyle 通道，GradedSynapse） |
| D    | HH 多室  | 每个神经元有独立形态学数据 |
| D1   | HH 多室  | D + GradedSynapse2 模拟突触 |

### 列出可用参数集

```python
from c302.parameters import list_parameter_sets

print(list_parameter_sets())  # ['A', 'B', 'C', 'C0', 'C1', 'D', 'D1']
```

### 加载参数集

```python
from c302.parameters import get_parameter_set

params = get_parameter_set("C0")
print(params.level)            # "C0"
print(len(params.bioparameters))  # 38
```

## 配置脚本

| 配置 | 说明 |
|------|------|
| IClamp      | 单细胞电流钳测试 |
| Syns        | 突触连接测试 |
| Social      | 社交行为回路 |
| Oscillator  | 运动振荡回路 |
| Muscles     | 含肌肉的网络 |
| Full        | 完整 302 神经元网络 |
| FW          | 前向运动回路 |
| Pharyngeal  | 咽部神经回路 |
| TapWithdrawal | 触碰退缩反射回路 |
| RIA         | RIA 中间神经元回路 |

## 数据读取器

c302 支持多种连接组学数据源：

- `SpreadsheetDataReader` — 经典电子表格数据（默认）
- `UpdatedSpreadsheetDataReader` — 更新版电子表格数据
- `UpdatedSpreadsheetDataReader2` — 进一步更新的数据
- `OpenWormReader` — OpenWorm 项目数据
- `White_whole` / `White_A` / `White_L4` — White et al. 数据

## 可视化

### 膜电位时序图

```python
from c302.visualization.traces import generate_traces_plot

generate_traces_plot("simulation_results.dat", cells=["ADAL", "ADAR"])
```

### 膜电位热力图

```python
from c302.visualization.heatmap import generate_heatmap

generate_heatmap("simulation_results.dat")
```

### 连接矩阵

```python
from c302.visualization.connectivity import generate_conn_matrix

generate_conn_matrix("network.nml", output="conn_matrix.png")
```

### 网络拓扑图

```python
from c302.visualization.graph import generate_graph

generate_graph("network.nml")
```

## 仿真执行

```python
from c302.simulation.runner import run_simulation

results = run_simulation(
    lems_file="LEMS_c302.xml",
    simulator="jNeuroML_NEURON",
    duration=1000.0,
)
```
