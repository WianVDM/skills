# Examples

Clean merges and validation-failure aborts are covered by the evals in `evals/evals.json`; the examples below show the branches evals do not cover.

## Inferred base branch

```
/merge-latest --to OC-4964
```

Result:
- Skill infers `OC-3626` as the base branch from git history.
- User confirms the inferred base (`OC-3626`, high confidence) before recon.
- Merges `OC-3626` into `OC-4964`.
- Inference is cached for future runs.

Chat summary:
> **Merge complete: `OC-4964` ← `OC-3626`**
> - Inferred base: `OC-3626` (high confidence)
> - Commits introduced: 3
> - Conflicts: 0
> - Build: passed

## Conflicted merge with trivial resolution

```
/merge-latest --to OC-1234
```

Result:
- Two files conflict.
- One is a one-sided import addition; resolved trivially.
- One is a semantic logic conflict; skill stops.

Chat summary:
> **Merge paused: `OC-1234` ← `origin/development`**
> - Conflicts: 2
> - Trivial resolved: 1 (`src/app/services/foo.service.ts`, one-sided import addition)
> - Semantic conflict requires action: `src/app/components/bar/bar.component.ts`
>   - Upstream changed: line 45–62, PR #1187
>   - Target changed: line 50–58, unmerged local work
> - Build: not run (merge incomplete)
> - Resolve the semantic conflict, then continue manually.

## Semantic conflict with investigation pause

You are on branch `oc-3626` and run:

```
/merge-latest SHB-317
```

Result:
- Target is resolved to `SHB-317` and checked out (you were on `oc-3626`).
- `origin/SHB-317` and `origin/SHB-315` are fetched.
- `SHB-317` is fast-forwarded to the remote.
- `branch-researcher` infers `origin/SHB-315` as the upstream with high confidence.
- The user confirms the inferred upstream before recon.
- The merge attempt reveals a conflict in `src/checkout/payment.ts`.
- `conflict-classifier` flags it as semantic.
- `conflict-investigator` finds:
  - Target side (`SHB-317`) added a new payment-method guard.
  - Upstream (`origin/SHB-315`) refactored the payment validation helper to use a new schema.
  - Both changes overlap and neither is clearly authoritative.
- The skill pauses and asks the user which approach to keep.

Chat summary:
> **Merge paused: `SHB-317` ← `origin/SHB-315`**
> - Target fast-forwarded: yes
> - Inferred upstream: `origin/SHB-315` (high confidence)
> - Conflicts: 1
> - Semantic conflict requires action: `src/checkout/payment.ts`
>   - Target: added payment-method guard (SHB-317, 2 commits)
>   - Upstream: refactored validation helper to new schema (origin/SHB-315, 1 commit)
> - Recommendation: manual resolution required
> - Build: not run (merge incomplete)
> - Resolve `src/checkout/payment.ts`, then continue manually or retry `/merge-latest SHB-317`.
