# Standards

The `standards` gate applies project-specific rules to changed files. This document describes how standards are sourced, authored, inferred, and overridden.

## Source formats

Standards sources are configured under `preferences.gates.standards.sources`. Each source has a `type` and a `path`.

| Type | Description |
|------|-------------|
| `yaml` | A YAML file with a `rules` list. This is the canonical format. |
| `markdown-frontmatter` | A Markdown file with rules embedded in YAML frontmatter. The body is ignored for rule extraction. |

## YAML rule schema

```yaml
rules:
  - id: no-dead-code
    category: maintenance
    severity: violation
    threshold: null
    description: "Remove or justify unused code, exports, variables, and imports."
    examples:
      - bad: "const unused = 42;"
        good: "Remove the variable or use it."
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique rule identifier. Used in overrides and findings. |
| `category` | string | no | Grouping label, e.g. `naming`, `tests`, `complexity`, `architecture`. |
| `severity` | string | yes | `violation`, `consideration`, `warning`, or `disabled`. |
| `threshold` | number | no | Numeric threshold when the rule supports one. |
| `description` | string | yes | Human-readable description of the rule. |
| `examples` | list | no | `bad` and `good` examples for documentation. |

## Severity semantics

- `violation` — breaks the gate when found. Reported as `error` severity in findings.
- `consideration` — reported but does not break the gate by default. Reported as `consideration` severity.
- `warning` — reported but does not break the gate by default. Reported as `warning` severity.
- `disabled` — ignored entirely. Useful for project overrides.

## AI inference

If no YAML sources are configured, the `standards` gate can infer rules from markdown documents when `ai_inference.enabled` is `true`.

The inference process:

1. Read each configured `source_paths` markdown file.
2. Run `scripts/infer-standards.py` to extract candidate rules using deterministic heuristics.
3. If `edit_before_use` is `true`, present the inferred rules to the user for editing.
4. Once approved, persist the rules to a YAML file under `.agents/config/standards/`.
5. Add the generated YAML file to `sources` and proceed.

Inferred rules are advisory until reviewed. The gate does not treat them as authoritative without user approval.

## Overrides

Project-specific adjustments live in `.agents/config/verify-branch.yaml` under `preferences.gates.standards.overrides`:

```yaml
overrides:
  - id: nesting-depth
    severity: consideration
    threshold: 4
    reason: "Legacy widget tree makes deeper nesting unavoidable until refactor."
```

Each override must include:

| Field | Description |
|-------|-------------|
| `id` | The rule ID to override. |
| `severity` | New severity for the rule. |
| `threshold` | New threshold if the rule supports one. |
| `reason` | Why the override exists. |

Overrides are applied before checking files. The reason is recorded in the report.

## Templates

The skill ships with framework-agnostic and framework-specific templates under `assets/templates/standards/`:

| Template | Purpose |
|----------|---------|
| `agnostic.yaml` | Generic rules that apply to any project. |
| `angular.yaml` | Rules for Angular/TypeScript projects. |
| `react.yaml` | Rules for React/TypeScript projects. |
| `python.yaml` | Rules for Python projects. |
| `go.yaml` | Rules for Go projects. |

Projects can copy a template to `.agents/config/standards.yaml` and customize it.

## Migration from markdown standards

If a project has standards documented only in markdown:

1. Enable `ai_inference` and point `source_paths` to the markdown files.
2. Run the `standards` gate once.
3. Review and edit the inferred rules.
4. Persist the result as `.agents/config/standards.yaml`.
5. Disable `ai_inference` and add the YAML file to `sources`.

This produces a stable, version-controlled standards source that does not depend on AI inference for every run.

## Rules

- The `standards` gate must read standards from configured sources, not rely on memory or hardcoded rules.
- Only `violation` findings fail the gate.
- Inferred rules require user review before persisting.
- Overrides must always include a reason.
