# Description Field Optimization Guide

This document guides how to write and optimize the `description` frontmatter field.
The `description` is the **sole basis** for an agent to decide whether to activate a skill.
Its quality directly determines activation accuracy.

---

## Formula

```
description = {what it does (capabilities)} + {when to use it (trigger conditions)}
```

- **First half**: Start with a verb, describe 23 core capabilities
- **Second half**: Start with "Use when", list typical trigger scenarios

## Good Examples

```yaml
# Clear capabilities + explicit triggers + rich keywords
description: >-
  Review code against project standards and output graded issue reports.
  Use when the user submits code, requests a code review, or asks whether
  code follows conventions. Supports Python and TypeScript.

# Scope + multiple triggers + specific keywords
description: >-
  Check and fix design document formatting issues, and sync the document
  overview index. Use when the user needs to check document format, fill
  in headers, generate or fix table of contents, or restructure a doc.
```

## Bad Examples

```yaml
#  Too short, no trigger conditions
description: Checks code.

#  Too broad, will false-trigger on everything
description: Helps users process various files and tasks.

#  Too narrow, misses scenarios
description: Checks whether Python files use 4-space indentation.

#  Only capabilities, no trigger conditions
description: Supports PDF text extraction, form filling, and file merging.
```

## Keyword Strategy

Embed **specific vocabulary** that users would mention:

| Domain | Suggested keywords |
|--------|-------------------|
| Code review | code review, lint, standards, convention, PR review |
| Document format | document format, header, table of contents, normalize |
| PDF processing | PDF, form, text extraction, merge, OCR |
| Data analysis | CSV, chart, visualization, report, statistics |

## Avoiding False Triggers

When multiple skills share overlapping keywords:

1. Add **exclusion clauses** to each description ("Does not handle X")
2. Use more specific keywords instead of generic terms
3. State the boundary explicitly at the end of the description

## Length Guidelines

- Maximum: 1024 characters (hard limit)
- Recommended: 150400 characters
- Too short  imprecise matching; Too long  excessive token consumption during discovery

## Iterative Optimization

1. Write an initial description
2. Prepare 510 realistic user prompts (include positives that should trigger and negatives that should not)
3. Simulate agent matching:
   - Do all positive prompts match?  Add missing keywords
   - Do any negative prompts match?  Remove overly broad terms or add exclusions
4. Adjust and re-test until accuracy is satisfactory