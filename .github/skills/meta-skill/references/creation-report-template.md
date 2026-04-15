# Creation Report Template

Use this template to output the result of each skill creation or optimization run.

---

##  Skill Creation Report: `{skill-name}`

**Date**: `{YYYY-MM-DD}`  
**Operation**: `{Created / Updated / Self-Bootstrapped}`  
**Agent**: `{agent name}`

---

### Requirements Summary

| Dimension | Content |
|-----------|---------|
| Target Task | {What problem does this skill solve?} |
| Trigger Scenarios | {List primary trigger scenarios} |
| Input | {What inputs are needed?} |
| Output | {What outputs are expected?} |
| Knowledge Sources | {What docs / cases / specs were referenced?} |

---

### Generated File Listing

```
{skill-name}/
 SKILL.md                     {line count} lines
 references/
    {file-1}.md              {purpose}
    {file-2}.md              {purpose}
 scripts/                     {present / none}
 assets/                      {present / none}
 evals/                       {present / none}
```

---

### Metadata Summary

| Field | Value |
|-------|-------|
| `name` | `{skill-name}` |
| `description` | {description field content} |
| `license` | {license} |
| `compatibility` | {compatibility} |
| `version` | {version} |

---

### Quality Verification Results

| Category | Passed | Total | Result |
|----------|--------|-------|--------|
|  Format (MUST) | {n}/{total} | {total} |  /  |
|  Content (SHOULD) | {n}/{total} | {total} |  /  /  |
|  Structure (NIT) | {n}/{total} | {total} |  /  |

**Overall Assessment**: `{ Pass /  Needs Improvement /  Fail}`

---

### Failed Items (if any)

| # | Level | Check Item | Issue | Suggested Fix |
|---|-------|-----------|-------|---------------|
| {#} | {//} | {check item name} | {specific issue} | {how to fix} |

---

### Recommendations

- {Suggestion 1, e.g., collect real-world Gotchas after first use and iterate}
- {Suggestion 2, e.g., create evals/ test cases to measure description trigger accuracy}
- {Suggestion 3, e.g., clarify boundary with related skill X}