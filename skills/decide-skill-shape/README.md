# decide-skill-shape

A model-invoked conductor that helps decide whether a problem should be solved by a new skill, an existing skill, a script, an MCP server, a context file, or a mode.

## When to use

Use this skill when:

- The user is unsure what shape to build.
- A conductor reaches the `decide` gate and needs a shape recommendation.
- The user asks whether a problem should be a skill, script, MCP, context file, or mode.

## How to use

Invoke the skill by name, or let `write-a-skill` delegate the `decide` gate to it.

The skill will:

1. Capture the problem.
2. Explore existing skills and registry results.
3. Ask classification questions.
4. Apply decision rules.
5. Present a recommendation with rationale and alternatives.
6. Write a decision report to the context directory.

## Directory layout

```
decide-skill-shape/
├── SKILL.md
├── README.md
├── references/
│   ├── DEPENDENCIES.md
│   └── DECISION_RULES.md
└── evals/
    └── evals.json
```

## Key conventions

- **Conductor:** delegates exploration to `list-available-skills` and `search-skills-registry`.
- **No files written until approved:** only the decision report is written.
- **Decision report:** a structured context report with problem, recommendation, rationale, alternatives, and next action.
- **User confirms:** the recommendation is presented for confirmation.

## Maintenance notes

- Keep the decision rules in sync with `docs/skill-standards/patterns/` and `docs/skill-standards/fundamentals/`.
- Update the version when the decision rules change.
- Add near-miss triggers to `evals/evals.json` if new shape domains could collide with this skill.
