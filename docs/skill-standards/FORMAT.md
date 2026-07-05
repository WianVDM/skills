# Skill Format

The **portable core** of any skill is a `SKILL.md` file plus a small set of optional sibling directories. This document specifies that core so that a skill can be read, understood, and loaded across different agent harnesses.

Everything beyond this core — native harness discovery, tool scoping, MCP server wiring, sandbox configuration, and subagent envelope — is **harness-specific envelope**. The standard defines the boundary between the portable core and the envelope, not the envelope itself.

---

## The `SKILL.md` file

`SKILL.md` is the only required file in a skill. It has two parts:

1. **YAML frontmatter** — identity, routing, metadata, and harness hints.
2. **Markdown body** — the contract, steps, guidelines, and references that shape agent behavior.

A harness that does not parse YAML frontmatter can fall back to the markdown body as plain guidance and extract identity from the file path or a separate index.

### Example

```markdown
---
name: review-ui
version: 1.0.0
metadata:
  author: design-team
  tags: [ui, accessibility, design-system]
invocation: model-invoked
---

# Review UI code

Review UI code for design-system compliance, accessibility, and responsive behavior.

## In scope

- Check component usage against the design system.
- Flag accessibility issues (contrast, focus, labels, ARIA).
- Note responsive or layout risks.

## Out of scope

- Do not fix the code unless asked.
- Do not review business logic or backend concerns.

## Steps

1. Identify the framework and design system from the project.
2. Read the relevant component files.
3. Evaluate against the in-scope checklist.
4. Summarize findings and recommendations.
```

---

## Frontmatter schema

### Required fields

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `name` | string | Required. Lowercase letters, digits, and hyphens only. Must match the directory name. Max 128 chars. | The stable identifier for the skill. |
| `description` | string | Required. Min 1, max 1024 characters. | One-sentence routing surface. Tells the agent when to load the skill. |
| `version` | string | Semantic version (`MAJOR.MINOR.PATCH[-prerelease][+build]`). Required once the skill is shared, consumed, or versioned. | Version of the skill. |

`version` is optional for a personal, experimental skill that no one else depends on. Once a skill is shared, consumed, or versioned, it must have a version.

### Recommended fields

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `metadata` | object | See `metadata` object below. | Author, tags, provenance, verification level, and other non-behavior metadata. |
| `invocation` | string | Enum: `model-invoked`, `user-invoked`. | Determines how the skill is reached. |

#### `metadata` object

| Key | Type | Constraints | Purpose |
|-----|------|-------------|---------|
| `author` | string | Max 256 chars. | Human or team responsible for the skill. |
| `tags` | string[] | Unique. Each tag: lowercase, digits, hyphens; max 64 chars. | Keywords for cataloging and discovery. |
| `verification_level` | string | Enum: `unverified`, `declared`, `tested`, `formal`. | See `GOVERNANCE.md`. |
| `provenance` | object | See `GOVERNANCE.md`. | `authored_by`, `generated_by`, `origin`, `reviewed_by`, `reviewed_at`, `parent_session`. |

### Harness hints

Harnesses may support additional frontmatter fields for their own tool scoping or loading behavior. These are **harness hints**, not part of the portable core. Examples:

- `allowed-tools` / `disallowed-tools` — tool scoping supported by some harnesses. Array of non-empty strings.
- `disable-model-invocation: true` — equivalent to `invocation: user-invoked` in some harnesses. Boolean.
- `globs` or `paths` — file scoping supported by some harnesses. Array of non-empty strings.

A portable skill should not rely on harness hints for its core behavior. If a hint is essential, the skill should degrade gracefully when the hint is ignored. When both `invocation` and `disable-model-invocation` are present, they must agree: `disable-model-invocation: true` is incompatible with `invocation: model-invoked`.

### Unknown fields

Harnesses should ignore unknown top-level frontmatter fields rather than fail. This is the observed behavior in Codex and Hermes source code and the intended behavior for forward compatibility. The agentskills.io reference validator is stricter, but runtime behavior is unspecified.

- Codex loader: https://github.com/openai/codex/blob/98d28aab54ed86714901b6619400598598876dd0/codex-rs/core-skills/src/loader.rs#L46-L53
- Hermes skill utils: https://github.com/NousResearch/hermes-agent/blob/e670d9cdd6697d24c4b170ac0ecdf6d344dc96a7/agent/skill_utils.py#L123-L149

## Formal frontmatter schema

A JSON Schema for the portable frontmatter surface is maintained at `schemas/skill-frontmatter.schema.json`. The schema declares required fields, value constraints, harness hints, and forward-compatibility rules. Harnesses may use it for validation, but should still ignore unknown fields at runtime.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["name", "description"],
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "minLength": 1,
      "maxLength": 128
    },
    "description": {
      "type": "string",
      "minLength": 1,
      "maxLength": 1024
    },
    "version": {
      "type": "string",
      "pattern": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-([a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)*))?(?:\\+([a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)*))?$"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "author": { "type": "string", "maxLength": 256 },
        "tags": {
          "type": "array",
          "items": { "type": "string", "pattern": "^[a-z0-9-]+$", "maxLength": 64 },
          "uniqueItems": true
        },
        "verification_level": {
          "type": "string",
          "enum": ["unverified", "declared", "tested", "formal"]
        },
        "provenance": {
          "type": "object",
          "properties": {
            "authored_by": { "type": "string", "enum": ["human", "agent", "mixed"] },
            "generated_by": { "type": "string" },
            "origin": { "type": "string", "enum": ["foreground", "background_review", "import"] },
            "reviewed_by": { "type": "string" },
            "reviewed_at": { "type": "string", "format": "date-time" },
            "parent_session": { "type": "string" }
          }
        }
      }
    },
    "invocation": {
      "type": "string",
      "enum": ["model-invoked", "user-invoked"]
    },
    "allowed-tools": { "type": "array", "items": { "type": "string", "minLength": 1 } },
    "disallowed-tools": { "type": "array", "items": { "type": "string", "minLength": 1 } },
    "disable-model-invocation": { "type": "boolean" },
    "globs": { "type": "array", "items": { "type": "string", "minLength": 1 } },
    "paths": { "type": "array", "items": { "type": "string", "minLength": 1 } }
  },
  "additionalProperties": true
}
```

---

## The `description` field

The `description` is the most important field in `SKILL.md`. It is the **context pointer** that causes the agent to load the skill. A weak description makes the skill invisible; a strong description front-loads the leading words and domain signals that the agent should match against.

A good description:

- States what the skill does.
- Front-loads the **leading word** or domain.
- Lists one trigger per distinct branch. Synonyms that rename the same branch are duplication — collapse them.
- Includes a reach clause for when another skill needs it, if applicable.

Example:

```yaml
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
```

Weak example:

```yaml
description: Helps with UI reviews.
```

Keep the description under 1024 characters when possible. Some harnesses impose context budgets on descriptions.

See `fundamentals/structure.md` for trigger evals and description optimization.

---

## The `invocation` field

A skill is either **model-invoked** or **user-invoked**. The choice trades two loads:

- **Model-invoked**: the description stays in the agent's context, so the skill can fire autonomously and other skills can reach it. This pays **context load** on every turn. A model-invoked skill is still reachable by the user typing its name.
- **User-invoked**: the description is not kept in the agent's context for routing. Only the user can invoke it by name. This pays **cognitive load** — the user must remember it exists. No other skill can reach it.

Choose model-invocation only when the agent or another skill must reach the skill on its own. If it only ever fires by hand, make it user-invoked and pay no context load.

When both `invocation` and `disable-model-invocation` are present, they must agree. `disable-model-invocation: true` is equivalent to `invocation: user-invoked`.

---

## The markdown body

The body is the actual guidance. It should answer:

- What does this skill do?
- When should it run?
- What is the core contract?
- What is in and out of scope?
- Where does detailed reference live?

The body can take one of three forms:

1. **Instruction-heavy** — ordered steps for sequential processes.
2. **Guideline-heavy** — principles and rules for domain-shaped judgment.
3. **Hybrid** — steps for the sequence and guidelines for the decisions inside each step.

See `fundamentals/form-and-style.md` for choosing the right form and writing strong completion criteria.

---

## Sibling directories

These directories are optional. Include them only when they add value.

### `references/`

Deep detail: schemas, edge cases, examples, config patterns, context report schemas, and dependency declarations. Every reference file should be reachable from `SKILL.md` or another reference file.

Common files:

- `references/REFERENCE.md` — general reference.
- `references/CONFIG_PATTERN.md` — config schema.
- `references/CONTEXT_REPORTS.md` — report schemas and contracts.
- `references/SUBAGENTS.md` — worker contracts.
- `references/EXAMPLES.md` — sample prompts and expected outputs.
- `references/DEPENDENCIES.md` — required skills, tools, MCP servers, environment variables.
- `references/VERSIONING.md` — versioning policy and migration paths.

### `subagents/`

Worker personas for delegation. Each worker prompt must state role, scope, allowed tools, forbidden actions, and return format. Workers should be shorter than the parent skill and should not duplicate shared context.

### `scripts/`

Deterministic helpers. Scripts are documented, safe, isolated, and failure-explicit. Prefer read-only inspection unless the script is explicitly designed to mutate state. Scripts should not ask the user for input; the skill should collect input and pass it as arguments or environment variables.

### `assets/`

Templates and static resources. Especially useful for non-coding skills that ship fonts, images, sample files, or document templates.

---

## Conventional layout

```text
skill-name/
├── SKILL.md                 # required: identity and contract
├── README.md                # for human maintainers
├── references/              # disclosed detail
├── subagents/               # worker personas
├── scripts/                 # deterministic helpers
└── assets/                  # templates and static resources
```

Principles:

- `SKILL.md` is required.
- Include `README.md` for non-trivial skills.
- Optional directories should contain content; do not include empty ones.
- Prefer a flat structure; avoid deep nesting.
- Reference links must resolve.

---

## Harness-agnostic and project-agnostic language

The portable core must not assume a specific agent harness, tool name, slash command, or vendor API.

| Project-specific | Global |
|------------------|--------|
| Run `/ticket OC-1234`. | Invoke the ticket-research skill for ticket OC-1234. |
| Call the `Agent` tool. | Spawn a focused worker. |
| Use `git status`. | Check the current working state. |
| Open Jira ticket PROJ-123. | Open the configured issue tracker for ticket PROJ-123. |
| Run `npm test`. | Run the project's test command. |

The skill should detect the environment, consult config, or ask the user.

---

## Plain-markdown export mode

For harnesses that do not parse YAML frontmatter, a skill can be exported in plain-markdown mode:

- The YAML frontmatter is stripped or summarized in a header comment.
- Identity and routing are provided by an external index (e.g., `skills.json`) or by the file path.
- The body remains the primary guidance.

This is the recommended degradation path for minimal harnesses like Aider. See [docs/PORTABILITY.md](../PORTABILITY.md) for the full degradation model.

---

## Research basis

- The portable core format is a common denominator across Claude Code, Cursor, Codex, Aider, and Hermes. Each uses a markdown file with a routing description and a body of guidance.
- The agentskills.io specification defines a minimal frontmatter surface: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. https://agentskills.io/specification
- Codex source confirms that unknown top-level frontmatter fields are silently ignored, supporting forward compatibility. https://github.com/openai/codex/blob/98d28aab54ed86714901b6619400598598876dd0/codex-rs/core-skills/src/loader.rs#L46-L53
- Hermes source confirms that frontmatter is parsed as a YAML dict and only known keys are extracted. https://github.com/NousResearch/hermes-agent/blob/e670d9cdd6697d24c4b170ac0ecdf6d344dc96a7/agent/skill_utils.py#L123-L149
- The description-as-routing-surface and context-load framing are supported by Claude Code's skills documentation and the context-stack analysis across harnesses. https://code.claude.com/docs/en/skills
- The plain-markdown export and minimal-harness degradation path are informed by Aider's `/run` and `--read` surfaces and the aider-skills third-party injector. https://aider.chat/docs/

Many harness-specific details (exact trigger thresholds, rule-vs-skill precedence, file-scoping behavior) are **limited** and are documented as limitations rather than core format requirements.
