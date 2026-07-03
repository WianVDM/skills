# 12 — Reusability and composition

Skills become more powerful when they compose. A reusable skill is one that other skills can reach, consume, and build on without contradiction or duplication.

---

## Building-block skills

A building-block skill is a reusable piece of reference, vocabulary, or lightweight process. Other skills consume it.

**When to extract one**

- The same concept appears in three or more skills.
- The same convention is explained in multiple `SKILL.md` files.
- A domain vocabulary is needed by both conductors and hybrids.

**Examples**

- A shared `config-pattern` skill that defines how all skills load config.
- A shared `context-reports` skill that defines report schema and freshness rules.
- A `codebase-design` skill that provides shared design vocabulary.

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

The canonical place is `references/DEPENDENCIES.md` or a `dependencies`/`consumes`/`requires` section in `SKILL.md` frontmatter.

Example:

```yaml
---
name: project-orchestration
requires:
  - ticket-research
  - state-capture
consumes:
  - .agents/context/ticket-research/{key}.md
  - .agents/context/state-capture/{key}-{branch}.md
---
```

---

## Composition patterns

### Conductor consumes building blocks

A conductor skill uses building-block skills for shared vocabulary and standalone skills for focused work.

**Example:** a project-orchestration skill consumes ticket-research and state-capture reports, and uses a shared design-vocabulary skill when evaluating implementation options.

### Hybrid embeds building blocks

A hybrid skill embeds building-block reference directly into its workflow.

**Example:** a test-driven-development skill uses a red-green-refactor workflow and embeds principles from a shared design-vocabulary skill for interface design.

### Standalone stands alone

A standalone skill does not depend on other skills. It may be invoked by conductors, but it does not invoke them.

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

## When not to reuse

Not everything should be extracted. Avoid premature abstraction.

Do not extract a building block when:

- The concept is only used in one skill.
- The extraction would create indirection without reducing duplication.
- The shared version would be so generic that it loses meaning.

A skill that is standalone by nature should not be forced into a composition model.

---

## One-way pattern consistency

A reusable skill should encode exactly one canonical way to solve each recurring problem. When a skill offers multiple valid approaches, the agent faces decision paralysis and output becomes inconsistent.

| Inconsistent skill | Consistent skill |
|--------------------|------------------|
| "Use either classes or factory functions." | "Use factory functions for create-X helpers." |
| "Return errors or throw, whichever you prefer." | "Throw for programmer errors; return `Result` for expected failures." |
| "Use mocks or stubs as needed." | "Use stubs for dependencies; avoid mocking internal functions." |

One-way consistency does not mean ignoring context. It means the skill makes the default choice explicit and explains when to deviate.

---

## Framework-aware and version-aware skills

The most reusable skills are often tied to specific technologies. There are two strategies for keeping them current:

### Framework-aware

The skill knows the framework's patterns, APIs, and conventions. Example: `vercel-react-best-practices` encodes 70 rules for React and Next.js.

Framework-aware skills should:

- Declare which framework versions they target.
- Use the framework's official terminology.
- Update when the framework's recommended patterns change.

### Version-aware

The skill fetches or ships version-specific guidance so it does not go stale.

Strategies:

- **Fetch fresh rules** from a canonical URL before each use. Example: Vercel's `web-design-guidelines` fetches `command.md` from the source repo.
- **Ship versioned guidance** inside the skill or package. Example: library authors generate `SKILL.md` files with each release.
- **Pin a version** in metadata and document the expected target.

Version-aware skills reduce hallucinations caused by the agent's training cutoff.

---

## Reusability checklist

- [ ] The skill declares what it needs from other skills and the environment.
- [ ] Shared conventions are not duplicated across skills.
- [ ] Building-block skills have a clear, narrow scope.
- [ ] Consumers handle missing dependencies gracefully.
- [ ] The skill does not force reuse where none exists.
