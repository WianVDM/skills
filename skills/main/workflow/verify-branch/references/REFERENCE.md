# Reference

Diff procedure, gate types, verdict rules, report templates, and edge cases for `verify-branch`.

## Diff procedure

1. Detect the repository's default branch:
   ```bash
   git rev-parse --abbrev-ref origin/HEAD
   ```
   Use the returned value as `<default-branch>` unless the config overrides it.

2. Ensure `<default-branch>` is up to date:
   ```bash
   git fetch origin
   ```

3. Get committed branch changes:
   ```bash
   git diff --name-status <default-branch>...HEAD
   ```

4. Get uncommitted changes (staged + unstaged + untracked):
   ```bash
   git status --porcelain
   ```

5. Merge both lists into the verification set. For uncommitted files, derive the equivalent `git diff --name-status` status (`M`, `A`, `D`) from the porcelain output.

6. Filter files based on gate configuration. Some gates ignore files that do not contain logic (for example, generated files or lock files). The exact filter is gate-specific and documented in the gate subagent.

7. Tag every file as `committed` or `uncommitted` in the report.

## Gate types

Each gate has a `type` that determines which subagent fulfills it.

### `command`

- Runs the project's configured shell commands.
- Commands are configured in `.agents/config/verify-branch.yaml` under `preferences.gates.<name>.commands`.
- Non-zero exit or timeout produces a `FAIL`.
- Findings are reported with `rule: command_failure`, `command_timeout`, or `command_error`.

### `mapper`

- Maps changed source files to expected spec files using configured `mappings` and `exemptions`.
- Reports `FAIL` if a required spec file is missing or was not modified.
- Uses the `default-mapper` adapter.

### `standards`

- Applies project standards rules to changed files.
- Rules are loaded from configured `sources` (`yaml` or `markdown-frontmatter`).
- AI inference can generate rules from markdown docs when no YAML sources exist.
- `violation` findings fail the gate; `consideration`/`warning` findings are reported but do not fail by default.

### `custom`

- Runs a single adapter through `scripts/run-gate.js`.
- Used for arbitrary tool-backed gates (e.g., lint, security, dead-code, complexity).
- The adapter can return `PASS`, `FAIL`, `ERROR`, `NOT_APPLICABLE`, or `SKIPPED`.

### Legacy: `static-analysis`

- v3 configs used `static-analysis` with `sub_gates`.
- The `static-analysis-gate` subagent remains available for backwards compatibility.
- New configs should define each sub-gate as a separate `custom` gate.

## Verdict rules

The overall verdict is computed by `scripts/lib/evaluate-verdict.js` from the collected gate results and the configured `verdict_policy`.

Default policy (`all_required`):
- **PASS** — all required gates returned `PASS` or `NOT_APPLICABLE`, and no required gate errored or was skipped.
- **FAIL** — any required gate returned `FAIL`, `ERROR`, or was skipped when it should have run.

Other policy modes:
- `any_required` — PASS if at least one required gate passes cleanly.
- `threshold` — PASS if required failures, errors, and total violations are within configured thresholds.

Example `threshold` policy:

```yaml
preferences:
  verdict_policy:
    mode: threshold
    threshold:
      max_failures: 0
      max_errors: 0
      max_violations: 3
```

Optional gates report their status but do not change the verdict unless their importance is explicitly set to `required` or the policy includes them.

## Report templates

Reports are rendered from templates under `assets/templates/reports/`:

| Template | Purpose |
|----------|---------|
| `default` | Full gate summary, context consumed, and findings. |
| `compact` | One-line summary and failures only. |
| `detailed` | Everything in `default` plus raw adapter output per gate. |

Use `preferences.report_template` to select a template, or `preferences.report_template_path` to provide a custom template. Custom templates use the same Mustache-like syntax as the built-in templates.

## Report template syntax

Templates use a minimal Mustache-like syntax:
- `{{variable}}` — insert escaped value.
- `{{{variable}}}` — insert raw value.
- `{{#section}} ... {{/section}}` — repeat for arrays, or include if truthy.
- `{{^section}} ... {{/section}}` — include if falsy or empty array.

Available variables include `branch`, `base`, `commit`, `generated_at`, `verdict`, `verdict_reason`, `verdict_details`, `gate_results`, `fresh_context`, `stale_context`, and derived helpers like `has_fresh`, `has_stale`, `has_any_findings`, `total_findings`.

## Report template

Save the full report to `.agents/context/verify-branch/{branch-name}.md`:

```markdown
---
skill: verify-branch
version: 1.0.0
branch: {branch-name}
base: {base-ref}
commit: {commit-sha}
generated_at: {iso-date}
verdict: {PASS | FAIL}
required_gates_passed: {N}
required_gates_total: {M}
optional_gates_passed: {N}
optional_gates_total: {M}
consumed_context:
  fresh:
    - path: .agents/context/{type}/{key}.md
      skill: {skill-name}
      summary: "..."
  stale:
    - path: .agents/context/{type}/{key}.md
      skill: {skill-name}
      reason: "..."
---

# Branch Verification: {branch-name}

## Files Verified

### Committed on branch
| File | Status |
|------|--------|
| `src/example.ts` | M |

### Uncommitted (working tree)
| File | Status |
|------|--------|
| `src/example.spec.ts` | M |

## Gates

| Gate | Importance | Status | Adapter | Findings |
|------|------------|--------|---------|----------|
| test | required | PASS | npm-test | 0 |
| spec-coverage | required | PASS | default-mapper | 0 |
| standards | required | FAIL | yaml-standards | 3 |
| security | optional | PASS | npm-audit | 0 |

## Context consumed

### Fresh
- `.agents/context/baseline/OC-1234.md` (baseline): "Bug reproduced on auth guard."

### Stale
- `.agents/context/debrief/OC-1234.md` (debrief): commit mismatch.

## Findings

### standards
| File | Line | Rule | Severity | Message |
|------|------|------|----------|---------|
| `src/example.ts` | 42 | no-any | error | `calculate` uses `any` at line 34 |

## Summary
- **Verdict:** {PASS | FAIL}
- **Reason:** {verdict_reason}
- **Required gates passed:** {N}/{M}
- **Optional gates passed:** {N}/{M}
- **Total findings:** {N}
```

## Edge cases

### No changed files
- The `test` gate may still run if configured to run globally.
- The `spec-coverage` and `standards` gates return `NOT_APPLICABLE` if no relevant files changed.

### Missing default branch
- Stop and ask the user for a default branch override if auto-detection fails and `preferences.default_branch` is not set.

### Missing config
- Run the `bootstrap` subagent to detect tools and propose config.
- If the user declines, mark required gates as `ERROR` and optional gates as `SKIPPED`.

### Stale context reports
- Note stale reports in the `consumed_context` section.
- Never let a stale report influence the verdict.

### Resuming after interruption
- Read the state file `.agents/context/verify-branch/{branch-name}-state.md`.
- Call `checkpoint-manager` to recover pending gates.
- Resume from the first pending gate; do not re-run completed gates unless git state changed.

## Rules

- **No WARNs.** Gate statuses are `PASS`, `FAIL`, `ERROR`, `NOT_APPLICABLE`, or `SKIPPED`. Standards findings are `violation` (contributes to `FAIL`) or `consideration` (reported only).
- **Fail fast.** When `preferences.fail_fast` is `true`, stop after the first required gate failure.
- **Do not fix.** This skill reports only. It does not modify code.
- **Do not justify.** Violations are violations. Report them plainly.
- **Dynamic config.** Always read the config at runtime; never rely on hardcoded project values.
