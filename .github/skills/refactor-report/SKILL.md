---
name: refactor-report
description: Write structured multi-file refactoring proposal reports under design-docs/reports/refactor/. Use when a plan involves refactoring existing code, when the user asks to write a refactoring proposal, or after a code-analysis-report has been completed and refactoring is needed. Covers problem inventory with severity, layer-by-layer issue analysis, and phased implementation plans. Typically used AFTER the code-analysis-report skill and BEFORE the plan-write skill. DO NOT USE FOR: code analysis snapshots (use code-analysis-report), bug reports (use bug-report), or writing implementation plans (use plan-write).
license: MIT
compatibility: c302（C. elegans 神经网络建模框架，OpenWorm 子项目）。Python 项目，需要 design-docs/reports/refactor/ 目录。
metadata:
  author: Copilot
  version: "1.0"
allowed-tools: Read Edit Terminal
---

# Refactor Report

## When to Use

- A development plan involves refactoring existing code and a code analysis report has been completed
- User asks to write a refactoring proposal or improvement report
- User asks to analyze code quality issues and propose fixes
- The plan-write skill's refactoring workflow (Step R2) triggers this skill

## Directory Convention

**Location**: `design-docs/reports/refactor/`

**Directory naming**: `refactor-{YYYYMMDD}-{short-hash}`

- `YYYYMMDD` = report date (e.g. `20260330`)
- `short-hash` = the 7-char short hash of the **most recent commit** at the time of writing (use `git rev-parse --short HEAD`)
- Example: `refactor-20260330-7548402`

## Document Structure

Reports are split into numbered files. The structure adapts to the number and category of issues found.

### Standard layout

| File | Purpose |
|---|---|
| `00-报告概览.md` | Overview: metadata table, report index, review methodology, core findings summary |
| `01-问题总览与优先级.md` | Full issue table (all problems), priority phases, things NOT to change |
| `02-{layer}问题.md` | Detailed analysis of issues in layer 1 (e.g. 数据层) |
| `03-{layer}问题.md` | Detailed analysis of issues in layer 2 (e.g. 路由层) |
| `04-{layer}问题.md` | Detailed analysis of issues in layer 3 (e.g. 服务层) |
| `05-{topic}问题.md` | Cross-cutting concerns (e.g. 安全与防护) |
| `0N-重构实施计划.md` | Phased implementation plan (always the last file) |

Layer files (`02`–`05`) are organized by architectural layer or concern area. Common groupings:
- **数据层**: ORM models, database schema, queries, serialization
- **路由层**: API endpoints, input validation, response format, error handling
- **服务层**: Business logic, state management, threading, exception handling
- **安全与防护**: Upload validation, secrets protection, audit logging

Adjust the number and naming of layer files based on where issues are found.

## File Content Guidelines

### `00-报告概览.md`

Start with a descriptive `# {Project Name} 后端重构建议报告` heading.

**Required metadata table:**

```markdown
| 项目 | 内容 |
|------|------|
| **报告时间** | {YYYY-MM-DD} |
| **分支** | `{branch}` |
| **提交 Hash** | `{short-hash}` |
| **报告人** | GitHub Copilot (Claude Opus 4.6) |
| **报告范围** | {scope description} |
| **报告类型** | 架构审查 + 重构建议 |
```

**Required sections:**
- **报告目录**: Table with file number, filename (linked), and content description
- **审查方法**: Numbered list of review methods used (full code read, code standard check, architecture review, security review, cross-validation)
- **核心发现**: Summary statistics table (severity | count | description) + a principle statement

### `01-问题总览与优先级.md`

**全部问题清单**: Complete table of ALL issues found, sorted by priority:

```markdown
| # | 严重度 | 类别 | 问题标题 | 涉及文件 | 详情 |
|---|--------|------|----------|----------|------|
| 1 | 🔴 高 | {layer} | {title} | {files} | [{link}]({file}#{anchor}) |
```

**实施优先级建议**: Group issues into phases:
- **🔴 第一阶段（建议立即修复）**: High severity issues, estimated effort
- **🟡 第二阶段（建议近期安排）**: Medium severity issues, estimated effort
- **🟢 第三阶段（持续改进）**: Low severity issues

**不建议大动的部分**: Table of design decisions that should be kept as-is, with rationale:

```markdown
| 决策 | 当前做法 | 理由 |
|------|----------|------|
| {decision} | {current approach} | {why it's fine} |
```

### Layer analysis files (`02`–`05`)

Each layer file follows this pattern per issue:

```markdown
## {N}. {Issue title}

**严重度**：{🔴 高 / 🟡 中 / 🟢 低}
**涉及文件**：{file list}

### 问题描述

{Explanation with concrete code examples showing the problem}

### 风险 / 为什么当前能正常工作

{Impact analysis — what can go wrong, or why it works despite the issue}

### 建议修复

{Concrete fix with code snippets, alternative approaches if applicable}
```

**Severity levels:**
- 🔴 高 — Affects data correctness or has security implications
- 🟡 中 — Affects maintainability or has potential risk
- 🟢 低 — Code quality improvement suggestions

### `0N-重构实施计划.md` (always last file)

**实施原则**: Numbered list of guiding principles (progressive improvement, backward compatibility, minimal dependencies, fix bugs before optimizing)

**Per phase:**

```markdown
## 第{N}阶段：{phase description}

**预计工作量**：{duration estimate}
**目标**：{one-line goal}

### 任务 {N}.{M} — {task title}

**涉及文件**：{file list}

| 步骤 | 操作 |
|------|------|
| 1 | {step description} |
| 2 | {step description} |

**注意事项**：
- {important notes, gotchas, dependencies}
```

## Workflow

### Step 1: Review Code Analysis Report

Read the code analysis report (from `design-docs/reports/analysis/`) to understand the current codebase state. If no code analysis report exists, inform the user that one should be written first (using the code-analysis-report skill).

### Step 2: Deep Dive into Problem Areas

Based on the code analysis, read the actual source files to:
- Confirm each suspected issue with concrete code evidence
- Determine the exact severity (🔴/🟡/🟢)
- Identify the full scope of affected files
- Check for issues the code analysis might have missed

### Step 3: Write Report Files

Write files in order `00` → `01` → `02`...`05` → `0N` (implementation plan last).

### Step 4: Review Report

After writing, verify:
- Every issue in `01-问题总览与优先级.md` has a detailed entry in the corresponding layer file
- All code examples are accurate (cross-check with actual source)
- The 不建议大动的部分 section is present (avoids unnecessary churn)
- The implementation plan references specific issues from `01`

### Step 5: Commit Report

```bash
git add design-docs/reports/refactor/refactor-{date}-{hash}/
git commit -m "docs: add refactor report refactor-{date}-{hash}"
```

Do **not** push — the caller (plan-write workflow or user) decides when to push.

## Gotchas

- **Always include "不建议大动的部分"**: This is as important as the issues themselves. It prevents unnecessary churn and shows the reviewer that stable parts were evaluated.
- **Code examples must be verifiable**: Include file names and line numbers. The reader should be able to `read_file` and confirm.
- **The implementation plan is the last file**: It depends on all issue analysis. Never write it first.
- **Severity must be justified**: Each 🔴 issue must clearly state the correctness/security impact. 🟡 issues must explain the maintainability risk. Don't inflate severity.
- **Cross-reference between files**: Use Markdown anchors to link from `01` issue table to detail sections in layer files.
- **This report feeds into plan-write**: The refactoring implementation plan (`0N`) informs the task checklist in the subsequent plan documents. Keep tasks concrete enough to be directly adopted.
- **Review methodology must be documented**: The `00-报告概览.md` must list exactly what was done (full code read, security review, etc.), not just "reviewed the code".
