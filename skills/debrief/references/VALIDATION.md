# Validation and Testing

Before considering the `debrief` skill complete, validate its structure, content, and behavior.

---

## Structural validation

- `name` matches the directory name.
- `description` is under 1024 characters and includes triggers.
- `SKILL.md` focuses on intent and workflows.
- References are in `references/` and linked correctly.
- Subagent docs are in `subagents/`.
- Tracker adapters are in `references/trackers/`.
- `README.md` exists.

---

## Content validation

- `SKILL.md` uses harness-agnostic language.
- No tool-specific commands or slash commands in the main file.
- Tracker-specific details live in tracker adapter docs.
- Output template uses the unified context convention.
- Config schema is documented.
- Incremental checkpointing and recontextualization are documented.

---

## Reference file validation

- `DEPENDENCIES.md` and `CONTEXT_REPORTS.md` exist and are linked from `SKILL.md` and other reference files.
- No project-specific URLs, emails, or identifiers appear in examples, config templates, or tracker setup snippets.
- All tracker adapters use harness-agnostic language (they describe MCP server env vars, not a specific client's config file format).
- Version is consistent across `SKILL.md`, report templates, and state templates.
- Baseline integration references the correct report path: `.agents/context/baseline/{scope}-{branch}.md`.
- Subagent docs reference `references/WORKER_CONTRACT.md`.
- Examples use the current report schema (`version: 3`, `generated_at`, `consumed_context`).

---

## Behavioral validation

Walk through these scenarios:

1. **Happy path** — ticket key provided, Jira configured, baseline succeeds.
2. **Branch inference** — no key provided, branch name contains ticket key.
3. **No tracker** — no issue tracker configured, user provides manual context.
4. **Ambiguous ticket** — ticket lacks acceptance criteria, skill forms and challenges assumptions.
5. **Baseline failure** — baseline subagent returns `needs_input` or fails.
6. **Delta mode** — existing debrief is recent, skill reuses and updates it.

For each scenario, verify:

- The skill knows what to do first.
- It asks the user only when necessary.
- It persists useful information.
- It produces artifacts in the right place.
- It handles failures gracefully.

---

## Security validation

- No plaintext secrets in skill files or example configs.
- Tokens are referenced via env vars.
- Session files are stored in context, not committed.

---

## Review checklist

- [ ] Frontmatter is valid and complete.
- [ ] `SKILL.md` is lean and guideline-oriented.
- [ ] Language is harness-agnostic.
- [ ] Skill type is declared.
- [ ] Config schema is documented.
- [ ] Tracker adapters cover Jira and manual fallback at minimum.
- [ ] Subagent scopes and return contracts are defined.
- [ ] Checkpoint manager scope and usage are defined.
- [ ] Assumption challenging is documented.
- [ ] Baseline integration uses the baseline skill workflow (not a generic subagent prompt).
- [ ] Incremental output and phase checklist are documented.
- [ ] Output paths use `.agents/context/debrief/{key}-{slug}.md`.
- [ ] Examples are included and globally applicable.
- [ ] `README.md` exists for human maintainers.
