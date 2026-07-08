# Skill Standards Quick Reference

A one-page guide for authors, reviewers, and consumers. For full details, follow the links into the standards package.

---

## For authors

### Before writing a skill

- [ ] Read `fundamentals/what-is-a-skill.md` and `fundamentals/when-to-create-a-skill.md`.
- [ ] Confirm a skill is the right shape (not a script, MCP server, prompt, or rule).
- [ ] Choose the type: building block, conductor, wrapper, or multi-layer.
- [ ] Decide the invocation mode: model-invoked or user-invoked.
- [ ] Write a one-sentence intent: *This skill makes the agent more predictable at ___ by enforcing ___.*

### Drafting `SKILL.md`

| Element | Rule of thumb |
|---------|---------------|
| `name` | Lowercase, hyphen-separated, matches directory name. |
| `version` | Optional. Add a semantic version once the skill is shared, consumed, or versioned. |
| `description` | One sentence, front-load the leading word, keep under 1024 chars. |
| `invocation` | Declare `model-invoked` or `user-invoked`. |
| In scope / out of scope | Be explicit about what is and is not the skill's job. |
| Steps or guidelines | One per line; each must be load-bearing. |
| Completion criteria | Every step ends with a checkable condition. |

### Structural checklist

- [ ] `SKILL.md` is required; `README.md` is for non-trivial skills.
- [ ] Optional directories (`references/`, `subagents/`, `scripts/`, `assets/`) are non-empty if present.
- [ ] Deep detail lives in `references/`, not in `SKILL.md`.
- [ ] Worker prompts live in `subagents/` and include role, scope, tools, forbidden actions, and return format.
- [ ] Scripts are deterministic, documented, safe, isolated, and failure-explicit.
- [ ] Language is harness-agnostic and project-agnostic where required.

### Tooling awareness checklist

- [ ] Each capability step names the outcome before choosing a tool.
- [ ] The skill detects available tools (adapters, MCP servers, native binaries, APIs, harness tools) for each capability.
- [ ] The skill selects the best available tool and discloses the choice in output.
- [ ] If a degraded source is used, the skill tells the user what better option was available and gets consent or records the preference.

### Packaging and trust

- [ ] Add `skills.json` once the skill has consumers or external dependencies.
- [ ] Declare dependencies in `requirements` (skills, tools, MCP servers, binaries, environment variables).
- [ ] Never store secrets in `SKILL.md`, references, or config files.

---

## For reviewers

### First-pass questions

1. Does the skill satisfy the fundamentals? (See `fundamentals/evaluation.md`.)
2. Is it the right type? (See `fundamentals/types.md`.)
3. Is the description likely to trigger at the right times?
4. Are the scope boundaries clear and defensible?
5. Are dependencies declared? Are hidden dependencies removed?

### Bloat and consistency

- [ ] Every line is load-bearing. If removing it does not change behavior, remove it.
- [ ] No duplication with other skills or context files.
- [ ] No harness-specific commands or project-specific paths in the portable core.
- [ ] No references to the local agent harness or active skills from the current library used as examples.
- [ ] Completion criteria are checkable, not vague.

### Safety and governance

- [ ] Destructive actions require confirmation.
- [ ] The skill fails closed when a required capability is missing.
- [ ] Agent-authored skills pass staging.
- [ ] No secrets or tokens in files.
- [ ] Scripts do not ask for user input; the skill collects input and passes it.

### Tooling awareness review

- [ ] The skill is capability-first: it names outcomes before choosing tools.
- [ ] It checks for better tools outside its own adapter set before invoking adapters.
- [ ] It discloses which tool fulfilled each capability and which alternatives were available.
- [ ] Degraded sources are accepted only with user consent or a recorded preference.

### Evaluation

- [ ] Trigger evals exist for model-invoked skills (10 should-trigger, 10 should-not-trigger).
- [ ] Behavioral evals compare with-skill and baseline runs.
- [ ] Discipline skills have pressure tests against the documented failure pattern.
- [ ] Composable skills have composition tests.

---

## For consumers

### What a skill is

A skill is a reusable unit of process guidance that shapes how an agent behaves for a specific task. It is not a script, prompt, or plugin — though it may contain any of those.

### How to use a skill

1. **Install it** into `{project-root}/.agents/skills/` or `~/.agents/skills/`.
2. **Declare it** in your project's `skills.json` or let the harness discover it.
3. **Invoke it** by name (user-invoked) or by describing the task (model-invoked).
4. **Read `README.md`** for human-oriented usage notes.

### When to reach for a skill

| Situation | What to use |
|-----------|-------------|
| Repeated, judgment-shaped task | Skill |
| Always-on baseline convention | Context file (`AGENTS.md`, `CONVENTIONS.md`, `.cursorrules`) |
| One-off deterministic operation | Script or MCP server |
| Transient stance change | Mode (if your harness supports it) |
| Multi-skill workflow | Conductor skill |
| Narrow reusable capability | Building-block skill |
| Human-facing prompt/confirmation | Wrapper skill |

### Troubleshooting

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| Skill does not fire | Weak description | Rewrite description with leading words and trigger phrases. |
| Skill fires too often | Description too broad | Add should-not-trigger cases and narrow the description. |
| Skill is too long | Detail in `SKILL.md` | Move deep detail to `references/`. |
| Skill ignores its own rules | Vague completion criteria | Make stopping conditions checkable. |
| Skill makes unsafe changes | Missing confirmation gate | Add explicit confirmation for destructive actions. |
| Skill fails on a new project | Hardcoded paths | Use detection, config, or ask the user. |

---

## Key documents

| Need | Read |
|------|------|
| Philosophy | `../PHILOSOPHY.md` |
| Architecture | `../ARCHITECTURE.md` |
| Portability | `../PORTABILITY.md` |
| Format | `FORMAT.md` |
| Package | `PACKAGE.md` |
| Governance | `GOVERNANCE.md` |
| Evaluation | `EVALUATION.md` |
| Trigger evals | `TRIGGER_EVALS.md` |
| Migration | `MIGRATION.md` |
| Glossary | `GLOSSARY.md` |

---

## One-line pattern guide

| Pattern | Use when | See |
|---------|----------|-----|
| Building block | Narrow, reusable capability | `patterns/building-block.md` |
| Conductor | Coordination through phases | `patterns/conductor.md` |
| Wrapper | Human-facing adaptation | `patterns/wrapper.md` |
| Discipline skill | Enforce a rule against rationalization | `patterns/discipline-skill.md` |
| Context-file | Always-on baseline guidance | `patterns/context-file.md` |
| Mode | Transient behavior switch | `patterns/mode.md` |
| Conductor/implementer split | Separate reasoning from execution | `patterns/conductor-implementer-split.md` |
| Global / pluggable | Work in any project | `patterns/global-pluggable.md` |
| Configurable | Per-project preferences | `patterns/configurable.md` |
| Initialization | First-run setup | `patterns/initialization.md` |
| Stateful | Survive context compaction | `patterns/stateful.md` |
| Context reports | Structured skill outputs | `patterns/context-reports.md` |
| Versioning | Consumers depend on behavior | `patterns/versioning.md` |
