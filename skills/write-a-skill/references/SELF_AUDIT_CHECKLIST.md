# Self-audit checklist

Before presenting any design to the user, the `write-a-skill` conductor must run this lightweight self-audit. If any check fails, fix the design or escalate to the user with a recorded reason before drafting.

## Principle checks

- [ ] **One core objective.** The proposed skill owns exactly one problem domain.
- [ ] **Explicit out-of-scope.** The skill declares what it does not handle.
- [ ] **Explicit dependencies.** Required tools, APIs, skills, MCP servers, and environment variables are listed.
- [ ] **No secrets in files.** Secrets are referenced via environment variables or secure stores, not hardcoded.
- [ ] **Destructive actions confirmed.** Any mutation requires explicit user confirmation.
- [ ] **Harness-agnostic and project-agnostic.** Global skills contain no hardcoded harness tools, project paths, or vendor APIs.
- [ ] **No hidden assumptions.** All assumptions are declared, and the skill fails closed when required capabilities are missing.
- [ ] **Appropriate skill type.** The type matches the shape of the problem.
- [ ] **Form matches domain.** The mix of instructions and guidelines is chosen for the right reason.
- [ ] **Steps have completion criteria.** Every phase ends with a checkable condition.
- [ ] **Description is trigger-rich.** The description lists realistic triggers and front-loads a leading word.
- [ ] **No duplicate triggers.** The same keyword does not trigger multiple unrelated skills.
- [ ] **Leading word used.** A compact leading word anchors behavior where the agent's priors are strong.
- [ ] **Negation pairs.** Every "do not" is paired with a positive directive.
- [ ] **No vague guideline soup.** Every guideline is paired with a principle, criterion, or leading word.
- [ ] **No no-op lines.** Every line changes behavior versus the default.
- [ ] **Progressive disclosure.** Detail lives in `references/` or external standards, not in `SKILL.md`.
- [ ] **State and reports documented.** If stateful, the skill documents where state lives, its schema, and resumption logic.
- [ ] **Worker contract defined.** Subagents use a structured return format and do not ask users directly.
- [ ] **Scripts for deterministic logic.** Repeatable logic is pushed into scripts, not AI inference.
- [ ] **Review cadence planned.** Trigger and behavioral evals are documented or planned.

## Anti-over-complication checks

For every proposed feature, ask:

- Does this need to be a skill, or could a script, MCP server, extension, or prompt template solve it?
- Does this skill need all proposed features, or can the first version be smaller?
- Are proposed building blocks actually reusable, or are they premature abstraction?
- Does the skill need state, or can it be stateless?
- Does it need config, or can it detect everything?
- Does it need to delegate, or is the work small enough to do inline?
- Does it need a new subagent, or can an existing one be reused?
- Does it need a dedicated reference file, or can it fit in `SKILL.md`?

If any of these checks suggest a simpler alternative, default to the simpler alternative and escalate to the user if the simpler path is unacceptable.

## Recording the result

The self-audit result is written to `{context}/skill-review/{skill-name}-self-audit.md` with the following structure:

```markdown
---
skill: skill-name
version: "1.0"
timestamp: ISO-8601
result: pass | fail | override
---

## Summary
One-sentence verdict.

## Checks
- [ ] Criterion — observation
- ...

## Overrides
- Criterion — reason for override — user approval yes/no

## Blockers
Any failed checks that must be resolved before drafting.
```
