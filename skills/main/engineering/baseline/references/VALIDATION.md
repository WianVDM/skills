# Validation

Checklist for validating the `baseline` skill after changes or before release.

---

## Structure checks

- [x] `SKILL.md` frontmatter is complete: `name`, `description`, `scope`, `invocation`, `metadata`.
- [x] The report `version` declared in `CONTEXT_REPORTS.md` and `REFERENCE.md` matches the current report schema.
- [x] All reference links resolve: `CONFIG_PATTERN.md`, `CAPABILITIES.md`, `CONTEXT_REPORTS.md`, `REFERENCE.md`, `AUTH.md`, `WORKFLOW.md`, `DEPENDENCIES.md`, `EXAMPLES.md`.
- [x] `SKILL.md` is concise and does not duplicate deep detail from `references/`.
- [x] Progressive disclosure is followed: overview in `SKILL.md`, detail in `references/`.
- [x] The skill type is declared as `conductor` or `hybrid` and matches the actual delegation pattern.
- [x] The description front-loads a leading word (e.g., "Capture").

## Dependency declaration

- [x] Required skills are declared in `DEPENDENCIES.md` and match `SKILL.md` (none; `baseline` is standalone).
- [x] Optional consumed context is declared in `DEPENDENCIES.md` and `CONTEXT_REPORTS.md` generically, without depending on specific other skills.
- [x] Required capabilities are declared in `DEPENDENCIES.md`.
- [x] No hidden harness or vendor dependencies exist in skill files.
- [x] Auth handling references environment variables or secure stores, not hardcoded secrets.

## Context scanning

- [x] The skill scans `{context_dir}/` for relevant reports before capture.
- [x] The scan matches scope, ticket, and branch keys generically by filename and frontmatter.
- [x] The skill handles missing consumed context gracefully.
- [x] The skill records consumed context in the report frontmatter.
- [x] `consumed_context` excludes reports produced by this skill and files inside `{context_dir}/baseline/` unless explicitly provided as non-baseline context.
- [x] The skill does not fail silently when a consumed report is missing but expected by explicit config.

## Standard worker return contracts

- [x] Any subagent worker prompts reference the standard return contract defined in the project.
- [x] Workers return `status`, `artifacts`, `summary`, `findings`, `decisions made`, `open questions`, and `blockers`.
- [x] Workers do not ask the user directly unless explicitly authorized; they return `needs_input`.
- [x] The main skill owns user interaction when a worker returns `needs_input` or `blocked`.

## Branch and commit tracking

- [x] Every report records `scope`, `branch`, `commit`, and `method`.
- [x] The skill confirms the target branch before capture.
- [x] The skill does not silently switch branches; it asks the user when the target differs from current.
- [x] The skill records the current commit hash at capture time.
- [x] The skill checks report freshness by comparing branch and commit on reuse.

## Report schema

- [x] Every report includes all required frontmatter fields: `skill`, `version`, `scope`, `branch`, `commit`, `method`, `baselined_at`, `type`, and `summary`.
- [x] `reproducible` is only present when `type` is `bug`; it is omitted for all other baseline types.
- [x] `artifacts_dir` matches the directory name used for the report's artifacts.

## State and resumption

- [x] The skill writes a state file after each step.
- [x] The state file records `scope`, `branch`, `target_commit`, `current_step`, `selected_method`, and `consumed_context`.
- [x] The skill resumes from a matching state file when the branch and commit still match.
- [x] The skill archives stale state files when the branch or commit differs.
- [x] The skill records pending user input and resumes after the user responds.

## Config and bootstrap

- [x] Default config does not hardcode project-specific values such as URLs, ports, or commands.
- [x] Default `verification_method` is `auto` or detection-based.
- [x] Bootstrap includes scope resolution, branch resolution, method detection, and validation.
- [x] The skill persists resolved choices in `{config_dir}/baseline.yaml` without overwriting existing values silently.
- [x] The skill asks the user when detection is ambiguous or insufficient.

## Method agnosticism

- [x] Capability detection is project-type driven, not UI-only.
- [x] UI, API, test, code snapshot, and manual methods are documented generically.
- [x] The report template generalizes beyond UI screenshots.
- [x] Checklists cover bug reproduction, feature baseline, API baseline, code snapshot, and manual fallback.

## Global and pluggable

- [x] The skill does not depend on specific other skills being present.
- [x] The skill does not name specific harnesses, vendors, or project tools in core skill files or reference templates.
- [x] Project-specific values (URLs, ports, commands, viewports) are placeholders, null, or detection-based, not hardcoded defaults.
- [x] Detection scripts contain tool-specific logic, but the skill contract and references do not leak project or harness assumptions.
- [x] The skill fails closed when a required capability is missing rather than assuming a specific project setup.

## Behavioral scenarios

- [x] Happy path: scope, branch, and method resolve automatically; report is produced.
- [x] Missing config: skill detects environment, asks for missing values, persists choices.
- [x] Missing context report: skill continues without failing.
- [x] Worker returns `blocked`: skill stops and consults the user.
- [x] Worker returns `needs_input`: skill collects input and resumes.
- [x] User rejects a proposal: skill offers alternatives or aborts cleanly.
- [x] Stale context report: skill detects branch/commit mismatch and re-captures or warns.
- [x] No capture method available: skill offers manual fallback and asks the user.

## Evaluation and maintenance

- [x] Trigger evals are documented and test realistic invoke phrases.
- [x] Behavior evals cover happy path, missing config, ambiguous scope, no capture method, stale report, user rejects branch, and manual fallback.
- [x] Report evals cover required frontmatter, summary generation, and type-appropriate `reproducible` handling.
- [x] A review cadence is documented (e.g., on every minor/major version bump and at least quarterly).
- [x] `EXAMPLES.md` uses the current report schema (`version: 1.0.1`, `scope:`, `branch:`, `commit:`, `summary:`).

## Security

- [x] No secrets are stored in skill files or config files.
- [x] Authentication config uses environment variables, session files, or manual entry, not hardcoded credentials.
- [x] Destructive actions require explicit user confirmation.
- [x] The skill fails closed if a required capability is missing.

---

## Validation outcome

After running through this checklist, record the result:

- **PASS** — all checks pass, no blockers.
- `PARTIAL` — some non-blocking gaps remain; document them in the skill notes.
- `FAIL` — blocking issue must be resolved before release.

Result: ________________

Validated by: ________________
Date: ________________
Notes: ________________
