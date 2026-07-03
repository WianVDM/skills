# Examples

## Example 1: Interactive bug fix

```
orchestrate OC-4644
```

1. Load config and state.
2. Resolve key `OC-4644`.
3. Prepare git workspace.
4. Bootstrap `debrief` and `baseline` if missing.
5. Run `plan-next`.
6. Run `diagnose`.
7. Run `grill-with-docs`.
8. Pass challenge gate.
9. Draft plan and ask user to confirm.
10. Execute phases with verification and handoff after each.

## Example 2: Auto mode

```
orchestrate OC-4644 --auto
```

Same as Example 1, but the orchestrator makes recommended choices and logs them in state. Still stops if validation fails repeatedly.

## Example 3: Resume from checkpoint

```
orchestrate OC-4644
```

When state.md already exists, read it, read the latest checkpoint, and resume from `## Next Action`.

## Example 4: Inferred ticket

```
orchestrate this
```

Infer the ticket key from the current branch name, e.g., `OC-4644-feature-x` → `OC-4644`.
