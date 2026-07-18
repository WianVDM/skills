# Validation and Composition Test

Two layers of quality gates for `pr-report`: a deterministic composition test, and a manual pre-flight checklist for releases.

## Composition test

Exercises the conductor's wiring without requiring a live PR or external APIs.

```bash
python skills/main/workflow/pr-report/scripts/composition-test.py
```

### What it tests

- `SKILL.md` frontmatter validates against the JSON schema (validator resolved from the `validate-skill-frontmatter` building block).
- `config.yaml` is parseable and declares the expected tooling keys.
- All internal markdown links in `SKILL.md`, `references/*.md`, and `subagents/*.md` resolve.
- `evals/evals.json` is valid and includes at least one `behavior` and one `pressure` eval.
- `config.yaml` provider values use provider names, not adapter names.

### What it does not test

- Live PR fetching from GitHub, CI providers, or static-analysis tools.
- Model-invoked routing and chat summaries.

### Expected output

```json
{
  "overall": "PASS",
  "results": [...]
}
```

The script exits with code `0` on success and code `1` on failure.

## Pre-flight checklist

Before considering a change complete or using the skill in a real run:

### Frontmatter and SKILL.md

- [ ] `name` is lowercase with hyphens and matches the directory name.
- [ ] `description` is under 1024 characters and includes triggers.
- [ ] `invocation` and `depends` are present.
- [ ] Declares skill type, out-of-scope behavior, focused mode, and progress reporting.
- [ ] Documents capability-first tool discovery and manual fallback.

### Config

- [ ] `config.yaml` exists next to `SKILL.md` and declares shared and skill-specific keys.
- [ ] `requires_setup: true` is declared.
- [ ] Config uses provider names (`pr-report.tools.{capability}.provider`), not adapter names.
- [ ] New shared keys are registered in `docs/skill-standards/reference/config-keys.md`.

### References and workers

- [ ] All linked reference files exist.
- [ ] Each worker has a narrow scope, references the `worker-contract`, and returns the standard contract.
- [ ] Workers do not write to the report, except the authorized report writer.
- [ ] Related reports are discovered via the `scan-context` block with `{context_dir}` as input.

### Dependencies and security

- [ ] Required skills are declared in `references/DEPENDENCIES.md` and `SKILL.md` frontmatter.
- [ ] Absence of an optional dependency is handled gracefully.
- [ ] No secrets are hardcoded; tokens are resolved by `token-resolver` and never logged.
- [ ] Direct API calls require an explicit user-configured endpoint and confirmation.

### Scenarios to walk through

1. First run with no config — asks for missing values and persists them.
2. Second run on the same PR — reads chainlog observations and reports deltas.
3. PR with only bot comments — challenges and downgrades appropriately.
4. PR with failing CI — surfaces blocker and summarizes logs.
5. Context compaction mid-run — resumes from the pending phase via `checkpoint`.
6. No configured PR tool — falls back to manual input and still produces a report.
7. Empty tool result plus lookup failure — treated as inconclusive, fallback or ask.
8. Better tool available — discloses it and asks before accepting degraded data.
9. Conflicting tools disagree on a blocker — records conflict and asks the user.
10. Focused mode (`/pr-report ci`) — collects only the requested capability.

## References

- `validate-skill-frontmatter` — frontmatter schema validation
- `audit-skill` — full fundamentals audit
- `eval-format` — eval schema conventions
