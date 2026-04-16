# gen_graph.py 源码分析

> 自动生成于 2026-04-16，基于 commit e9e1100

## 模块概要

`project/c302/gen_graph.py` 是 NeuroML 网络拓扑图生成工具。
它负责解析 `.nml` 文件中的 population、electricalProjection 和 continuousProjection，
将细胞类型、边样式和连接方向映射为 Graphviz DOT 描述，并调用 `neato` 等命令行工具输出 PNG 图像。

模块整体职责较单一，主要由“提取节点”“提取电突触”“提取化学突触”“写出 DOT 文件”“调用 Graphviz”五步组成。

## 分析记录

### 2026-04-16 — 阶段五勘误（计划2）

**B 类旗标（注释代码标注）**

- 为 8 处注释代码补充了 `[备选]` / `[废弃]` 标签，覆盖以下旧逻辑：
	- `get_cells()` 中早期直接定位 `network` 节点的废弃写法
	- `get_cells()` / `get_elec_conns()` / `get_chem_conns()` 中“仅保留神经元、过滤肌肉”的备选过滤逻辑
	- `write_graph_file()` 中 Graphviz `concentrate=false` 的备选布局参数

**验证结果**：`gen_index.py` ×2 ✅ → `check_index.py` ✅ → `verify_comment_only.py` ✅（代码等价，仅注释变更）

## 修改记忆

| 日期 | commit | 修改范围 | 修改原因 |
|------|--------|---------|---------|
| 2026-04-16 | 待提交 | B 类标注 ×8 | 计划2阶段五注释勘误 |

| 2026-04-16 | 计划2阶段八 | 头块更新日志 | 记录计划2汇总校验完成并同步 SP-CODE 更新日志 |

## 踩坑记录

<!-- 记录非显而易见的问题和解决方案 -->
