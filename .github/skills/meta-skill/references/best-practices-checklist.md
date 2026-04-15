# Best Practices Checklist

This document summarizes skill authoring best practices, for reference during Step 4 (writing the body).

---

## Content Principles

### 1. Ground in Real Expertise

| Source | Description |
|--------|-------------|
| Real task extraction | Complete a real task, then extract the reusable pattern |
| Project artifact synthesis | Internal docs, runbooks, API specs, code review comments, incident reports |
| Version control history | Patches and fixes reveal recurring patterns |

**Anti-pattern**: Generating a skill with no domain context  produces generic filler like "handle errors appropriately" and "follow best practices."

### 2. Write Only What the Agent Doesn't Know

-  Project-specific conventions and patterns
-  Domain-specific procedures
-  Non-obvious edge cases
-  Specific tools, APIs, or commands to use
-  General concept explanations (what is a PDF, how HTTP works)
-  Programming language syntax tutorials

### 3. Calibrate Specificity to Fragility

| Task characteristic | Instruction style |
|--------------------|-------------------|
| Multiple valid approaches, high tolerance | **Flexible**: Explain "why", let the agent decide "how" |
| Order-sensitive, format-strict, has side-effects | **Prescriptive**: Give exact steps and commands |

### 4. Provide Defaults, Not Menus

```markdown
<!--  Bad: too many equivalent options -->
You can use A, B, C, or D for this task...

<!--  Good: clear default + escape hatch -->
Use A for this task.
If you encounter X, switch to B instead.
```

## Structural Patterns

### Validation Loop

```markdown
1. Perform the operation
2. Run validation: `python scripts/validate.py output/`
3. If validation fails:
   - Review the error message
   - Fix the issue
   - Re-run validation
4. Only proceed when validation passes
```

### Plan-Validate-Execute (for batch/destructive operations)

```markdown
1. Generate an operation plan (intermediate file)
2. Validate the plan against the source of truth
3. Execute only after validation passes
```

### Progressive Loading

```markdown
<!-- Tell the agent WHEN to load, not just WHERE -->
For detailed validation rules, load:
- `references/field-spec.md`  when processing field validation
- `references/error-codes.md`  when encountering API errors
```

### Gotchas Section Pattern

```markdown
## Gotchas
- {Specific, actionable trap  not "be careful with errors"}
- {Each entry corresponds to a concrete mistake the agent would make}
- {Collected from corrections made during real execution}
```

## Context Budget

| Layer | Content | Token budget |
|-------|---------|-------------|
| Metadata | `name` + `description` | ~100 tokens |
| Instructions | Full SKILL.md body |  5,000 tokens (~500 lines) |
| Resources | references/ + scripts/ | Loaded on demand, no hard limit |

**When over 500 lines  splitting strategy:**

1. Move detailed field tables / validation rules to `references/`
2. Move output templates to `assets/`
3. Move script logic to `scripts/`
4. Keep only the core workflow steps in SKILL.md