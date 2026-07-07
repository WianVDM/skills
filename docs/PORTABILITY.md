# Portability

## At a glance

This manifesto defines portability as **contract plus degradation rules**: a portable core, canonical install paths, and fallback behavior for harnesses that only support a subset of the standard. It covers plain-markdown export, convention-file fallback, dependency mapping, and minimal-harness injection.

**Read this if:** you want a skill to work across Claude Code, Cursor, Codex, Aider, and future harnesses.

A portable skill standard is not "write once, run everywhere" in the naive sense. It is a **contract plus degradation rules**: define the portable core, define canonical install paths, define fallback behavior for harnesses that do not support the full feature set, and let richer harnesses use the full feature set.

This document specifies the portability model for skills in this library.

---

## The portable core

The portable core of any skill is:

- A `SKILL.md` file with YAML frontmatter and a markdown body.
- Optional sibling directories: `references/`, `subagents/`, `scripts/`, `assets/`.
- Optional package metadata in `skills.json` and `skills.lock`.

A harness that supports this core can load and execute the skill. A harness that does not support some features (e.g., subagents, scripts, or YAML frontmatter) falls back to the parts it does support.

See [docs/skill-standards/FORMAT.md](./skill-standards/FORMAT.md) for the full format specification and [docs/skill-standards/PACKAGE.md](./skill-standards/PACKAGE.md) for the package envelope.

---

## Canonical install paths

The canonical locations for installed skills are:

```text
{project-root}/.agents/skills/          # project-level skills
~/.agents/skills/                     # user-level skills
```

A harness may also read skills from native paths for compatibility:

```text
{project-root}/.claude/skills/
{project-root}/.codex/skills/
{project-root}/.cursor/skills/
~/.claude/skills/
~/.codex/skills/
~/.cursor/skills/
```

Native paths should be **symlinks** or **loader indexes** to the canonical `.agents/skills/` tree where possible. This avoids duplication and keeps the project as the single source of truth.

### Source evidence

- Codex source confirms it scans both `.codex/skills/` and `.agents/skills/` at the project level and user level. https://github.com/openai/codex/blob/98d28aab54ed86714901b6619400598598876dd0/codex-rs/core-skills/src/loader.rs#L303-L395
- Cursor documentation claims support for `.claude/skills/` and `.agents/skills/`, though practitioner reports note that the slash-command UI sometimes only scans `.cursor/skills/`.
- Claude Code uses `.claude/skills/` as its native path.

---

## Convention-file fallback

For harnesses that do not support native skills, the standard defines a **convention-file fallback**:

- `AGENTS.md` or `CONVENTIONS.md` at the project root contains the always-on baseline conventions.
- Skill-like guidance can be copied into a convention file as a fallback, but it loses on-demand loading and routing.

This fallback is the recommended degradation path for minimal harnesses like Aider, which does not have a native skill system but can read markdown files via `/run` and `--read`.

---

## Plain-markdown export mode

For harnesses that do not parse YAML frontmatter, a skill can be exported in **plain-markdown mode**:

- The YAML frontmatter is stripped or summarized in a header comment.
- Identity and routing are provided by an external index (e.g., `skills.json`) or by the file path.
- The body remains the primary guidance.

This mode sacrifices description-driven routing and structured metadata but preserves the core guidance.

---

## Harness compatibility metadata

`skills.json` declares harness compatibility so that a harness can decide whether and how to load a skill:

```json
{
  "compatibility": {
    "harnesses": ["claude-code", "cursor", "codex", "aider"],
    "min_aider_version": "0.75.0",
    "features": [
      "subagents",
      "scripts",
      "context_reports"
    ]
  }
}
```

A harness that does not support a feature can either:

- Ignore the feature and run the skill with degraded behavior.
- Refuse to load the skill and explain which feature is missing.
- Ask the user whether to proceed with degraded behavior.

The default behavior should be **graceful degradation** unless the missing feature is required for safety.

---

## Dependency mapping

Harnesses have different ways of declaring tool scoping and MCP server requirements. The portable standard separates:

- **Dependency declaration** in `skills.json` (`requirements.tools`, `requirements.mcp_servers`, `requirements.binaries`, `requirements.environment_variables`).
- **Runtime tool scoping** in `SKILL.md` frontmatter (e.g., `allowed-tools`, `disallowed-tools`).

A harness maps the portable `requirements` object to its native configuration files:

| Portable field | Claude Code | Codex | Cursor | Aider |
|---|---|---|---|---|
| `tools` | `allowed-tools` frontmatter | `requirements.toml` | native tool config | `--read` / `/run` |
| `mcp_servers` | `mcpServers` setting | `requirements.toml` `[mcp_servers]` | native MCP config | external wrapper |
| `binaries` | capability check | capability check | capability check | shell check |
| `environment_variables` | env var check | env var check | env var check | env var check |

These mappings are approximate: portable dependency declarations describe what the skill needs, while native entries such as `allowed-tools` describe what the harness permits at runtime. The standard intentionally separates declaration from runtime scoping so that harnesses can enforce their own policies.

---

## Degradation rules

When a skill runs in a harness that does not support its full feature set, the following rules apply:

1. **If the harness does not parse YAML frontmatter**, use the plain-markdown export and fall back to file-path routing or `skills.json`.
2. **If the harness does not support subagents**, the conductor should run the worker logic inline, possibly with a shorter context window.
3. **If the harness does not support scripts**, the agent should execute the script logic as plain inference or ask the user to run the script manually.
4. **If the harness does not support context reports**, the skill should write reports to a local file and inform the user.
5. **If a required MCP server is not available**, fail closed or ask the user to configure it.
6. **If a required binary is not available**, fail closed and explain what is missing.
7. **If a recommended capability for the current path is not available**, report `degraded` for that path and offer remediation or a fallback. Do not ask the user to configure unrelated capabilities.
8. **If a recommended capability is missing but the path can still proceed**, continue only after explaining the reduced capability and, if needed, confirming the fallback with the user.

A skill should document its degradation behavior in `references/PORTABILITY.md` or in `README.md`, including whether it uses lazy dependency evaluation for recommended or optional capabilities.

---

## Minimal-harness injection (Aider compatibility)

Aider does not have a native skill system, but it can load markdown files via `--read` and execute scripts via `/run`. The standard supports Aider-compatible injection by:

- Keeping the skill body in plain markdown.
- Avoiding harness-specific frontmatter hints that Aider cannot parse.
- Using scripts for deterministic logic that Aider can run.
- Providing a plain-markdown export or a wrapper script that loads the skill into Aider's context.

The aider-skills third-party project demonstrates one approach to this injection, though it is an early project with limited version support.

---

## Limitations

The following portability concerns are **limited** and are documented as such rather than resolved:

- **Exact trigger thresholds** and false-positive rates for description-driven routing are not published by any harness.
- **Rule-vs-skill precedence** when both apply is not documented as a deterministic rule by any harness.
- **Cursor's handling of skills from `.claude/skills/` or `.codex/skills/`** is inconsistent in current builds; the slash-command UI may not surface them.
- **Future tooling** (Skills Over MCP, OCI artifacts) is not mature enough to be a near-term target.

The standard is **transport-agnostic** so that OCI artifacts, npm packages, and other distribution mechanisms can be added later without changing the core model.

---

## Key takeaways

- The **portable core** is `SKILL.md` + optional sibling directories + `skills.json`/`skills.lock`.
- **Canonical install paths** are `.agents/skills/` at the project and user level; native paths are for compatibility.
- **Degrade gracefully** by stripping frontmatter, inlining subagents, running scripts manually, or writing reports locally.
- **Fail closed** when a required capability (MCP server, binary, environment variable) is missing.
- **Dependency declaration** is portable; **runtime tool scoping** is harness-specific.
- Some details (exact trigger thresholds, rule-vs-skill precedence, inconsistent Cursor behavior) are **accepted limitations**.

## Research basis

- The **portability as contract plus degradation** model is our own design choice, synthesized from the research across Claude Code, Cursor, Codex, Aider, and Hermes.
- **Canonical install paths** (`.agents/skills/`, `~/.agents/skills/`) are a design decision based on the broadest cross-harness path observed in the research, with native-path symlinks allowed for compatibility.
- **Codex** source confirms `.codex/skills/` and `.agents/skills/` are both scanned. https://github.com/openai/codex/blob/98d28aab54ed86714901b6619400598598876dd0/codex-rs/core-skills/src/loader.rs#L303-L395
- **Cursor** docs and practitioner reports inform the native-path compatibility matrix. https://cursor.com/docs/skills
- **Aider** compatibility and the minimal-harness injection path are informed by Aider's `/run` and `--read` surfaces and the aider-skills project. https://aider.chat/docs/
- **Plain-markdown export** and **convention-file fallback** are our own degradation rules, designed to support minimal harnesses.
- **Dependency mapping** to native harness configs is our own layered approach, supported by the research on tool scoping and MCP governance across harnesses.
- **Accepted limitations** are drawn from the research gaps checklist and are explicitly documented rather than hidden.
