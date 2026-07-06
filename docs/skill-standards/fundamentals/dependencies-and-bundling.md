# Dependencies and bundling

A skill must declare what it needs, and a harness must be able to install those needs reliably. This document defines the dependency taxonomy, the surfaces where dependencies are declared, the transitive closure rule for installing skills, named capability bundles, and the self-diagnostics contract a skill uses to report its own readiness.

---

## Dependency taxonomy

Every dependency of a skill is either **required**, **recommended**, or **optional**. The distinction controls installation behavior, runtime expectations, and what the user is told when a dependency is missing.

### Required

A **required** dependency is one the skill cannot function without. If it is missing, the skill is blocked.

Use `required` for:

- Other skills the skill invokes or consumes through context reports.
- Tools, binaries, or MCP servers the skill uses on every happy path.
- Environment variables the skill reads to operate.
- File conventions or scripts the skill assumes exist.

A skill must fail closed when a required dependency is missing. It may explain the missing dependency and offer a remediation step, but it must not silently proceed.

### Recommended

A **recommended** dependency is one that improves the skill's output or experience but is not strictly necessary. If it is missing, the skill runs in a degraded state.

Use `recommended` for:

- Building-block skills that add polish, speed, or richer output.
- Tools that make the skill more convenient but have acceptable fallbacks.
- Registry or lookup sources that broaden coverage but are not the only source.

Recommended dependencies are installed by default. A harness may let the user opt out at install time. A skill must handle their absence gracefully and explain the reduced capability.

### Optional

An **optional** dependency is one that unlocks a side branch or advanced feature. It is never installed automatically.

Use `optional` for:

- Extra tools or registries that only matter for a rare branch.
- Integrations the user must configure or authorize explicitly.
- Network fetches, premium APIs, or sandbox features that require explicit consent.

Optional dependencies are surfaced in the install output and in documentation. The skill must work without them on the main path.

### Summary

| Kind | Installed by default? | Missing behavior | Example |
|------|---------------------|------------------|---------|
| `required` | Yes | Skill is blocked | `worker-contract` for a skill that composes worker prompts |
| `recommended` | Yes, but can be opted out | Skill runs degraded | `search-skills-registry` for a skill that can still search locally |
| `optional` | No | Skill runs on the main path | A specific cloud provider CLI for an optional deployment branch |

---

## Declaration surfaces

Dependencies should be declared in the places both humans and harnesses can read. A human-readable declaration and a machine-readable declaration serve different purposes; a skill should provide both.

### `references/DEPENDENCIES.md`

Each skill should include a `references/DEPENDENCIES.md` file that lists its dependencies in plain language. This is the human-readable source of truth. It explains *why* a dependency is needed, not just *what* it is.

```markdown
# Dependencies

## Required skills

- `worker-contract` — provides the shared worker return format this conductor's subagents must follow.
- `context-reports` — defines the report schemas this skill writes.

## Recommended skills

- `search-skills-registry` — discovers third-party skills before creating a new one.
- `find-skills` — lists already-installed skills that might cover the same need.

## Optional skills

- `prototype` — only used when the user explicitly asks to prototype a UI variation.

## Required tools and binaries

- `read`, `write`, `edit`, `bash` — core tooling used on every invocation.
- Python 3.x — used by bundled scripts.

## Required environment

- `PROJECT_KEY` — identifies the project when writing context reports.
```

A `DEPENDENCIES.md` file should distinguish required, recommended, and optional dependencies explicitly. It should also list any consumed context reports, binaries, MCP servers, or environment variables.

### `skills.json` `requirements.skills`

For packages, the `requirements.skills` array in `skills.json` is the machine-readable declaration. It is used for transitive closure, policy gates, and lock-file generation. See [`PACKAGE.md`](../PACKAGE.md) for the full `requirements` schema.

The Vercel `skills` CLI also uses a root `skills.json` for one-shot bundle installs: when `npx skills add owner/repo` sees `skills.json`, it installs every skill path listed in the `skills` array. Those paths must be relative, starting with `./` (e.g., `"./skills/write-a-skill"`).

The `requirements.skills` array is currently **flat**. To encode the taxonomy, use a naming convention in `references/DEPENDENCIES.md` and separate `recommended_skills` / `optional_skills` fields only if the harness supports them. If the harness only supports `requirements.skills`, treat the listed entries as required by default and note exceptions in `references/DEPENDENCIES.md`. See [`PACKAGE.md`](../PACKAGE.md) for the full schema.

### `SKILL.md` frontmatter `depends`

The Vercel `skills` CLI supports an optional `depends` field in `SKILL.md` frontmatter. When a user selects a skill for install, the CLI resolves and installs every dependency listed in `depends` first.

Use `depends` for **required and recommended** skill dependencies that must be present for the skill to work well. Do not include optional dependencies in `depends`; surface them in `references/DEPENDENCIES.md` instead.

Example:

```yaml
---
name: write-a-skill
description: Design partner for creating, reviewing, and updating skills.
depends:
  - detect-project-context
  - decide-skill-shape
  - audit-skill
  - validate-skill-frontmatter
  - review-skill
  - eval-format
  - worker-contract
  - context-reports
  - parse-skill-frontmatter
  - list-available-skills
  - search-skills-registry
  - install-skill
  - run-trigger-evals
metadata:
  author: Wian van der Merwe
  tags: [skill-authoring, conductor, standards]
---
```

`depends` is a harness hint for the Vercel CLI. A skill must still declare its dependencies in `references/DEPENDENCIES.md` and should still run its own self-diagnostics in case `depends` is ignored or only partially satisfied.

### Claude Code / Vercel plugin manifests

For grouping in the Vercel `skills` CLI interactive prompts, declare a plugin manifest:

- `.claude-plugin/plugin.json` — a single plugin at the repository root.
- `.claude-plugin/marketplace.json` — a catalog of multiple plugins in one repository.

Each plugin entry has a `name` used for grouping and a `skills` array of relative paths starting with `./`. The CLI groups skills under their plugin name in the `skills add` and `skills list` prompts.

Example `.claude-plugin/marketplace.json`:

```json
{
  "metadata": { "pluginRoot": "./" },
  "plugins": [
    {
      "name": "Skill authoring",
      "skills": [
        "./skills/write-a-skill",
        "./skills/audit-skill",
        "./skills/validate-skill-frontmatter"
      ]
    },
    {
      "name": "Core tooling",
      "skills": [
        "./skills/detect-project-context",
        "./skills/list-available-skills",
        "./skills/install-skill"
      ]
    }
  ]
}
```

Plugin manifests are a presentation layer, not a replacement for dependency declarations. They help users navigate a large catalog; `depends` and `references/DEPENDENCIES.md` ensure the right skills are installed.

### Frontmatter and `config.yaml` hints

Harness-specific dependency hints can live in `SKILL.md` frontmatter or in a `config.yaml` file. These are **envelope hints**, not the portable core. They tell a specific harness how to wire tools, MCP servers, or sandbox features, but they do not replace the declaration in `skills.json` or `references/DEPENDENCIES.md`.

Examples of harness hints:

- `allowed-tools` / `disallowed-tools` in `SKILL.md` frontmatter for runtime tool scoping.
- `mcp_servers` in `config.yaml` for harness-specific MCP wiring.
- `sandbox_features` in `skills.json` for sandbox capability requests.

A skill must degrade gracefully if the harness ignores these hints. The portable dependency declaration must always be sufficient for a human to install the skill by hand.

---

## Transitive closure rule

When a skill is selected for install, the harness must resolve its full dependency graph.

### Rule

- **Required** dependencies are installed recursively until the closure is complete.
- **Recommended** dependencies are installed by default, but the user may opt out.
- **Optional** dependencies are surfaced only; install only when explicitly selected.
- **Conflicts** fail the install with a clear explanation.

The resolved graph is recorded in `skills.lock` (see [`PACKAGE.md`](../PACKAGE.md)). A skill must check availability at initialization and report one of the states in the self-diagnostics contract below. Even when the harness pre-installs dependencies, network failures, partial installs, or harness-specific loader limits can leave a dependency missing.

---

## Capability bundles

A **capability bundle** is a named group of skills that install together to provide a whole workflow. Bundles are convenience layers for users and harnesses. They are declared in a package manifest or bundle catalog, not inside individual skills.

A bundle should have:

- A clear name that describes the workflow it enables.
- A one-sentence purpose.
- A list of member skills, including the dependencies of each.
- A default expectation: whether recommended dependencies are included by default.

### Examples

A **skill-authoring** bundle might include:

```text
Core skills:
- skill-designer

Required building blocks:
- skill-audit
- frontmatter-validator
- worker-contract
- context-reports

Recommended building blocks:
- skill-search
- eval-generator

Optional:
- prototype (for UI or workflow prototyping before drafting)
```

Other bundles in this repo include **project-workflow** (orchestrate, plan, issue tracking) and **core-tooling** (detection, discovery, install). Bundle members are repo-specific; the important property is that each bundle respects the dependency taxonomy and does not duplicate skills.

### Bundle design principles

- A bundle should be **justified by a real workflow**, not by similarity of topic.
- A bundle should **respect the taxonomy**: include required dependencies recursively, include recommended dependencies by default, and surface optional dependencies.
- A bundle should **not duplicate skills** across nested bundles if the install system already handles transitive closure.
- A bundle should **declare a version** and be locked like any other package.

---

## Self-diagnostics contract

A skill must check its own dependency availability at initialization and report one of three states: `full`, `degraded`, or `blocked`. This contract lets callers and harnesses decide what to do next.

### `full`

All required dependencies and all recommended dependencies are present. The skill can run its full workflow without reduced capability.

Report `full` when:

- Every skill listed as required or recommended is installed and loadable.
- Every required tool, binary, MCP server, and environment variable is available.
- The skill's optional dependencies are either present or irrelevant to the current task.

### `degraded`

All required dependencies are present, but one or more recommended dependencies are missing. The skill can run, but output or experience is reduced.

Report `degraded` when:

- A recommended lookup source is missing, so the skill falls back to a narrower search.
- A recommended building block is missing, so the skill performs a step inline instead of delegating.
- A recommended convenience tool is missing, so the user must supply information manually.

The skill must tell the user what is missing and how the behavior changes. It must not fail silently into degraded mode.

### `blocked`

One or more required dependencies are missing. The skill cannot run.

Report `blocked` when:

- A required skill is not installed or not loadable.
- A required tool, binary, MCP server, or environment variable is missing.
- A required context report or config file cannot be found.

The skill must explain what is missing, why it matters, and how to fix it. It may offer to install the missing dependency if an install skill is available, but it must not proceed without the dependency.

### Reporting format

When a skill reports its state, it should include:

- `status`: `full`, `degraded`, or `blocked`.
- `missing`: a list of missing dependencies and their kind.
- `impact`: a brief explanation of how behavior changes.
- `remediation`: the recommended next step for the user or harness.

Example:

```markdown
Status: degraded
Missing: `search-skills-registry` (recommended), `find-skills` (recommended)
Impact: Local-only skill discovery; third-party skills may be missed.
Remediation: Install the missing skills, or continue with reduced discovery.
```

### Initialization check

A skill should run this check once per session, usually in its initialization phase. The check should be lightweight: it reads the dependency declaration, checks for the presence of each listed skill or capability, and reports the worst applicable state. It should not perform expensive validation or network calls during the check itself.

---

## Examples from this repo

### `write-a-skill`

`write-a-skill` declares its dependencies in `references/DEPENDENCIES.md`. Its required closure is:

```text
write-a-skill
├── detect-project-context
├── decide-skill-shape
├── audit-skill
├── validate-skill-frontmatter
├── review-skill
├── eval-format
├── worker-contract
├── context-reports
└── parse-skill-frontmatter
```

Its recommended default closure is:

```text
write-a-skill
├── list-available-skills
├── search-skills-registry
├── install-skill
└── run-trigger-evals
```

If the user opts out of recommended dependencies, `write-a-skill` runs in `degraded` mode. For example, without `search-skills-registry`, it cannot check whether a similar third-party skill already exists.

A blocked initialization would look like:

```markdown
Status: blocked
Missing: `worker-contract` (required)
Impact: Subagent prompts cannot be composed correctly.
Remediation: Install `worker-contract` before using `write-a-skill`.
```

---

## Related documents

- [`PACKAGE.md`](../PACKAGE.md) — `skills.json`, `skills.lock`, versioning, and lifecycle.
- [`FORMAT.md`](../FORMAT.md) — `SKILL.md` frontmatter and portable core.
- [`patterns/building-block.md`](../patterns/building-block.md) — reusable skills and dependency declaration.
- [`patterns/conductor.md`](../patterns/conductor.md) — how conductors compose building blocks.
- [`fundamentals/structure.md`](./structure.md) — skill layout and reference conventions.
- [`fundamentals/types.md`](./types.md) — choosing skill types and their dependency patterns.
- [`fundamentals/evaluation.md`](./evaluation.md) — testing skills, including dependency failure cases.
- [`PORTABILITY.md`](../PORTABILITY.md) — cross-harness degradation model.

---

## Research basis

- The dependency taxonomy (required, recommended, optional) and transitive closure rules are a synthesis of common package models from npm, Python packaging, and agent-harness skill ecosystems. The explicit degradation contract is our own adaptation to agent workflows, where missing a tool is often recoverable by asking the user.
- The `references/DEPENDENCIES.md` surface and `skills.json` `requirements` object are documented in the project's own [`PACKAGE.md`](../PACKAGE.md) and [`patterns/building-block.md`](../patterns/building-block.md) as canonical declaration surfaces.
- The capability-bundle concept is our own framing for grouping agent skills into workflow-ready sets, informed by observed bundles in Claude Code, Cursor, and Codex ecosystems.
- The `full` / `degraded` / `blocked` self-diagnostics contract is our own practice, designed to let conductor skills make informed decisions about whether to proceed, fall back, or stop.
- The `write-a-skill` example is drawn directly from `skills/write-a-skill/SKILL.md` in this repository.
