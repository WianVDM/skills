# Versioning

## Current version

`verify-branch` 4.0.1

## Version history

- `4.0.1` — Security and robustness hardening: adapters now execute commands via argument arrays instead of shell interpolation, custom-command supports array commands, Python frontmatter parsers use PyYAML, npm-audit and snyk correctly report ERROR on tool failures, and required gates that are explicitly disabled are treated as `NOT_APPLICABLE`.
- `4.0` — Open gate registry, dynamic adapter discovery, ecosystem templates, configurable verdict policies, and customizable report templates. Removed internal `fallow` toolchain fallbacks from the core skill. v3 configs with `static-analysis.sub_gates` are supported by the legacy `static-analysis-gate` subagent but are not automatically migrated.
- `3.0` — Refactored into a global, pluggable-gate conductor skill. Reports moved to `.agents/context/verify-branch/`. Config moved to `.agents/config/verify-branch.yaml`. Added generic `.agents/context/` scanning, adapter architecture, and subagent delegation.
- `2.0` — Previous stable version. Used hardcoded gates, `.verify-branch/` reports, and project-specific `fallowrc.json` configuration.

## Report schema changes (4.0)

- Report `version` frontmatter field is `4`.
- Template rendering moved to `scripts/lib/render-report.js` with `assets/templates/reports/default.md`, `compact.md`, and `detailed.md`.
- Reports can be customized via `preferences.report_template` or `preferences.report_template_path`.

## Config schema changes (4.0)

- Gate registry is now open. Any gate can be defined under `preferences.gates` with a `type` of `command`, `mapper`, `standards`, or `custom`.
- Added `preferences.report_template` and `preferences.report_template_path`.
- Deprecated `preferences.report_format` (legacy v3 key). Use `report_template` instead.
- Added `preferences.verdict_policy` with modes `all_required`, `any_required`, and `threshold`.
- Adapters are discovered dynamically from `preferences.adapter_paths`, `{project_root}/.agents/verify-branch/adapters`, extension directories, and built-in adapters.
- Legacy `static-analysis` gate with `sub_gates` is still supported via `static-analysis-gate` for backwards compatibility.

## Migration from v3.0 to v4.0

- Rename `preferences.report_format` to `preferences.report_template`.
- Replace `static-analysis.sub_gates` with individual `custom` gates under `preferences.gates`.
- Add `preferences.verdict_policy` if you want non-default verdict behavior (default `all_required` matches v3 behavior).
- Re-run the skill on each branch to generate v4.0 reports. Old v3.0 reports are advisory only and do not need migration.
- If you used the internal `fallow` toolchain, either provide a custom adapter in `.agents/verify-branch/adapters` or switch to a public tool such as `knip`, `eslint-sonarjs`, or `jscpd`.

## Report schema changes (3.0)

- New report location: `.agents/context/verify-branch/{branch-name}.md` (previously `.verify-branch/{branch-name}.md`).
- New state file location: `.agents/context/verify-branch/{branch-name}-state.md`.
- Added frontmatter fields:
  - `skill`
  - `version`
  - `required_gates_passed`
  - `required_gates_total`
  - `optional_gates_passed`
  - `optional_gates_total`
  - `consumed_context` with `fresh` and `stale` subsections
- Gate results are now summarized in a table with adapter, status, and findings.

## Config schema changes (3.0)

- Config now lives in `.agents/config/verify-branch.yaml`.
- Added `preferences` block:
  - `fail_fast`
  - `max_concurrent_gates`
  - `report_format`
  - `include_uncommitted`
  - `default_branch`
  - `base_ref`
- Gates are configured under `preferences.gates`:
  - `test` with `commands`, `detect_ci_jobs`, and per-command options.
  - `spec-coverage` with `mappings` and `exemptions`.
  - `standards` with `sources`, `ai_inference`, and `overrides`.
  - `static-analysis` with `sub_gates` and adapter configuration.
- Added support for optional gates like `security-audit` and `style-format`.
- Added notes (`notes`) for workarounds, preferences, gotchas, decisions, and assumptions.

## Migration from v2.0 to v3.0

- Old reports in `.verify-branch/` are not automatically migrated.
- To generate new v3.0 reports, re-run the skill on each branch.
- Old config files (`fallowrc.json`) are not read by v3.0. Let the `bootstrap` subagent create `.agents/config/verify-branch.yaml`, then port any custom overrides manually.

## State file schema (4.0)

- Location: `.agents/context/verify-branch/{branch-name}-state.md`
- Frontmatter:
  - `skill`
  - `version`
  - `branch`
  - `base`
  - `updated_at`
- Body contains:
  - Gate checklist
  - Current focus
  - Last completed action
  - Collected results
  - Next action
