---
name: src-doc-tracking
description: "源码文档跟踪：为每个 Python 源文件维护一份对应的 .md 分析文档，记录模块功能摘要、分析记录、修改记忆和踩坑记录。代码结构目录（类与方法索引）已在源码头部 SP-CODE 注释块中维护，文档中不重复收录。内置三个工具脚本：gen_src_doc.py（生成文档骨架）、check_doc_sync.py（检测 git 暂存区中源码变更但文档未变更的情况）、check_doc_length.py（检测文档是否超长并提示压缩）。Use when: 用户要求对源码进行分析勘误、要求创建或更新源码分析文档、要求检查文档与源码的同步状态、要求压缩过长的分析文档。"
license: MIT
compatibility: "Python 3.10+ 项目。需要 git。"
metadata:
  author: Copilot
  version: "1.0"
allowed-tools: Read Edit Terminal
---

# 源码文档跟踪（src-doc-tracking）

## 何时使用

- 用户要求对源码进行分析、勘误、审阅
- 用户要求为源码文件创建或更新分析文档
- 用户要求检查文档与源码的同步状态
- 用户要求压缩过长的分析文档
- 用户执行类似"源码勘误"、"注释审阅"的任务

## 映射规则

源码路径与文档路径的映射关系：

```
project/c302/{name}.py  →  project/c302-docs/src/{name}.py.md
```

即：将源码的父目录 `c302/` 替换为 `c302-docs/src/`，文件名追加 `.md` 后缀。

## 文档规范

每份文档必须包含以下章节（按顺序）：

```markdown
# {文件名} 源码分析

> 自动生成于 YYYY-MM-DD，基于 commit {短哈希}

## 模块概要

一段话描述此模块的职责和在项目中的位置。

> 注：代码结构目录（类与方法索引）已在源码头部 SP-CODE 注释块中维护，文档中不重复收录。

## 分析记录

按时间倒序记录每次分析/勘误的发现。每条记录格式：

### YYYY-MM-DD 分析主题

**范围**：涉及的函数/类/行号范围
**发现**：具体问题描述
**结论**：是否需修改 / 修改方案

## 修改记忆

记录对该文件的每次修改及其原因，便于追溯。

| 日期 | commit | 修改范围 | 修改原因 |
|------|--------|---------|---------|

## 踩坑记录

记录分析/修改过程中遇到的非显而易见的问题。

- **坑点**：描述
  **原因**：根因
  **解决**：方案
```

### 章节规则

| 章节 | 是否必须 | 自动生成 | 说明 |
|------|---------|---------|------|
| 模块概要 | 必须 | 首次生成骨架 | 后续由人工/AI 维护 |
| 分析记录 | 必须 | 否 | 分析时追加 |
| 修改记忆 | 必须 | 否 | 修改时追加 |
| 踩坑记录 | 可选 | 否 | 遇到坑时追加 |

## 内置工具

所有工具位于本 skill 的 `scripts/` 目录：

| 工具 | 文件 | 用途 |
|------|------|------|
| gen_src_doc.py | [scripts/gen_src_doc.py](scripts/gen_src_doc.py) | 生成文档骨架（已存在则跳过） |
| check_doc_sync.py | [scripts/check_doc_sync.py](scripts/check_doc_sync.py) | 检测 git 暂存区中源码变更但文档未同步 |
| check_doc_length.py | [scripts/check_doc_length.py](scripts/check_doc_length.py) | 检测文档是否超过长度阈值 |

## 工作流程

### 场景 A：首次为源码创建文档

```bash
SKILL_SCRIPTS=".github/skills/src-doc-tracking/scripts"

# 为单个文件生成文档
python $SKILL_SCRIPTS/gen_src_doc.py project/c302/bioparameters.py

# 为目录下所有 .py 文件批量生成
python $SKILL_SCRIPTS/gen_src_doc.py project/c302/
```

生成后手动填写「模块概要」，其余章节在后续分析过程中逐步填充。

### 场景 B：分析/勘误源码

1. 打开源码和对应文档
2. 分析源码，将发现追加到「分析记录」章节
3. 如需修改源码，修改后：
   - 在「修改记忆」中记录本次修改
4. 运行 `check_doc_length.py` 检查文档是否过长

### 场景 C：提交前检查

```bash
# 检查暂存区中是否有源码变更但文档未同步的情况
python $SKILL_SCRIPTS/check_doc_sync.py

# 检查文档长度
python $SKILL_SCRIPTS/check_doc_length.py project/c302-docs/
```

可配置为 Git pre-commit hook：

```bash
# .git/hooks/pre-commit 中添加：
python .github/skills/src-doc-tracking/scripts/check_doc_sync.py || exit 1
```

## 文档压缩策略

当 `check_doc_length.py` 报告文档超过阈值（默认 300 行）时：

1. **分析记录**：将超过 3 个月的旧记录合并为摘要条目
2. **修改记忆**：保留最近 20 条，更早的归档到 `## 历史修改归档` 折叠块
3. **踩坑记录**：已解决且不再复现的坑可删除

压缩时在文档开头添加注释：

```markdown
<!-- 上次压缩: YYYY-MM-DD, 原始行数: N, 压缩后: M -->
```

## 注意事项

- `gen_src_doc.py` 仅在文档不存在时创建骨架，不会覆盖已有文档
- 代码结构目录（类与方法索引）在源码头部 SP-CODE 注释块中维护，文档中不重复收录
- `check_doc_sync.py` 仅检查 `git diff --cached`（暂存区），未暂存的变更不报错
- `__version__.py`、`__pycache__/` 等非逻辑文件自动跳过
