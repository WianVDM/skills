# Skill Package and Lifecycle

## At a glance

This document specifies the **package envelope** around the portable core: `skills.json`, `skills.lock`, versioning, namespacing, dependencies, and lifecycle stages. It defines when a skill needs a package and how to move from idea to retirement.

**Read this if:** you are distributing a skill, adding dependencies, or managing a skill lifecycle.

A skill is a reusable unit of process guidance. A **skill package** wraps one or more skills with metadata, dependencies, versioning, and verification so they can be discovered, installed, distributed, and trusted.

This document specifies the package envelope and the lifecycle stages a skill moves through. The package layer sits around the portable core defined in `FORMAT.md`; it does not change the core format.

---

## When a skill needs a package

A single skill with no consumers and no dependencies can live as a lone `SKILL.md`. A package becomes necessary when:

- The skill has external dependencies (tools, MCP servers, binaries, environment variables).
- The skill is consumed by other skills or conductors.
- The skill is distributed beyond its origin project.
- Multiple related skills are shipped together.
- The skill needs verification or governance metadata.

---

## `skills.json`

`skills.json` is the package manifest. It is required for packages with multiple skills or external dependencies. It is optional but recommended for a standalone single skill that is distributed.

```json
{
  "name": "ui-design-kit",
  "version": "2.1.0",
  "description": "Skills for reviewing and generating UI components against a design system.",
  "license": "MIT",
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
  },
  "verification": {
    "level": "tested",
    "evals": "evals/evals.json"
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
| `license` | string | Max 256 chars. Prefer SPDX identifier. | License identifier. |
| `compatibility` | object | See `compatibility` object below. | Harness compatibility, minimum versions. |
| `namespaces` | object | Keys: skill names. Values: namespaced identifiers (`package:skill`). | Mapping from skill name to namespaced identifier. |
| `verification` | object | See `verification` object below. | Verification level and evaluation artifact path. |

### `requirements` object

| Key | Type | Constraints | Purpose |
|-----|------|-------------|---------|
| `skills` | string[] | Unique. Non-empty strings. | Other skills this package expects to be available. |
| `tools` | string[] | Unique. Non-empty strings. | Native tools the skills need. |
| `mcp_servers` | object[] | Each object requires `name`. Optional `capabilities` array of unique strings. | MCP servers by name and capability. |
| `binaries` | string[] | Unique. Non-empty strings. | External binaries the skills need. |
| `environment_variables` | string[] | Unique. Non-empty strings. | Environment variables the skills reference. |
| `sandbox_features` | string[] | Unique. Non-empty strings. | Sandbox capabilities required at runtime. |

### `verification` object

| Key | Type | Constraints | Purpose |
|-----|------|-------------|---------|
| `level` | string | Enum: `unverified`, `declared`, `tested`, `formal`. | Verification level. |
| `evals` | string | Non-empty path. Typically `evals/evals.json`. | Path to the evaluation artifact. |

Runtime tool scoping stays in `SKILL.md` frontmatter (e.g., `allowed-tools`). The `requirements` object is for dependency declaration and policy gates, not for runtime behavior.

See `GOVERNANCE.md` for verification levels and governance rules.

## Formal package schemas

The package layer is formalized by JSON Schema files in `schemas/`:

- `schemas/skills.json.schema.json` — `skills.json` manifest.
- `schemas/evals.json.schema.json` — `evals/evals.json` evaluation artifact.
- `schemas/skills.lock.schema.json` — generated `skills.lock` lock file.

These schemas enable tooling, validation, and forward compatibility. The schemas declare required fields, value constraints, and harness hints, but they do not change the portable core defined in `FORMAT.md`.

### `skills.json` schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["name", "version", "skills"],
  "properties": {
    "name": { "type": "string", "pattern": "^[a-z0-9-]+$", "maxLength": 128 },
    "version": { "type": "string", "pattern": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-([a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)*))?(?:\\+([a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)*))?$" },
    "description": { "type": "string", "maxLength": 1024 },
    "license": { "type": "string", "maxLength": 256 },
    "compatibility": {
      "type": "object",
      "properties": {
        "harnesses": { "type": "array", "items": { "type": "string" }, "uniqueItems": true },
        "min_aider_version": { "type": "string" }
      }
    },
    "skills": { "type": "array", "items": { "type": "string", "pattern": "^[a-z0-9-]+$" }, "minItems": 1, "uniqueItems": true },
    "namespaces": { "type": "object", "additionalProperties": { "type": "string", "pattern": "^[a-z0-9-]+:[a-z0-9-]+$" } },
    "requirements": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "skills": { "type": "array", "items": { "type": "string" }, "uniqueItems": true },
        "tools": { "type": "array", "items": { "type": "string" }, "uniqueItems": true },
        "mcp_servers": {
          "type": "array",
          "items": { "type": "object", "required": ["name"], "properties": { "name": { "type": "string" }, "capabilities": { "type": "array", "items": { "type": "string" }, "uniqueItems": true } } }
        },
        "binaries": { "type": "array", "items": { "type": "string" }, "uniqueItems": true },
        "environment_variables": { "type": "array", "items": { "type": "string" }, "uniqueItems": true },
        "sandbox_features": { "type": "array", "items": { "type": "string" }, "uniqueItems": true }
      }
    },
    "verification": {
      "type": "object",
      "properties": {
        "level": { "type": "string", "enum": ["unverified", "declared", "tested", "formal"] },
        "evals": { "type": "string", "minLength": 1 }
      }
    },
    }
  },
  "additionalProperties": true
}
```

### `evals.json` schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["version", "skill", "tests"],
  "properties": {
    "version": { "type": "string", "enum": ["1"] },
    "skill": { "type": "string", "pattern": "^[a-z0-9-:]+$", "maxLength": 128 },
    "tests": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "type", "prompt"],
        "properties": {
          "id": { "type": "string", "pattern": "^[a-z0-9-]+$", "maxLength": 128 },
          "type": { "type": "string", "enum": ["trigger", "behavior", "composition", "pressure", "security"] },
          "category": { "type": "string", "enum": ["should-trigger", "should-not-trigger"] },
          "prompt": { "type": "string", "minLength": 1, "maxLength": 4096 },
          "expected": { "type": "string" },
          "baseline_type": { "type": "string", "enum": ["no_skill", "previous_version", "failure_documentation"] },
          "available_skills": { "type": "array", "items": { "type": "string" }, "uniqueItems": true },
          "expected_selection": { "type": "array", "items": { "type": "string" }, "uniqueItems": true },
          "assertions": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["type"],
              "properties": {
                "type": { "type": "string", "enum": ["file_read", "file_write", "command", "output_contains", "output_excludes", "output_format", "regex_match", "regex_exclude"] },
                "path": { "type": "string" },
                "value": { "type": "string" },
                "pattern": { "type": "string" }
              }
            }
          }
        }
      }
    }
  }
}
```

### `skills.lock` schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["version"],
  "properties": {
    "version": { "type": "string", "enum": ["1"] },
    "skills": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["version"],
        "properties": {
          "version": { "type": "string", "pattern": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-([a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)*))?(?:\\+([a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)*))?$" },
          "hash": { "type": "string", "pattern": "^sha256:[a-fA-F0-9]{64}$" }
        }
      }
    },
    "dependencies": {
      "type": "object",
      "properties": {
        "skills": { "type": "array", "items": { "type": "string" }, "uniqueItems": true },
        "mcp_servers": { "type": "array", "items": { "type": "string" }, "uniqueItems": true }
      }
    }
  }
}
```

See `EVALUATION.md` for the runner interface, assertion semantics, and baseline types. The lock file is generated at install or publish time and should not be hand-edited.

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

Versioning matters when a skill has consumers. A version number is a promise about compatibility. Use semantic meaning for version changes:

- **Major version bump** — breaking change. Consumers must update.
- **Minor version bump** — new capability, behavior, or schema field added. Existing consumers continue to work.
- **Patch version bump** — bug fix, clarification, or non-behavioral change. Existing consumers are unaffected.

The exact scheme is less important than consistency. Pick a scheme and document it in `references/VERSIONING.md` or `skills.json`.

See `patterns/versioning.md` for migration paths and deprecation.

---

## Dependencies

A skill must declare what it needs. Dependencies are not bad; hidden dependencies are.

### Skill dependencies

Declare other skills in `requirements.skills`. The skill can be invoked by name or consumed through context reports. Consumers must handle missing dependencies gracefully.

### External tools and MCP servers

Declare native tools, binaries, and MCP servers in `requirements`. The standard separates:

- **Dependency declaration** — what the skill needs, in `skills.json`.
- **Runtime tool scoping** — which tools the skill is allowed to use, in `SKILL.md` frontmatter.

A harness maps the portable requirements to its native configuration files (e.g., Claude Code's `mcpServers`, Codex's `requirements.toml`).

### Environment variables

If a skill needs credentials, declare the variable name in `requirements.environment_variables`. Never store the secret value in `SKILL.md`, `references/`, or config files. See `fundamentals/security.md`.

---

## Lifecycle stages

A skill moves through intentional stages. Each stage has entry and exit criteria.

### 1. Decide

Confirm that a skill is the right solution. Ask:

- Is the task repeated?
- Does the agent vary without guidance?
- Could a script, MCP server, prompt template, or documentation change solve it instead?

See `fundamentals/when-to-create-a-skill.md`.

### 2. Design

Choose the skill type, form, invocation, and scope before writing files.

- Type: building block, conductor, wrapper, or multi-layer.
- Form: instruction-heavy, guideline-heavy, or hybrid.
- Invocation: model-invoked or user-invoked.
- Scope: what is in and what is out.
- Dependencies: other skills, tools, APIs, environment variables.

Write a one-sentence intent statement:

> This skill makes the agent more predictable at ______ by enforcing ______.

If both blanks are hard to fill, the design is not ready.

### 3. Draft

Write the minimal `SKILL.md` plus only the supporting files that are needed. Keep `SKILL.md` focused. Push deep detail into `references/` and worker prompts into `subagents/`.

### 4. Validate

Check the draft against structure and style standards before testing behavior:

- Does the description include what and when?
- Are reference links resolvable?
- Is every line load-bearing?
- Are dependencies declared?
- Is the language harness-agnostic and project-agnostic where required?

### 5. Test

Run the skill against representative prompts:

- **Trigger evals** — does the description fire at the right times?
- **Behavioral evals** — does the skill improve the agent's output compared to no skill?
- **Edge cases** — missing config, missing context report, ambiguous input, user rejection.

See `EVALUATION.md` and `fundamentals/evaluation.md`.

### 6. Iterate

Improve the skill based on test results and real usage. Remove instructions that do not change behavior. Sharpen completion criteria. Rewrite the description if triggering is unreliable.

### 7. Publish

Once the skill is stable, publish or install it. At publish time:

- Bump the version if the schema, config, or behavior changed.
- Document breaking changes and migration paths.
- Add or update `README.md` for human maintainers.
- Declare compatibility and dependencies in `skills.json`.
- Record verification metadata.

### 8. Maintain

Skills rot without attention. Maintenance tasks:

- Review after significant real-world usage.
- Remove sediment — guidance that no longer applies.
- Update framework-specific advice when the target technology changes.
- Add notes to config when user preferences or workarounds emerge.
- Re-run trigger evals if the agent harness or model changes.

### 9. Deprecate or retire

Retire a skill when:

- It is no longer used.
- Its job is better handled by a script, MCP server, or another skill.
- It has grown too many unrelated concerns and should be split.
- A newer version replaces it.

When deprecating, document the replacement path and update any skills that depended on it.

---

## Canonical install paths

The canonical locations for installed skills are:

```text
{project-root}/.agents/skills/          # project-level skills
~/.agents/skills/                     # user-level skills
```

A harness may also read from native paths for compatibility (e.g., `.claude/skills/`, `.codex/skills/`, `.cursor/skills/`). Native paths are secondary; they should be symlinks or loader indexes to the canonical `.agents/skills/` tree where possible.

See [docs/PORTABILITY.md](../PORTABILITY.md) for the full degradation model.

---

## Governance in the package layer

The package layer is where governance metadata lives. For distributed skills, `skills.json` should include:

- Verification level.
- Required dependencies for policy gates.
- License.

For personal or local skills, these fields are recommended but not required. See `GOVERNANCE.md` for the full governance model.

---

## Key takeaways

- A **package** is needed when a skill has dependencies, consumers, distribution, or multiple related skills.
- **`skills.json`** is the manifest; **`skills.lock`** records the resolved dependency graph and content hashes.
- Use **semantic versioning** consistently; bump major for breaking changes, minor for additions, patch for fixes or clarifications.
- **Namespacing** (`package-name:skill-name`) prevents collisions when skills are shared.
- Declare all **dependencies** (skills, tools, MCP servers, binaries, environment variables) so policy gates can validate them.
- The **lifecycle** stages have clear entry and exit criteria: decide → design → draft → validate → test → iterate → publish → maintain → deprecate.
- For distributed skills, add governance metadata: verification level and license.

## Research basis

- The package envelope (`skills.json`, versioning, dependencies, lifecycle) is a synthesis of package models from Codex, Claude Code, Hermes, and the agentskills.io ecosystem.
- Codex uses a `config_folder` for project-level skills and supports both `.codex/skills/` and `.agents/skills/`. https://github.com/openai/codex/blob/98d28aab54ed86714901b6619400598598876dd0/codex-rs/core-skills/src/loader.rs#L303-L315
- Hermes has a write-approval system (`tools/write_approval.py`) that informs the staging/approval model. https://github.com/NousResearch/hermes-agent
- The agentskills.io specification defines package-level metadata, compatibility, and harness compatibility declarations. https://agentskills.io/specification
- The lifecycle model is our own synthesis of standard software lifecycle stages with the evaluation and governance requirements drawn from the research.
- Canonical install paths (`./agents/skills/`, `~/.agents/skills/`) are a design decision based on the broadest cross-harness path observed in the research, with native-path symlinks allowed for compatibility.

Exact harness-specific package formats and approval workflows are **limited** and are intentionally abstracted behind the portable `skills.json` envelope.
