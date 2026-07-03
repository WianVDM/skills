# Script curation

A skill should prefer deterministic scripts over AI inference for repeatable decisions. Scripts reduce reliance on inference: they make behavior predictable, testable, and fast.

## When to use scripts

Use a script when the skill needs to:

- Detect the environment or project type.
- Validate a convention or schema repeatedly.
- Check for hardcoded paths, tool names, or assumptions.
- Transform data in a stable way.
- Enforce naming or structure rules.

Do not use a script when the task requires judgment, synthesis, or natural language understanding that is better done by the agent.

## Script conventions

Scripts used by skills should be:

- **Deterministic.** Given the same input and environment, they produce the same result. No randomness or undocumented side effects.
- **Documented.** Include a docstring or header explaining purpose, inputs, and outputs.
- **Safe.** Do not perform destructive operations unless explicitly designed and labeled. Prefer read-only inspection.
- **Isolated.** They should not ask the user for input. The skill collects input and passes it as arguments or environment variables.
- **Failure-explicit.** Exit with a non-zero status and a clear message on failure.

## Scripts-first mindset

Before building a skill, ask which parts of its work could be moved from AI reasoning into deterministic checks. The more repeatable logic lives in scripts, the leaner and more reliable the skill becomes.

## Script lifecycle

Scripts live in `scripts/`. They should be small, focused, and reusable. If a script is useful to multiple skills, consider extracting it into a shared script or an internal skill.
