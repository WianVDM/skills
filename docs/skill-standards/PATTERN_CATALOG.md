# Pattern Catalog

A quick composition reference for the skill architecture patterns. Use this table to see which patterns work together and which combinations are common, rare, or unsupported.

## Composition matrix

| Pattern | Type | Composes with | Notes |
|---------|------|---------------|-------|
| **Building block** | Capability | Conductor, wrapper, multi-layer skill, other building blocks | The primary unit of reuse. Consumed by conductors and wrappers. |
| **Conductor** | Coordination | Building blocks, subagents/workers, context reports, stateful, discipline skills | Orchestrates other skills. Often produces state or reports. |
| **Wrapper** | Human-facing | Building blocks, conductors | Adapts another skill for human interaction. Usually user-invoked. |
| **Discipline skill** | Cross-cutting | Building block, conductor, wrapper | Can be applied inside any layer. Enforces a rule against rationalization. |
| **Context-file** | Always-on baseline | Any skill | Sets conventions; skills handle workflows. Avoid overlap. |
| **Mode** | Transient stance | Any skill (recommendation only) | Skills should not depend on modes being active. |
| **Conductor/implementer split** | Sub-pattern of conductor | Conductor, building blocks, context reports | Separates reasoning from execution. |
| **Global / pluggable** | Scope | Configurable, initialization, stateful, context reports | Makes a skill work across projects and harnesses. |
| **Configurable** | Runtime adaptation | Initialization, global/pluggable, stateful, context reports | Loads project config and notes. |
| **Initialization** | First-run | Configurable, global/pluggable | Sets up config on first run. |
| **Stateful** | Persistence | Conductor, context reports, global/pluggable | Survives context compaction and multi-session work. |
| **Context reports** | Structured output | Conductor, building blocks, stateful, global/pluggable | Shared artifacts between skills. |
| **Versioning** | Lifecycle | Building blocks, conductors, context reports | Needed once a skill has consumers. |

## Common compositions

### Small reusable capability

```text
building block
  └── versioning (if consumed)
```

A building block may need versioning once other skills depend on its output.

### Coordinated workflow

```text
conductor
  ├── building block A
  ├── building block B
  ├── discipline skill (guardrail)
  ├── context reports (shared artifacts)
  └── stateful (survives compaction)
```

A conductor composes building blocks, enforces discipline, produces reports, and persists state.

### Human-friendly interface

```text
wrapper
  └── building block or conductor
```

A wrapper sits on top of a reusable capability or workflow and adds prompts, confirmation, and presentation.

### Project-agnostic global skill

```text
global / pluggable
  ├── configurable (loads project preferences)
  ├── initialization (first-run setup)
  ├── context reports (output)
  └── versioning (if distributed)
```

A skill that works in any project needs detection, config, initialization, and often reports.

### Reasoning / execution split

```text
conductor (reasoning)
  └── implementer worker (execution)
       └── context reports (results)
```

The conductor/implementer split isolates planning from file changes and uses reports to hand off results.

## Combinations to avoid

| Combination | Why it is risky |
|-------------|-----------------|
| Wrapper + Conductor logic | A wrapper should not coordinate phases; promote it to a conductor with a thin wrapper on top. |
| Context-file + Skill overlap | The harness resolves conflicts heuristically; let the context file set baseline and the skill handle the workflow. |
| Skill depends on a Mode | Modes are transient and harness-dependent. Encode essential behavior in the skill itself. |
| Two model-invoked skills with nearly identical descriptions | They will compete for triggers; merge them or differentiate the descriptions sharply. |
| Stateful without context reports | State files can become opaque; pair state with a report that summarizes what a resumer needs. |

## Choosing a starting point

1. **Do one narrow thing well?** → Start with **building block**.
2. **Coordinate multiple skills or tools?** → Start with **conductor**.
3. **Adapt another skill for a human?** → Start with **wrapper**.
4. **Need a rule that resists rationalization?** → Add **discipline skill**.
5. **Need it everywhere with no trigger?** → Use **context-file** instead.
6. **Need it in any project without changes?** → Add **global/pluggable**, **configurable**, and **initialization**.
7. **Need to survive long sessions?** → Add **stateful** and **context reports**.
8. **Other skills depend on it?** → Add **versioning**.

## Related documents

- [`fundamentals/types.md`](./fundamentals/types.md) — the primary skill types.
- [`patterns/building-block.md`](./patterns/building-block.md) — narrow reusable capabilities.
- [`patterns/conductor.md`](./patterns/conductor.md) — coordination and delegation.
- [`patterns/wrapper.md`](./patterns/wrapper.md) — user-facing adaptation.
- [`ARCHITECTURE.md`](../ARCHITECTURE.md) — the full context stack and layered model.
