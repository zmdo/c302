# Quality Checklist

Use this checklist during Step 6 (Quality Verification) to verify a newly created or updated skill.

---

##  Format Checks (MUST  all must pass)

| # | Check Item | Rule | Status |
|---|-----------|------|--------|
| F1 | `name` field exists | Non-empty,  64 characters |  |
| F2 | `name` valid characters | Only lowercase letters, digits, hyphens |  |
| F3 | `name` boundary rules | No leading/trailing hyphens, no consecutive hyphens |  |
| F4 | `name` matches directory | Parent directory name == `name` field value |  |
| F5 | `description` field exists | Non-empty,  1024 characters |  |
| F6 | YAML syntax valid | Frontmatter can be parsed without errors |  |
| F7 | Markdown body non-empty | Content exists after frontmatter |  |

---

##  Content Checks (SHOULD  aim for all)

| # | Check Item | Rule | Status |
|---|-----------|------|--------|
| C1 | Body line count |  500 lines (split to references/ if over) |  |
| C2 | "When to Use" section | Exists, lists  3 trigger scenarios |  |
| C3 | Workflow steps | Contains at least 1 `Step N` structure |  |
| C4 | "Gotchas" section | Exists, contains at least 1 specific actionable warning |  |
| C5 | References linked | All files in references/ are explicitly referenced in SKILL.md |  |
| C6 | No common knowledge | Does not explain concepts the agent already knows |  |
| C7 | Description keywords | Description covers key trigger-scenario keywords |  |
| C8 | Description format | Contains both capability summary and trigger conditions |  |
| C9 | No vague directives | Does not contain "be careful", "follow best practices", etc. |  |
| C10 | Defaults over menus | When multiple approaches exist, recommends one default |  |

---

##  Structure Checks (NIT)

| # | Check Item | Rule | Status |
|---|-----------|------|--------|
| S1 | No empty files | No 0-byte files in the skill directory |  |
| S2 | Reference headers | Each references/ file starts with a purpose statement |  |
| S3 | No dead links | All file paths referenced in SKILL.md actually exist |  |
| S4 | No orphan files | No files in references/ that are never referenced in SKILL.md |  |
| S5 | Metadata complete | Includes `author`, `version`, `agent` keys |  |
| S6 | License field | License is declared |  |

---

## Scoring

| Result | Condition |
|--------|-----------|
|  **Pass** | All F checks pass +  8/10 C checks pass |
|  **Needs Improvement** | All F checks pass + 57/10 C checks pass |
|  **Fail** | Any F check fails, or < 5/10 C checks pass |