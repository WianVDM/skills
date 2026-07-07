# merge-latest

Merge the latest upstream branch into a target branch safely.

## Purpose

This skill brings upstream changes into the right feature branch, classifies conflicts as trivial, semantic, or review, resolves only trivial conflicts automatically, validates the result with a build, and produces a report. It prioritizes safety over convenience and never guesses at semantic conflicts.

## When to use

- Sync a feature branch with its base branch.
- Prepare a branch for PR.
- Resolve merge conflicts with clear logging.

## Directory layout

```
merge-latest/
├── SKILL.md                        # main skill instructions
├── README.md                       # this file
├── references/
│   ├── REFERENCE.md                # full workflow, decision matrix, report format
│   ├── CONFIG_PATTERN.md           # config + notes pattern
│   ├── CAPABILITIES.md             # VCS, remote, ticket adapter, and build detection
│   ├── CONTEXT_REPORTS.md          # output locations
│   ├── SUBAGENTS.md                # delegation patterns
│   ├── CHECKPOINTING.md            # incremental state + resume rules
│   ├── BUILD_SYSTEMS.md            # build command detection
│   ├── BRANCH_INFERENCE.md         # upstream branch inference
│   ├── CONFLICT_ANALYSIS.md        # deep conflict investigation workflow
│   ├── MERGE_VS_REBASE.md          # when to consider rebase
│   ├── EXAMPLES.md                 # example merges
│   ├── VALIDATION.md               # review checklist
│   └── TICKET_ADAPTERS.md          # Jira, GitHub Issues, Linear, Asana, custom
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
    ├── build-validator.md          # run project build
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
- Lockfiles and generated files are classified as `review` and surfaced to the user.
- The merge is aborted if the build fails.
- Rebase is only used with explicit user approval.
- Old backups are cleaned up periodically.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on intent and move detailed guidance into `references/`. Preserve existing user preferences by pre-populating first-run questions with previous defaults.
