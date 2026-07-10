# Frontmatter

A skill declares its identity in the frontmatter of `SKILL.md`. See [`../../../reference/format.md`](../../../reference/format.md) for the full portable frontmatter schema and [`../../../reference/package.md`](../../../reference/package.md) for package-level metadata. The rest of this document covers the structural role of frontmatter and how to write a strong description.

```yaml
---
name: skill-name
description: What this skill does and when to trigger it.
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
- `invocation` is required and must be `model-invoked` or `user-invoked`.
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

The frontmatter must declare the invocation mode explicitly. Use `invocation: model-invoked` or `invocation: user-invoked`. For harnesses that only recognize the boolean flag, `disable-model-invocation: true` is equivalent to `invocation: user-invoked`. If both fields are present, they must agree.

If a harness encounters a `SKILL.md` without an explicit `invocation`, it may fall back to a default, but that behavior is harness-specific and not guaranteed by this standard. Always declare `invocation` explicitly for portability.

---

## Description as a context pointer

The `description` is the most important field in `SKILL.md`. It is the context pointer that causes the agent to load the skill. See [`../../../reference/format.md`](../../../reference/format.md) for the full portable frontmatter description guidance, and [`../../../reference/trigger-evals.md`](../../../reference/trigger-evals.md) for how to test descriptions with trigger evals.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
