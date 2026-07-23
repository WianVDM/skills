# Merge Intelligence

The semantic layer of reconnaissance. Mechanical recon (`scripts/recon.js`, run by `recon-runner`) predicts textual conflicts. Merge intelligence answers the questions textual prediction cannot: what did each side actually do since the merge base, where might the two sides interact *behaviorally* without a textual conflict, and what verification does that imply.

## Two-layer recon

| Layer | Tool | Output |
|---|---|---|
| Mechanical | `scripts/recon.js` via `recon-runner` | Commit/file lists, merge-tree conflict prediction |
| Semantic | `scripts/change-summary.js` via `change-summarizer` | Timelined narratives, overlap hotspots, interaction risk, proposed verification tier |

The layers cross-check each other. If the semantic overlap says both sides rewrote the same area but the merge-tree prediction reports zero conflicts (or vice versa), stop and investigate before proceeding — a disagreement means one of the layers is wrong, not that the merge is safe.

## Extraction contract

`scripts/change-summary.js --upstream <ref> --target <ref>` emits deterministic JSON: per-side commit timelines (hash, ISO date, author, subject), per-side file lists, the file/directory overlap matrix, hotspot ranking (directories both sides touched, by combined file count), UI-path signals, and counts. The script contains no judgment; the summarizer supplies it.

## Context tiering

The skill's "do not drown in context" rule applies to summaries. Tier by divergence size:

| Tier | Condition | What the summarizer produces |
|---|---|---|
| Compact | Always | Counts, overlap matrix, hotspots, per-side one-line themes |
| Hierarchical | > 50 upstream commits or > 10 overlap files | Group timelines by directory/module; summarize per group |
| Full timeline | Only for overlap regions | Commit-level narrative for hotspot areas only |

Never summarize the full history of both sides at commit level. The point is interaction judgment, not a changelog.

## Interaction risk categories

Classify each hotspot or overlap area:

- **Collision** — textual overlap confirmed by the merge-tree prediction. Handled by conflict classification after the merge attempt.
- **Interaction risk** — both sides changed the same area with no textual conflict predicted: API/contract files with new call sites, shared config, renamed semantics, schema changes. These are the breaks git cannot see.
- **Independent** — no meaningful relationship; list and move on.

Commit subjects, file types, and the timeline (what landed in what order) are the evidence. The preserve-vs-overwrite policy's timing rule ("upstream change made after target creation") reads directly off the timeline.

## Pre-merge brief

The summarizer persists a brief at `.agents/context/merge-latest/{target}-pre-merge-brief.md` so it survives compaction and feeds the merge report. Frontmatter follows the `context-reports` shared envelope (`skill`, `key`, `generated_at`, `branch`, `commit`). Body:

1. **Upstream timeline** — tiered narrative of upstream changes since merge-base.
2. **Target timeline** — same for the target branch.
3. **Overlap and hotspots** — the matrix, ranked.
4. **Interaction risk assessment** — collision / interaction risk / independent, with evidence.
5. **Proposed verification tier** — see [VALIDATION.md](VALIDATION.md#verification-tiers).
6. **Unknowns** — what the summary could not determine.

## Pre-merge gate

The gate always fires before the merge attempt; only its content scales with the prediction. When the prediction is non-empty (conflicts expected or preview degraded) or any interaction risk is flagged, present the full gate: the brief, the predicted conflict map, and the proposed verification tier, then wait for go. For clean, independent merges, present the lightweight gate instead — target ← upstream, the gap, and the verification pipeline in one or two lines — then wait for go. The skill never skips the gate on its own; only the user decides to proceed or stop. On the `preview` branch this presentation *is* the output — nothing is applied.
