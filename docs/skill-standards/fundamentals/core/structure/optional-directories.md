# Optional directories

**Layer:** universal fundamentals. **Mode:** rule.

These directories are optional but common. Do not include empty ones.

---

## `references/`

Deep detail: schemas, edge cases, examples, config patterns, context report schemas. Every reference file should be reachable from `SKILL.md` or another reference file.

---

## `subagents/`

Worker personas for delegation. Each worker prompt must state role, scope, allowed tools, forbidden actions, and return format. Workers should be shorter than the parent skill and should not duplicate shared context.

See [`../examples/worker-prompt.md`](../examples/worker-prompt.md) for an example worker prompt.

---

## `scripts/`

Deterministic helpers. Scripts should be documented, safe, isolated, and failure-explicit. Prefer read-only inspection unless the script is explicitly designed to mutate state. Scripts should not ask the user for input; the skill collects input and passes it as arguments or environment variables.

---

## `assets/`

Templates and static resources. Useful when a skill produces files from a fixed template.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
