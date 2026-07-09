# debrief

A thin conductor that produces a structured, confidence-rated understanding of one ticket before implementation.

## What it does

- Resolves a ticket key from user input, branch, or previous state.
- Gathers ticket data, relationships, codebase evidence, and related context.
- Forms and challenges assumptions.
- Calculates confidence and identifies gaps.
- Writes a debrief report and presents a summary.

## What it does not do

- Handle multiple tickets in one invocation.
- Implement, test, or modify code.
- Recommend the next skill to run.
- Produce execution plans.

## Directory layout

```text
debrief/
├── SKILL.md
├── README.md
├── references/
│   ├── DEPENDENCIES.md
│   └── CONFIG_PATTERN.md
├── subagents/
│   ├── form-assumptions.md
│   └── synthesis-writer.md
├── evals/
│   └── evals.json
└── scripts/         # populated during implementation
    └── ...
```

## Key conventions

- One ticket per invocation.
- Reports are written to `{context_dir}/debrief/{key}-{slug}.md`.
- State is maintained by `checkpoint` at `{context_dir}/debrief/{key}/state.md`.
- `baseline` is a recommended dependency; it is only used when the ticket is verifiable.

## Adapting the skill

- Change `debrief.yaml` defaults to adjust confidence thresholds or baseline behavior.
- Add tracker-specific config under `trackers.{name}`.
- Customize the report schema by updating `subagents/synthesis-writer.md`.

## Testing

- Trigger evals: `evals/evals.json`.
- Composition tests: verify the conductor calls the right building blocks in order.
- Pressure tests: missing credentials, stale reports, Red-confidence loops, manual tracker fallback.
