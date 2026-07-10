# Frontmatter

A skill declares its identity in the frontmatter of `SKILL.md`. See [`../../../reference/format.md`](../../../reference/format.md) for the full portable frontmatter schema and [`../../../reference/package.md`](../../../reference/package.md) for package-level metadata. The rest of this document covers the structural role of frontmatter and how to write a strong description.

```yaml
---
name: skill-name
description: What this skill does and when to trigger it.
metadata:
  author: your-name
invocation: model-invoked
---
```

`version` is optional; add it once the skill is shared, consumed, or versioned.

---

## Naming conventions

- **Skill names**: lowercase, hyphen-separated. Example: `review-code`.
- **Config keys**: lowercase, snake_case. Group related keys under namespaces.
- **Report types**: lowercase, hyphen-separated, matching the directory name.
- **Worker names**: lowercase, role-focused. Example: `investigator.md`.
- **Script names**: lowercase, hyphen-separated, descriptive. Example: `detect-env.py`.

---

## Requirements

- `name` matches the directory name.
- `description` is under 1024 characters.
- The description states what the skill does and when to use it, with trigger keywords.
- `version` is optional; if used, it should follow semantic meaning for schema or behavior changes once the skill is shared or consumed.

---

## Invocation mode

A skill is either **model-invoked** or **user-invoked**. The choice trades two loads:

- **Model-invoked**: the description stays in the agent's context, so the skill can fire autonomously and other skills can reach it. This pays **context load** on every turn. A model-invoked skill is still reachable by the user typing its name.
- **User-invoked**: the description is stripped or marked as human-facing. Only the user can invoke it by name. This pays **cognitive load** — the user must remember it exists. No other skill can reach it.

Choose model-invocation only when the agent or another skill must reach the skill on its own. If it only ever fires by hand, make it user-invoked and pay no context load.

When user-invoked skills multiply past what the user can remember, the cure is a **router skill**: a single user-invoked skill that names the others and when to reach for each. A router skill can only hint; it cannot invoke user-invoked skills on the user's behalf.

---

### Declaring the invocation mode

The frontmatter should declare the invocation mode explicitly. Use `invocation: model-invoked` or `invocation: user-invoked`. For harnesses that only recognize the boolean flag, `disable-model-invocation: true` is equivalent to `invocation: user-invoked`. If both fields are present, they must agree. Model-invoked is the default when neither field is present. Declaring the mode is recommended by the portable core standard; omitting it leaves the default to the harness.

---

## Description as a context pointer

The `description` is not just metadata. It is the top-level **context pointer** that causes the agent to load the skill. Its wording, not just its content, decides when and how reliably the skill fires.

A good description:

- States what the skill does.
- Front-loads the **leading word** or domain.
- Lists one trigger per distinct branch. Synonyms that rename the same branch are duplication — collapse them.
- Includes a reach clause for when another skill needs it, if applicable.

Example:

```yaml
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
```

Weak example:

```yaml
description: Helps with UI reviews.
```

---

### Trigger evals

Test the description with a trigger eval set before finalizing a skill:

- **10 should-trigger queries** — realistic prompts that should load the skill. Include varied phrasing, casual speech, and cases where the user does not name the skill explicitly.
- **10 should-not-trigger queries** — near-miss prompts that share keywords but should *not* load the skill. These are the most valuable cases.

Run the queries against the agent and check which trigger. If activation is unreliable, rewrite the description and test again. Save the eval set in `references/EVAL.md`.

Avoid easy negatives like "write a Fibonacci function" for a UI review skill. Test the boundary, not the obvious miss.

For user-invoked skills, the description is primarily human-facing, but a clarity eval still helps: collect realistic prompts that should and should not lead a human to reach for the skill. The 10/10 numeric target is most critical for model-invoked skills.

See [`../../../reference/trigger-evals.md`](../../../reference/trigger-evals.md) for the trigger eval format.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
