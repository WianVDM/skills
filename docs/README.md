# Documentation

This directory contains the specification and standards for the skill architecture library.

## Start here

| Document | Purpose |
|---|---|
| [`PHILOSOPHY.md`](./PHILOSOPHY.md) | The mission, core beliefs, and root virtue of the standard. |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | The structural layers: context stack, building blocks, conductors, wrappers, and cross-cutting patterns. |
| [`PORTABILITY.md`](./PORTABILITY.md) | How the portable core degrades gracefully across agent harnesses. |
| [`skill-standards/README.md`](./skill-standards/README.md) | The comprehensive standards wiki: format, package, fundamentals, patterns, governance, evaluation, and extensibility. |

## How to navigate

- **For motivation and principles** → read `PHILOSOPHY.md`.
- **For structural layers and composition** → read `ARCHITECTURE.md`.
- **For portability and cross-harness concerns** → read `PORTABILITY.md`.
- **For concrete rules, patterns, and examples** → read `skill-standards/README.md` and follow the links into the format, package, fundamentals, patterns, governance, evaluation, and extensibility documents.
- **For term definitions** → see `skill-standards/GLOSSARY.md`.

## Directory layout

```
docs/
├── README.md
├── PHILOSOPHY.md
├── ARCHITECTURE.md
├── PORTABILITY.md                 # portability and degradation
└── skill-standards/
    ├── README.md                  # standards wiki and index
    ├── GLOSSARY.md                # term definitions
    ├── FORMAT.md                  # SKILL.md core format
    ├── PACKAGE.md                 # package and lifecycle
    ├── GOVERNANCE.md              # provenance and agent-authored skills
    ├── EVALUATION.md              # evaluation framework
    ├── EXTENSIBILITY.md           # non-coding and multi-agent concerns
    ├── fundamentals/              # universal requirements for every skill
    └── patterns/                  # opt-in architecture patterns
```
