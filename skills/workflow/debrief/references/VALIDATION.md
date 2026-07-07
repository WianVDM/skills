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
- Baseline integration references the correct report path: `{context_dir}/baseline/{scope}-{branch}.md`.
- Subagent docs reference `references/WORKER_CONTRACT.md`.
- Examples use the current report schema (`version: 4.0`, `generated_at`, `consumed_context`, `task_type`, `assumptions`, `confidence_gap`).
- Report and state templates include `version: 4.0`.
- Project layout detection is documented.
- Task type classification and duplicate detection are documented.
- Generic artifact discovery and ranking are documented.
- Confidence gap and blocker report are documented.

---

## Trigger evals

Verify the skill is invoked for these phrases and patterns:

- "debrief this ticket"
- "understand this ticket"
- "get context on PROJ-123"
- "PROJ-123" (when no clear next step is given)
- "what is this ticket about?"
- "debrief PROJ-123"
- "context on ticket PROJ-123"

For each trigger, verify:

- The skill identifies the ticket key or asks for it.
- The skill begins Phase 0 (Bootstrap) without requiring additional user direction.
- The skill does not implement, test, or recommend next skills.

---

## Behavioral validation

Walk through these scenarios:

1. **Happy path** — ticket key provided, Jira configured, baseline succeeds.
2. **Branch inference** — no key provided, branch name contains ticket key.
3. **Manual fallback** — no issue tracker configured, user provides manual context.
4. **Ambiguous ticket** — ticket lacks acceptance criteria, skill forms and challenges assumptions.
5. **Vague ticket** — no clear acceptance criteria, skill produces a blocker report.
6. **Baseline failure** — baseline subagent returns `needs_input` or fails.
7. **Duplicate / already implemented** — ticket or PR already exists; skill surfaces it.
8. **Monorepo** — skill detects workspace and scopes codebase search.
9. **Context compaction** — skill resumes from state without restarting.
10. **No git** — skill works without branch inference.
11. **Non-English ticket** — skill preserves original text and works best-effort.
12. **Multiple trackers** — skill allows user to choose or configure multiple trackers.
13. **Delta mode** — existing debrief is recent, skill reuses and updates it in place.

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

- [ ] Frontmatter is valid and complete, including `scope: global` and `invocation: user-invoked`.
- [ ] `disable-model-invocation: true` is set if the skill should be user-invoked only.
- [ ] `SKILL.md` is lean and guideline-oriented.
- [ ] Language is harness-agnostic.
- [ ] Skill type is declared as conductor / orchestrator.
- [ ] Config schema is documented with v4 keys.
- [ ] Tracker adapters cover Jira, GitHub, Linear, and manual fallback at minimum.
- [ ] Subagent scopes and return contracts are defined.
- [ ] Checkpoint manager scope and usage are defined.
- [ ] Assumption challenging is documented with the grilling-session guideline.
- [ ] Baseline integration uses the baseline skill workflow (not a generic subagent prompt).
- [ ] Incremental output and phase checklist are documented.
- [ ] Output paths use `{context_dir}/debrief/{key}-{slug}.md` and `{context_dir}/debrief/{key}-blockers.md`.
- [ ] Project layout detection is documented and implemented.
- [ ] Task type classification and duplicate detection are documented and implemented.
- [ ] Generic artifact discovery and ranking are documented and implemented.
- [ ] Confidence calculation and confidence gap are documented.
- [ ] Examples are included and globally applicable.
- [ ] `README.md` exists for human maintainers.
