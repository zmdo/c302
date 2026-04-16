# __init__.py 源码分析

> 自动生成于 2026-04-16，基于 commit e9e1100

## 模块概要

`project/c302/__init__.py` 是 c302 框架的核心网络生成模块（2172 行）。
主要职责：将连接组数据（connectome）与参数化细胞/突触模型组装为完整的 NeuroML2 网络，
输出 `.net.nml` 文件和 LEMS 仿真文件。

核心函数 `generate()` 是约 1100 行的主循环，分 9 个步骤：
1. 加载数据读取器和参数模块
2. 构建神经元种群 + 注入刺激
3. 构建肌肉种群（若启用）
4. 遍历神经元-神经元连接（电突触 + 化学突触）
5. 遍历神经肌肉连接（若启用）
6. 注入外部刺激（IClamp / Sine）
7. 处理连接极性覆盖 / 数量缩放
8. 填写 lems_info 字典（用于 LEMS 模板渲染）
9. 调用 `write_to_file()` 写出文件

其他辅助函数涵盖：坐标获取、刺激构建、连接 ID 生成、数据读取器动态加载等。

## 分析记录

### 2026-04-16 — 阶段四勘误（计划2）

**A 类旗标（英文注释翻译）**

| 位置 | 旧文本 | 新文本 |
|------|--------|--------|
| 方法索引 `load_data_reader` | `Imports and returns data reader module` | `动态导入并返回指定名称的数据读取器模块` |
| 方法索引 `get_str_from_exponential` | `Returns a formatted string representing...` | `将浮点数格式化为字符串表示（如 0.00001 → "1e-05"）` |
| 方法索引 `process_args` | `Parse command-line arguments.` | `解析 CLI 命令行参数，返回 argparse.Namespace 对象` |

**B 类旗标（注释代码标注）**

共为 20 处注释代码行添加 `[调试]`/`[备选]`/`[废弃]` 标签：
- `[备选]` × 8：`# import c302.bioparameters`、旧版 `DEFAULT_DATA_READER`、`cell_file_path`、`phase=`、`lems_file`、`def_file`、`elem_in_coll_matches_conn`、`number_syns=conn.number*...`
- `[调试]` × 11：soma 坐标打印、owmeta 查询打印、细胞匹配警告、lems_info 最终返回、肌肉坐标打印、缩放因子打印（×2）、运动神经元连接打印、cell_id 路径打印（×2）、pprint 调试
- `[废弃]` × 1：`target = "%s/0/%s"...` 旧写法（已弃用）
- muscle_to_neuron 逻辑块（2 行）`[备选]`

**验证结果**：`gen_index` ✅（两次） → `check_index` ✅ → `verify_comment_only` ✅（代码等价，仅注释变更）

## 修改记忆

| 日期 | commit | 修改范围 | 修改原因 |
|------|--------|---------|---------|
| 2026-04-16 | e9e1100 | 添加中文 docstring 和步骤标记（计划1阶段四） | 注释工程 |
| 2026-04-16 | 待提交 | A 类翻译 ×3、B 类标注 ×20（计划2阶段四） | 注释勘误 |

## 踩坑记录

- **双重 `# print("Scaling by %s"%scale)`**：`generate()` 中神经元连接和肌肉连接循环各有一处（L1591、L1892），需分别标注，不能合并替换。
- **三引号字符串块**：`generate()` 内有两处 `"""..."""` 字符串块（约 L1614–1622、L1624–1631），内部含注释代码，但它们是字符串字面量，不是注释行，不应添加 `[备选]`/`[调试]` 标签。
- **行号偏移**：B 类标签逐条插入时行号会依次偏移，必须在顺序替换时用精确上下文锚定，不能依赖预先扫描的行号。
