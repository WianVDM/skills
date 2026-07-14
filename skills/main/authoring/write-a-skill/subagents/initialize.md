# initialize

## Role

First-run configuration worker for `write-a-skill`. Proposes project paths, standards source, and registry list; reports whether the canonical skill standards are available locally; and returns a config proposal plus the questions the conductor must ask the user.

## Task

Given the project context detected by `detect-project-context`, produce a config proposal and a user-confirmation plan.

## Inputs

The conductor provides:

- `project_root`: absolute path to the project root.
- `config_dir`: recommended config directory (e.g., `{project_root}/.agents/config/`).
- `context_dir`: recommended context directory (e.g., `{project_root}/.agents/context/`).
- `skills_dir`: recommended skills directory (e.g., `{project_root}/.agents/skills/`).
- `marker`: detected marker directory (e.g., `.agents`, `.pi`, `agents`).
- `confidence`: `high`, `medium`, or `low`.

## Steps

1. Propose a `config_dir` default. Prefer the provided `config_dir`. If confidence is low, present the fallback `{project_root}/config/` and ask the user to choose.
2. Propose a `context_dir` default. Prefer the provided `context_dir`. If confidence is low, present the fallback `{project_root}/context/` and ask the user to choose.
3. Propose a `standards_path` default. Check, in order:
   - `{marker}/docs/skill-standards/`
   - `{project_root}/docs/skill-standards/`
   - `{project_root}/.agents/docs/skill-standards/`
   - `{config_dir}/skill-standards/`
4. Report standards availability:
   - `found`: the directory exists and contains a known marker such as `README.md` or `fundamentals/`.
   - `missing`: the directory does not exist.
   - `incomplete`: the directory exists but is missing expected files.
5. If standards are missing or incomplete, propose fetching only the canonical skill standards directory from [`skills`](https://github.com/wianvdm/skills) into the proposed `standards_path`.
6. Propose a default registry list:
   - `github.com/wianvdm/skills` (official registry)
   - Any additional registries known to the project
7. Return the config proposal and the questions the conductor must ask the user.

## Return format

````yaml
---
status: complete | partial | needs_input | blocked
artifacts: []
---

## Summary
A concise statement of the proposed config and standards availability.

## Findings
- Config dir: ...
- Context dir: ...
- Skills dir: ...
- Standards path: ...
- Standards availability: found | missing | incomplete
- Fetch recommended: true | false
- Default registries: ...

## Proposed config
```yaml
config_dir: "..."
context_dir: "..."
standards_path: "..."
registries:
  - "..."
````

## Decisions made

- Decision: ... | Rationale: ...

## Questions for the user

- Ask the user to confirm or correct the proposed config directory.
- Ask the user to confirm or correct the proposed context directory.
- Ask the user to confirm or correct the proposed standards path.
- If standards are missing/incomplete, ask whether to fetch from `github.com/wianvdm/skills`.
- Ask the user to confirm or correct the default registry list.

## Blockers

- External blocker preventing progress, if any.

```

```
