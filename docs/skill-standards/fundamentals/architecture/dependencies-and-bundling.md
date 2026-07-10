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

## Tool categories

Dependencies are not limited to other skills. A skill may depend on any of the following tool categories:

| Category | Examples |
|---|---|
| **Skill adapters** | `github-pr-adapter`, `sonarcloud-adapter`, `jira-adapter` |
| **MCP tools / servers** | `github_get_pull_request_reviews`, SonarQube MCP, Jira MCP |
| **Native binaries** | `gh`, `git`, `curl`, `jq` |
| **Direct APIs** | Provider REST or GraphQL endpoints |
| **Harness tools** | Built-in browser, file system, search, shell |
| **Manual fallback** | User input, CSV, markdown files |

Each category should be declared in `references/DEPENDENCIES.md` and, where applicable, in `skills.json`. A skill must not report a source as "unavailable" if a configured tool in any of these categories could fulfill the same capability. See [tooling-awareness.md](./tooling-awareness.md) for the capability-first approach to tool selection.

---

## Lazy dependency evaluation

A skill does not have to check every declared dependency at initialization. It can check **required** dependencies eagerly and **recommended** or **optional** dependencies **lazily**, only when the specific feature or method that needs them is selected.

This avoids overwhelming the user with setup decisions for tools they may never use. It also keeps the skill lightweight in projects that only exercise a subset of its capabilities.

### When to use lazy evaluation

- The skill has multiple independent methods or branches.
- Each method has its own tooling catalog (e.g., UI capture, API capture, code snapshot).
- The user should only be asked about tooling for the method actually being used.

### When to use eager evaluation

- The dependency is **required** for the skill to function at all.
- The dependency is used on the main happy path and has no acceptable fallback.
- Checking it early prevents a later hard stop after the user has already invested effort.

### Lazy evaluation rules

1. **Check required dependencies at initialization.** If a required dependency is missing, report `blocked` and stop.
2. **Evaluate recommended/optional dependencies only when the relevant branch or method is chosen.** If a recommended dependency is missing for that path, report `degraded` for that path and explain the impact.
3. **Offer remediation for the specific path.** Do not ask the user to configure unrelated tooling. For example, a UI baseline should only ask about browser automation; it should not ask about API clients or test runners.
4. **Persist the user's choice.** If the user declines a recommended tool for a path, record that preference so the same question is not repeated on every run.
5. **Never silently degrade.** The skill must tell the user what is missing and what fallback is being used.

### Example

A `baseline` skill checks at initialization that `git` and `python3` are present. If they are, initialization reports `full`.

Later, when the user baselines a UI route, the skill selects `ui-browser` and checks for browser automation tooling. If none is found, it reports:

```text
Status: degraded (for method ui-browser)
Missing: browser automation tool or MCP (recommended)
Impact: UI capture will fall back to manual screenshots.
Remediation: Configure a Playwright MCP, use a project-local test runner, or proceed with manual fallback.
```

The skill then asks the user which path to take. It does not bring up API or test tooling because those are irrelevant to this baseline.

### Designing for lazy evaluation

When declaring dependencies, document which path triggers each recommended or optional dependency. In `references/DEPENDENCIES.md`, group recommended tools by the method or branch that uses them. In `config.yaml`, reserve a `tooling` or `preferences` section for per-path choices so the skill can remember them.

A skill that uses lazy evaluation should still declare its full dependency surface in `skills.json` and `references/DEPENDENCIES.md`. Laziness is a runtime behavior, not a way to hide dependencies.

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

For packages, the `requirements.skills` array in `skills.json` is the machine-readable declaration. It is used for transitive closure, policy gates, and lock-file generation. See [`PACKAGE.md`](../../reference/package.md) for the full `requirements` schema.

The Vercel `skills` CLI also uses a root `skills.json` for one-shot bundle installs: when `npx skills add owner/repo` sees `skills.json`, it installs every skill path listed in the `skills` array. Those paths must be relative, starting with `./` (e.g., `"./skills/authoring/write-a-skill"`).

The `requirements.skills` array is currently **flat**. To encode the taxonomy, use a naming convention in `references/DEPENDENCIES.md` and separate `recommended_skills` / `optional_skills` fields only if the harness supports them. If the harness only supports `requirements.skills`, treat the listed entries as required by default and note exceptions in `references/DEPENDENCIES.md`. See [`PACKAGE.md`](../../reference/package.md) for the full schema.

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
  tags: [authoring, conductor, skill-design, standards]
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
        "./skills/authoring/write-a-skill",
        "./skills/authoring/audit-skill",
        "./skills/tooling/validate-skill-frontmatter"
      ]
    },
    {
      "name": "Core tooling",
      "skills": [
        "./skills/core/detect-project-context",
        "./skills/tooling/list-available-skills",
        "./skills/tooling/install-skill"
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

The resolved graph is recorded in `skills.lock` (see [`PACKAGE.md`](../../reference/package.md)). A skill must check availability at initialization and report one of the states in the self-diagnostics contract below. Even when the harness pre-installs dependencies, network failures, partial installs, or harness-specific loader limits can leave a dependency missing.

---

## Capability bundles

A **capability bundle** is a named group of skills that install together to provide a whole workflow. Bundles are convenience layers for users and harnesses. They are declared in a package manifest or bundle catalog, not inside individual skills.

A bundle should have:

- A clear name that describes the workflow it enables.
- A one-sentence purpose.
- A list of member skills, including the dependencies of each.
- A default expectation: whether recommended dependencies are included by default.

### Examples

An **authoring** bundle might include:

```text
Core conductor:
- write-a-skill

Required building blocks:
- audit-skill
- validate-skill-frontmatter
- worker-contract
- context-reports

Recommended building blocks:
- list-available-skills
- search-skills-registry
- run-trigger-evals

Optional:
- prototype (for UI or workflow prototyping before drafting)
```

Other bundles in this repo include **workflow** (orchestrate, plan, issue tracking), **core** (detection, shared contracts, reports), and **tooling** (discovery, install, validation). Bundle members are repo-specific; the important property is that each bundle respects the dependency taxonomy and does not duplicate skills.

### Bundle design principles

- A bundle should be **justified by a real workflow**, not by similarity of topic.
- A bundle should **respect the taxonomy**: include required dependencies recursively, include recommended dependencies by default, and surface optional dependencies.
- A bundle should **not duplicate skills** across nested bundles if the install system already handles transitive closure.
- A bundle should **declare a version** and be locked like any other package.

---

## Self-diagnostics contract

A skill must check its own dependency availability at initialization and report one of three states: `full`, `degraded`, or `blocked`. This contract lets callers and harnesses decide what to do next.

### `full`

All required dependencies are present. The skill can run its core workflow without reduced capability.

Report `full` at initialization when:

- Every required skill is installed and loadable.
- Every required tool, binary, MCP server, and environment variable is available.

If the skill uses lazy evaluation, `full` at initialization does **not** imply that every recommended or optional dependency is present. It only means the required surface is satisfied and the skill can proceed to method/path selection.

Report `full` at runtime for a specific path when:

- All required dependencies are present.
- All recommended dependencies needed for that path are present.
- Optional dependencies are either present or irrelevant to the current path.

### `degraded`

All required dependencies are present, but a recommended or optional dependency needed for the current path is missing. The skill can still run, but output or experience is reduced for that path.

Report `degraded` when:

- A recommended lookup source is missing, so the skill falls back to a narrower search.
- A recommended building block is missing, so the skill performs a step inline instead of delegating.
- A recommended convenience tool is missing, so the user must supply information manually.
- A recommended tool for a lazily evaluated method is missing, so the skill must switch to a fallback method or manual mode.

The skill must tell the user what is missing, how behavior changes, and which path triggered the check. It must not fail silently into degraded mode.

When the skill uses lazy evaluation, report `degraded` for the specific method or branch, not for the entire skill. For example, `degraded (ui-browser)` is clearer than `degraded` alone.

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
- `scope`: `initialization` or the specific method/branch the check applies to (e.g., `ui-browser`).
- `missing`: a list of missing dependencies and their kind.
- `better_tool_available`: a list of configured-but-unused tools that could improve a specific capability (optional but recommended for tool-aware skills).
- `impact`: a brief explanation of how behavior changes.
- `remediation`: the recommended next step for the user or harness.

For tool-aware skills, include `better_tool_available` when the skill is using a weaker source for a capability while a better tool is configured. For example, a PR-report skill using a `github-pr-adapter` while `github_get_pull_request_reviews` via MCP is available should report the better tool and offer to switch.

Example — eager check at initialization:

```markdown
Status: full
Scope: initialization
Missing: none
Better tool available: none
Impact: Core workflow can proceed.
Remediation: none.
```

Example — lazy check for a specific method:

```markdown
Status: degraded
Scope: ui-browser
Missing: `playwright-mcp` (recommended)
Better tool available: none
Impact: UI capture will fall back to manual screenshots.
Remediation: Configure a browser automation MCP, switch to a test-runner baseline, or proceed with manual fallback.
```

Example — a better tool is available for a capability:

```markdown
Status: degraded
Scope: pr-report
Missing: none
Better tool available: `github_get_pull_request_reviews` (MCP) for top-level review bodies
Impact: Current adapter returns partial review data; full review bodies are available via MCP.
Remediation: Confirm and I will fetch top-level reviews from the MCP tool instead.
```

### Initialization check

A skill should run this check once per session, usually in its initialization phase. The check should be lightweight: it reads the dependency declaration, checks for the presence of each required skill or capability, and reports the worst applicable state. It should not perform expensive validation or network calls during the check itself.

For skills that use lazy evaluation, the initialization check covers only required dependencies. Recommended and optional dependencies are checked later, when the relevant method or branch is selected. The skill should still document the full dependency surface in `references/DEPENDENCIES.md` so that the lazy checks are predictable.

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

If the user opts out of recommended dependencies, `write-a-skill` runs in `degraded` mode. For example, without `search-skills-registry`, it cannot check whether a similar third-party skill already exists. Because these are general-purpose recommended dependencies, this degradation is reported eagerly at initialization.

A skill with lazy evaluation (such as `baseline`) would report `full` at initialization if only its required dependencies are present, then report `degraded` later when a specific method lacks tooling.

A blocked initialization would look like:

```markdown
Status: blocked
Missing: `worker-contract` (required)
Impact: Subagent prompts cannot be composed correctly.
Remediation: Install `worker-contract` before using `write-a-skill`.
```

---

## Related documents

- [`PACKAGE.md`](../../reference/package.md) — `skills.json`, `skills.lock`, versioning, and lifecycle.
- [`FORMAT.md`](../../reference/format.md) — `SKILL.md` frontmatter and portable core.
- [`patterns/building-block.md`](../../patterns/building-block.md) — reusable skills and dependency declaration.
- [`patterns/conductor.md`](../../patterns/conductor.md) — how conductors compose building blocks.
- [`fundamentals/core/structure/`](../core/structure/) — skill layout and reference conventions.
- [`fundamentals/core/types/`](../core/types/) — choosing skill types and their dependency patterns.
- [`evaluation.md`](./evaluation.md) — testing skills, including dependency failure cases.
- [`PORTABILITY.md`](../../patterns/portability.md) — cross-harness degradation model.

---

## Research basis

See [SOURCES.md](../../reference/sources.md).
