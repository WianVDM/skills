# Validation

Pre-flight checklist and validation rules for `pr-review`. Each phase's detailed rules live in its own reference; this file is the quick gate list.

## Before starting the workflow

- [ ] `detect-project-context` found a project root.
- [ ] `{config_dir}/pr-review.yaml` exists or `initialize-skill` created it.
- [ ] Style profile resolved (intake done or config already answers it).
- [ ] PR source and checkout each have one working path (manual fallback counts).
- [ ] The user has provided a PR identifier or the current branch context allows resolution.

## Before collecting context

- [ ] `identity-resolver` returned a complete identity (`pr_number`, `repo`, `branch`, `base`, `url`).
- [ ] Each capability has a selected tool: cached recipe re-validated, or a fresh derivation validated against the contract.

## Before running checks

- [ ] `git-worktree-inspector` created a clean worktree.
- [ ] Changed files are known.
- [ ] Gate commands are scoped to changed files.
- [ ] The user consented to running checks against this branch when the branch is untrusted.

## Before drafting

- [ ] Conversation comments were collected (or the gap is disclosed in the report).
- [ ] Existing discussion classified: settled items carry evidence and are out of the draft unless the user re-flags them.
- [ ] `scope-checker` has flagged scope-drift or unrelated items.
- [ ] Every proposed finding has evidence; the signal-to-noise budget held.
- [ ] Reviewer position determined; optional-comments policy applied.

## Before posting

- [ ] The user explicitly approved the exact draft.
- [ ] `scripts/validate-review-coordinates.py` returned `ok` for every comment.
- [ ] The `commit_id` matches the current PR head.
- [ ] The posting tool is present and authenticated.
- [ ] The draft contains no report content (confidence notes, process narration, settled-item discussion).

## If any item fails

- Stop and consult the user, or
- Switch to manual payload mode and hand back the exact payload.
