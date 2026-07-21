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
│   ├── REFERENCE.md                # decision detail, report format sketch, cleanup procedures
│   ├── CONFIG_PATTERN.md           # config + notes pattern
│   ├── CAPABILITIES.md             # VCS, remote, authentication, binary files, script detection
│   ├── CONTEXT_REPORTS.md          # output locations and context-reports pattern
│   ├── SUBAGENTS.md                # delegation patterns
│   ├── CHECKPOINTING.md            # incremental state + resume rules
│   ├── VALIDATION.md               # merge validation command pipeline
│   ├── BRANCH_INFERENCE.md         # upstream branch inference
│   ├── MERGE_INTELLIGENCE.md       # two-layer recon, pre-merge brief, interaction risk
│   ├── CONFLICT_ANALYSIS.md        # deep conflict investigation workflow
│   ├── MERGE_VS_REBASE.md          # when to consider rebase
│   ├── EXAMPLES.md                 # example merges
│   ├── TICKET_ADAPTERS.md          # Jira, GitHub Issues, Linear, Asana, custom
│   └── DEPENDENCIES.md             # dependency declaration
├── scripts/
│   ├── parse-args.js               # parse invocation tokens
│   ├── infer-base.js               # score base-branch candidates
│   ├── conflict-brief.js           # extract conflict versions and context
│   ├── recon.js                    # gather merge metadata and conflict preview
│   ├── recon.smoke-test.js         # verify recon conflict preview against fixture repos
│   ├── change-summary.js           # extract timelines, overlap, hotspots for the pre-merge brief
│   ├── resolve-trivial.js          # safe trivial conflict resolution
│   └── report.js                   # report, chat summary, confidence block generation
└── subagents/
    ├── latest-fetcher.md           # fetch remote refs and fast-forward target
    ├── branch-researcher.md        # investigate branch relationships
    ├── preflight-checker.md        # pre-flight validation
    ├── recon-runner.md             # run reconnaissance
    ├── change-summarizer.md        # pre-merge brief: timelines, interaction risk, tier proposal
    ├── conflict-classifier.md      # classify conflicts
    ├── conflict-investigator.md    # deep conflict investigation and resolution re-review
    ├── validation-runner.md        # run verification tiers
    └── report-writer.md            # compile report
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

## Usage and options

See `SKILL.md` — the branch entry table and argument handling sections are canonical for invocation forms, branch flags (`--preview`, `--continue`, `--status`, `--abort`), `--to`/`--from`, and `--stash`.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on intent and move detailed guidance into `references/`. Preserve existing user preferences by pre-populating first-run questions with previous defaults.
