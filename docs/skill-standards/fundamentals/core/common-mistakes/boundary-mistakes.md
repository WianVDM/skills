# Boundary mistakes

Boundary mistakes are the class of mistakes that make the skill's edges unclear. Dependencies, scope, and invocation mode are not declared, so the agent either stalls or drifts into neighboring work.

---

## Upfront setup overload

A skill that forces the user to configure every recommended or optional tool before it can do anything useful.

**Causes**

- Checking all recommended dependencies eagerly at initialization.
- Asking the user to decide on tooling for branches or methods they may never use.
- Treating recommended tooling as if it were required.

**Cure**

Use **lazy dependency evaluation**: check required dependencies at initialization, and check recommended or optional dependencies only when the specific method or branch that needs them is selected. Offer remediation only for the active path.

See [`../../architecture/dependencies-and-bundling.md`](../../architecture/dependencies-and-bundling.md) for the dependency taxonomy.

---

## Hidden dependencies

The skill relies on a tool, API, MCP server, convention, or environment variable without declaring it.

**Examples**

- Calling `gh issue create` without stating that GitHub CLI access is required.
- Reading `.env` files without mentioning it.
- Assuming a specific test runner exists.

**Cure**

Declare dependencies explicitly. Detect the environment or ask the user when uncertain.

See [`../../architecture/dependencies-and-bundling.md`](../../architecture/dependencies-and-bundling.md) for how to declare dependencies.

---

## Over-configuring

Adding config for things that should be inferred or that do not change behavior. Config is not free: it adds decision points and maintenance surface.

**Cure**

Only persist choices that change how future invocations behave. Default to detection and inference.

---

## Under-declaring scope

A skill that does not clearly say what is out of scope. The agent drifts into neighboring tasks.

**Cure**

Include an explicit "Out of scope" section in `SKILL.md`.

---

## Mixing invocation concerns

A user-invoked skill that tries to behave like a model-invoked skill, or vice versa.

**Examples**

- A user-invoked skill with a long model-facing description.
- A model-invoked skill that only makes sense when the user explicitly types it.

**Cure**

Choose the invocation mode that matches the skill's consumer. If the skill is meant to be reached by the agent or other skills, make it model-invoked and write a trigger-rich description. If it is meant to be reached only by the user typing its name, make it user-invoked and keep the description concise and human-facing. Do not try to serve both audiences with one description; split the skill if both modes are genuinely needed.

See [`../structure/frontmatter.md`](../structure/frontmatter.md) for invocation mode.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
