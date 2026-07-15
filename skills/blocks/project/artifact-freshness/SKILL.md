---
name: artifact-freshness
description: Check whether a context report or evidence-store entry is fresh enough to reuse. Evaluates branch, commit, source timestamp, schema version, and age dimensions and returns a structured reason for any staleness.
version: 1.0.0
invocation: model-invoked
depends:
  - worker-contract
  - context-reports
---

# artifact-freshness

## Purpose

Decide whether a context report or evidence-store entry is safe to reuse. The block checks multiple freshness dimensions and returns a structured result so the caller can choose to reuse, refresh, or regenerate the artifact.

## Skill type

Building block. It only reads and evaluates freshness; it does not fetch new data or write files.

## When to use

A skill should use `artifact-freshness` when:

- It wants to reuse a previously generated context report.
- It wants to reuse an evidence entry from `evidence-store`.
- It needs a consistent, explainable freshness decision across multiple artifact types.

## In scope

- Read report frontmatter and extract freshness metadata.
- Accept evidence entries directly as JSON.
- Check branch, commit, source timestamp, schema version, and age dimensions.
- Auto-detect current branch and commit from git when not provided.
- Return a structured `fresh`/`stale` result with a reason and per-dimension details.

## Out of scope

- Fetching new data or re-running the producer.
- Writing reports or evidence entries.
- Deciding whether to delete or archive stale artifacts.
- Prompting the user when data is missing.

## Core contract

Accepts a report path or an evidence entry, plus optional current branch/commit and freshness rules. Returns a JSON result indicating whether the artifact is fresh and why.

## Modes

### Report mode

Reads the frontmatter of a markdown report and checks its freshness metadata.

### Evidence mode

Checks a provided evidence entry directly. This is used by `evidence-store` consumers.

## Supported dimensions

| Dimension | Meaning |
|---|---|
| `branch` | The artifact applies to a branch; stale if the current branch differs. |
| `commit` | The artifact applies to a commit; stale if the current commit differs. |
| `source_timestamp` | The underlying source was updated after the artifact was generated. |
| `generated_timestamp` | The artifact is older than the last commit on the branch or an age threshold. |
| `schema_version` | The artifact's schema version differs from the expected version. |
| `age` | The artifact is older than a configured threshold in hours. |

## Interface

See [references/INTERFACE.md](references/INTERFACE.md) for input/output schemas and examples.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Interface](references/INTERFACE.md)
- [Dependencies](references/DEPENDENCIES.md)
