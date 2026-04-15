---
name: code-analysis-report
description: "Generate comprehensive code analysis reports by examining git history, codebase structure, and source code changes. Use when the user asks to write a code analysis report, review recent code changes, produce a codebase snapshot, or document the current state of the project after commits. Covers commit history analysis, backend/frontend architecture review, model layer inspection, API endpoint inventory, deployment configuration, and change tracking. DO NOT USE FOR: bug reports (use bug report workflow), design documents, or code reviews."
license: MIT
compatibility: "c302（C. elegans 神经网络建模框架，OpenWorm 子项目）。Python 项目，Git 仓库，需要 git CLI。"
metadata:
  author: Copilot
  version: "1.0"
allowed-tools: Read Edit Terminal
---

# Code Analysis Report

## When to Use

- User asks to write a code analysis report after code changes
- User asks to document the current state of the codebase
- User wants a snapshot of the project architecture and code structure
- User requests a comparison of changes between two commits
- User needs a comprehensive technical overview for onboarding or review
- New features or refactoring work has been completed and needs documentation

## Report Directory

Create reports under: `design-docs/reports/analysis/`

Directory naming: `analysis-{YYYYMMDD}-{commit-hash-7-chars}`

## Report Structure

Split into 8 + 1 files (never write everything into a single document):

| File | Content |
|------|---------|
| `00-报告概览.md` | Metadata table, report index, version info, key changes summary |
| `01-项目总览与定位.md` | Project positioning, core capabilities, tech stack, version comparison |
| `02-系统架构分析.md` | Architecture diagram, layers, middleware, data flow, dependency map |
| `03-后端服务层分析.md` | All `services/` modules: purpose, key functions, external dependencies |
| `04-后端路由层分析.md` | All `routes/` API endpoints: method, path, function, parameter models |
| `05-数据模型分析.md` | ORM entities + Pydantic parameter models, relationships, schema |
| `06-前端架构分析.md` | Frontend tech stack, directory structure, pages, components, i18n |
| `07-部署与运维.md` | Docker, environment variables, database migration, runtime directories |
| `08-变更追踪与演进.md` | Commit history, key changes detail, code quality evolution, suggestions |

## Workflow

### Step 1: Gather Context

Run these commands to collect data:

```bash
# Latest commit hash (7 chars)
git log --oneline -1

# Commits since last analysis
git log --oneline {last-analysis-hash}..HEAD

# File change statistics (code only)
git diff --shortstat {last-hash}..HEAD -- nds-backend/ nds-frontend/

# Backend and frontend separately
git diff --shortstat {last-hash}..HEAD -- nds-backend/
git diff --shortstat {last-hash}..HEAD -- nds-frontend/
```

Find the previous analysis report directory under `design-docs/reports/analysis/` to determine the last analysis hash.

### Step 2: Read Key Source Files

Read the following files to understand the current codebase state:

**Backend core**: `app.py`, `config.py`, `database.py`, `migrator.py` (if exists), `requirements.txt`, `VERSION`

**Models**: `models/__init__.py`, `models/entities/__init__.py`, `models/parameters/base.py`

**Routes**: `routes/__init__.py` (registration), first 50-100 lines of each route file

**Services**: first 50-100 lines of each service file

**Frontend**: `api.js`, `VERSION`, first 100 lines of key views

**DDL**: `ddl/README.md`, list DDL directory structure

**Tests**: list test directories, read conftest and key test files

### Step 3: Reference Previous Reports

Read the previous analysis report's `00-报告概览.md` and `08-变更追踪与演进.md` to understand:
- What was documented last time
- The baseline for comparison
- Writing style and depth

### Step 4: Write Reports

Write each report file following the structure in the table above.

**Formatting rules**:
- Each file starts with a `# Title` and metadata table (报告时间, 分支, 报告人)
- Use Markdown tables for structured data
- Use code blocks for architecture diagrams (ASCII art)
- Include specific numbers (line counts, file counts, commit counts)
- Cross-reference between files using relative links

**Content rules**:
- Be factual — report what IS, not what SHOULD BE
- Include exact version numbers, dependency versions, and configuration defaults
- List ALL API endpoints with method, path, and parameter model
- Count things precisely (files, lines, endpoints)
- In `08-变更追踪与演进.md`, list every commit in the range with hash, type, and description

### Step 5: Verify Report

After writing, verify:
- [ ] All 9 files are created
- [ ] `00-报告概览.md` links to all other files
- [ ] Commit count matches `git log --oneline | wc -l`
- [ ] Version numbers match actual `VERSION` files
- [ ] File change statistics match `git diff --shortstat`
- [ ] No broken relative links between report files

## Report Metadata Table

Every report file starts with:

```markdown
| 项目 | 内容 |
|------|------|
| **报告时间** | {YYYY-MM-DD} |
| **分支** | `{branch}` (`{hash}`) |
| **报告人** | GitHub Copilot (Claude Opus 4.6) |
```

The `00-报告概览.md` file additionally includes:

```markdown
| **提交 Hash** | `{hash}` |
| **上次分析** | `{prev-hash}` ({prev-date}) |
```

## Gotchas

- **Never write a single monolithic document**: Always split into the 9-file structure. Each file should be independently readable.
- **Commit hash is 7 characters**: Use `git log --oneline` format, not the full 40-char hash.
- **Report the CURRENT state, not the diff**: The report is a snapshot. `08-变更追踪与演进.md` covers diffs, but files 01-07 describe what exists NOW.
- **Count code files separately from docs**: When reporting change statistics, separate code files (`nds-backend/`, `nds-frontend/`) from documentation files.
- **Previous analysis hash matters**: Always identify the last analysis directory to compute the correct diff range.
- **API endpoint count must be exact**: Manually count endpoints from route files. Do not estimate.
- **Always check for new files**: `git diff --stat` shows new files. Don't miss newly added modules (like `migrator.py`).
- **Architecture diagrams use ASCII art**: Don't use Mermaid or other formats — use plain text box diagrams for maximum compatibility.
