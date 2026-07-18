# map-skill-flow

A model-invoked building block that turns a skill into an explicit flow model: branches, gates, phases, success paths, and break points with causes, handling, and confidence.

## When to use

- A conductor is designing a skill and wants the pre-draft flow as a design gate.
- A reviewer wants to confirm comprehension of an existing skill before scoring it.
- An eval generator wants break points as systematic test candidates.

## How to use

Invoke the skill by name with a skill directory or a design draft. It returns a flow report (see `references/FLOW_MODEL.md`), a mermaid diagram, and a break-point list sorted `silent` first.

## Key conventions

- **Read-only:** never modifies the mapped skill.
- **Confidence labels:** every element is `declared` (written in the skill) or `inferred` (derived from prose). Inferred elements are never presented as fact.
- **Silent breaks surface:** any failure the skill does not handle is reported, not smoothed over.
- **Unmappable input blocks:** the block returns `blocked` rather than inventing a flow.

## Directory layout

```
map-skill-flow/
├── SKILL.md
├── README.md
├── references/
│   └── FLOW_MODEL.md       # flow report schema
└── evals/
    └── evals.json          # behavior evals
```
