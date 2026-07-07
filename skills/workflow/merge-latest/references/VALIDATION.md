# Validation

Before considering the skill complete:

## Frontmatter

- [ ] `name` matches directory name.
- [ ] `description` is under 1024 characters and includes triggers.
- [ ] `license` and `metadata` are present.

## SKILL.md

- [ ] Declares skill type (workflow).
- [ ] Focuses on intent and workflow, not exact commands.
- [ ] Lists out-of-scope behavior.
- [ ] Links to all reference files.
- [ ] Documents argument forms and conflict rules.
- [ ] Documents fetch and checkout behavior.

## References

- [ ] All linked reference files exist.
- [ ] `CONFIG_PATTERN.md` documents config + notes and new schema fields.
- [ ] `CAPABILITIES.md` documents VCS, remote, ticket adapter, and script detection.
- [ ] `CONTEXT_REPORTS.md` documents output locations.
- [ ] `SUBAGENTS.md` documents delegation.
- [ ] `BRANCH_INFERENCE.md` documents the new inference algorithm.
- [ ] `CONFLICT_ANALYSIS.md` documents the investigation workflow.
- [ ] `BUILD_SYSTEMS.md` documents build detection.
- [ ] `MERGE_VS_REBASE.md` documents rebase rules.
- [ ] `CHECKPOINTING.md` documents state and resume.
- [ ] `TICKET_ADAPTERS.md` documents adapter examples.

## Scripts

- [ ] `scripts/parse-args.js` parses all supported forms and emits errors correctly.
- [ ] `scripts/infer-base.js` scores candidates and outputs JSON.
- [ ] `scripts/conflict-brief.js` extracts versions and context and outputs JSON.
- [ ] `scripts/recon.js` uses resolved remote refs and outputs JSON.
- [ ] `scripts/resolve-trivial.js` only resolves truly one-sided or non-overlapping additions.
- [ ] `scripts/report.js` generates the report and chat summary.
- [ ] All scripts exit non-zero on error.

## Subagents

- [ ] Each subagent has a narrow scope.
- [ ] Each uses the standard worker return format.
- [ ] Workers do not modify the working tree unless explicitly instructed.
- [ ] `latest-fetcher.md` handles fetch and fast-forward rules.
- [ ] `branch-researcher.md` requires high confidence.
- [ ] `conflict-investigator.md` only auto-resolves when confidence and downstream risk are low.
- [ ] `conflict-classifier.md` feeds into the investigator and classifies review files.

## Scenarios to walk through

1. Clean merge with inferred base branch.
2. Merge with trivial conflicts only.
3. Merge with semantic conflict requiring user input.
4. Merge that fails build and aborts.
5. Large merge triggering conflict investigation.
6. Review-file conflict (lockfile/generated) surfaced to user.
7. Context compaction mid-merge.
8. `/merge-latest SHB-317` while on `oc-3626` with semantic conflict pause.
