# Workflow

Detailed step sequence and resume rules for `pr-review`.

## Phase 0: Intake

First run in a project only. Skip when config already resolves the style profile.

1. Ask the intake questions (depth, approve opener, second-approver policy, nitpick policy) using the harness's question UI where available. See [CONFIG_PATTERN.md](CONFIG_PATTERN.md#intake-first-run-in-a-project).
2. Persist answers through `initialize-skill`.
3. Set state phase to `intaken`.

**Completion:** style profile resolved for this project.

## Phase 1: Initialize

1. Detect project context with `detect-project-context`.
2. Load or create `{config_dir}/pr-review.yaml` with `initialize-skill`.
3. Resolve tools for the two gating capabilities — **PR source** and **checkout** — via `tool-discovery`. Model-first detection: enumerate tools visible in-session, probe CLIs (presence + auth), detect the hosting platform from `git remote get-url origin`. Fall back to the discovery script when in-session detection is impossible.
4. Ensure at least one working path exists for each gating capability, manual fallback included.
5. Write initial state with phase `initialized`.

**Completion:** config exists; PR source and checkout each have one working path. Non-gating capabilities (CI, issue tracker, static analysis) resolve lazily in Phase 4.

## Phase 2: Resolve PR

1. Invoke `identity-resolver` with user input.
2. If status is `needs_input`, ask the user for a PR number or URL.
3. Record `pr_number`, `repo`, `branch`, `base`, `ticket_key`, `url` in state.
4. Scan `{context_dir}/` for prior `pr-review` reports matching the key.
5. Use `artifact-freshness` to decide whether prior reports can be reused.
6. Set state phase to `resolved`.

## Phase 3: Resolve tools

1. For each remaining capability (reviews, changed files, CI, issue tracker, posting), resolve the tool: reuse the cached project recipe when fresh, otherwise derive and validate a new one (see `tool-discovery`'s resolution guide).
2. Record the selected tool per capability in state.
3. Set state phase to `tools_resolved`.

## Phase 4: Collect context

1. For each capability, invoke the selected tool and map output to the `pr-adapter-contract` shape at fetch time.
2. Collect:
   - PR metadata
   - Existing reviews and inline review threads
   - **Conversation (issue-level) comments** — the third feedback surface, where deferrals and bot decorations live
   - Changed files with diff
   - CI/build status
   - Ticket scope
3. Store observations in `chainlog` under identity `{work_item_type}/{work_item_key}` when chainlog is enabled for the run (default: enabled for large PRs and resume runs, optional otherwise).
4. Disclose any degraded source and record it in state.
5. Set state phase to `context_collected`.

## Phase 5: Checkout and inspect

1. Invoke `git-worktree-inspector` to check out the branch and list changed files.
2. **Read each changed file in full**, not just the diff hunks — findings live around the hunk (callers, callees, invariants).
3. Run targeted checks scoped to changed files, from config gates or auto-detected gates. Confirm with the user before executing checks on an untrusted branch — gate commands run code from the PR.
4. Record check results and any unintended file resets.
5. Set state phase to `inspected`.

## Phase 6: Synthesize review

1. Invoke `review-synthesizer` with all collected context and the resolved style profile. It hunts per [REVIEW_RUBRIC.md](REVIEW_RUBRIC.md): issue classes in priority order, disposition classification of existing discussion, reviewer position, budget enforcement.
2. Invoke `scope-checker` on the proposed findings (when ticket scope exists).
3. Record findings, settled items, open items, and cut items in state.
4. Set state phase to `synthesized`.

## Phase 7: Draft report and review

Two artifacts, two audiences. Never mix them.

1. Write the **user-facing report** to `{context_dir}/pr-review/{key}/{key}-review-report.md` per [REVIEW_REPORT.md](REVIEW_REPORT.md): findings with evidence, settled items, scope check, checks run, degradations, size-gate disclosure, open questions.
2. Invoke `review-writer` to render the **PR-facing draft** to `{context_dir}/pr-review/{key}/{key}-review-draft.md` per [REVIEW_DRAFT.md](REVIEW_DRAFT.md) from the findings that survive policy.
3. Set state phase to `drafted`.

## Phase 8: Review with user

1. Present the report first (what the skill knows), then the draft (what would be posted).
2. Ask the open questions: settled-item re-flag decisions, ambiguous scope, degraded-source consent.
3. Iterate on the draft until the user explicitly confirms the exact text. Re-render through `review-writer` after substantive edits.
4. Set state phase to `confirmed`.

## Phase 9: Post or hand back

1. If posting confidence is high and the user confirmed:
   - Assemble the payload from the confirmed draft.
   - Validate every inline coordinate against the diff hunks.
   - Post via the selected posting tool in one call.
   - Record the post URL or result.
2. Otherwise: write the exact manual payload to `{context_dir}/pr-review/{key}/{key}-review-payload.md` and explain how to post it.
3. Set state phase to `complete` or `manual_payload`.

## Resume rules

- On entry, read `{context_dir}/pr-review/{key}/state.md`.
- Resume from the earliest pending phase.
- Re-validate cached tool recipes if the environment changed; re-derive if validation fails.
- Re-check `artifact-freshness` for any report being reused.
