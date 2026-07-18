# Building block

**Layer:** proposed architecture. **Mode:** rule.

A building block is a narrow, reusable skill with a clear interface and structured output. Other skills — usually conductors — consume it to compose larger workflows without duplicating capability.

There are two common shapes of building block:

1. **Tool building block** — a functional, narrow capability. It performs one task and returns structured output. Examples: `find-skills`, `install-skill`, `verify-skill`, `summarize-text`.
2. **Vocabulary building block** — shared reference, language, or conventions that other skills embed. Examples: `design-vocabulary`, `config-pattern`, `context-reports`.

Both are building blocks because they are narrow, with a clear interface, and composable. A building block is defined by its **interface and composability**, not by its invocation mode. A building block can be model-invoked or user-invoked; what matters is whether other skills can consume it through a stable contract.

---

## Tool building blocks

A tool building block does one narrow thing and returns output that another skill can act on.

**Characteristics**

- One core objective.
- A clear input and output contract.
- Structured output (markdown, JSON, or a context report) that consumers can parse or display.
- No presentation logic, no workflow coordination, no heavy state management.
- Explicit dependency declarations.

**When to use**

- The task is well-bounded.
- The capability could be reused by conductors or other skills.
- The output should be structured and predictable.

**Examples**

- `find-skills` — discovers available skills and returns structured results.
- `install-skill` — installs a skill given a name or source.
- `verify-skill` — checks a skill against the standards and returns a report.
- `summarize-text` — compacts text into a specified format.

**Common mistake**

Adding presentation logic, workflow phases, or heavy state management that belongs in a wrapper or conductor. A building block should stay narrow.

---

## Vocabulary building blocks

A vocabulary building block provides shared language, reference, or conventions that other skills consume. It does not perform a workflow itself.

**Characteristics**

- Shared meaning across multiple skills.
- Precise definitions, principles, or conventions.
- Often embedded into a conductor or multi-layer skill rather than invoked as a standalone step.
- No workflow; it is reference, not process.

**When to extract one**

- The same concept appears in three or more skills.
- The same convention is explained in multiple `SKILL.md` files.
- A domain vocabulary is needed by multiple skills, including conductors and multi-layer skills.

**Examples**

- `design-vocabulary` — shared terms for deep modules, seams, and public interfaces.
- `config-pattern` — shared conventions for loading and validating project config (see [configurable.md][configurable]).
- `context-reports` — report schema and freshness rules.
- `chainlog` — shared append-only observation ledger (see [chainlog.md](./chainlog.md)).

---

## Shared references

Cross-cutting conventions should live in one place. Do not copy the same explanation into every skill.

| Instead of | Use |
|------------|-----|
| Each skill has its own `references/CONFIG_PATTERN.md`. | One shared `config-pattern` skill or reference file. |
| Each skill explains the context directory layout. | One shared `context-reports` skill or reference file. |
| Each skill defines the worker return contract. | One shared `worker-contract` skill or reference file. |

This is the clean-architecture instinct applied to skills: extract what is shared, keep what is specific.

---

## Dependency declaration

A skill must declare what it needs from other skills and the environment.

Declare:

- Other skills it expects to be available.
- External tools, APIs, MCP servers, or extensions it requires.
- Specific scripts, files, or conventions it relies on.
- Environment variables or secure stores it references.
- Reports from other skills it consumes.

Dependencies are not bad. Hidden dependencies are.

The canonical human-readable place is `references/DEPENDENCIES.md`. The canonical machine-readable place is `skills.json` (`skill_dependencies` for the structured taxonomy, or `requirements.skills` for the flat compatibility surface). See [PACKAGE.md][package] for the package-level dependency model.

Example `references/DEPENDENCIES.md`:

```markdown
# Dependencies

## Required skills

- `ticket-research` — provides initial ticket context.
- `state-capture` — captures initial UI or system state.

## Consumed reports

- `.agents/context/ticket-research/{key}.md`
- `.agents/context/state-capture/{key}-{branch}.md`

## Required tools

- Read files in the project.
- Search the codebase.

## Required environment

- `ISSUE_TRACKER` — identifies the configured issue tracker.
- `PROJECT_KEY` — identifies the project or repo.
```

---

## Composition over monoliths

Complex behavior should emerge from simple skills composed together, not from one skill that does everything. A building block is the unit of that composition. When a skill grows past one narrow capability, extract a new building block rather than inflate the original.

---

## Composition patterns

### Conductor consumes building blocks

A conductor skill uses building-block skills for shared vocabulary and focused work.

**Example:** a project-orchestration skill consumes ticket-research and state-capture reports, and uses a shared design-vocabulary skill when evaluating implementation options.

### Wrapper consumes building blocks

A wrapper skill adapts one or more building blocks for human interaction.

**Example:** a find-and-install concierge uses the `find-skills` and `install-skill` building blocks, adding prompts and confirmation for the user.

### Multi-layer skills embed building blocks

A skill whose primary role is a conductor or wrapper may still embed building-block reference directly into its workflow.

**Example:** a test-driven-development skill uses a red-green-refactor workflow and embeds principles from a shared design-vocabulary skill for interface design.

### Building block stands alone

A building block skill does not depend on other skills. It may be invoked by conductors or wrappers, but it does not invoke them.

### External reference

Some reference is not a skill at all. It is a plain file — `CONTEXT.md`, an ADR, a glossary — that any skill can point at. This is the only shared home two user-invoked skills can use, since neither has a description and neither can invoke the other.

---

## Avoiding duplication

Duplication is not just repeated text. It is repeated meaning. Two symptoms:

1. The same guidance exists in two `SKILL.md` files.
2. The same concept is defined in two places with different wording.

**Cures**

- Extract shared meaning into a building-block skill.
- Use context pointers instead of inline repetition.
- Use a leading word to anchor a concept once and reference it elsewhere.

---

## Colocation by default

A capability should live inside the skill that owns it unless extraction is justified by reuse. This is the default starting point for every skill design decision.

**Colocate when:**
- The capability is only used by one skill.
- The capability changes when the owning skill changes.
- The capability is provider-specific or workflow-specific.
- The capability does not need its own identity, version, or routing surface.

**Extract when:**
- The capability is cross-cutting (e.g., token resolution, context reports, worker contracts).
- Two or more skills currently consume it.
- It has a stable, narrow interface that changes more slowly than its consumers.
- It solves a generic-domain problem rather than a workflow-specific problem.

Extraction is not justified by "it might be useful someday" or "it is nice and self-contained." A skill that exists only to serve one other skill is usually a submodule pretending to be a building block.

## When not to reuse

Not everything should be extracted. Avoid premature abstraction.

Do not extract a building block when:

- The concept is only used in one skill.
- The extraction would create indirection without reducing duplication.
- The shared version would be so generic that it loses meaning.
- The capability is tightly coupled to one consumer's contract or workflow.

A skill that is standalone by nature should not be forced into a composition model.

---

## One-way pattern consistency

A reusable skill should encode exactly one canonical way to solve each recurring problem. When a skill offers multiple valid approaches, the agent faces decision paralysis and output becomes inconsistent.

| Inconsistent skill | Consistent skill |
|--------------------|------------------|
| "Use either classes or factory functions." | "Use factory functions for create-X helpers." |
| "Return errors or throw, whichever you prefer." | "Throw for programmer errors; return `Result` for expected failures." |
| "Use mocks or stubs as needed." | "Use stubs for dependencies; avoid mocking internal functions." |

One-way consistency does not mean ignoring context. It means the skill makes the default choice explicit and explains when to deviate. This is especially important for tool building blocks, where consumers rely on a stable output shape.

---

## Framework-aware and version-aware skills

The most reusable skills are often tied to specific technologies. There are two strategies for keeping them current:

### Framework-aware

The skill knows the framework's patterns, APIs, and conventions. Example: a React best-practices skill encodes rules for React and Next.js.

Framework-aware skills should:

- Declare which framework versions they target.
- Use the framework's official terminology.
- Update when the framework's recommended patterns change.

### Version-aware

The skill fetches or ships version-specific guidance so it does not go stale.

Strategies:

- **Fetch fresh rules** from a canonical URL before each use.
- **Ship versioned guidance** inside the skill or package.
- **Pin a version** in frontmatter and document the expected target.

Version-aware skills reduce hallucinations caused by the agent's training cutoff.

---

## Reusability checklist

- [ ] The skill declares what it needs from other skills and the environment.
- [ ] Shared conventions are not duplicated across skills.
- [ ] Building-block skills have a clear, narrow scope.
- [ ] Tool building blocks produce structured output that consumers can act on.
- [ ] Consumers handle missing dependencies gracefully.
- [ ] The skill does not force reuse where none exists.
- [ ] The skill is extracted as a separate building block only when reuse is justified.

---

## Research basis

- The distinction between **tool building blocks** (narrow, functional capabilities) and **vocabulary building blocks** (shared reference) is our own sharpening of the broader research concept of reusable skills.
- The research synthesis identifies **composition** as a core property of skills: skills become more powerful when they can be reached and consumed by other skills. This is a common denominator across Claude Code, Cursor, Codex, and Hermes.
- **Dependency declaration** and **avoiding duplication** are supported by the research on skill ecosystem quality and governance.
- **One-way pattern consistency** is our own practice, but it is strongly supported by the research finding that inconsistent guidance leads to decision paralysis and unpredictable output.
- **Framework-aware and version-aware skills** are our own framing of the broader research observation that the most useful skills are often tied to specific technologies and must stay current to remain reliable.
- The separation of tool building blocks from presentation and workflow is our own design choice, aligned with the building block / conductor / wrapper taxonomy.

[configurable]: ./configurable.md
[package]: ../reference/package.md
