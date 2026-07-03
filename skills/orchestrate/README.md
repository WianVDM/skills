# Orchestrate Skill

A conductor skill that moves a ticket from context to completed implementation by delegating to other skills and focused subagents.

## What this skill does

- Loads project config and existing orchestration state.
- Resolves the ticket key from input, branch name, or state.
- Prepares the git workspace.
- Ensures required context reports exist, bootstrapping them if needed.
- Runs an understanding loop using `plan-next` and other skills.
- Challenges understanding before allowing a plan to be drafted.
- Drafts a phased implementation plan and gets user confirmation.
- Executes the plan phase by phase with verification and checkpointing.
- Hands off state after each phase and at the end.

## Directory layout

```text
orchestrate/
├── SKILL.md                        # identity, intent, core workflow
├── README.md                       # this file
├── references/
│   ├── REFERENCE.md                # state and artifact specifications
│   ├── CONFIG_PATTERN.md           # config schema and onboarding
│   ├── CAPABILITIES.md             # capability detection
│   ├── CONTEXT_REPORTS.md          # produced and consumed reports
│   ├── SUBAGENTS.md                # delegation contracts
│   ├── CHECKPOINTING.md            # checkpointing and incremental output
│   ├── CONDUCT_PATTERNS.md         # common loop patterns
│   ├── EXECUTION.md                # execution rules
│   ├── GIT_SETUP.md                # git workspace preparation
│   ├── EXAMPLES.md                 # example invocations
│   └── VALIDATION.md               # validation checklist
└── subagents/
    ├── context-loader.md           # load or bootstrap context
    ├── plan-runner.md              # run plan-next and interpret output
    ├── skill-executor.md           # execute a skill by role category
    ├── confidence-assessor.md      # assess and update confidence
    ├── challenge-gate.md           # challenge understanding
    ├── plan-drafter.md             # draft the implementation plan
    ├── phase-executor.md           # execute one phase
    ├── implementer.md              # generic implementation fallback
    └── checkpoint-manager.md       # maintain checkpoints and state
```

## Config file

Project-specific settings live in `.agents/config/orchestrate.yaml`.

See [references/CONFIG_PATTERN.md](references/CONFIG_PATTERN.md).

## Maintainer notes

- Keep `SKILL.md` focused on intent. Add detailed mechanics to `references/`.
- Subagent prompts should be harness-agnostic and describe outcomes, not tool calls.
- Never hardcode skill names in `SKILL.md`; map them through config role categories.
