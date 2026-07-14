# verify-branch

`verify-branch` is a global CI gatekeeper. It compares the current branch to the repository's default branch and runs a configurable, pluggable set of verification gates. It then delivers an unfiltered PASS or FAIL verdict and writes a report to `.agents/context/verify-branch/`.

It works for any project type: Node.js, Python, Go, Java, Rust, infrastructure-as-code, documentation, and more. The skill ships ecosystem starter templates, but it does not assume a specific technology stack.

## When to use

- Before opening a pull request.
- After a large refactor or merge.
- When you want to know if a branch will pass CI.
- When the user says "verify branch", "check my PR", or "are there tests for this".

## Directory layout

```
verify-branch/
├── SKILL.md                  # conductor intent and rules
├── README.md                 # this overview
├── references/               # contracts, schemas, and registry docs
│   ├── CONFIG_REFERENCE.md   # all settings
│   ├── ADAPTERS.md           # adapter contract
│   └── ...
├── subagents/                # gate, report, and checkpoint subagents
├── scripts/                  # reusable scripts and adapters
│   ├── adapters/             # tool-specific gate adapters
│   └── lib/                  # shared helper utilities
└── assets/templates/         # default config and standards templates
```

## Key conventions

- **Config**: `.agents/config/verify-branch.yaml`. Edit it directly, or let the skill re-run bootstrap when config is missing.
- **Gates**: All gates are pluggable. Adapters translate project-specific tool output into a common gate result. The gate registry is open: any gate can be added under `preferences.gates` with a `type` and the right config.
- **Execution modes**: Use `preferences.execution_mode` to switch between `full`, `quick`, and `security-audit` runs. Use `tags` and `depends_on` to filter and order gates.
- **Reports**: Written to `.agents/context/verify-branch/`. Each branch gets a report and a resume state file.
- **Advisory context**: The skill may scan `.agents/context/` for reports that match the current branch or ticket. Fresh reports are read as advisory context only; stale reports are noted but never influence the verdict.

## How to add a new adapter

1. Create a script in `scripts/adapters/<adapter-name>.js` (or `scripts/adapters/<category>/<adapter-name>.js` for legacy layout) that implements the adapter contract in `references/ADAPTERS.md`.
2. Register the adapter in `references/GATE_REGISTRY.md` for the relevant gate.
3. Add it to the fallback list in `references/CONFIG_REFERENCE.md` if it should be auto-selected.
4. For project-specific adapters, place them in `.agents/verify-branch/adapters/` or add the path to `preferences.adapter_paths`.
5. Test the adapter against a real project before relying on it.

## How to update project config

Edit `.agents/config/verify-branch.yaml` to change gate enablement, commands, importance, or overrides. If the file is missing or incomplete, run the skill; the `bootstrap` subagent will detect tools, ask you for any ambiguous choices, and write the file for you.

For every available setting, see `references/CONFIG_REFERENCE.md`.
