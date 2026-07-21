# Reference

Decision detail, report format sketch, and cleanup procedures for `merge-latest`. State schema lives in [CHECKPOINTING.md](CHECKPOINTING.md); this file does not restate it.

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

## Workflow detail

Argument forms and rules, checkout and fetch rules, pre-flight hard stops, the merge workflow steps, the conflict classification matrix, and the preserve-vs-overwrite policy are canonical in `SKILL.md` and are not restated here.

## Report format

The report is written to `.agents/context/merge-latest/{target}-merge-report.md` (layout deviation recorded in [CONTEXT_REPORTS.md](CONTEXT_REPORTS.md)). `scripts/report.js` is the single generator; the sketch below shows the shape it emits. The frontmatter envelope follows the `context-reports` shared schema.

```markdown
---
skill: merge-latest
version: 1
key: SHB-317
generated_at: 2026-06-26T08:00:00Z
branch: SHB-317
commit: abc123
result: success
summary: "Merged origin/development into SHB-317; 2 trivial resolutions; validation passed."
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

## Confidence
- Grade: {high | medium | low}

### Verified
- {claim with evidence}

### Not verified
- {claim}

### Assumptions
- {assumption}

### Reasons
- {why the grade; caps applied}

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
