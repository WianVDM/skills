# Branch Inference

When the upstream branch (`--from`) is not provided, `merge-latest` infers it. Inference combines git history, branch-name similarity, and optional ticket-link hints. It only proceeds when confidence is high.

## Inference order

1. **User override** — if `--from` is provided, use it.
2. **Cached inference** — check `.agents/context/merge-latest/{target}/state.md` for a previously confirmed base branch.
3. **Config default** — use `default_base_branch` from config.
4. **Research** — delegate to `branch-researcher`, which scores candidates using history and name similarity.
5. **Ask user** — if confidence is not high, ask and persist the answer.

## Candidate scoring

The bundled `scripts/infer-base.js` produces a ranked list of candidates. Each candidate is scored by combining a **relationship score** with a **name-similarity score**.

### Relationship signals

Given target `T`, candidate `C`, and merge base `B`:

- **Ancestor**: `C` is an ancestor of `T` (`git rev-list --count B..C == 0` and `T` has commits after `B`). This is the classic base-branch relationship.
- **Descendant**: `C` contains `T`; it is downstream, not a base.
- **Diverged**: both branches have unique commits; they are siblings or parallel work.
- **Same**: `C` and `T` point to the same commit; ignored.

An ancestor with a strongly related name is the strongest possible base signal. A diverged parallel branch is a weak base signal unless it is the configured default base branch.

### Name similarity

Name similarity considers:

- Exact normalized match.
- Substring relationships between branch names.
- Token overlap (Jaccard similarity) after normalizing separators.
- Ticket-key similarity: branches like `SHB-317` and `SHB-315` share a prefix and have close numeric identifiers, indicating a likely stacked relationship.

### Recency

More recent merge bases are stronger evidence that a candidate is the branch the target was based on. The script computes the merge-base timestamp relative to the target HEAD and adds a small recency score.

### Penalty for merged feature branches

A candidate that is an ancestor of **both** the target and the configured default base branch is likely an old feature branch that was merged into the default base, not the target's own base. The script penalizes such candidates so the default base wins.

### Default-base boost

If the candidate matches `default_base_branch` (e.g. `origin/development`), it receives a small boost. This lets the default base win when no strongly related ancestor exists.

### Remote preference

Remote tracking branches are kept in the candidate set. When a local branch and its remote twin tie at the same commit, the remote ref is preferred for freshness and confidence is kept high.

## Ticket-link inference

If a ticket tracker adapter is configured and the target branch name contains a ticket key, the adapter may be used to look up parent or dependency links. A matching candidate branch name or linked ticket strengthens confidence. This is a tie-breaker, not a primary signal.

## Confidence levels

| Level | Meaning |
|-------|---------|
| **high** | Single clear candidate with strong history signal and no close runner-up. |
| **medium** | Likely candidate but some ambiguity or a close runner-up. |
| **low** | Multiple candidates, no clear history, or no shared merge base. |

If confidence is medium or low, stop and ask the user.

## Example

Branch `feature-a` was based on `origin/development`:

```text
git merge-base feature-a origin/development  # → abc123
git rev-list --count abc123..origin/development   # → 0
git rev-list --count abc123..feature-a            # → 12
```

`origin/development` is the inferred base with high confidence.

## Example with stacked features

Branch `SHB-317` was based on `SHB-315`, which is itself a feature branch:

```text
git merge-base SHB-317 SHB-315  # → abc123
git rev-list --count abc123..SHB-315   # → 0
git rev-list --count abc123..SHB-317   # → 8
```

`SHB-315` is the inferred base because it is an ancestor and has a strongly related name. The skill prefers the remote tracking ref `origin/SHB-315` for freshness.

## Example with stacked features

Branch `OC-4964` was branched from `OC-3626`, which is itself a feature branch:

```text
git merge-base OC-4964 OC-3626  # → abc123
git rev-list --count abc123..OC-3626   # → 0
git rev-list --count abc123..OC-4964   # → 5
```

`OC-3626` is the inferred base. A project note such as "stacked features for OC-3626 base on OC-3626" strengthens confidence and helps distinguish it from `origin/development`.

## Persistence

Record inferred base in state:

```markdown
## Branch Inference History
| Branch | Inferred Base | Confidence | Method | Date |
|--------|---------------|------------|--------|------|
| SHB-317 | origin/SHB-315 | high | history + name-similarity | 2026-06-29 |
| OC-4964 | OC-3626 | high | history + note | 2026-06-29 |
```
