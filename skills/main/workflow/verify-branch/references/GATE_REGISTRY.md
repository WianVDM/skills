# Gate Registry

This document describes how gates are registered and fulfilled in `verify-branch`. The gate registry is **open and config-driven**: any gate can be defined under `preferences.gates` as long as it has a `type`. The skill ships common defaults as ecosystem templates, but no gate is mandatory.

## Gate types

Each gate must declare a `type`. The type determines which subagent fulfills the gate.

| Type | Subagent | Purpose |
|------|----------|---------|
| `command` | `test-gate` | Run one or more shell commands. |
| `mapper` | `spec-coverage-gate` | Map changed source files to expected spec files. |
| `standards` | `standards-gate` | Apply rules from configured standards sources. |
| `custom` | `custom-gate` | Run a single adapter through `scripts/run-gate.js`. |

Legacy configs may still use the old `static-analysis` gate with `sub_gates`. For those, the `static-analysis-gate` subagent remains available for backwards compatibility.

## Gate status semantics

- `PASS` — ran successfully and found no blocking issues.
- `FAIL` — ran successfully and found blocking issues.
- `ERROR` — could not run due to a tool error, missing config, or other problem.
- `NOT_APPLICABLE` — no relevant changed files or no work to do.
- `SKIPPED` — disabled or could not be resolved and is treated as optional.

A gate marked `ERROR` or `FAIL` fails the overall run only if its `importance` is `required` and the configured verdict policy says so. Optional gates with `FAIL` or `ERROR` are reported but do not change the overall verdict unless promoted.

## Adding a gate

Add any gate to `.agents/config/verify-branch.yaml`:

```yaml
preferences:
  gates:
    my-custom-gate:
      enabled: true
      importance: optional
      type: custom
      adapter: my-adapter
      fallback_adapters: []
      command: null
      cwd: "."
      timeout: 300
```

Then implement the adapter in one of the discovered adapter paths (e.g., `.agents/verify-branch/adapters/my-adapter.js`).

## Built-in adapters

See [ADAPTERS.md](ADAPTERS.md) for the shipped adapter registry and the adapter contract.
