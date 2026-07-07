# Initialization checklist format

After sync, the setup skill presents a checklist of skills that need skill-specific initialization.

## Format

```text
The following skills may need skill-specific initialization. Run each one when you need it:

- /debrief
- /triage
- /write-a-skill

Each skill will read `.agents/config/shared.yaml` first.
```

A skill appears on the checklist if:

- Its `config.yaml` declares `requires_setup: true`, or
- Its `SKILL.md` contains an `## Initialization` section.

The setup skill does not invoke these skills automatically.
