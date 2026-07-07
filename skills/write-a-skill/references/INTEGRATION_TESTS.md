# Integration tests

This reference documents how `write-a-skill` invokes each of its dependency skills. Use it to prevent interface drift and to write integration tests.

## Conventions

- All building-block scripts are run with `python {skill}/scripts/{script}.py`.
- All scripts support `--json` for structured output.
- Conductor skills (`decide-skill-shape`, `review-skill`) are invoked by name and produce context reports; they do not ship a CLI script.
- Vocabulary skills (`eval-format`, `worker-contract`, `context-reports`) provide schemas and contracts; they are not invoked as scripts.

## detect-project-context

**Script:** `skills/detect-project-context/scripts/detect-project-context.py`

**Invocation:**

```bash
python skills/detect-project-context/scripts/detect-project-context.py --start . --json
```

**Return code:** `0` always (falls back gracefully).

**Output schema:**

```json
{
  "project_root": "/path/to/project",
  "marker": ".agents",
  "confidence": "high",
  "recommended_skills_dir": "/path/to/project/.agents/skills",
  "recommended_context_dir": "/path/to/project/.agents/context",
  "recommended_config_dir": "/path/to/project/.agents/config",
  "skills_dir_candidates": [...],
  "context_dir_candidates": [...],
  "config_dir_candidates": [...]
}
```

## list-available-skills

**Script:** `skills/list-available-skills/scripts/list-available-skills.py`

**Invocation:**

```bash
python skills/list-available-skills/scripts/list-available-skills.py --project-root . --json
```

**Return code:** `0` always.

**Output schema:**

```json
{
  "project_scope": [...],
  "user_scope": [...],
  "skills": [
    {"name": "...", "path": "...", "invocation": "...", "version": "...", "tags": [...]}
  ],
  "errors": [...]
}
```

## search-skills-registry

**Script:** `skills/search-skills-registry/scripts/search-skills-registry.py`

**Invocation:**

```bash
python skills/search-skills-registry/scripts/search-skills-registry.py "lint typescript" --project-root . --json
```

**Return code:** `0` on success; `0` on registry errors with errors reported in JSON.

**Output schema:**

```json
{
  "query": "lint typescript",
  "registries": [...],
  "results": [
    {
      "source": "skills-sh",
      "name": "lint-ts",
      "description": "...",
      "url": "...",
      "trust_signals": {},
      "install_command": "install-skill lint-ts --source https://..."
    }
  ],
  "errors": [...]
}
```

## install-skill

**Script:** `skills/install-skill/scripts/install-skill.py`

**Invocation:**

```bash
python skills/install-skill/scripts/install-skill.py example-skill --source /path/to/example-skill --scope project --yes --json
```

**Return code:** `0` on installed; `1` on blocked or error.

**Output schema:**

```json
{
  "installed": true,
  "skill_name": "example-skill",
  "target_scope": "project",
  "installed_path": "/path/to/project/.agents/skills/example-skill"
}
```

**Confirmation contract:** without `--yes`, the script returns `"installed": false` and a reason. The conductor must obtain explicit user approval before passing `--yes`.

## parse-skill-frontmatter

**Script:** `skills/parse-skill-frontmatter/scripts/parse-skill-frontmatter.py`

**Invocation:**

```bash
python skills/parse-skill-frontmatter/scripts/parse-skill-frontmatter.py skills/example-skill/SKILL.md --json
```

**Return code:** `0` on success; `1` on file error.

**Output schema:**

```json
{
  "name": "example-skill",
  "description": "...",
  "version": "1.0.0",
  "invocation": "model-invoked",
  "depends": [...],
  "metadata": {
    "author": "...",
    "tags": [...],
    "verification_level": "declared"
  }
}
```

## validate-skill-frontmatter

**Script:** `skills/validate-skill-frontmatter/scripts/validate-skill-frontmatter.py`

**Invocation:**

```bash
python skills/validate-skill-frontmatter/scripts/validate-skill-frontmatter.py skills/example-skill/SKILL.md --json
```

**Return code:** `0` on valid; `1` on invalid.

**Output schema:**

```json
{
  "valid": true,
  "errors": []
}
```

## audit-skill

**Script:** `skills/audit-skill/scripts/audit-skill.py`

**Invocation:**

```bash
python skills/audit-skill/scripts/audit-skill.py skills/example-skill --json
```

**Return code:** `0` always.

**Output schema:**

```json
{
  "skill": "example-skill",
  "summary": {"blockers": 0, "warnings": 0, "suggestions": 0, "overall": "PASS"},
  "findings": [...],
  "remediation": [...]
}
```

## run-trigger-evals

**Script:** `skills/run-trigger-evals/scripts/run-trigger-evals.py`

**Invocation:**

```bash
python skills/run-trigger-evals/scripts/run-trigger-evals.py skills/example-skill --json
```

**Return code:** `0` on valid generated evals; `1` on invalid.

**Output schema:**

```json
{
  "skill": "example-skill",
  "path": "...",
  "valid": true,
  "errors": [],
  "should_trigger_count": 10,
  "should_not_trigger_count": 5
}
```

## decide-skill-shape

**Invocation:** invoked by name as a conductor. It produces a decision report at `{context}/decide-skill-shape/{key}-decision-report.md`.

## review-skill

**Invocation:** invoked by name as a conductor. It produces audit or remediation reports in `{context}/skill-review/`.

## eval-format, worker-contract, context-reports

These are vocabulary and contract skills. They are consumed by reading their references and schemas, not by running scripts.
