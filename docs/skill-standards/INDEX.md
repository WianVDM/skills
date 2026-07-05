# Skill Standards Index

## At a glance

This is the navigation map for the `docs/skill-standards/` wiki. It provides a visual overview of the standards layers, reading paths by role, topic indexes, and a pattern chooser. It does not replace the substantive docs; it points you to them.

**Read this if:** you are unsure where to start or need to find the right document for a specific question.

---

## Visual map of the standards layers

```text
Skill Standards Wiki
│
├── Top-level manifestos (short, abstract, stable)
│   ├── docs/PHILOSOPHY.md          — why we build skills this way
│   ├── docs/ARCHITECTURE.md         — structural shape, layers, composition
│   └── docs/PORTABILITY.md          — contract + degradation across harnesses
│
├── docs/skill-standards/            — the detailed wiki (this package)
│   ├──
│   │   Core format
│   │   ├── FORMAT.md                — SKILL.md core: frontmatter, body, layout
│   │   └── PACKAGE.md               — skills.json, lifecycle, versioning
│   │
│   ├── Fundamentals (every skill must satisfy these)
│   │   ├── what-is-a-skill.md
│   │   ├── types.md
│   │   ├── structure.md
│   │   ├── form-and-style.md
│   │   ├── common-mistakes.md
│   │   ├── evaluation.md
│   │   ├── lifecycle.md
│   │   ├── security.md
│   │   ├── when-to-create-a-skill.md
│   │   └── failure-recovery.md
│   │
│   ├── Patterns (adopt only when your role requires them)
│   │   ├── Core types
│   │   │   ├── building-block.md
│   │   │   ├── conductor.md
│   │   │   └── wrapper.md
│   │   ├── Cross-cutting
│   │   │   ├── discipline-skill.md
│   │   │   ├── context-file.md
│   │   │   ├── mode.md
│   │   │   └── conductor-implementer-split.md
│   │   └── Operational
│   │       ├── global-pluggable.md
│   │       ├── configurable.md
│   │       ├── initialization.md
│   │       ├── stateful.md
│   │       ├── context-reports.md
│   │       └── versioning.md
│   │
│   ├── Cross-cutting concerns
│   │   ├── GOVERNANCE.md            — provenance, approval, audit
│   │   ├── EVALUATION.md            — evals.json framework, tests, baselines
│   │   └── EXTENSIBILITY.md         — non-coding skills, multi-agent coordination
│   │
│   └── Utility and reference docs
│       ├── MIGRATION.md             — shape changes (rule→skill, v1→v2)
│       ├── QUICKREF.md              — one-page checklists
│       ├── TRIGGER_EVALS.md         — routing test guide
│       ├── CONTEXT_BUDGET.md        — context-load guidance
│       └── PATTERN_CATALOG.md       — pattern composition matrix
│
└── Trust layer (applies to distributed / agent-authored skills)
    ├── Provenance
    ├── Verification levels
    ├── Evaluation
    ├── Audit events
    └── Cryptographic signatures
```

---

## Role-based index

| Role | Start here | Deepen with |
|---|---|---|
| **New skill author** | [`README.md`](./README.md), [`fundamentals/what-is-a-skill.md`](./fundamentals/what-is-a-skill.md), [`fundamentals/types.md`](./fundamentals/types.md) | [`FORMAT.md`](./FORMAT.md), [`fundamentals/structure.md`](./fundamentals/structure.md), [`fundamentals/form-and-style.md`](./fundamentals/form-and-style.md), [`fundamentals/common-mistakes.md`](./fundamentals/common-mistakes.md), [`TRIGGER_EVALS.md`](./TRIGGER_EVALS.md), [`fundamentals/failure-recovery.md`](./fundamentals/failure-recovery.md) |
| **Reviewer** | [`QUICKREF.md`](./QUICKREF.md), [`fundamentals/evaluation.md`](./fundamentals/evaluation.md) | [`fundamentals/types.md`](./fundamentals/types.md), [`fundamentals/common-mistakes.md`](./fundamentals/common-mistakes.md), [`GOVERNANCE.md`](./GOVERNANCE.md), [`fundamentals/failure-recovery.md`](./fundamentals/failure-recovery.md) |
| **Architect / consumer** | [`docs/PHILOSOPHY.md`](../PHILOSOPHY.md), [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md), [`docs/PORTABILITY.md`](../PORTABILITY.md) | [`PATTERN_CATALOG.md`](./PATTERN_CATALOG.md), [`PACKAGE.md`](./PACKAGE.md), [`FORMAT.md`](./FORMAT.md) |
| **Evaluator / QA** | [`EVALUATION.md`](./EVALUATION.md), [`TRIGGER_EVALS.md`](./TRIGGER_EVALS.md) | [`CONTEXT_BUDGET.md`](./CONTEXT_BUDGET.md), [`fundamentals/evaluation.md`](./fundamentals/evaluation.md), [`patterns/discipline-skill.md`](./patterns/discipline-skill.md) |
| **End user / consumer** | [`QUICKREF.md`](./QUICKREF.md) | [`GLOSSARY.md`](./GLOSSARY.md), [`fundamentals/what-is-a-skill.md`](./fundamentals/what-is-a-skill.md) |

---

## Topic index

| Topic | Key documents |
|---|---|
| **Routing and description craft** | [`FORMAT.md`](./FORMAT.md), [`TRIGGER_EVALS.md`](./TRIGGER_EVALS.md), [`CONTEXT_BUDGET.md`](./CONTEXT_BUDGET.md) |
| **Skill structure and layout** | [`ARCHITECTURE.md`](../ARCHITECTURE.md), [`FORMAT.md`](./FORMAT.md), [`fundamentals/structure.md`](./fundamentals/structure.md) |
| **Writing style and form** | [`fundamentals/form-and-style.md`](./fundamentals/form-and-style.md), [`fundamentals/common-mistakes.md`](./fundamentals/common-mistakes.md), [`PHILOSOPHY.md`](../PHILOSOPHY.md) |
| **Evaluation and testing** | [`EVALUATION.md`](./EVALUATION.md), [`TRIGGER_EVALS.md`](./TRIGGER_EVALS.md), [`fundamentals/evaluation.md`](./fundamentals/evaluation.md) |
| **Failure recovery and iteration** | [`fundamentals/failure-recovery.md`](./fundamentals/failure-recovery.md), [`TRIGGER_EVALS.md`](./TRIGGER_EVALS.md), [`EVALUATION.md`](./EVALUATION.md) |
| **Governance and trust** | [`GOVERNANCE.md`](./GOVERNANCE.md), [`PACKAGE.md`](./PACKAGE.md), [`fundamentals/security.md`](./fundamentals/security.md) |
| **Portability and degradation** | [`PORTABILITY.md`](../PORTABILITY.md), [`PACKAGE.md`](./PACKAGE.md), [`patterns/global-pluggable.md`](./patterns/global-pluggable.md) |
| **Composition and workflows** | [`ARCHITECTURE.md`](../ARCHITECTURE.md), [`PATTERN_CATALOG.md`](./PATTERN_CATALOG.md), [`patterns/conductor.md`](./patterns/conductor.md), [`patterns/building-block.md`](./patterns/building-block.md), [`patterns/context-reports.md`](./patterns/context-reports.md) |
| **Multi-agent coordination** | [`EXTENSIBILITY.md`](./EXTENSIBILITY.md), [`patterns/conductor-implementer-split.md`](./patterns/conductor-implementer-split.md), [`patterns/conductor.md`](./patterns/conductor.md) |
| **Non-coding skills** | [`EXTENSIBILITY.md`](./EXTENSIBILITY.md) |
| **Lifecycle and versioning** | [`PACKAGE.md`](./PACKAGE.md), [`fundamentals/lifecycle.md`](./fundamentals/lifecycle.md), [`patterns/versioning.md`](./patterns/versioning.md), [`MIGRATION.md`](./MIGRATION.md) |
| **Patterns and when to adopt** | [`PATTERN_CATALOG.md`](./PATTERN_CATALOG.md), individual pattern docs in [`patterns/`](./patterns/) |
| **Quick reference and lookup** | [`QUICKREF.md`](./QUICKREF.md), [`GLOSSARY.md`](./GLOSSARY.md) |

---

## Pattern chooser

Use this table to find the right pattern doc for a specific need.

| Do you need… | Look at |
|---|---|
| A narrow, reusable capability | [`patterns/building-block.md`](./patterns/building-block.md) |
| To coordinate multiple skills or tools through phases | [`patterns/conductor.md`](./patterns/conductor.md) |
| A human-facing prompt, confirmation, or presentation layer | [`patterns/wrapper.md`](./patterns/wrapper.md) |
| To enforce a rule that resists rationalization | [`patterns/discipline-skill.md`](./patterns/discipline-skill.md) |
| Always-on baseline guidance (not a skill) | [`patterns/context-file.md`](./patterns/context-file.md) |
| A transient behavior switch | [`patterns/mode.md`](./patterns/mode.md) |
| To separate reasoning from execution | [`patterns/conductor-implementer-split.md`](./patterns/conductor-implementer-split.md) |
| A skill that works in any project or harness | [`patterns/global-pluggable.md`](./patterns/global-pluggable.md) |
| Per-project or per-user preferences | [`patterns/configurable.md`](./patterns/configurable.md) |
| First-run setup for a global or configurable skill | [`patterns/initialization.md`](./patterns/initialization.md) |
| To survive context compaction or multi-session work | [`patterns/stateful.md`](./patterns/stateful.md) |
| Structured outputs shared between skills | [`patterns/context-reports.md`](./patterns/context-reports.md) |
| Consumers to depend on a stable skill contract | [`patterns/versioning.md`](./patterns/versioning.md) |

For how these patterns compose, see [`PATTERN_CATALOG.md`](./PATTERN_CATALOG.md).

---

## Progressive reading paths

| Path | Order |
|---|---|
| **First 10 minutes** | [`PHILOSOPHY.md`](../PHILOSOPHY.md) → [`ARCHITECTURE.md`](../ARCHITECTURE.md) → [`fundamentals/what-is-a-skill.md`](./fundamentals/what-is-a-skill.md) |
| **Write a skill** | [`what-is-a-skill.md`](./fundamentals/what-is-a-skill.md) → [`types.md`](./fundamentals/types.md) → [`FORMAT.md`](./FORMAT.md) → [`structure.md`](./fundamentals/structure.md) → [`form-and-style.md`](./fundamentals/form-and-style.md) → [`common-mistakes.md`](./fundamentals/common-mistakes.md) → [`TRIGGER_EVALS.md`](./TRIGGER_EVALS.md) |
| **Review a skill** | [`QUICKREF.md`](./QUICKREF.md) → [`fundamentals/evaluation.md`](./fundamentals/evaluation.md) → [`types.md`](./fundamentals/types.md) → [`common-mistakes.md`](./fundamentals/common-mistakes.md) → [`GOVERNANCE.md`](./GOVERNANCE.md) |
| **Compose skills** | [`ARCHITECTURE.md`](../ARCHITECTURE.md) → [`PATTERN_CATALOG.md`](./PATTERN_CATALOG.md) → [`conductor.md`](./patterns/conductor.md) → [`building-block.md`](./patterns/building-block.md) → [`context-reports.md`](./patterns/context-reports.md) |
| **Make portable/global** | [`PORTABILITY.md`](../PORTABILITY.md) → [`PACKAGE.md`](./PACKAGE.md) → [`global-pluggable.md`](./patterns/global-pluggable.md) → [`configurable.md`](./patterns/configurable.md) → [`initialization.md`](./patterns/initialization.md) → [`MIGRATION.md`](./MIGRATION.md) |
| **Evaluate skills** | [`EVALUATION.md`](./EVALUATION.md) → [`TRIGGER_EVALS.md`](./TRIGGER_EVALS.md) → [`CONTEXT_BUDGET.md`](./CONTEXT_BUDGET.md) → [`fundamentals/evaluation.md`](./fundamentals/evaluation.md) |

---

## Related documents

- [`README.md`](./README.md) — the wiki entry point with role-based paths and progressive reading paths.
- [`QUICKREF.md`](./QUICKREF.md) — one-page checklists for authors, reviewers, and consumers.
- [`PATTERN_CATALOG.md`](./PATTERN_CATALOG.md) — composition matrix and common pattern combinations.
- [`GLOSSARY.md`](./GLOSSARY.md) — precise definitions of terms used across the standards.
