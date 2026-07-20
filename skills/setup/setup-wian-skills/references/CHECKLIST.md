# Initialization checklist format

After setup, the skill presents a checklist of skills that need skill-specific initialization. In the **lazy** branch the checklist has two lists: what was configured now, and what will configure itself on first use.

## Format (lazy branch)

```text
Configured now:

- shared keys written to {config_dir}/shared.yaml
- pr-report (requires_setup, not lazy-eligible — resolved at setup)

Will self-configure on first use:

- /debrief
- /handoff
- /write-a-skill

Each deferred skill reads `{config_dir}/shared.yaml` first and collects its
remaining keys through its own Initialization flow. Run each one when you need it.
```

## Format (full branch)

In the **full** branch the checklist lists the skills configured during setup, noting any marked `requires_setup`. The self-configures list does not appear.

A skill appears on the checklist if:

- Its `config.yaml` declares `requires_setup: true`, or
- Its `SKILL.md` contains an `## Initialization` section.

The **self-configures** list contains only lazy-eligible skills whose private keys were deferred. Skills that are not lazy-eligible never appear on it, because their keys were resolved at setup.

The setup skill does not invoke these skills automatically. The user chooses which items to run and when.
