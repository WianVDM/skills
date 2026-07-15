# Validation

Pre-flight checklist and validation rules for `pr-review`.

## Before starting the workflow

- [ ] `detect-project-context` found a project root.
- [ ] `{config_dir}/pr-review.yaml` exists or `initialize-skill` created it.
- [ ] At least one PR source tool is available.
- [ ] At least one local checkout method is available.
- [ ] The user has provided a PR identifier or the current branch context allows resolution.

## Before collecting context

- [ ] `identity-resolver` returned a complete identity (`pr_number`, `repo`, `branch`, `base`, `url`).
- [ ] `tool-discovery` found preferred tools for all required capabilities.

## Before running checks

- [ ] `git-worktree-inspector` created a clean worktree.
- [ ] Changed files are known.
- [ ] Gate commands are scoped to changed files.

## Before drafting the review

- [ ] All required context capabilities have evidence or a documented skip.
- [ ] Existing reviews and threads have been compared against proposed comments.
- [ ] `scope-checker` has flagged any scope-drift or unrelated items.
- [ ] Every proposed comment is anchored to a changed diff hunk or a nearby changed line.

## Before posting

- [ ] The user explicitly approved the exact draft.
- [ ] Every inline comment line is inside a changed diff hunk.
- [ ] The `commit_id` matches the current PR head.
- [ ] The posting tool is available and has required permissions.
- [ ] Posting confidence is `high`.

## If any item fails

- Stop and consult the user, or
- Switch to manual payload mode and hand back the exact payload.
