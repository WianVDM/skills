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

A line that changes nothing because the model already does it by default. You pay load to state the obvious.

**Test**

Does this line change behavior versus the default?

**Examples**

- “Be thorough.” The agent is already thorough-ish.
- “Think carefully.” The agent already reasons.
- “Consider all options.” Too vague to change behavior.

**Cure**

Replace weak guidance with a stronger leading word or a checkable criterion. If a line does not change behavior, delete it.

---

## Vague completion criteria

A step ends with “understand the problem” or “produce a plan.” The agent declares completion and moves on without doing the work.

**Cure**

Make completion criteria checkable and, where it matters, exhaustive:

- “The ticket key, summary, acceptance criteria, and status are recorded.”
- "A failing test exists for the first behavior and fails for the expected reason."

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

## Hidden dependencies

The skill relies on a tool, API, MCP server, convention, or environment variable without declaring it.

**Examples**

- Calling `gh issue create` without stating that GitHub CLI access is required.
- Reading `.env` files without mentioning it.
- Assuming a specific test runner exists.

**Cure**

Declare dependencies explicitly. Detect the environment or ask the user when uncertain.

---

## Manual in disguise

The skill lists every keystroke and command. The agent becomes a slow script executor.

**Examples**

- “Run `git status`, then `git diff`, then `git log --oneline -5`.”
- “Open file X, scroll to line Y, change Z.”

**Cure**

State intent, not mechanics. Let the agent decide the commands.

---

## Guideline soup

A skill that says many true things but gives the agent no purchase point. It feels wise but produces no consistent behavior.

**Examples**

- “Be thorough. Consider edge cases. Write good tests.”
- “Design good interfaces.”

**Cure**

Turn vague guidance into specific principles, leading words, or checkable criteria.

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

_Failure mode: violating the completion criterion lever._

Ending a step before it is genuinely done, because the agent's attention slips toward being finished. Caused by vague completion criteria or visible post-completion steps that pull the agent forward.

**Lever**

Sharpen the completion criterion first. Only if the criterion is irreducibly fuzzy and you observe the rush, hide the later steps by splitting or delegating.

---

## Research basis

- Most of the failure modes here are our own synthesis of skill-review experience, but they are strongly supported by the research emphasis on context cost, routing reliability, and the risk of "skill hell" (too many bloated or overlapping skills).
- **Sprawl**, **sediment**, and **duplication** are our own terms for the general problem of stale, inflated, or repeated guidance that the research identifies as a primary cause of skill ecosystem quality problems.
- **No-op instructions** and **vague completion criteria** are our own analytical tools, derived from the predictability root virtue and the observation that agents often rush or skip steps without strong guardrails.
- **Hidden dependencies** and **manual in disguise** are common denominators across the research sources; every harness and practitioner source warns against both.
- **Guideline soup** and **over-reliance on priors** are our own framing of the broader problem that LLMs need concrete, checkable guidance rather than generic good advice.
- **Over-configuring** and **under-declaring scope** are our own practices, aligned with the research on minimalism and explicit boundaries.
- **Mixing invocation concerns** is our own framing, based on the observed trade-off between context load and cognitive load.
- **Premature completion** is our own concept, derived from the interplay between completion criteria and attention dynamics in sequential tasks.

