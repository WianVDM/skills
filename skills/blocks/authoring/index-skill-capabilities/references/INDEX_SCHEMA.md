# Capability index schema

Version: 1.0.0

This document defines the canonical schema for the machine-readable capability index produced by the `index-skill-capabilities` building block. The index may live at any path; the most common locations are a project-local override (`.agents/skill-capability-index.json`) and a bundle default (`docs/skill-capability-index.json`).

## Purpose

The index lets skills and conductors answer questions like:

- Which skills implement the `tool-discovery` capability?
- What capabilities does `pr-review` share with `pr-report`?
- Is there a generic building block that already covers this job?

It is deterministic, versioned, and regenerated alongside the human-readable skill catalog.

## Scope

This version indexes **bundle skills** only: skills declared in `skills.json` under the `skills` array. The schema is designed so that user-scope skills and third-party registry skills can be merged in later without breaking consumers.

## File location

The index path is configurable. The generator writes to the path specified by `--output`, a project-local default, or a bundle CI default. Consumers resolve the index in this order:

1. Configured `capability_index_path` in `write-a-skill.yaml` (or equivalent project config).
2. Project-local override at `.agents/skill-capability-index.json`.
3. Bundle default at `docs/skill-capability-index.json`.

If both a project-local override and a bundle default exist, the project-local override takes precedence, but the consumer must disclose the override.

## Top-level envelope

```json
{
  "version": "1.0.0",
  "generated_at": "2026-07-14T12:00:00Z",
  "source_check": {
    "skills_json_hash": "sha256:...",
    "latest_skill_mtime": "2026-07-14T11:58:00Z"
  },
  "skills": []
}
```

| Field | Type | Description |
|---|---|---|
| `version` | string | Schema version of the index. Consumers must validate this before reading entries. |
| `generated_at` | string | ISO 8601 UTC timestamp when the index was generated. |
| `source_check` | object | Freshness metadata used by consumers to detect stale indices. |
| `source_check.skills_json_hash` | string | SHA-256 hash of `skills.json` at generation time. |
| `source_check.latest_skill_mtime` | string | ISO 8601 UTC timestamp of the most recently modified skill file at generation time. |
| `skills` | array | List of indexed skills. |

## Schema versioning

The index schema follows SemVer-ish rules:

- **Patch** changes (1.0.0 → 1.0.1) add optional fields or fix descriptions; consumers may ignore them.
- **Minor** changes (1.0.x → 1.1.0) add required fields or new categories; consumers must tolerate them but may degrade gracefully.
- **Major** changes (1.x → 2.0) change the structure or field semantics; consumers must reject incompatible versions and fall back to description-level detection.

The generator must remain backward-compatible for one major version: when `version` is `2.0.0`, the generator should still be able to emit a `1.x` compatible index if requested via `--schema-version`.

## Skill entry

```json
{
  "name": "pr-report",
  "path": "skills/main/workflow/pr-report",
  "origin": "bundle",
  "type": "conductor",
  "invocation": "model-invoked",
  "description": "Build an actionable understanding of a pull request.",
  "capabilities": [...],
  "references": ["context-reports", "worker-contract", "pr-adapter-contract"],
  "subagents": ["normalize-pr", "normalize-ci", "issue-synthesizer"],
  "scripts": ["composition-test.py"],
  "config_keys": ["pr-report.tools", "pr-report.tooling"],
  "produces": ["{context}/pr-report/{key}-report.md", "{context}/pr-report/{key}/state.md"],
  "consumes": ["pr-source", "ci-source", "static-analysis-source"],
  "depends": ["detect-project-context", "context-reports", "worker-contract"]
}
```

| Field | Type | Description |
|---|---|---|
| `name` | string | Skill name, matching `SKILL.md` frontmatter. |
| `path` | string | Repo-relative path to the skill directory. |
| `origin` | string | `bundle` for skills in this repo. Reserved for future values: `user-scope`, `registry`. |
| `type` | string | `conductor`, `building-block`, `vocabulary`, `mode`, or `wrapper`. |
| `invocation` | string | `model-invoked`, `user-invoked`, or the slash command. |
| `description` | string | First sentence or canonical description of the skill. |
| `capabilities` | array | Capabilities this skill implements. See below. |
| `references` | array | Other skills, contracts, or schemas referenced by this skill. |
| `subagents` | array | Names of subagent files in `subagents/`. |
| `scripts` | array | Names of scripts in `scripts/`. |
| `config_keys` | array | Top-level config keys the skill uses. |
| `produces` | array | Context report types or paths the skill writes. |
| `consumes` | array | Context report types, adapter roles, or capability categories the skill reads. |
| `depends` | array | Skill names declared in `depends` frontmatter. |

## Capability entry

```json
{
  "id": "pr-report:resolve-pr",
  "name": "Resolve PR identity",
  "category": "identity-resolution",
  "description": "Resolve a PR number, repo, branch, and ticket key from user input or context.",
  "sources": ["SKILL.md:workflow:Resolve PR", "references/REFERENCE.md"]
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Globally unique identifier: `{skill-name}:{capability-slug}`. |
| `name` | string | Human-readable capability name. |
| `category` | string | Category from the taxonomy. This is the primary matching key for overlap detection. |
| `description` | string | Optional one-sentence description of what the capability does. |
| `sources` | array | Pointers to where the capability was derived. Format: `file:section:detail`. |

## Capability taxonomy

Categories are the primary matching key for overlap detection. A capability should map to exactly one category. If a capability spans multiple categories, split it or use the most specific category.

### Core categories

| Category | Meaning | Example skills |
|---|---|---|
| `identity-resolution` | Resolve a work item from user input, branch, URL, or context. | `debrief`, `pr-report`, `pr-review` |
| `tool-discovery` | Discover, rank, and select the best available tool for a capability. | `pr-report`, `pr-review` |
| `data-collection` | Fetch data from external sources (API, MCP, CLI, file). | `pr-report`, `debrief` |
| `data-normalization` | Normalize provider-specific data into a shared shape. | `pr-report` (subagents) |
| `state-management` | Maintain checkpoint/resume state across turns. | `debrief`, `pr-report`, `merge-latest` |
| `checkout` | Check out a branch or commit locally for inspection. | `baseline`, `pr-review` |
| `config-initialization` | Detect project context and initialize skill config. | `debrief`, `pr-report`, `verify-branch` |
| `report-writing` | Write structured context reports. | `debrief`, `pr-report`, `handoff` |
| `scope-checking` | Challenge findings against ticket scope or changed files. | `pr-report` |
| `freshness-checking` | Determine whether a prior report is safe to reuse. | `debrief` |
| `posting` | Submit data to an external platform (e.g., PR review). | `pr-review` |
| `assumption-management` | Form and challenge assumptions. | `debrief` |
| `validation` | Validate artifacts against schemas or rubrics. | `audit-skill`, `validate-skill-frontmatter` |
| `notification` | Fetch or send feedback via chat/email/meeting tools. | `pr-report` (future) |
| `context-scanning` | Discover related context reports. | `scan-context`, `debrief` |

### Adding new categories

New categories should be added when:

- A capability clearly does not fit an existing category.
- The same capability appears in two or more skills.
- The category name is generic enough to be reused across skills.

Additions are documented in the generator's taxonomy file and versioned as a minor schema bump.

## Source annotation rules

Every capability should have at least one source. Source strings follow the format:

```text
{file}:{section}:{detail}
```

Examples:

- `SKILL.md:In scope:Resolve a single ticket key`
- `SKILL.md:Workflow:Phase 2 — Resolve PR`
- `subagents/normalize-pr.md:Role:Normalize PR metadata`
- `references/TOOL_SELECTION.md:Capability matrix:PR metadata`
- `scripts/initialize.py:Role:First-run config`

If a capability is inferred from multiple sources, list all of them. If a capability is derived from the presence of a file (e.g., a subagent), use `subagents/{name}.md:exists`.

## Extraction candidate rules

A capability is a strong extraction candidate when:

1. It appears in two or more skills under the same taxonomy category.
2. It has a narrow, stable interface (clear inputs and outputs).
3. It is generic-domain, not tied to one workflow.
4. It is framed as serving other skills, not just the skill that currently owns it.

A capability is **not** an extraction candidate when:

1. It is only used by one skill.
2. It is tightly coupled to a specific workflow phase.
3. Its interface is unstable or poorly defined.
4. Extracting it would create more coupling than it removes.

## Consumer rules

Skills that consume the index must:

1. Validate the `version` field and fall back to description-level detection if the version is incompatible.
2. Check `source_check` freshness and warn the user if the index is stale.
3. Not fail silently when the index is missing; disclose the degraded mode.
4. Record which index source was used in their decision log.

## Migration notes

### From no index (current state)

Consumers that do not yet read the index continue to work as before. When the index is available, they use it to enhance findings. The index is additive, not a breaking change.

### To future user-scope / registry support

When `origin` values other than `bundle` are added, consumers should:

- Treat `bundle` skills as the most authoritative source.
- Treat `user-scope` skills as project-local overrides.
- Treat `registry` skills as optional extensions.

The merge order is: bundle → user-scope → registry. Conflicts are resolved by preferring the more local source.

## Example: minimal index excerpt

```json
{
  "version": "1.0.0",
  "generated_at": "2026-07-14T12:00:00Z",
  "source_check": {
    "skills_json_hash": "sha256:abc123",
    "latest_skill_mtime": "2026-07-14T11:58:00Z"
  },
  "skills": [
    {
      "name": "debrief",
      "path": "skills/main/workflow/debrief",
      "origin": "bundle",
      "type": "conductor",
      "invocation": "model-invoked",
      "description": "Debrief a ticket before implementation.",
      "capabilities": [
        {
          "id": "debrief:extract-ticket-key",
          "name": "Extract ticket key",
          "category": "identity-resolution",
          "description": "Resolve a ticket key from user input, branch, or previous state.",
          "sources": ["SKILL.md:Workflow:Phase 0 — Bootstrap and resume"]
        },
        {
          "id": "debrief:initialize-config",
          "name": "Initialize skill config",
          "category": "config-initialization",
          "description": "Detect project context and create or migrate skill config.",
          "sources": ["SKILL.md:Initialization", "scripts/initialize.py:Role"]
        },
        {
          "id": "debrief:check-freshness",
          "name": "Check report freshness",
          "category": "freshness-checking",
          "description": "Determine whether a prior debrief report is safe to reuse.",
          "sources": ["SKILL.md:Workflow:Phase 0 — Bootstrap and resume"]
        }
      ],
      "references": ["context-reports", "worker-contract", "checkpoint"],
      "subagents": ["form-assumptions", "synthesis-writer"],
      "scripts": ["initialize.py", "get-git-state.py", "detect-issue-tracker.py"],
      "config_keys": ["debrief.issue_tracker", "debrief.baseline_mode"],
      "produces": ["{context}/debrief/{key}-{slug}.md", "{context}/debrief/{key}/state.md"],
      "consumes": ["ticket-research", "ticket-relationships", "baseline"],
      "depends": ["checkpoint", "research-ticket", "context-reports", "worker-contract", "detect-project-context"]
    }
  ]
}
```
