# Agent Skills Specification Reference

This document is a self-contained copy of the core Agent Skills specification,
included so that meta-skill does not depend on external file paths.

Source: [agentskills/agentskills](https://github.com/agentskills/agentskills)

---

## Directory Structure

A skill is a directory containing, at minimum, a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

## SKILL.md Format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Frontmatter Fields

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | **Yes** | Max 64 chars. Lowercase `a-z`, digits `0-9`, hyphens `-` only. Must not start/end with `-`. No consecutive `--`. Must match parent directory name. |
| `description` | **Yes** | Max 1024 chars. Non-empty. Describes what the skill does and when to use it. |
| `license` | No | License name or reference to a bundled license file. |
| `compatibility` | No | Max 500 chars. Environment requirements (intended product, system packages, network access, etc.). |
| `metadata` | No | Arbitrary key-value mapping for additional metadata. |
| `allowed-tools` | No | Space-delimited list of pre-approved tools. (Experimental) |

### Minimal Example

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

### Full Example

```yaml
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: Apache-2.0
compatibility: Requires pdfplumber and pytesseract installed
metadata:
  author: example-org
  version: "1.0"
allowed-tools: Bash(python:*) Read
---
```

## Progressive Disclosure

Skills use a three-layer context management strategy:

| Layer | Content | When loaded | Token budget |
|-------|---------|-------------|-------------|
| Metadata | `name` + `description` | Session start (all skills) | ~100 tokens/skill |
| Instructions | Full SKILL.md body | On activation (task match) | Recommended ≤ 5,000 tokens |
| Resources | scripts/, references/, assets/ | On demand (referenced in instructions) | Varies |

**Best practices:**
- Keep SKILL.md body ≤ 500 lines
- Move detailed references to separate files
- In instructions, tell the agent *when* to load each file (not just *where*)

## Discovery Paths

Agents scan these directories for skills at session start:

| Scope | Path | Notes |
|-------|------|-------|
| Project | `<project>/.<client>/skills/` | Client-specific |
| Project | `<project>/.agents/skills/` | Cross-client interop |
| User | `~/.<client>/skills/` | Client-specific |
| User | `~/.agents/skills/` | Cross-client interop |

Project-level skills override user-level skills when names conflict.

## Activation Methods

1. **File read**: Agent reads the SKILL.md path from the catalog directly
2. **Dedicated tool**: Register an `activate_skill` tool that accepts a skill name and returns content
3. **Explicit user trigger**: Slash commands (`/skill-name`) or mentions (`@skill-name`)

## Recommended Body Sections

- **Step-by-step instructions**: How to execute the task
- **Gotchas**: Environment-specific traps and non-obvious facts
- **Input/output examples**: Concrete formats
- **Output format templates**: Templates beat prose descriptions
- **Multi-step checklists**: Help the agent track progress

## Validation

Use the official reference implementation to validate a skill:

```bash
skills-ref validate ./my-skill
```
