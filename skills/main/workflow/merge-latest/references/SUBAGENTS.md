# Subagent Delegation

`merge-latest` delegates focused tasks to workers. The main skill orchestrates and integrates results.

## Worker return contract

All workers follow the canonical `worker-contract` skill's return contract: status `complete | partial | needs_input | blocked`, an artifacts list in the frontmatter, and the standard Summary / Findings / Decisions made / Open questions / Blockers sections. Workers never ask the user directly; they return `needs_input` and the main skill owns user interaction. Worker files below add role-specific output fields on top of the contract.

## Subagents

| Subagent | Responsibility |
|----------|----------------|
| `latest-fetcher` | Fetch remote refs and fast-forward the local target branch when safe. |
| `branch-researcher` | Investigate branch relationships and infer the upstream branch with high confidence. |
| `preflight-checker` | Run pre-flight validation checks, including checkout and stash handling. |
| `recon-runner` | Run reconnaissance and gather merge metadata using resolved remote refs. |
| `change-summarizer` | Produce the pre-merge brief: timelined change summaries, interaction risk assessment, proposed verification tier. |
| `conflict-classifier` | Classify each conflict as trivial, semantic, or review. |
| `conflict-investigator` | Deep analysis of complex conflicts; produces per-file briefs and safe recommendations. |
| `validation-runner` | Run the user-configured validation command pipeline. |
| `report-writer` | Compile the merge report and chat summary. |

State, phase checklist, and resume are delegated to the `checkpoint` block; no private worker is needed.

Workers do not modify the working tree unless explicitly instructed. They return findings and recommendations.
