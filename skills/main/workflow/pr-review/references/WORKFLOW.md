# Workflow

Detailed step sequence and resume rules for `pr-review`.

## Phase 1: Initialize

1. Detect project context with `detect-project-context`.
2. Load or create `{config_dir}/pr-review.yaml` with `initialize-skill`.
3. For each required capability (PR source, reviews, changed files, CI, issue tracker, checkout, posting), invoke `tool-discovery/scripts/discover-tools.py`.
4. Ensure at least one tool is available for PR source and checkout.
5. Write initial state with phase `initialized`.

## Phase 2: Resolve PR

1. Invoke `identity-resolver/scripts/resolve-identity.py` with user input.
2. If status is `needs_input`, ask the user for a PR number or URL.
3. Record `pr_number`, `repo`, `branch`, `base`, `ticket_key`, `url` in state.
4. Scan `{context_dir}/` for prior `pr-review` reports matching the key.
5. Use `artifact-freshness` to decide whether prior reports can be reused.
6. Set state phase to `resolved`.

## Phase 3: Discover tools

1. For each capability, invoke `tool-discovery/scripts/discover-tools.py` with the capability name and config directory.
2. Record the ranked list and the preferred tool per capability.
3. Set state phase to `tools_discovered`.

## Phase 4: Collect context

1. For each capability, invoke the preferred tool.
2. Store the tool output in `evidence-store` under identity `{work_item_type}/{work_item_key}` (e.g., `pr/42@owner-repo`).
3. If the preferred tool returns partial or no data and a better-ranked tool exists, fall back.
4. Disclose any degraded source and record it in state.
5. Collect:
   - PR metadata
   - Existing reviews and inline threads
   - Changed files
   - CI/build status
   - Ticket scope
6. Set state phase to `context_collected`.

## Phase 5: Checkout and inspect

1. Invoke `git-worktree-inspector/scripts/inspect-worktree.py` with the PR branch and base.
2. Read changed files locally.
3. Run targeted checks on changed files only, using gates from config or auto-detected gates.
4. Record check results and any unintended file resets.
5. Set state phase to `inspected`.

## Phase 6: Synthesize review

1. Summarize PR changes and intent.
2. Compare against ticket scope and project conventions.
3. Invoke `scope-checker` subagent to challenge proposed comments against scope.
4. Compare against existing reviews and threads to avoid duplication.
5. Generate:
   - Top-level summary with verdict.
   - Required inline comments.
   - Optional inline comments.
   - Confidence level for each item.
6. Set state phase to `synthesized`.

## Phase 7: Draft review

1. Write the review draft to `{context_dir}/pr-review/{key}/{key}-review-draft.md`.
2. Include event, body, inline comments with path and line, and confidence statement.
3. Mark the report `<!-- STATUS: completed -->`.
4. Set state phase to `drafted`.

## Phase 8: Review with user

1. Present the draft to the user.
2. Ask for feedback, edits, or approval.
3. Iterate until the user explicitly confirms the exact text.
4. Set state phase to `confirmed`.

## Phase 9: Post or hand back

1. If posting confidence is high and the user confirmed:
   - Assemble the complete payload.
   - Validate every inline comment coordinate against the diff hunk.
   - Post via the preferred posting tool in one call.
   - Record the post URL or result.
2. If posting confidence is not high, the user declines, or posting fails:
   - Write the exact manual payload to `{context_dir}/pr-review/{key}/{key}-review-payload.md`.
   - Tell the user how to post it manually.
3. Set state phase to `complete` or `manual_payload`.

## Resume rules

- On entry, read `{context_dir}/pr-review/{key}/state.md`.
- Resume from the earliest pending phase.
- Re-run `tool-discovery` if the preferred tool is no longer available.
- Re-check `artifact-freshness` for any report being reused.
