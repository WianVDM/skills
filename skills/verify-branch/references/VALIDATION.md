# Validation

Checklist for reviewing the `verify-branch` skill before releasing a new version or after a refactor.

## Frontmatter and identity

- [ ] `SKILL.md` has valid YAML frontmatter.
- [ ] `name` is `verify-branch`.
- [ ] `description` matches the skill's purpose.
- [ ] `metadata.version` is set and follows semver.
- [ ] `license` is present.

## SKILL.md guidelines

- [ ] `SKILL.md` is under 140 lines.
- [ ] The skill has one clear core objective: verify whether a branch will pass CI.
- [ ] It is classified as a conductor skill.
- [ ] It contains guidelines, not step-by-step instructions.
- [ ] All heavy work is delegated to subagents.
- [ ] It references all relevant reference files.
- [ ] It declares what is out of scope.

## Global portability

- [ ] No project-specific paths (e.g., `src/app/...`, `docs/agents/...`) appear in skill files.
- [ ] No project-specific commands (e.g., `npm run test-headless`) appear in skill files.
- [ ] No project-specific framework assumptions are baked into the main skill or subagents.
- [ ] `fallowrc.json` does not appear in skill root; it is only allowed as an example template under `assets/templates/`.
- [ ] Detection scripts use generic candidates and offer configuration for project-specific additions.

## Reference files

- [ ] `README.md` exists and explains the skill's purpose and layout.
- [ ] `references/WORKER_CONTRACT.md` exists and all subagents reference it.
- [ ] `references/DEPENDENCIES.md` declares required and optional capabilities.
- [ ] `references/CONTEXT_REPORTS.md` documents produced and consumed reports.
- [ ] `references/CONFIG_PATTERN.md` and `references/CONFIG_REFERENCE.md` document every config field.
- [ ] `references/WORKFLOW.md` describes the conductor flow and subagent orchestration.
- [ ] `references/GATE_REGISTRY.md` lists every built-in gate and sub-gate.
- [ ] `references/ADAPTERS.md` documents the adapter contract and shipped adapters.
- [ ] `references/STANDARDS.md` documents standards sources, inference, and overrides.
- [ ] `references/REFERENCE.md` provides generic diff, gate, verdict, and report templates.
- [ ] `references/EXAMPLES.md` provides global examples.
- [ ] `references/VALIDATION.md` exists (this file).
- [ ] `references/VERSIONING.md` documents schema changes and migration.
- [ ] All reference links in `SKILL.md` and `README.md` resolve.

## Subagents

- [ ] Every subagent has a clear role and scope.
- [ ] Every subagent uses the standard worker return contract.
- [ ] Every subagent declares escalation rules (`needs_input`, `blocked`, `partial`).
- [ ] `bootstrap` does not run gates or tests.
- [ ] `context-scout` does not depend on specific skill names.
- [ ] `checkpoint-manager` is invoked after each gate and after context compaction.
- [ ] `report-writer` does not compute the verdict or run gates.
- [ ] Gate subagents route work through `scripts/run-gate.js` where applicable.

## Scripts and adapters

- [ ] All scripts run without syntax errors (`node --check`, `python -m py_compile`).
- [ ] All adapters follow the input/output contract in `references/ADAPTERS.md`.
- [ ] Adapters exit 0 when they run successfully, even if the wrapped tool reports violations.
- [ ] Adapters return valid JSON to stdout.
- [ ] `scripts/run-gate.js` resolves adapter paths correctly for all gate types.
- [ ] Legacy scripts that were moved to adapters have been removed.
- [ ] `scripts/infer-standards.py` exists and can parse markdown files.

## Config and templates

- [ ] `assets/templates/config.yaml` exists and is a valid template.
- [ ] `assets/templates/ecosystems/` contains starter templates for multiple project types.
- [ ] `assets/templates/standards/agnostic.yaml` exists and is a valid YAML file.
- [ ] Framework-specific standards templates (`angular.yaml`, `react.yaml`, `python.yaml`, `go.yaml`) exist.
- [ ] The config template uses placeholders instead of project-specific values.
- [ ] The config schema documents `execution_mode`, `tags`, `dry_run`, and `depends_on`.
- [ ] The config schema is fully documented in `references/CONFIG_PATTERN.md` and `references/CONFIG_REFERENCE.md`.

## Reports and state

- [ ] The report schema in `references/CONTEXT_REPORTS.md` matches the output of `report-writer`.
- [ ] The state file schema in `references/CONTEXT_REPORTS.md` matches the output of `checkpoint-manager`.
- [ ] Reports are written to `.agents/context/verify-branch/`.
- [ ] Stale context reports never influence the verdict.
- [ ] Fresh context reports are consumed generically, not tied to specific skills.

## Behavior scenarios

- [ ] Happy path: all gates pass, report is written, verdict is PASS.
- [ ] Missing config: bootstrap is triggered, config is proposed, user can confirm/edit.
- [ ] Missing tool: optional gates are skipped; required gates error and fail the verdict.
- [ ] All optional gates: no optional gate failure changes the overall verdict.
- [ ] Stale context: stale reports are noted but ignored for decision-making.
- [ ] Resume after interruption: completed gates are skipped, pending gates run.
- [ ] Fail fast: when `fail_fast` is true, the run stops after the first required gate failure.
- [ ] No git repo: the skill hard-stops and asks the user.
- [ ] Execution mode `quick`: only required and fast-tagged gates run.
- [ ] Execution mode `security-audit`: only security-tagged gates run.
- [ ] Gate dependencies: gates are ordered so dependencies run first.
- [ ] Dry run: the planned gates are reported without execution.
- [ ] Corrupted config: the skill reports the error and enters bootstrap instead of crashing.
- [ ] Corrupted state: the skill warns and restarts from Phase 1 instead of losing progress.

## Structural checks

- [ ] No empty directories.
- [ ] No orphaned files that are no longer referenced.
- [ ] No project-specific strings in skill files (except explicitly allowed examples).
- [ ] Line counts are reasonable (no files are excessively long without good reason).
- [ ] YAML files parse as valid YAML.
- [ ] Markdown files render without broken links or malformed frontmatter.

## Release readiness

- [ ] `metadata.version` is updated to `4.0` if the schema changed.
- [ ] `references/VERSIONING.md` is updated with v4.0 changes and migration notes.
- [ ] A final review report is written to `.agents/context/skill-review/verify-branch-review.md`.
- [ ] The skill is tested against a real branch when possible.

## Global portability rating

After validation, assign a global portability rating from 1 to 10:

- 10: fully generic, no project-specific strings, works out of the box for any project type.
- 8: generic with templates/examples that users can customize.
- 5: generic core but ships with project-specific defaults that must be changed.
- 2: mostly project-specific.
- 1: only works for the original project.

Target for this refactor: **8/10**.
