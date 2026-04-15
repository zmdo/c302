---
name: meta-skill
description: Guide an AI agent through the full lifecycle of creating, validating, and optimizing Agent Skills. Use when the user needs to create a new skill directory and SKILL.md, design references or scripts, optimize an existing skill's description or structure, validate a skill against the specification, or bootstrap the meta-skill itself. Covers requirements analysis, directory scaffolding, content authoring, quality verification, and self-bootstrapping.
license: MIT
compatibility: Any AI agent that supports the Agent Skills specification (agentskills/agentskills). No project-specific dependencies.
metadata:
  author: meta-skill
  version: "2.0"
allowed-tools: Read Edit
---

# Meta-Skill: The Skill for Creating Skills

## When to Use

Activate this skill when:

- The user asks to create a brand-new skill from scratch
- The user wants to package a workflow or domain task into a reusable skill
- The user needs to optimize an existing skill's `description`, structure, or references
- The user requests a format review or quality assessment of a skill before publishing
- The user wants to batch-validate all skills in a directory
- The user asks to validate this meta-skill against itself (self-bootstrap)

## Core Principles

Before creating any skill, internalize these principles:

1. **Ground in real expertise**  Extract skills from real tasks, project artifacts, or domain documents. Never generate generic instructions from thin air.
2. **Write only what the agent doesn't know**  Project-specific conventions, domain-specific procedures, non-obvious edge cases, specific tools/APIs. Skip general concepts.
3. **One skill, one job**  Design like a function: encapsulate one coherent unit of work. Not too narrow (forces multiple skills per task), not too broad (hard to activate precisely).
4. **Progressive disclosure**  Keep `SKILL.md` body  500 lines /  5,000 tokens. Move detailed references to `references/`. Tell the agent *when* to load each file, not just *where*.
5. **Defaults over menus**  Provide one recommended approach + a fallback. Don't present equivalent options as equals.

> For the complete Agent Skills specification, load `references/agent-skills-spec.md`.
> For best practices details, load `references/best-practices-checklist.md`.

## Creation Workflow

### Step 1: Requirements Analysis

Confirm the following with the user (do not skip any):

| Dimension | Question |
|-----------|----------|
| **Target task** | What problem does this skill solve? What would the agent get wrong without it? |
| **Trigger scenarios** | What words or phrases would the user say to trigger this skill? |
| **Input** | What does the skill need? Files, code, config, user descriptions? |
| **Output** | What should it produce? Reports, modified files, code, config? |
| **Boundaries** | What does it NOT do? Any overlap with existing skills? |
| **Environment** | What tools, packages, APIs, or network access does it need? |
| **Knowledge source** | Any existing docs, runbooks, code reviews, or incident reports to draw from? |

**If requirements are vague**: Generate a requirements summary from the user's description, ask for confirmation, then proceed to Step 2.

### Step 2: Design Directory Structure

Based on Step 1, determine the layout:

```
{skill-name}/
 SKILL.md            # Required: metadata + core instructions
 references/         # Optional: reference docs (loaded on demand)
    {topic-1}.md
    {topic-2}.md
 scripts/            # Optional: executable code
    {script}.py
 assets/             # Optional: templates, schemas, resources
    {template}.md
 evals/              # Optional: test cases
     evals.json
```

**Naming rules (load `references/naming-rules.md` for full validation rules):**

- `skill-name`: lowercase letters + digits + hyphens, 164 chars
- Must not start/end with hyphen, no consecutive hyphens
- Directory name must exactly match the `name` field in SKILL.md

**Decision tree  when to add optional directories:**

| Condition | Action |
|-----------|--------|
| Core instructions > 500 lines | Split detailed content into `references/` |
| Skill needs reusable executable code | Create `scripts/` |
| Output requires a fixed format | Place templates in `assets/` |
| Need systematic quality evaluation | Create `evals/` with test cases |

### Step 3: Write YAML Frontmatter

Fill in each field using this template:

```yaml
---
name: {skill-name}
description: {what it does} + {when to use it}. Max 1024 chars.
license: {license, e.g. MIT, Apache-2.0, Proprietary}
compatibility: {environment requirements, if any. Omit if none.}
metadata:
  author: {author or org}
  version: "1.0"
allowed-tools: {space-separated tool list, e.g. Read Edit Bash}
---
```

**`description` field  the most critical field (determines activation accuracy):**

1. First half: **what it does** (start with a verb, list 23 core capabilities)
2. Second half: **when to use it** (start with "Use when", list trigger conditions)
3. Include **specific keywords** users would mention
4. Avoid being too broad (false triggers) or too narrow (missed triggers)

```yaml
#  Good
description: Review code against project standards and output graded issue reports. Use when the user submits code, requests a code review, or asks whether code follows conventions.

#  Bad
description: Checks code.
```

> For systematic description optimization, load `references/description-optimization.md`.

### Step 4: Write SKILL.md Body

Use this standard structure (not all sections are mandatory  include what fits):

```markdown
# {Skill Title}

## When to Use
List trigger conditions (58 bullet points)

## {Core Workflow}
### Step 1: ...
### Step 2: ...
### Step 3: ...

## Output Format
Provide an output template (concrete structures beat prose)

## Gotchas
List environment-specific traps, non-obvious facts, common mistakes
```

**Section-by-section guidance:**

#### "When to Use" section

- List 58 specific trigger scenarios using `- ` bullets
- Describe from the user's perspective ("User requests", "User needs")
- Cover main scenarios + edge cases

#### Core workflow section

- Use `### Step N: {name}` structure with consecutive numbering
- Each step: explain **what** to do and **how** to do it
- **Prescriptive** for fragile operations (order-sensitive, format-strict, side-effects)
- **Flexible** for tolerant operations (explain "why", let the agent decide "how")
- Include **validation loops**: do  validate  fix  re-validate

#### "Output Format" section

- Provide **output templates**  more reliable than prose descriptions
- Short templates: inline in SKILL.md
- Long templates: in `assets/`, referenced with explicit load instructions

#### "Gotchas" section

- **Highest-value content**: what the agent would get wrong without this skill
- Each gotcha: specific, actionable, not generic ("handle errors appropriately" )
- When the agent makes a mistake during real execution, add the correction here

### Step 5: Write references/ Documents

**When to split into references/:**

- Content > 50 lines that's only needed during a specific step
- Detailed validation rules, field tables, API format specs
- Self-contained technical references

**Rules:**

- One topic per file (e.g. `naming-rules.md`, `report-template.md`)
- First line of each file: one sentence explaining its purpose
- In SKILL.md, **tell the agent when to load**:

```markdown
For detailed validation rules, load:
- `references/field-spec.md`  when processing field validation

<!--  Bad: vague reference -->
See the references/ directory for details.
```

### Step 6: Quality Verification

After writing, run the full checklist (load `references/quality-checklist.md` for the complete list):

**Format checks (MUST  all must pass):**

- [ ] `name`: lowercase+digits+hyphens,  64 chars, matches directory name
- [ ] `description`: non-empty,  1024 chars, contains function + trigger
- [ ] YAML frontmatter parses correctly
- [ ] Markdown body is non-empty

**Content checks (SHOULD  aim for  8/10):**

- [ ] SKILL.md body  500 lines
- [ ] Contains a "When to Use" section
- [ ] Contains at least one Step N in the workflow
- [ ] Contains a "Gotchas" section (even if only 12 items)
- [ ] All `references/` files have explicit load instructions in SKILL.md
- [ ] No general knowledge the agent already knows
- [ ] Description keywords cover primary trigger scenarios

**Structure checks (NIT):**

- [ ] No empty files in the directory
- [ ] Each references/ file has a purpose statement on line 1
- [ ] No dead links or references to nonexistent files
- [ ] No orphaned files in references/ (not referenced by SKILL.md)

### Step 7: Output Creation Report

Use `references/creation-report-template.md` to produce the final report.

## Special Scenarios

### Scenario A: Vague Requirements

```
If the user says "create a skill for X" without details:
  1. Analyze what task type X involves
  2. List 35 possible trigger scenarios
  3. Generate a requirements summary, ask the user to confirm/amend
  4. After confirmation, proceed to Step 2
```

### Scenario B: Overlap with Existing Skills

```
If the new skill's scope overlaps with an existing skill:
  1. Read both descriptions, analyze the overlap
  2. Propose one of:
     a. Draw clear boundaries  add exclusion clauses to both "When to Use" sections
     b. Merge into one skill (if they're really one unit of work)
     c. Extract shared content into references/ that both skills load
  3. Confirm with the user
```

### Scenario C: Skills That Run Scripts

```
If the skill needs to run executable code:
  1. Prefer one-off commands (uvx, npx, etc.)  avoid creating scripts/
  2. If scripts/ is needed:
     - Scripts must be self-contained, or clearly state dependencies at the top
     - Include helpful error messages
     - Handle edge cases gracefully
     - In SKILL.md, call with exact commands: `python scripts/validate.py {input}`
  3. If the agent reinvents the same logic across runs  extract into a script
```

### Scenario D: Strict Output Format Requirements

```
When the skill's output must match a specific format:
  1. Create a template file in assets/
  2. In SKILL.md, provide load instructions and usage notes
  3. Add a "format validation" step in the workflow (do  validate  fix  re-validate)
```

### Scenario E: Optimizing an Existing Skill

```
When the user wants to improve an existing skill:
  1. Read the current SKILL.md, run Step 6 quality verification
  2. Identify issues (format/content/structure), sort by severity
  3. Fix each issue
  4. Pay special attention to:
     - Is description precise (not too broad / not too narrow)?
     - Do Gotchas cover errors found during real execution?
     - Are there orphaned files in references/?
     - Is the body over 500 lines (needs splitting)?
```

### Scenario F: Self-Bootstrapping (Validating meta-skill with itself)

```
When the user asks to validate meta-skill against itself:
  1. Load references/quality-checklist.md
  2. Run every check item against the meta-skill's own SKILL.md and references/
  3. Report findings using references/creation-report-template.md
  4. Fix any issues found
  5. Re-run verification to confirm all issues are resolved
  This proves the meta-skill is self-consistent and can bootstrap itself.
```

## Gotchas

- **Never generate a skill from thin air**: If the user provides no domain knowledge source (docs, cases, specs), prompt them to supply material first. Otherwise the skill will be generic filler.
- **`description` is the only activation gate**: The agent decides whether to activate a skill based solely on `name` + `description`. A perfect body is useless if the description doesn't match user prompts.
- **references/ files need explicit load triggers**: Writing "see references/" is useless. Write "when X condition, load `references/X.md`".
- **SKILL.md is an instruction manual, not documentation**: It should say "do X, then Y"  not "X is a concept that means"
- **One skill should not do two unrelated things**: If the `description` needs "and" to connect two completely different capabilities, split into two skills.
- **Gotchas are higher-value than the main workflow**: The workflow tells the agent the happy path; Gotchas tell it where it will fall  the latter has higher marginal value.
- **`name` field is always ASCII**: Only lowercase letters, digits, and hyphens. No CJK, no spaces, no underscores. Use the `# Title` heading for human-readable names.
- **Self-bootstrap is the ultimate test**: If meta-skill cannot pass its own quality checklist, it is not ready to validate other skills.