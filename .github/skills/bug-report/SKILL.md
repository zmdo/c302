---
name: bug-report
description: Write structured multi-file bug analysis reports under design-docs/reports/bugs/. Use when the user reports a bug, asks to document a bug, or when the plan-execute skill discovers bugs during review. Covers symptom documentation, root cause analysis, code-level analysis, and fix recommendations. DO NOT USE FOR: fixing bugs (handle separately after the report), feature plans (use plan-write skill), or code reviews.
license: MIT
compatibility: c302（C. elegans 神经网络建模框架，OpenWorm 子项目）。Python 项目，需要 design-docs/reports/bugs/ 目录。
metadata:
  author: Copilot
  version: "1.0"
allowed-tools: Read Edit Terminal
---

# Bug Report

## When to Use

- User reports a bug and asks to document it
- Plan execution review discovers bugs that need formal reporting
- User asks to write a bug analysis report
- Agent finds runtime errors during code review or testing

## Directory Convention

**Location**: `design-docs/reports/bugs/`

**Directory naming**: `bug-{YYYYMMDD}-{short-hash}`

- `YYYYMMDD` = report date (e.g. `20260331`)
- `short-hash` = the 7-char short hash of the **most recent commit** at the time of the bug report (use `git rev-parse --short HEAD`)
- Example: `bug-20260331-2a28c1d`, `bug-20260331-f1279cd`

## Document Structure

Bug reports are split into numbered files. The exact layout depends on how many bugs are reported.

### Single Bug — standard 5-file layout

| File | Purpose |
|---|---|
| `00-概述.md` | Overview: summary table, report structure, key conclusions |
| `01-现象与复现.md` | Symptoms, environment, reproduction steps, affected scope |
| `02-根因分析.md` | Causal chain (ASCII diagram), root cause, trigger conditions |
| `03-代码分析.md` | Problem code snippets with analysis tables, call chain diagram |
| `04-修复建议.md` | Fix proposals table (P0/P1/P2), code-level fix details |

### Multiple Bugs — grouped layout

When a single report covers multiple bugs:

| File | Purpose |
|---|---|
| `00-概述.md` | Overview with **Bug 清单** table listing all bugs |
| `01-BUG1-{brief-name}.md` | Full analysis of Bug 1 (symptoms + root cause + code analysis) |
| `02-BUG2-{brief-name}.md` | Full analysis of Bug 2 |
| `...` | One file per bug |
| `0N-修复建议.md` | Combined fix proposals for all bugs |

## File Content Guidelines

### `00-概述.md`

Start with a descriptive `# Bug 分析报告：{brief description}` heading.

**Required metadata table:**

```markdown
| 项目 | 内容 |
|------|------|
| **报告日期** | {YYYY-MM-DD} |
| **基准提交** | `{short-hash}`（`{branch}` 分支） |
| **严重等级** | {P0/P1/P2} — {impact summary} |
| **影响范围** | {affected pages/modules} |
| **错误信息** | `{exact error message}` |
```

For multiple bugs, replace **严重等级/影响范围/错误信息** with a **Bug 清单** table:

```markdown
| 编号 | 错误信息 | 严重等级 | 影响页面 |
|------|---------|---------|---------|
| BUG-1 | `{error}` | P1 | {pages} |
```

**Severity levels:**
- **P0** — 功能完全不可用（all pages broken, data loss）
- **P1** — 多页面/核心功能不可用
- **P2** — 用户体验缺陷（degraded but functional）

Always include:
- **问题摘要**: 2–3 sentence plain-language summary
- **报告结构**: Table linking to all files
- **关键结论**: Numbered list of direct cause, indirect cause, trigger conditions

### `01-现象与复现.md` (Single Bug)

- **错误现象**: Exact error message in code block
- **运行环境**: Table of component | port | status
- **复现步骤**: Numbered steps with exact commands
- **影响范围**: Table of page/component | endpoint | trigger method
- **验证测试**: Show commands that prove the issue (working vs failing cases)

### `02-根因分析.md` (Single Bug)

- **因果链**: ASCII diagram using `│`, `▼`, `→` showing the full chain from trigger to symptom
- **根因定位**: Tables showing config mismatches or code flaws
- **触发条件**: Numbered list of conditions that must all be true
- **引入时间点**: When each root cause was introduced

### `03-代码分析.md` (Single Bug)

- For **each involved file**: show the problem code block, then an analysis table:

```markdown
| 问题 | 说明 |
|------|------|
| **{issue name}** | {explanation} |
```

- End with **调用链路全景**: ASCII diagram showing the full call path

### `04-修复建议.md`

- **修复方案总览**: Table with priority | fix | type | affected files
- For each fix: provide concrete code with **改动说明** bullets
- Order by priority: P0 → P1 → P2

## Workflow

### Step 1: Gather Context

Before writing, collect:
- Exact error messages (from terminal, browser console, or logs)
- Git commit hash: `git rev-parse --short HEAD`
- Current date
- Relevant source files (use `read_file` / `grep_search`)

### Step 2: Reproduce and Verify

If possible, reproduce the bug to confirm the issue. Document working vs failing cases.

### Step 3: Analyze Root Cause

Trace the full causal chain from trigger to symptom. Identify:
- Direct cause (what immediately triggers the error)
- Indirect cause (why the direct cause exists)
- Trigger conditions (what must be true for the bug to manifest)

### Step 4: Write Report Files

Write files in order `00` → `01` → `02` → `03` → `04`.

### Step 5: Commit Report

```bash
git add design-docs/reports/bugs/bug-{date}-{hash}/
git commit -m "docs: add bug report bug-{date}-{hash}"
```

Do **not** push — the caller (plan-execute or user) decides when to push.

## Gotchas

- **Always use real error messages**: Copy-paste from terminal/console. Never paraphrase or guess error text.
- **ASCII diagrams for causal chains**: Text-based `│▼→` diagrams, not Mermaid or images. They render everywhere.
- **P0/P1/P2 severity is mandatory**: Every bug must have a severity level. When in doubt, use P1.
- **Code blocks must be verifiable**: Include file paths and enough context that a reader can `read_file` and confirm.
- **Commit hash comes from `git rev-parse --short HEAD`**: Don't guess or use a placeholder.
