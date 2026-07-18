# Skill Package and Lifecycle

## At a glance

**Layer:** proposed architecture. **Mode:** reference.

This document specifies the **package envelope** around the portable core: `skills.json`, `skills.lock`, versioning, namespacing, dependencies, and lifecycle stages. It defines when a skill needs a package and how to move from idea to retirement.

**Read this if:** you are distributing a skill, adding dependencies, or managing a skill lifecycle.

A skill is a reusable unit of process guidance. A **skill package** wraps one or more skills with metadata, dependencies, and versioning so they can be discovered, installed, and distributed.

This document specifies the package envelope and the lifecycle stages a skill moves through. The package layer sits around the portable core defined in [`format.md`](./format.md); it does not change the core format.

---

## When a skill needs a package

A single skill with no consumers and no dependencies can live as a lone `SKILL.md`. A package becomes necessary when:

- The skill has external dependencies (tools, MCP servers, binaries, environment variables).
- The skill is consumed by other skills or conductors.
- The skill is distributed beyond its origin project.
- Multiple related skills are shipped together.

---

## `skills.json`

`skills.json` is the package manifest. It is required for packages with multiple skills or external dependencies. It is optional but recommended for a standalone single skill that is distributed.

```json
{
  "name": "ui-design-kit",
  "version": "2.1.0",
  "description": "Skills for reviewing and generating UI components against a design system.",
  "compatibility": {
    "harnesses": ["claude-code", "cursor", "codex", "aider"],
    "min_aider_version": "0.75.0"
  },
  "skills": [
    "review-ui",
    "generate-component"
  ],
  "namespaces": {
    "review-ui": "ui-design-kit:review-ui",
    "generate-component": "ui-design-kit:generate-component"
  },
  "requirements": {
    "skills": [
      "accessibility-audit"
    ],
    "tools": [
      "read_file",
      "search_code"
    ],
    "mcp_servers": [
      {
        "name": "design-system",
        "capabilities": ["query_component"]
      }
    ],
    "binaries": [
      "jq"
    ],
    "environment_variables": [
      "DESIGN_SYSTEM_API_TOKEN"
    ]
  }
}
```

### Required fields

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `name` | string | Required. Lowercase letters, digits, and hyphens only. Max 128 chars. | Package name. |
| `version` | string | Required. Semantic version (`MAJOR.MINOR.PATCH[-prerelease][+build]`). | Package version. |
| `skills` | string[] | Required. Min 1 item. Each skill name: lowercase letters, digits, hyphens; max 128 chars. Unique. | The skills included in this package. |

### Recommended fields

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `description` | string | Max 1024 chars. | Human-readable purpose. |
| `compatibility` | object | See `compatibility` object below. | Harness compatibility, minimum versions. |
| `namespaces` | object | Keys: skill names. Values: namespaced identifiers (`package:skill`). | Mapping from skill name to namespaced identifier. |

### `requirements` object

| Key | Type | Constraints | Purpose |
|-----|------|-------------|---------|
| `skills` | string[] | Unique. Non-empty strings. | Other skills this package expects to be available. Use `skill_dependencies` for the structured taxonomy; `requirements.skills` is the flat compatibility surface. |
| `tools` | string[] | Unique. Non-empty strings. | Native tools the skills need. |
| `mcp_servers` | object[] | Each object requires `name`. Optional `capabilities` array of unique strings. | MCP servers by name and capability. |
| `binaries` | string[] | Unique. Non-empty strings. | External binaries the skills need. |
| `environment_variables` | string[] | Unique. Non-empty strings. | Environment variables the skills reference. |
| `sandbox_features` | string[] | Unique. Non-empty strings. | Sandbox capabilities required at runtime. |

### Skill dependency taxonomy

| Key | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `skill_dependencies` | object | Keys are skill names from `skills`. Values are objects with `required`, `recommended`, and `optional` arrays of skill names. | Structured declaration of skill dependencies per skill. |

### Capability bundles

| Key | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `bundles` | object[] | Each bundle has a `name`, optional `description`, and a `skills` array. | Named groups of skills that install together to enable a workflow. |

Runtime tool scoping stays in `SKILL.md` frontmatter (e.g., `allowed-tools`). The `requirements` object is for dependency declaration and policy gates, not for runtime behavior.

See [`governance.md`](./governance.md) for governance and audit rules.

## Formal package schemas

The package layer is formalized by JSON Schema files in `schemas/`:

- `schemas/skills.json.schema.json` — `skills.json` manifest.
- `schemas/evals.json.schema.json` — `evals/evals.json` evaluation artifact.
- `schemas/skills.lock.schema.json` — generated `skills.lock` lock file.

These schemas enable tooling, validation, and forward compatibility. The schemas declare required fields, value constraints, and harness hints, but they do not change the portable core defined in [`format.md`](./format.md).

The schema files are the machine-readable source of truth for tooling and validation. They are not restated here; the tables above describe intent, [`../schemas/`](../schemas/) carries the constraints.

See [`evaluation-framework.md`](./evaluation-framework.md) for the runner interface, assertion semantics, and baseline types. The lock file is generated at install or publish time and should not be hand-edited.

---

## `skills.lock`

`skills.lock` records the resolved dependency graph and content hashes for reproducible installs.

```json
{
  "version": "1",
  "skills": {
    "ui-design-kit:review-ui": {
      "version": "2.1.0",
      "hash": "sha256:..."
    }
  },
  "dependencies": {
    "skills": [
      "accessibility-audit@1.0.0"
    ],
    "mcp_servers": [
      "design-system"
    ]
  }
}
```

The lock file is generated at install or publish time. It is not hand-written. It lets a harness reproduce the exact skill set that was approved.

---

## Namespacing

A standalone skill has a flat name: `review-ui`. A skill inside a package is namespaced: `ui-design-kit:review-ui`.

Namespacing prevents collisions when multiple packages ship skills with similar names. The namespace prefix derives from the package `name` in `skills.json`.

A standalone skill can be promoted to a package later. Its name becomes its namespace.

---

## Versioning

Versioning matters when a skill has consumers: a version number is a promise about compatibility. The package `version` in `skills.json` follows semantic meaning — major for breaking changes, minor for additions, patch for fixes. See [`../patterns/versioning.md`](../patterns/versioning.md) for the full policy, migration paths, and deprecation.

---

## Dependencies

A skill must declare what it needs. Dependencies are not bad; hidden dependencies are.

### Skill dependencies

Declare skill dependencies in the structured `skill_dependencies` object, using `required`, `recommended`, and `optional` arrays per skill. The flat `requirements.skills` array is a compatibility surface for harnesses that only understand a single list. See [`../fundamentals/architecture/dependencies-and-bundling.md`](../fundamentals/architecture/dependencies-and-bundling.md) for the dependency taxonomy and how `skill_dependencies` and `requirements.skills` relate.

### External tools and MCP servers

Declare native tools, binaries, and MCP servers in `requirements`. The standard separates:

- **Dependency declaration** — what the skill needs, in `skills.json`.
- **Runtime tool scoping** — which tools the skill is allowed to use, in `SKILL.md` frontmatter.

A harness maps the portable requirements to its native configuration files (e.g., Claude Code's `mcpServers`, Codex's `requirements.toml`).

### Environment variables

If a skill needs credentials, declare the variable name in `requirements.environment_variables`. Never store the secret value in `SKILL.md`, `references/`, or config files. See [`../fundamentals/architecture/security.md`](../fundamentals/architecture/security.md).

---

## Lifecycle stages

A skill moves through intentional stages, each with entry and exit criteria: decide → design → draft → validate → test → iterate → publish → maintain → deprecate or retire. At publish time, bump the package version if the schema, config, or behavior changed, and declare compatibility and dependencies in `skills.json`.

See [`../fundamentals/core/lifecycle/`](../fundamentals/core/lifecycle/) for the full stage model.

---

## Canonical install paths

The canonical locations for installed skills are:

```text
{project-root}/.agents/skills/          # project-level skills
~/.agents/skills/                     # user-level skills
```

A harness may also read from native paths for compatibility (e.g., `.claude/skills/`, `.codex/skills/`, `.cursor/skills/`). Native paths are secondary; they should be symlinks or loader indexes to the canonical `.agents/skills/` tree where possible.

See [patterns/portability.md](../patterns/portability.md) for the full degradation model.

---

## Governance in the package layer

Governance lives outside the package manifest. The `skills.json` file should declare only identity, versioning, compatibility, and dependencies so that policy gates and harnesses can reason about the package without loading its contents.

See [`governance.md`](./governance.md) for the governance and audit model.

---

## Research basis

- The package envelope (`skills.json`, versioning, dependencies, lifecycle) is a synthesis of package models from Codex, Claude Code, Hermes, and the agentskills.io ecosystem.
- Codex uses a `config_folder` for project-level skills and supports both `.codex/skills/` and `.agents/skills/`. https://github.com/openai/codex/blob/98d28aab54ed86714901b6619400598598876dd0/codex-rs/core-skills/src/loader.rs#L303-L315
- Hermes has a write-approval system (`tools/write_approval.py`) that informs the staging/approval model. https://github.com/NousResearch/hermes-agent
- The agentskills.io specification defines package-level metadata, compatibility, and harness compatibility declarations. https://agentskills.io/specification
- The lifecycle model is our own synthesis of standard software lifecycle stages with the evaluation and governance requirements drawn from the research.
- Canonical install paths (`./agents/skills/`, `~/.agents/skills/`) are a design decision based on the broadest cross-harness path observed in the research, with native-path symlinks allowed for compatibility.

Exact harness-specific package formats and approval workflows are **limited** and are intentionally abstracted behind the portable `skills.json` envelope.
