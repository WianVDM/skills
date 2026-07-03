# Reference

Full decision matrix, report format, cleanup procedures, and state specification for `merge-latest`.

---

## Defaults and configuration

| Setting | Default | Override |
|---------|---------|----------|
| Target branch | Current branch | `--to` argument or first positional |
| Upstream branch | Inferred or config `default_base_branch` | `--from` argument or second positional |
| Remote | Inferred from `git remote -v` or config `remote` | Config `remote` |
| Protected branches | `main`, `development`, `master` | Config `protected_branches` |
| Output directory | `.agents/context/merge-latest` | Config `output_dir` |
| Build command | Auto-detected | Config `build_command` or `custom_build_command` |
| Deep analysis threshold | 5 files / 10 conflict blocks | Config `deep_analysis_threshold` |
| Ticket key pattern | Inferred or config | Config `ticket_key_pattern` |
| Ticket tracker adapter | None | Config `ticket_tracker_adapter` |

---

## Argument resolution

### Named arguments

```bash
--to <branch>
--from <branch>
--stash
```

### Positional arguments

```bash
<target> [<upstream>]
```

### Supported forms

| Input | Meaning |
|---|---|
| `/merge-latest` | `to` = current branch, `from` = inferred |
| `/merge-latest <branch>` | `to` = branch, `from` = inferred |
| `/merge-latest <to> <from>` | explicit target and upstream |
| `/merge-latest --from <from>` | `to` = current, `from` = given |
| `/merge-latest --to <to> --from <from>` | explicit both |
| `/merge-latest <to> --from <from>` | mixed |

### Rules

1. Named arguments override positional values.
2. If the same role is specified both by name and by position, stop and ask.
3. If more than two positional arguments appear, stop and ask.
4. `--stash` is a boolean flag; it may also be set via `auto_stash: true`.

---

## Pre-flight checks

Run in order before any merge attempt:

1. Parse arguments and detect conflicts.
2. Resolve `to` and `from`.
3. If `to` is not the current branch:
   - If the working tree is clean, check it out.
   - If the working tree is dirty and stashing is approved, stash, check out, and plan to restore.
   - Otherwise, stop and ask.
4. Fetch both `<remote>/<to>` and `<remote>/<from>`.
5. Fast-forward local `to` if it is behind its remote tracking ref and the tree is clean.
6. Stop if local `to` has diverged from its remote tracking ref.
7. Working tree must be clean unless stashing is approved.
8. Target branch must not be in `protected_branches`.
9. No merge must be in progress (`MERGE_HEAD` must not exist).
10. Target and upstream must resolve to different commits.

---

## Merge workflow

1. Parse arguments with `scripts/parse-args.js`.
2. Load config and state.
3. Resolve target branch and check out if needed.
4. Delegate to `latest-fetcher` to fetch remote refs.
5. Resolve upstream branch via argument or `branch-researcher`.
6. Delegate to `preflight-checker`.
7. Checkpoint start of run.
8. Run `recon-runner` with resolved remote refs to gather metadata and conflict preview.
9. Create backup of current HEAD.
10. Attempt merge in no-commit mode if conflicts are expected.
11. Classify each conflict via `conflict-classifier`.
12. Investigate semantic or review conflicts via `conflict-investigator`.
13. Resolve trivial conflicts with `scripts/resolve-trivial.js`.
14. Pause on semantic conflicts for user input.
15. Surface review-file conflicts to the user.
16. Run build validation.
17. Write report and chat summary.
18. Update state.

---

## Conflict classification matrix

| Situation | Classification | Action |
|-----------|----------------|--------|
| Only one side changed the conflicted region | Trivial | Resolve in favor of the changed side |
| Both sides added non-overlapping lines in the same hunk | Trivial | Combine the additions |
| Whitespace or formatting-only difference | Trivial | Resolve using the formatted side; run linter if configured |
| Both sides changed the same logic / API / behavior | Semantic | STOP and ask user |
| One side deleted the file, the other modified it | Semantic | STOP and ask user |
| Both sides renamed the same file differently | Semantic | STOP and ask user |
| Lockfile or generated file conflict | Review | Surface to user; do not auto-resolve |

---

## Preserve-vs-overwrite policy

Default: preserve target-side changes.

Override signals (prefer upstream side):

- Upstream commit message indicates fix, revert, hotfix, or security patch.
- Upstream change is from a protected branch and was made **after** the target branch was created.
- Upstream change resolves a known bug or security issue documented in a linked ticket.

When uncertain, ask the user.

---

## Report format

The report is written to `.agents/context/merge-latest/{target}-merge-report.md`.

```markdown
---
skill: merge-latest
version: 1
key: SHB-317
status: complete
updated_at: 2026-06-26T08:00:00Z
---

# Merge Report: {target} ← {upstream}

## Summary
- Result: {success | aborted | paused}
- Upstream: {ref} ({commit})
- Target: {ref} ({commit})
- Remote: {remote}
- Merge base: {commit}
- Build: {passed | failed | not run}

## Branch Inference
- Inferred upstream: {ref}
- Confidence: {high | medium | low}
- Method: {cached | config | history | name-similarity | ticket-link | user-provided}

## Fetch result
- <remote>/<target> → {commit}
- <remote>/<upstream> → {commit}
- Local target fast-forwarded: {true | false}

## Commits introduced from upstream
{list}

## Files touched by upstream
{list}

## Files touched by target
{list}

## Conflicts
### {filename}
- Classification: {trivial | semantic | review}
- Resolution: {resolved | paused}
- Reason: {why}

## Trivial resolutions applied
- {filename}: {reason}

## Conflict investigation
{findings from conflict-investigator, if triggered}

## Build output
```
{build log excerpt}
```

## Next steps
{action items}
```

---

## Cleanup procedures

### On success

1. The merge commit is local.
2. Report and state files are updated.
3. Suggest the user review and push.

### On build failure

1. Run `git merge --abort`.
2. Preserve the report with result `aborted`.
3. Preserve the pre-merge backup.
4. Summarize the build failure and ask the user how to proceed.

### On semantic conflict

1. Do not abort unless the user asks.
2. Leave the merge in progress.
3. Present both sides with context.
4. Ask the user to resolve.

### On review-file conflict

1. Do not auto-resolve.
2. Surface the file, the likely generator, and the upstream change to the user.
3. Ask the user to regenerate or manually merge the file.

### Backup cleanup

Old backups under `.agents/context/merge-latest/backups/` may be removed after a configurable retention period (default 30 days) or when the number of backups exceeds a threshold.

---

## State file specification

Path: `.agents/context/merge-latest/{target}/state.md`

Sections:

- `## Run` — timestamp, upstream, target, remote, result
- `## Branch Inference` — inferred upstream, confidence, method
- `## Fetch` — remote refs fetched, local target fast-forward status
- `## Commits` — upstream and target divergence lists
- `## Files` — changed files on each side
- `## Conflicts` — conflict classification and status
- `## Resolutions` — what was resolved and why
- `## Build` — build command and result
- `## Decisions` — user decisions during the merge
- `## Phase Checklist` — current progress
