---
name: plan-execute
description: Execute development plans from design-docs/plans/ by plan number. Use when the user says "执行计划N", "execute plan N", or asks to implement a numbered plan. Reads the plan's task checklist, implements each task, checks off completed items, reviews for bugs, writes bug reports, fixes issues, and commits+pushes when done. DO NOT USE FOR: writing new plans (use plan-write skill), general coding without a plan, or bug reports outside plan execution context.
license: MIT
compatibility: c302（C. elegans 神经网络建模框架，OpenWorm 子项目）。Python 项目，需要 design-docs/plans/ 下的编号计划目录。
metadata:
  author: Copilot
  version: "1.0"
allowed-tools: Read Edit Terminal
---

# Plan Execution

## When to Use

- User says "执行计划N" or "execute plan N" (N is a number)
- User asks to implement a specific numbered plan
- User references a plan directory and says to start working on it
- User says "继续执行计划N" to resume a partially completed plan

## Workflow

### Step 1: Locate Plan

1. Find the plan directory under `design-docs/plans/` that starts with `计划{N}-`
2. Read all files in the plan directory, starting from `01-概述与目标.md`
3. Identify the task checklist file (always the last numbered file, typically `05-任务清单.md`)

If the directory is not found, inform the user and stop.

### Step 2: Read and Understand

Read all plan documents in order:
1. `01-概述与目标.md` — scope and goals
2. `02-现状分析.md` — current state
3. `03-方案设计.md` — architecture and design decisions
4. `04-实施细节.md` — concrete implementation details (code snippets, file changes, i18n keys)
5. `05-任务清单.md` — task checklist to execute

Parse the task checklist into an ordered list of actionable items.

### Step 3: Execute Tasks

For each task in the checklist:

1. **Mark in-progress**: Use the todo list tool to track the current task
2. **Implement**: Write code, modify config, add i18n keys — following the details in `04-实施细节.md`
3. **Check off**: After completing a task, update the checklist file — change `- [ ]` to `- [x]` for that task
4. **Commit checkpoint**: After completing each **phase** (阶段), commit:

```bash
git add -A
git commit -m "feat: 计划{N} — 完成{phase name}"
```

Do **not** push during execution — push only at the very end (Step 7).

**Execution rules:**
- Follow `04-实施细节.md` code snippets closely — they have been reviewed for correctness
- When the plan specifies a function signature, use it exactly
- When adding i18n keys, add to **both** `zh-CN.js` and `en-US.js`
- Run the code style skills (python-code-style / web-frontend-code-style) for new files if the 收尾 phase requires it
- Use the version-management skill for version bumps if required by the 收尾 phase

### Step 4: Post-Execution Review

After all tasks are checked off, perform a thorough review:

1. **Functional check**: Verify the implementation matches the plan's goals from `01-概述与目标.md`
2. **Code review**: Read all changed files and check for:
   - Syntax errors or typos
   - Missing imports
   - Incorrect API call patterns (e.g. `api.get()` instead of `api()`)
   - Wrong file paths or extensions
   - Missing i18n keys in either language
   - Inconsistent naming
3. **Scope check**: Ensure nothing was implemented beyond what the plan specified (check `不做什么`)
4. **Runtime verification** (if backend/frontend are running): Start the services and verify key endpoints respond correctly

If all checks pass, proceed to Step 7 (Commit and Push).

If bugs are found, proceed to Step 5.

### Step 5: Write Bug Report

When bugs are discovered during review:

1. Get the current commit hash: `git rev-parse --short HEAD`
2. Get the current date
3. Create a bug report directory: `design-docs/reports/bugs/bug-{YYYYMMDD}-{short-hash}/`
4. Write the bug report following the **bug-report** skill conventions (load `.github/skills/bug-report/SKILL.md` for details)
5. Commit the bug report:

```bash
git add design-docs/reports/bugs/bug-{date}-{hash}/
git commit -m "docs: add bug report bug-{date}-{hash}"
```

Do **not** push yet.

### Step 6: Fix Bugs and Re-Review

1. Fix each bug documented in the report
2. Commit the fixes:

```bash
git add -A
git commit -m "fix: 计划{N} — 修复 bug-{date}-{hash}"
```

3. **Re-review**: Repeat Step 4 on the fixed code
4. If new bugs are found, repeat Steps 5–6 (write new bug report → fix → re-review)
5. Continue until the review passes cleanly with no bugs

### Step 7: Commit and Push

Once all reviews pass:

```bash
git push
```

Notify the user that the plan has been fully executed, reviewed, and pushed.

## Task Checklist Conventions

The checklist file uses this format:

```markdown
## 阶段一：{phase name}

- [ ] 1.1 {task}
  - [ ] 1.1.1 {sub-task}
- [ ] 1.2 {task}
```

**Check-off rules:**
- Mark `- [x]` only after the task is fully implemented and verified
- Mark sub-tasks individually, then mark the parent when all sub-tasks are done
- Commit after each **phase** is complete, not after each individual task

## Gotchas

- **Do not push until Step 7**: All intermediate commits (task phases, bug reports, bug fixes) are local only. Push once at the end.
- **`04-实施细节.md` is the source of truth for implementation**: Don't deviate from the code snippets in the plan unless they contain obvious errors. If you find a plan error, fix it via the bug report process.
- **Check off tasks in the actual markdown file**: The checklist is in `design-docs/plans/计划{N}-{title}/05-任务清单.md` (or the last numbered file). Edit the file to change `- [ ]` to `- [x]`.
- **Bug reports go to `design-docs/reports/bugs/`**: Not in the plan directory.
- **Re-review is mandatory after fixing bugs**: Never assume a fix is correct — verify by re-running Step 4.
- **The 收尾 phase is the final task phase**: It includes style checks, version bumps, and git operations. Execute it like any other phase.
- **Resume support**: If the user says "继续执行", read the checklist to find the first unchecked task and resume from there.
