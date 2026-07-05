# Skill fundamentals (condensed)

> **This is a condensed fallback.** The canonical skill fundamentals live in `docs/skill-standards/fundamentals/`. If that directory is available, prefer it and treat this file as a degraded copy for projects that ship without the full standards wiki.

## What a skill is

A skill is the smallest load-bearing shape that makes an agent reliably do the right thing for a specific domain. It is a contract between the author and the agent, not a script, prompt, or manual.

## What a skill is not

- A script.
- An MCP server.
- A prompt template.
- A rule or context file.
- Application code.

A skill may contain scripts, calls to MCP servers, or references to context files, but its primary purpose is to shape the agent's behavior predictably.

## The three skill types

| Type | Use when | Example |
|---|---|---|
| **Building block** | The skill does one narrow, reusable thing and is consumed by other skills or the model. | `find-skills`, `audit-skill` |
| **Conductor** | The skill coordinates multiple tools, skills, or subagents through phases to reach a larger goal. | `write-a-skill`, `debrief` |
| **Wrapper** | The skill adapts another skill for human interaction, adding prompts, confirmation, or presentation. | Human-facing concierge over a building block |

A skill may participate in more than one layer if it has a clear primary role.

## Identity and frontmatter

Every `SKILL.md` must declare:

- `name`: lowercase, hyphen-separated, matches directory name.
- `description`: one sentence, ≤ 1024 chars, front-loads the leading word or domain, lists distinct triggers.
- `version`: top-level SemVer once the skill is shared or consumed.
- `invocation`: `model-invoked` or `user-invoked`.
- `metadata`: author, tags, and provenance if distributed or agent-authored.

## Scope

A skill must have:

- One core objective.
- Explicit in-scope items.
- Explicit out-of-scope items.
- Clear boundaries between what it does and what it does not do.

## Form and style

- **Load-bearing minimalism.** Every line must earn its place. If removing it does not change behavior, remove it.
- **Completion criteria.** Every step ends with a checkable condition.
- **Leading words.** Anchor behavior in compact concepts the model already understands.
- **Negation pairs.** Pair every "do not X" with a positive "do Y."
- **Harness-agnostic language.** No hardcoded harness commands, tool names, or vendor APIs in the portable core.
- **Project-agnostic language.** No hardcoded project paths or conventions; use detection or config.
- **Progressive disclosure.** Keep the top of `SKILL.md` clean; push deep detail into `references/`.

## Structure

- `SKILL.md` is required.
- `README.md` is required for non-trivial skills.
- `references/` holds disclosed detail.
- `subagents/` holds worker prompts.
- `scripts/` holds deterministic helpers.
- `assets/` holds static resources.
- Optional directories should be non-empty if present.

## Security

- No secrets in files.
- Destructive actions require explicit confirmation.
- Fail closed when a required capability is missing.
- Prefer read-only inspection in untrusted projects.

## Dependencies

Declare all dependencies:

- Other skills.
- Native tools.
- MCP servers.
- External binaries.
- Environment variables.

Do not hide dependencies.

## Evaluation

- Model-invoked skills need trigger evals (10 should-trigger, 10 should-not-trigger).
- Behavioral evals compare with-skill vs. baseline output.
- Composable skills need composition tests.
- Discipline skills need pressure tests against the documented failure pattern.

## Portability

- The portable core is `SKILL.md` + optional sibling directories.
- Global skills detect the environment or ask the user.
- Degrade gracefully when the harness does not support a feature.

## Canonical source

For the full, maintained version of these fundamentals, see `docs/skill-standards/fundamentals/`:

- `what-is-a-skill.md`
- `types.md`
- `structure.md`
- `form-and-style.md`
- `common-mistakes.md`
- `evaluation.md`
- `lifecycle.md`
- `security.md`
- `when-to-create-a-skill.md`
- `failure-recovery.md`

Update this fallback only after the canonical docs change, and only to the minimum needed for self-contained operation.
