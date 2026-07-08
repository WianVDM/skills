# Common mistakes

These are the failure modes that make skills unreliable, bloated, or ineffective. Avoid them. When reviewing a skill, check it against this list.

---

## Sprawl

A skill that is simply too long. Even if every line is live and unique, the agent has to wade through too much before it can act. Attention thins across the excess.

**Causes**

- Reference material left in `SKILL.md`.
- Multiple unrelated concerns merged into one skill.
- Examples that explain more than they illustrate.

**Cure**

Push reference behind context pointers. Split by branch or sequence so each path carries only what it needs.

---

## Sediment

Stale layers of content that accumulate because adding feels safe and removing feels risky. The skill slowly drifts out of alignment with its actual behavior.

**Causes**

- No pruning discipline.
- Notes and examples added for one-off cases and never reviewed.
- Version changes that leave old guidance in place.

**Cure**

Review the skill after any significant behavior change. Delete guidance that no longer applies.

---

## Duplication

The same meaning expressed in more than one place. It costs maintenance, tokens, and inflates a concept's prominence beyond its real rank.

**Causes**

- Shared conventions copied into every skill.
- The same example repeated in `SKILL.md` and `references/EXAMPLES.md`.
- Synonyms restating the same branch in the description.

**Cure**

Maintain a single source of truth. Extract shared reference into a building-block skill or shared reference file.

---

## No-op instructions

A line that changes nothing because the model already does it by default. See [form-and-style.md](./form-and-style.md) for the no-op test, examples, and how to replace weak guidance with stronger leading words or checkable criteria.

---

## Vague completion criteria

A step ends with fuzzy language like “understand the problem” or “produce a plan.” See [form-and-style.md](./form-and-style.md) for how to write strong, checkable completion criteria and avoid premature completion.

---

## Over-reliance on priors

Assuming the agent already knows what you mean. This works for well-known tasks and fails for domain-specific or ambiguous ones.

**Examples**

- “Write a summary document” — the agent probably knows the shape.
- “Follow clean architecture” — the agent's version may not match yours.
- “Be pragmatic” — too vague; every agent has a different prior.

**Cure**

Use leading words where priors are strong. Define terms where they are domain-specific. Add steps where the agent would vary.

---

## Upfront setup overload

A skill that forces the user to configure every recommended or optional tool before it can do anything useful.

**Causes**

- Checking all recommended dependencies eagerly at initialization.
- Asking the user to decide on tooling for branches or methods they may never use.
- Treating recommended tooling as if it were required.

**Cure**

Use **lazy dependency evaluation**: check required dependencies at initialization, and check recommended or optional dependencies only when the specific method or branch that needs them is selected. Offer remediation only for the active path.

---

## Hidden dependencies

The skill relies on a tool, API, MCP server, convention, or environment variable without declaring it.

**Examples**

- Calling `gh issue create` without stating that GitHub CLI access is required.
- Reading `.env` files without mentioning it.
- Assuming a specific test runner exists.

**Cure**

Declare dependencies explicitly. Detect the environment or ask the user when uncertain.

---

## Adapter tunnel vision

The skill treats its own built-in adapters, scripts, or preferred paths as the only way to fulfill a capability, ignoring better tools that are already configured or available. See [tooling-awareness.md](./tooling-awareness.md) for the capability-first alternative.

**Symptoms**

- Reconstructing data from partial outputs instead of using a better tool.
- Declaring a source “unavailable” when an MCP server or native tool could reach it.
- Recording limitations and moving on without suggesting alternatives.
- Marking a section complete while a better tool sits unused.

**Cure**

Design each capability step as "what outcome do I need?" first, then "which available tool gives the best result?" Route through the best tool and disclose the choice.

---

## Manual in disguise

The skill lists every keystroke and command. See [form-and-style.md](./form-and-style.md) for the full anti-pattern and how to state intent instead of mechanics.

---

## Guideline soup

A skill that says many true things but gives the agent no purchase point. See [form-and-style.md](./form-and-style.md) for how to turn vague guidance into specific principles, leading words, or checkable criteria.

---

## Wrong type for the job

Forcing a skill into a shape that does not match the problem.

**Examples**

- A conductor skill that does all the work inline.
- A building block that tries to coordinate other skills.
- A building-block skill that includes a workflow.

**Cure**

Revisit [types.md](./types.md). Choose the type that matches the work.

---

## Over-configuring

Adding config for things that should be inferred or that do not change behavior. Config is not free: it adds decision points and maintenance surface.

**Cure**

Only persist choices that change how future invocations behave. Default to detection and inference.

---

## Under-declaring scope

A skill that does not clearly say what is out of scope. The agent drifts into neighboring tasks.

**Cure**

Include an explicit “Out of scope” section in `SKILL.md`.

---

## Mixing invocation concerns

A user-invoked skill that tries to behave like a model-invoked skill, or vice versa.

**Examples**

- A user-invoked skill with a long model-facing description.
- A model-invoked skill that only makes sense when the user explicitly types it.

**Cure**

Choose the invocation mode that matches the skill's consumer. If the skill is meant to be reached by the agent or other skills, make it model-invoked and write a trigger-rich description. If it is meant to be reached only by the user typing its name, make it user-invoked and keep the description concise and human-facing. Do not try to serve both audiences with one description; split the skill if both modes are genuinely needed.

---

## Premature completion

Ending a step before it is genuinely done because the agent's attention slips toward being finished. See [form-and-style.md](./form-and-style.md) for how completion criteria and post-completion steps cause or prevent this.

---

## Research basis

See [SOURCES.md](../SOURCES.md).
