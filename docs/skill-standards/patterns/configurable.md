# Configurable

Configuration lets a skill adapt to a project without changing its core contract. It separates invariant principles from project-specific preferences.

---

## Config location

Configuration lives at the project level:

```text
{project-root}/.agents/config/
├── shared.yaml              # cross-skill settings
└── {skill-name}.yaml        # skill-specific config + notes
```

Shared config is loaded first. Skill-specific config overrides shared values. A skill should document which shared keys it reads.

User-level skills write project-level config. Do not store project context in user-level settings.

---

## Config + notes structure

```yaml
preferences:
  issue_tracker: github
  output_format: md

notes:
  - text: "GitHub API requires a token; use GITHUB_TOKEN."
    category: gotcha
    added: "2026-06-26"
```

- `preferences` are machine-readable settings.
- `notes` are human-readable operational memory.

Note categories:

| Category | Purpose |
|----------|---------|
| `workaround` | A non-obvious method that worked. |
| `preference` | User's stated preference. |
| `assumption` | Something taken as true that could change. |
| `gotcha` | A trap the skill hit. |
| `decision` | A deliberate choice with rationale. |

Only record information that changes how a future invocation behaves. If the information is only useful for the current session, do not add it.

---

## Bootstrap routine

A configurable skill follows a load-detect-validate-resolve-persist-execute-curate routine:

1. **Load** existing shared config and skill-specific config.
2. **Detect** the environment.
3. **Validate** whether config matches the environment and is sufficient.
4. **Resolve** ambiguity by asking the user.
5. **Persist** choices and reasoning.
6. **Execute** using resolved config.
7. **Curate** notes afterward.

This routine should be documented, but it does not need to appear verbatim in every skill. A building-block `config-pattern` skill can hold the shared convention; individual skills reference it.

---

## Detection before config

Prefer detection over configuration. Ask the user only when detection is ambiguous or impossible.

| Detect | Ask |
|--------|-----|
| Package manager from lockfiles. | Preferred verification method when multiple are available. |
| Issue tracker from `git remote`. | Custom workflow for an unsupported tracker. |
| Project key from branch name. | Project key when no branch or convention exists. |

This reduces friction and makes skills more pluggable.

---

## Adding config without bloating SKILL.md

Config detail should not live in `SKILL.md`. Use progressive disclosure:

- `SKILL.md` states that the skill is configurable and which keys it reads.
- `references/CONFIG_PATTERN.md` documents the full schema, defaults, and examples.
- A shared `config-pattern` building-block skill can hold cross-cutting config conventions.

Example from `SKILL.md`:

> This skill reads config from `.agents/config/{skill-name}.yaml` and shared settings from `.agents/config/shared.yaml`. See `references/CONFIG_PATTERN.md` for the full schema.

---

## Never overwrite without asking

Existing config represents user decisions. A skill must:

- Read existing config before proposing changes.
- Present the current value and the proposed change.
- Ask before overwriting, unless the user has previously approved automatic updates.

This applies to preferences and notes.

---

## Research basis

- The **configurable** pattern (separating invariant principles from project-specific preferences) is our own, but it is supported by the research finding that skills must adapt to different projects and users without changing their core contract.
- The `.agents/config/` layout and the distinction between skill-specific config and shared config are our own convention.
- The **bootstrap routine** (load-detect-validate-resolve-persist-execute-curate) is our own synthesis, informed by the research on initialization and context management.
- The **detection before config** rule is our own practice, aligned with the research emphasis on reducing friction and making skills pluggable.
- The note categories (`workaround`, `preference`, `assumption`, `gotcha`, `decision`) are our own taxonomy.
---

## Config schema conventions

- Use lowercase, snake_case keys.
- Group related keys under namespaces.
- Provide sensible defaults.
- Document required vs optional keys.
- Keep secrets out of config files; reference environment variables instead.
