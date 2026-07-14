# merge-latest

Merge the latest upstream branch into a target branch safely.

## Purpose

This skill brings upstream changes into the right feature branch, classifies conflicts as trivial, semantic, or review, resolves only trivial conflicts automatically, validates the merge with a user-configured command pipeline, and produces a report. It prioritizes safety over convenience and never guesses at semantic conflicts.

## When to use

- Sync a feature branch with its base branch.
- Prepare a branch for PR.
- Resolve merge conflicts with clear logging.
- Resume, inspect, or abort a paused merge.

## Directory layout

```
merge-latest/
├── SKILL.md                        # main skill instructions
├── README.md                       # this file
├── references/
│   ├── REFERENCE.md                # full workflow, decision matrix, report format
│   ├── CONFIG_PATTERN.md           # config + notes pattern
│   ├── CAPABILITIES.md             # VCS, remote, authentication, binary files, script detection
│   ├── CONTEXT_REPORTS.md          # output locations and context-reports pattern
│   ├── SUBAGENTS.md                # delegation patterns
│   ├── CHECKPOINTING.md            # incremental state + resume rules
│   ├── VALIDATION.md               # merge validation command pipeline
│   ├── BRANCH_INFERENCE.md         # upstream branch inference
│   ├── CONFLICT_ANALYSIS.md        # deep conflict investigation workflow
│   ├── MERGE_VS_REBASE.md          # when to consider rebase
│   ├── EXAMPLES.md                 # example merges
│   ├── TICKET_ADAPTERS.md          # Jira, GitHub Issues, Linear, Asana, custom
│   └── DEPENDENCIES.md             # dependency declaration
├── scripts/
│   ├── parse-args.js               # parse invocation tokens
│   ├── infer-base.js               # score base-branch candidates
│   ├── conflict-brief.js           # extract conflict versions and context
│   ├── recon.js                    # gather merge metadata
│   ├── resolve-trivial.js          # safe trivial conflict resolution
│   └── report.js                   # report and chat summary generation
└── subagents/
    ├── latest-fetcher.md           # fetch remote refs and fast-forward target
    ├── branch-researcher.md        # investigate branch relationships
    ├── preflight-checker.md        # pre-flight validation
    ├── recon-runner.md             # run reconnaissance
    ├── conflict-classifier.md      # classify conflicts
    ├── conflict-investigator.md    # deep conflict investigation
    ├── validation-runner.md        # run the validation command pipeline
    ├── report-writer.md            # compile report
    └── checkpoint-manager.md       # track state and resume
```

## Key conventions

- Reports and state live in `.agents/context/merge-latest/`.
- Config and user preferences live in `.agents/config/merge-latest.yaml`.
- Notes in config are **AI guidance**, not logs.
- The upstream branch is inferred from git history and name similarity when not provided.
- Remote refs are fetched and preferred for the merge.
- Trivial conflicts are resolved automatically; semantic conflicts pause for user input.
- Lockfiles, generated files, and binary files are classified as `review` and surfaced to the user.
- The merge is aborted if the validation pipeline fails.
- Rebase is only used with explicit user approval.
- Old backups are cleaned up periodically.

## Usage

```text
/merge-latest
/merge-latest --preview
/merge-latest --continue
/merge-latest --status
/merge-latest --abort
/merge-latest --stash
/merge-latest <target-branch>
/merge-latest <target-branch> <upstream-branch>
/merge-latest --to <target-branch> --from <upstream-branch>
/merge-latest --from <upstream-branch>
```

## Options

- `--preview`: Show the plan without applying changes.
- `--continue`: Resume a paused merge from state.
- `--status`: Show current merge state without modifying.
- `--abort`: Abort the in-progress merge and restore the pre-merge state.
- `--stash`: Allow stashing a dirty working tree before checkout.
- `--to <branch>`: Explicit target branch.
- `--from <branch>`: Explicit upstream branch.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on intent and move detailed guidance into `references/`. Preserve existing user preferences by pre-populating first-run questions with previous defaults.
