# Naming Rules Reference

This document defines validation rules for the skill directory name and the `name` frontmatter field.

---

## `name` Field Rules

| Rule | Description | Example |
|------|-------------|---------|
| Length | 164 characters | `code-review` (11 chars)  |
| Allowed chars | Lowercase `a-z`, digits `0-9`, hyphens `-` only | `pdf-processing`  |
| No uppercase | Uppercase letters are not allowed | `PDF-Processing`  |
| Boundaries | Must not start or end with a hyphen | `-pdf` , `pdf-`  |
| No consecutive hyphens | `--` is not allowed | `pdf--processing`  |
| Directory match | Must exactly match the parent directory name | Dir `code-review/`  `name: code-review` |

## Valid vs Invalid Examples

| Name | Valid? | Reason |
|------|--------|--------|
| `code-review` |  | Lowercase + hyphens |
| `doc-normalize` |  | Lowercase + hyphens |
| `meta-skill` |  | Lowercase + hyphens |
| `my-skill-2` |  | Includes digit |
| `Code-Review` |  | Contains uppercase |
| `-review` |  | Starts with hyphen |
| `review-` |  | Ends with hyphen |
| `code--review` |  | Consecutive hyphens |
| `my skill` |  | Contains space |
| `my_skill` |  | Contains underscore |

## CJK and Non-ASCII

- The `name` field does **not** support CJK characters, spaces, or underscores
- Use the `# Title` heading inside SKILL.md body for human-readable names in any language
- The `description` field supports any Unicode text