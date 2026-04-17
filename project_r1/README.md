# c302 — C. elegans 302 Neuron NeuroML 2 Network

c302 是一个用于生成秀丽隐杆线虫（*C. elegans*）302 个神经元 NeuroML 2 网络模型的 Python 框架。它是 [OpenWorm](https://openworm.org/) 项目的一部分。

## 功能特性

- **多级参数化模型** — 从简单的 IAF（A/B 级）到完整的 Hodgkin-Huxley 导电模型（C/D 级）
- **可插拔数据源** — 支持多种连接组学数据读取器
- **灵活的配置** — 通过配置脚本定义不同的神经回路
- **NeuroML 2 输出** — 生成标准化的 NeuroML 2 / LEMS 文件
- **可视化工具** — 膜电位时序图、热力图、连接矩阵、网络拓扑图

## 安装

```bash
# 基本安装
pip install -e .

# 含开发依赖
pip install -e ".[dev]"
```

要求 Python ≥ 3.10。

## 快速开始

```python
from c302.configs import get_config

# 使用 IClamp 配置 + A 级参数生成网络
setup = get_config("IClamp")
cells, cells_total, params, muscles, nml_doc = setup(
    "A", generate_flag=True, target_directory="./output"
)
```

## 文档

- [使用文档](docs/usage.md) — 安装、API 使用、参数集和配置说明
- [开发文档](docs/development.md) — 项目结构、开发环境、工作流

## 参数集层级

| 级别 | 模型 | 细胞类型 | 化学突触 | 电突触 |
|------|------|---------|---------|--------|
| A | IAF | IafCell | ExpTwoSynapse | ExpTwoSynapse |
| B | IAF | IafActivityCell | ExpTwoSynapse | GapJunction |
| C | HH | Cell (ca_boyle) | ExpTwoSynapse | GapJunction |
| C0 | HH | Cell (ca_simple) | GradedSynapse2 | GapJunction |
| C1 | HH | Cell (ca_boyle) | GradedSynapse | GapJunction |
| D | HH 多室 | Cell (per-neuron) | ExpTwoSynapse | GapJunction |
| D1 | HH 多室 | Cell (per-neuron) | GradedSynapse2 | GapJunction |

## 测试

```bash
pytest tests/
```

## 许可

MIT License — 详见 [LICENSE](../LICENSE)。
