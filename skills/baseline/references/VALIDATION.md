# Validation

Checklist for validating the `baseline` skill after changes or before release.

---

## Structure checks

- [x] `SKILL.md` frontmatter is complete: `name`, `description`, `version`, `scope`, `invocation`, `disable-model-invocation`.
- [x] The skill version matches the report `version` declared in `CONTEXT_REPORTS.md` and `REFERENCE.md` (major version alignment: skill 3.1, report 3).
- [x] All reference links resolve: `CONFIG_PATTERN.md`, `CAPABILITIES.md`, `CONTEXT_REPORTS.md`, `REFERENCE.md`, `AUTH.md`, `PLAYWRIGHT-SETUP.md`, `WORKFLOW.md`, `DEPENDENCIES.md`, `EXAMPLES.md`.
- [x] `SKILL.md` is concise and does not duplicate deep detail from `references/`.
- [x] Progressive disclosure is followed: overview in `SKILL.md`, detail in `references/`.
- [x] The skill type is declared as `conductor` or `hybrid` and matches the actual delegation pattern.
- [x] The description front-loads a leading word (e.g., "Capture").

## Dependency declaration

- [x] Required skills are declared in `DEPENDENCIES.md` and match `SKILL.md`.
- [x] Optional consumed context is declared in `DEPENDENCIES.md` and `CONTEXT_REPORTS.md`.
- [x] Required capabilities are declared in `DEPENDENCIES.md`.
- [x] No hidden harness or vendor dependencies exist in skill files.
- [x] Auth handling references environment variables or secure stores, not hardcoded secrets.

## Context scanning

- [x] The skill scans `.agents/context/` for relevant reports before capture.
- [x] The scan matches scope, ticket, and branch keys.
- [x] The skill handles missing consumed context gracefully.
- [x] The skill records consumed context in the report frontmatter.
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

## State and resumption

- [x] The skill writes a state file after each step.
- [x] The state file records `scope`, `branch`, `target_commit`, `current_step`, `selected_method`, and `consumed_context`.
- [x] The skill resumes from a matching state file when the branch and commit still match.
- [x] The skill archives stale state files when the branch or commit differs.
- [x] The skill records pending user input and resumes after the user responds.

## Config and bootstrap

- [x] Default config does not hardcode project-specific values such as `http://localhost:4200` or `npm run start`.
- [x] Default `verification_method` is `auto` or detection-based.
- [x] Bootstrap includes scope resolution, branch resolution, method detection, and validation.
- [x] The skill persists resolved choices in `.agents/config/baseline.yaml` without overwriting existing values silently.
- [x] The skill asks the user when detection is ambiguous or insufficient.

## Method agnosticism

- [x] Capability detection is project-type driven, not UI-only.
- [x] UI, API, test, code snapshot, and manual methods are documented.
- [x] The report template generalizes beyond UI screenshots.
- [x] Checklists cover bug reproduction, feature baseline, API baseline, and code snapshot.

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
- [x] A review cadence is documented (e.g., on every minor/major version bump and at least quarterly).
- [x] `EXAMPLES.md` uses the current report schema (`version: 3`, `scope:`, `branch:`, `commit:`).

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

**Result: PASS**

Validated by: baseline redesign session (2026-07-03)
Notes: All structure, dependency, context, worker, branch/commit, state, config, method, scenario, evaluation, and security checks pass. The skill is ready for the final `write-a-skill` audit.
