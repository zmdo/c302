# 开发文档

本文档面向参与 c302 开发的贡献者，介绍项目结构、开发环境搭建和常见工作流。

## 项目结构

```
project_r1/
├── c302/                    # 主包
│   ├── __init__.py
│   ├── __version__.py
│   ├── configs/             # 配置脚本 (IClamp, Syns, Social, …)
│   ├── data_readers/        # 数据读取器 (Spreadsheet, Updated, OpenWorm)
│   ├── generator/           # NeuroML 生成引擎
│   │   ├── __init__.py      # generate() 入口
│   │   ├── connection.py    # 连接/投射创建
│   │   ├── io.py            # 文件写出
│   │   ├── population.py    # 种群创建
│   │   ├── position.py      # 坐标计算
│   │   └── stimulation.py   # 刺激注入
│   ├── parameters/          # 参数层
│   │   ├── __init__.py      # get_parameter_set() / list_parameter_sets()
│   │   ├── bioparameter.py  # BioParameter 数据类
│   │   ├── custom_types.py  # 自定义 NeuroML 组件类型
│   │   ├── factory/         # 模型工厂子包
│   │   │   ├── __init__.py  # create_model() + _LEVEL_TO_CLASS
│   │   │   ├── base.py      # _ModelBase + _GradedSynapse2Mixin
│   │   │   ├── iaf.py       # _IafModel / _IafActivityModel / _BC1Model
│   │   │   ├── hh.py        # _HHModel / _HHC0Model / _HHC1Model
│   │   │   ├── hh_multi.py  # _HHMultiCompModel / _HHGradedModel
│   │   │   ├── c2.py        # _C2Model
│   │   │   └── w2d.py       # _W2DModel
│   │   ├── loader.py        # YAML 加载器
│   │   ├── model.py         # c302ModelPrototype 基类
│   │   └── registry.py      # 参数集注册表
│   ├── simulation/          # 仿真执行
│   │   └── runner.py        # 命令行 & Python API
│   ├── visualization/       # 可视化
│   │   ├── traces.py        # 膜电位时序图
│   │   ├── heatmap.py       # 膜电位热力图
│   │   ├── connectivity.py  # 连接矩阵
│   │   └── graph.py         # 网络拓扑图
│   └── cells.py             # 细胞名称常量
├── data/                    # 数据文件
│   ├── parameters/          # YAML 参数集
│   └── cell_info/           # 细胞信息
├── tests/                   # 测试
│   ├── test_parameters/
│   ├── test_data_readers/
│   ├── test_generator/
│   ├── test_configs/
│   ├── test_simulation/
│   ├── test_visualization/
│   └── test_equivalence.py  # 等价性测试
├── docs/                    # 文档
└── pyproject.toml           # 项目配置
```

## 开发环境搭建

### 前置条件

- Python ≥ 3.10
- pip / uv

### 安装

```bash
# 克隆并进入项目目录
cd project_r1

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装（含开发依赖）
pip install -e ".[dev]"
```

### 运行测试

```bash
# 全部测试
pytest tests/

# 仅等价性测试
pytest tests/test_equivalence.py -v

# 带覆盖率
pytest tests/ --cov=c302 --cov-report=term-missing
```

## 核心工作流

### 1. 添加新参数集

1. 在 `data/parameters/` 下创建 YAML 文件（如 `level_x.yaml`）：
   ```yaml
   level: X
   custom_component_types_definitions: "cell_C.xml"
   bioparameters:
     - name: "param_name"
       value: "0.1 nS"
       source: "Reference"
       certainty: "0.5"
   ```
2. 如需继承，加 `inherits: level_c`。
3. 在 `parameters/factory/__init__.py` 的 `_LEVEL_TO_CLASS` 注册对应模型类。
4. 在 `parameters/__init__.py` 的 `_LEVEL_REGISTRY` 添加级别名。
5. 添加等价性测试用例到 `tests/test_equivalence.py`。

### 2. 添加新配置脚本

1. 在 `c302/configs/` 下创建 `{name}.py`。
2. 使用 `@register_config("{Name}")` 装饰器注册 `setup()` 函数。
3. 在 `tests/test_configs/` 下添加测试。

### 3. 修改生成引擎

生成引擎分模块位于 `c302/generator/`：

- `population.py` — 种群/细胞创建
- `connection.py` — 突触连接创建
- `stimulation.py` — 刺激注入
- `io.py` — NeuroML/LEMS 文件输出
- `__init__.py` — `generate()` 入口，串联上述模块

修改后请运行等价性测试确保输出不变：
```bash
pytest tests/test_equivalence.py -v
```

## 参数层级架构

```
_ModelBase (c302ModelPrototype)
├── _IafModel (A)          — IAF 细胞 + ExpTwoSynapse
├── _IafActivityModel (B)  — IafActivityCell + GapJunction
│   └── _BC1Model (BC1)    — B + GradedSynapse
├── _HHModel (C)           — HH 细胞 (ca_boyle) + ExpTwoSynapse
│   ├── _HHC1Model (C1)    — HH 细胞 (ca_boyle) + GradedSynapse
│   └── _C2Model (C2)      — HH + GradedSynapse + 自定义缝隙连接
├── _GradedSynapse2Mixin + _ModelBase
│   └── _HHC0Model (C0)    — HH 细胞 (ca_simple) + GradedSynapse2
├── _HHMultiCompModel (D)  — HH 多室模型（每神经元独立形态）
│   └── _HHGradedModel (D1) — D + GradedSynapse2
└── _W2DModel (W2D)        — CellW2D 偏置-增益细胞 + OutputSynapse
```

## 代码规范

本项目遵循 SP-CODE-2026-001 编码规范。关键要求：

- 每个 `.py` 文件必须有标准文件头（功能描述 / 类与方法索引 / 更新日志 / 维护者）
- 每个函数/方法必须有 reST 格式 docstring
- 关键逻辑、条件分支、循环必须有行内注释
- 命名遵循 PEP 8（`snake_case` 函数/变量，`PascalCase` 类）
