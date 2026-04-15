---
name: plan-write
description: Write structured multi-document development plans for new features, refactoring tasks, or architecture changes. Creates numbered markdown files under design-docs/plans/{N}-{title}/ following the project's plan conventions. Use when the user asks to write a plan, design document, or implementation spec before coding. Covers requirements analysis, current-state analysis, architecture design, implementation details, and phased task checklists. DO NOT USE FOR: post-implementation analysis reports (use code-analysis-report skill), bug reports, or quick single-file notes.
license: MIT
compatibility: c302（C. elegans 神经网络建模框架，OpenWorm 子项目）。Python 项目，需要 design-docs/plans/ 目录。
metadata:
  author: Copilot
  version: "1.0"
allowed-tools: Read Edit Terminal
---

# Plan Writing

## When to Use

- User asks to "write a plan" or "write a design doc" for a new feature
- User wants to plan a refactoring, migration, or architecture change before coding
- User provides a numbered requirement (计划N or u-计划N) and asks to document it
- User says "先写计划" or "先写文档，不要写代码"
- User provides a plan markdown file (e.g. `plans/计划21-40/计划32.md`) and says to execute it with plan-first intent

## Plan Directory Convention

**Location**: `design-docs/plans/`

**Directory naming**: `计划{N}-{verb}{object}/`

- `N` = same number used in `plans/计划{range}/计划{N}.md`
- The title must include **both an action verb and the target object** — not just a noun. This makes the plan's purpose self-explanatory at a glance.
- Good examples: `计划32-新增百炼账单模块/`, `计划31-自动数据库升级/`, `计划29-迁移百炼设置/`
- Bad examples: `计划32-账单模块/` (noun only, no verb), `计划32-账单/` (too vague)

**Reference existing plans** before writing: check `design-docs/plans/` for structure patterns.

## Document Structure

Each plan is split into **4–6 numbered files**. The task checklist is always the last file.

### Standard 5-file layout (recommended)

| File | Name Pattern | Purpose |
|---|---|---|
| `01-概述与目标.md` | Overview | Background, goals, scope, what NOT to do |
| `02-现状分析.md` | Current state | Existing code/structure, gap analysis, issue table |
| `03-方案设计.md` | Solution design | Architecture, components, data flow diagrams |
| `04-实施细节.md` | Implementation | File change manifest, code snippets, i18n keys, config details |
| `05-任务清单.md` | Task checklist | Phased checklist with unchecked boxes, see format below |

### When to use 6-file layout

Use 6 files when the design has enough complexity to warrant splitting `03` into two: naming convention / struct design AND interface definitions. See 计划30 as an example.

### When to use 4-file layout

Omit `02-现状分析.md` only when the feature is entirely new with no existing related code.

---

## File Content Guidelines

### `01-概述与目标.md`

- **背景**: Why this is needed. Cite concrete pain points, actual runtime errors, or user friction.
- **目标**: Numbered list of what this plan achieves. Be specific ("support filtering by month" not "improve UX").
- **产品范围** (optional table): Key parameters, API codes, product identifiers.
- **涉及文件** (table): File path | operation (新增/修改/删除) | one-line description.
- **不做什么**: Explicit exclusions to prevent scope creep.

### `02-现状分析.md`

- Show **existing code state** with tables and code blocks (not prose).
- Include a table of existing API endpoints, service functions, or components relevant to this plan.
- End with a **问题汇总** table: Problem | Impact | Severity (🔴高 / 🟡中 / 🟢低).
- Severity emoji convention: 🔴 blocks the feature, 🟡 degrades UX/dev experience, 🟢 cosmetic.

### `03-方案设计.md`

- Start with a **总体架构** ASCII diagram showing the call flow from user action to system response.
- Use `→` for call direction in diagrams.
- For each major component: state what it does, its interface, and key decisions.
- Use comparison tables when proposing approach selection (like 计划31's option table with ✅/❌).

### `04-实施细节.md`

- Start with a **文件变更清单** table (File | Operation | Description).
- For each changed file, provide concrete specifics: function signatures, code snippets, config values, i18n key tables.
- **i18n key tables** must cover: Key | zh-CN value | en-US value.
- Code snippets should be complete enough that an agent can implement without guessing.
- **代码示例必须遵循项目编码规范**：
  - Python 代码必须符合 `python-code-style` 技能要求（load `.github/skills/python-code-style/SKILL.md`）：文件头、reST docstring、类型注解、双引号、强制注释、强制单测
  - 前端代码必须符合 `web-frontend-code-style` 技能要求（load `.github/skills/web-frontend-code-style/SKILL.md`）：文件头、JSDoc、SFC 块顺序、强制注释、强制单测

### `05-任务清单.md` — TASK CHECKLIST FORMAT

```markdown
# 05 - 任务清单

> 执行任务时每完成一项请勾选对应复选框。

---

## 阶段一：{phase name}

- [ ] 1.1 {task description}
  - [ ] 1.1.1 {sub-task}
  - [ ] 1.1.2 {sub-task}
- [ ] 1.2 {task description}

## 阶段二：{phase name}

- [ ] 2.1 {task description}
...

## 阶段X：收尾

- [ ] X.1 代码风格自查（后端符合 SP-CODE-2026-001，前端符合 SP-CODE-2026-002）
- [ ] X.2 Python 注释自查（函数体关键逻辑、条件分支、循环、异常处理必须有行内注释）
- [ ] X.3 前端注释自查（函数体关键逻辑、条件分支、循环、异步操作、watch/生命周期钩子必须有行内注释）
- [ ] X.4 后端单元测试自查（每个新增/修改的 Python 模块必须有对应 tests/test_*.py，覆盖正向+异常用例）
- [ ] X.5 前端单元测试自查（每个新增/修改的前端模块必须有对应 __tests__/*.test.js，覆盖渲染+交互+边界用例）
- [ ] X.6 运行 pytest 和 vitest 确认所有测试通过
- [ ] X.7 版本号 commit 递增
- [ ] X.8 Git 提交并推送
```

**Rules**:
- Tasks are **always unchecked** (`- [ ]`) when writing the plan; only mark `- [x]` during execution
- Always include a final **收尾** phase with style check, version bump, git push
- Phase names describe the deliverable, not the action: "后端 — 服务层" not "编写服务函数"
- Sub-tasks use decimal notation: `1.1`, `1.1.1`, `2.3`

---

## Workflow

### Step 1: Read Existing Plans

Before writing, read at least one similar plan from `design-docs/plans/` to calibrate structure and level of detail.

### Step 2: Identify Plan Number

Check `plans/计划21-40/` and `plans/计划1-20/` to find the plan number the user is referring to. If writing a new plan not yet numbered, ask the user for the number or infer from context.

### Step 3: Research Current State

Before writing `02-现状分析.md`, explore:
- Existing service functions relevant to the feature
- Existing route endpoints
- Frontend views, router config, sidebar nav groups
- Existing i18n keys
- **Verify file extensions**: check whether locale files are `.js` or `.json`, check `api.js` export signature

Use `grep_search` and `read_file` to collect real data — never guess file contents.

### Step 4: Write Files in Order

Write files `01` through `0N` in order. The task checklist (`05` or `0N`) must be written last because it depends on content from all prior files.

### Step 5: Verify Structure

After writing, verify:
- [ ] Directory name matches `计划{N}-{verb}{object}` convention
- [ ] Files are numbered sequentially starting from `01`
- [ ] Task checklist is the last file
- [ ] All tasks in checklist start with `- [ ]` (unchecked)
- [ ] 收尾 phase is included
- [ ] 不做什么 section is present in `01`
- [ ] 现状分析 ends with 问题汇总 table

### Step 6: Review Plan

After writing all files, perform a review pass:

1. **Cross-reference `02` → `04`**: Every problem listed in `02-现状分析.md`'s 问题汇总 table must be addressed in `03-方案设计.md` or `04-实施细节.md`.
2. **Verify code examples in `04`**: Run `grep_search` / `read_file` to confirm that:
   - Referenced functions/routes actually exist (or are clearly marked as new)
   - API call syntax matches `api.js` export style (no `api.get(...)`, no double `/api` prefix)
   - Locale file extensions are `.js` not `.json`
   - Import paths and module names are accurate
3. **Check task completeness in `05`**: Every file listed in `04`'s 文件变更清单 must appear in at least one task. No orphaned file changes.
4. **Confirm scope alignment**: The plan's tasks must not exceed what is stated as in-scope in `01-概述与目标.md`'s 不做什么.

If any issue is found during review, fix it before proceeding to Step 7.

### Step 7: Commit and Push

After writing and reviewing the plan, commit and push all new files:

```bash
git add design-docs/plans/计划{N}-{title}/
git commit -m "docs: add 计划{N} {title} plan"
git push
```

---

## Refactoring Plans — Extended Workflow

When the plan involves **refactoring existing code**, the standard Steps 1–7 are wrapped with a prerequisite phase. The full sequence becomes:

### Step R1: Write Code Analysis Report

Before writing any plan documents, produce a code analysis report using the **code-analysis-report** skill (load `.github/skills/code-analysis-report/SKILL.md` for details).

1. Write the report under `design-docs/reports/analysis/`
2. **Review the report**: cross-check all findings against actual source code. Fix any inaccuracies.
3. Commit but do **not** push:

```bash
git add design-docs/reports/analysis/analysis-{date}-{hash}/
git commit -m "docs: add code analysis report analysis-{date}-{hash}"
```

### Step R2: Write Refactoring Proposal Report

Based on the code analysis report, write a refactoring proposal using the **refactor-report** skill (load `.github/skills/refactor-report/SKILL.md` for details).

1. Write the report under `design-docs/reports/refactor/`
2. **Review the report**: verify every issue's severity, code examples, and proposed fixes against the actual codebase. Fix any inaccuracies.
3. Commit but do **not** push:

```bash
git add design-docs/reports/refactor/refactor-{date}-{hash}/
git commit -m "docs: add refactor report refactor-{date}-{hash}"
```

### Step R3: Write Plan Documents

Only after both reports are written and reviewed, proceed with the standard plan-write workflow (Steps 1–7). The plan's `02-现状分析.md` and `04-实施细节.md` should reference findings from the refactoring proposal report.

At Step 7, commit the plan documents **and push** all accumulated commits (analysis report + refactor report + plan):

```bash
git add design-docs/plans/计划{N}-{title}/
git commit -m "docs: add 计划{N} {title} plan"
git push
```

### Summary: Refactoring Plan Commit Flow

| Phase | Action | Commit | Push |
|-------|--------|--------|------|
| R1 | Code analysis report + review | ✅ | ❌ |
| R2 | Refactoring proposal report + review | ✅ | ❌ |
| R3 | Plan documents (Steps 1–7) | ✅ | ✅ |

---

## Gotchas

- **Never skip 现状分析**: Even if you think you know the current state, read the actual files. Counts of routes, function names, and i18n keys are frequently wrong when guessed.
- **Task checklist last**: Writing the checklist before the design docs leads to vague tasks that require re-reading the plan. Always draft design docs first.
- **Concrete code in 04**: The 实施细节 must be specific enough that another agent (or a human) can implement it without reading the plan. Vague descriptions like "add a function to query bills" are not acceptable — include the function signature and key logic.
- **i18n tables must be bilingual**: Every new i18n key needs both zh-CN and en-US values. Single-language tables will require a second pass.
- **收尾 phase is mandatory**: Plans without a wrap-up phase lead to missing style checks and version bumps.
- **File naming uses Chinese**: Plan docs use Chinese filenames like `01-概述与目标.md`, not English like `01-overview.md`.
- **Unchecked tasks only**: When writing a new plan, ALL task checkboxes must be `- [ ]`. The `- [x]` format is only used after execution (like in 计划31 which is already complete).
- **i18n files are `.js`, not `.json`**: This project stores locale files as `src/locales/zh-CN.js` and `src/locales/en-US.js` with `export default { ... }` syntax. Writing `.json` in plans leads to wrong paths in the task checklist.
- **`api.js` exports a plain async function, not an axios instance**: Calls must be `api('/some/path')` or `api('/some/path?qs=...')`, never `api.get(...)`. Also, `api()` prepends `/api` internally — route paths in call sites must NOT include `/api` prefix (e.g. use `'/bailian/balance'` not `'/api/bailian/balance'`). Verify the `api.js` implementation before writing API call examples in `04-实施细节.md`.
- **Refactoring plans require two prerequisite reports**: If the plan scope includes refactoring, you MUST write a code analysis report and a refactoring proposal report BEFORE writing the plan. Skipping these leads to plans based on assumptions rather than verified code state. See the "Refactoring Plans — Extended Workflow" section.
