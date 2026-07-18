# Skill Format

## At a glance

**Layer:** universal fundamentals. **Mode:** reference.

This document specifies the **portable core** of a skill: the `SKILL.md` file with YAML frontmatter and a markdown body, plus optional sibling directories. It defines the required frontmatter fields, the `description` as routing surface, invocation modes, and the conventional layout.

**Read this if:** you are writing a `SKILL.md` or building a harness loader.

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
| `invocation` | string | Enum: `model-invoked`, `user-invoked`. Required. | Determines how the skill is reached and whether it pays context load or cognitive load. |

These three fields are the entire portable core. Versioning, once a skill has consumers, lives at the package level — see [`package.md`](./package.md) and [`../patterns/versioning.md`](../patterns/versioning.md).

### Harness hints

Harnesses may support additional frontmatter fields for their own tool scoping, loading behavior, or installation convenience. These are **harness hints**, not part of the portable core. Examples:

- `allowed-tools` / `disallowed-tools` — tool scoping supported by some harnesses. Array of non-empty strings.
- `disable-model-invocation: true` — equivalent to `invocation: user-invoked` in some harnesses. Boolean.
- `globs` or `paths` — file scoping supported by some harnesses. Array of non-empty strings.
- `depends` — skill names used by the Vercel `skills` CLI to install dependencies automatically. Array of non-empty strings. Not a portable dependency declaration; use `skills.json` for that.

A portable skill should not rely on harness hints for its core behavior. If a hint is essential, the skill should degrade gracefully when the hint is ignored. When both `invocation` and `disable-model-invocation` are present, they must agree: `disable-model-invocation: true` is incompatible with `invocation: model-invoked`.

### Unknown fields

Harnesses should ignore unknown top-level frontmatter fields rather than fail. This is the observed behavior in Codex and Hermes source code and the intended behavior for forward compatibility. The agentskills.io reference validator is stricter, but runtime behavior is unspecified.

- Codex loader: https://github.com/openai/codex/blob/98d28aab54ed86714901b6619400598598876dd0/codex-rs/core-skills/src/loader.rs#L46-L53
- Hermes skill utils: https://github.com/NousResearch/hermes-agent/blob/e670d9cdd6697d24c4b170ac0ecdf6d344dc96a7/agent/skill_utils.py#L123-L149

## Formal frontmatter schema

A JSON Schema for the portable frontmatter surface is maintained at [`../schemas/skill-frontmatter.schema.json`](../schemas/skill-frontmatter.schema.json). The schema declares required fields, value constraints, harness hints, and forward-compatibility rules. Harnesses may use it for validation, but should still ignore unknown fields at runtime.

---

## The `description` field

The `description` is the most important field in `SKILL.md`. It is the **context pointer** that causes the agent to load the skill. A weak description makes the skill invisible; a strong description front-loads the leading words and domain signals that the agent should match against.

The canonical shape:

```text
<What the skill does, leading word or domain first>. Use when <trigger 1>, <trigger 2>, <trigger 3>. <Reach clause if other skills consume it>.
```

A good description:

- States what the skill does.
- Front-loads the **leading word** or domain. The first 10–15 words decide routing.
- Lists one trigger per distinct branch. Synonyms that rename the same branch are duplication — collapse them.
- Adds a **reach clause** when another skill needs it: a sentence naming the consuming situation, so a conductor or building block can route to the skill without the user naming it. "Lets adapters resolve tokens without exposing secrets" is a reach clause; "Use when asked to review UI" is a user trigger.

Example:

```yaml
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
```

Example with a reach clause:

```yaml
description: Resolve secure tokens from environment variables, MCP config files, or a one-time user prompt. Use when an adapter needs credentials. Lets skills reference a token without exposing the secret value.
```

Weak example:

```yaml
description: Helps with UI reviews.
```

Keep the description under 1024 characters. The schema enforces this cap, and some harnesses impose shorter budgets — see [`context-budget.md`](../fundamentals/core/context-budget.md).

Test descriptions with trigger evals in [`trigger-evals.md`](../guides/trigger-evals.md). Craft guidance — leading words, pruning, the no-op test — lives in [`../fundamentals/core/form-and-style/`](../fundamentals/core/form-and-style/).

---

## The `invocation` field

`invocation` is a **required** field. A skill is either **model-invoked** (the agent and other skills can reach it, at the cost of context load on every turn) or **user-invoked** (reachable only by name, at the cost of cognitive load). See [`../fundamentals/core/structure/frontmatter.md`](../fundamentals/core/structure/frontmatter.md) for the full trade-off and how to choose.

Always declare `invocation` explicitly. If a harness encounters a `SKILL.md` without one, it may fall back to a default (often model-invoked), but that behavior is harness-specific and not guaranteed by this standard.

When both `invocation` and `disable-model-invocation` are present, they must agree. `disable-model-invocation: true` is equivalent to `invocation: user-invoked`.

---

## The markdown body

The body is the actual guidance: what the skill does, when it runs, the contract, the scope, and where detailed reference lives. It can be instruction-heavy, guideline-heavy, or a hybrid of the two.

See [`../fundamentals/core/structure/skill-md.md`](../fundamentals/core/structure/skill-md.md) for the body's job and [`../fundamentals/core/form-and-style/`](../fundamentals/core/form-and-style/) for choosing the form and writing strong completion criteria.

---

## Sibling directories

These directories are optional. Include them only when they add value, and never empty.

| Directory | Purpose |
|-----------|---------|
| `references/` | Deep detail: schemas, edge cases, examples, config patterns, dependency declarations. Every reference file is reachable from `SKILL.md` or another reference file. |
| `subagents/` | Worker personas for delegation. Each worker prompt states role, scope, allowed tools, forbidden actions, and return format. |
| `scripts/` | Deterministic helpers: documented, safe, isolated, failure-explicit. |
| `assets/` | Templates and static resources: fonts, images, sample files, document templates. |

See [`../fundamentals/core/structure/optional-directories.md`](../fundamentals/core/structure/optional-directories.md) for the rules each directory must satisfy.

Common `references/` files:

- `references/REFERENCE.md` — general reference.
- `references/CONFIG_PATTERN.md` — config schema.
- `references/CONTEXT_REPORTS.md` — report schemas and contracts.
- `references/SUBAGENTS.md` — worker contracts.
- `references/EXAMPLES.md` — sample prompts and expected outputs.
- `references/DEPENDENCIES.md` — required skills, tools, MCP servers, environment variables.
- `references/CHAINLOG.md` — chainlog classification for producers, consumers, or both. Absent means `neither`.
- `references/VERSIONING.md` — versioning policy and migration paths.

### File naming

Filename case signals how a file is reached.

- **UPPERCASE.md** — the file is found *by name*, not by link. A harness, tool, audit, or convention looks for it directly: `SKILL.md`, `README.md`, and the canonical contract docs in `references/` (`DEPENDENCIES.md`, `INTERFACE.md`, `CHAINLOG.md`). The name is part of the API.
- **lowercase-hyphenated.md** — the file is reached *through* a link from another document: documentation trees, templates, and fixtures (e.g., `chainlog-template-producer.md`). The link text is the interface; the filename is an implementation detail.
- **Data and config files** follow their ecosystem convention: `config.yaml`, `skills.json`, `evals.json`, `*.schema.json`.

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

The portable core must not assume a specific agent harness, tool name, slash command, or vendor API. Write "spawn a focused worker," not "call the `Agent` tool"; write "run the project's test command," not "`npm test`". The skill should detect the environment, consult config, or ask the user.

See [`../fundamentals/core/structure/harness-agnostic-language.md`](../fundamentals/core/structure/harness-agnostic-language.md) for the full translation table.

---

## Plain-markdown export mode

For harnesses that do not parse YAML frontmatter, a skill can be exported in plain-markdown mode:

- The YAML frontmatter is stripped or summarized in a header comment.
- Identity and routing are provided by an external index (e.g., `skills.json`) or by the file path.
- The body remains the primary guidance.

This is the recommended degradation path for minimal harnesses like Aider. See [patterns/portability.md](../patterns/portability.md) for the full degradation model.

---

## Research basis

- The portable core format is a common denominator across Claude Code, Cursor, Codex, Aider, and Hermes. Each uses a markdown file with a routing description and a body of guidance.
- The agentskills.io specification defines a minimal frontmatter surface: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. https://agentskills.io/specification
- Codex source confirms that unknown top-level frontmatter fields are silently ignored, supporting forward compatibility. https://github.com/openai/codex/blob/98d28aab54ed86714901b6619400598598876dd0/codex-rs/core-skills/src/loader.rs#L46-L53
- Hermes source confirms that frontmatter is parsed as a YAML dict and only known keys are extracted. https://github.com/NousResearch/hermes-agent/blob/e670d9cdd6697d24c4b170ac0ecdf6d344dc96a7/agent/skill_utils.py#L123-L149
- The description-as-routing-surface and context-load framing are supported by Claude Code's skills documentation and the context-stack analysis across harnesses. https://code.claude.com/docs/en/skills
- The plain-markdown export and minimal-harness degradation path are informed by Aider's `/run` and `--read` surfaces and the aider-skills third-party injector. https://aider.chat/docs/

Many harness-specific details (exact trigger thresholds, rule-vs-skill precedence, file-scoping behavior) are **limited** and are documented as limitations rather than core format requirements.
