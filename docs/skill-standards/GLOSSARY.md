# Glossary

This glossary defines the terms used across the skill fundamentals documents. Use consistent terminology when writing or reviewing skills. The model reads meaning from how words are used, so precision matters.

---

## Skill terms

### Skill

The smallest load-bearing shape that makes an agent reliably do the right thing for a specific domain. A contract between author and agent, not a script or manual.

### Determinism device

A mechanism that makes a stochastic system behave more predictably. A skill is a determinism device for an agent.

### Predictability

The degree to which a skill makes the agent follow the same *process* on every run. Output may vary; behavior should not. The root virtue every other concept serves.

### Root virtue

The single value that every other lever in a skill serves. For agent skills, the root virtue is **Predictability**.

### Load-bearing minimalism

Every line in a skill must earn its place. If removing a sentence does not change behavior, it should be removed. Not about word count; about signal density.

### Completion criterion

A checkable condition that tells the agent a step or unit of work is done. Strong criteria are clear and exhaustive.

### Leading word

A compact concept already present in the model's pretraining, used to anchor behavior in few tokens. Example: `deep`, `tight`, `red`, `grill`. Recruits priors the model already holds.

### Legwork

The work an agent does within a step or guideline — reading files, exploring code, testing assumptions — without being told explicitly how to do it.

### Premature completion

Ending a step before it is genuinely done because the agent's attention slips toward being finished. Caused by vague completion criteria or visible **post-completion steps** pulling attention forward. Cured by sharpening the criterion first; splitting or delegating is the fallback when the criterion cannot be made sharp and the rush is observed.

### Post-completion steps

The steps that follow the current step. When visible, they tempt the agent toward **premature completion**. Hiding them by splitting or delegating reduces the pull, but only if the later steps truly leave the agent's context.

### Progressive disclosure

Moving reference material out of `SKILL.md` and behind a pointer, so the top level stays legible. Inline what every path needs; disclose what only some branches need.

### Context pointer

A reference in the agent's context that names out-of-context material and encodes when to reach for it. The **description** of a model-invoked skill is the top-level context pointer. The wording of the pointer matters more than the target.

### Information hierarchy

A ranking of a skill's content by how immediately the agent needs it. The rungs are: in-skill steps, in-skill reference, disclosed reference (behind a context pointer), and external reference (outside the skill system). The hierarchy decides how far down a piece sits; co-location decides what sits beside it once there.

### Branch

A distinct way a skill can be invoked — a case or path that changes what the skill does.

---

## Skill types

### Standalone / Atomic skill

A skill that does one narrow job, complete in itself, with little or no dependency on other skills.

### Building-block / Vocabulary skill

A skill that provides shared language, rules, or reference material consumed by other skills.

### Conductor / Orchestrator skill

A skill that coordinates other skills, subagents, or tools through a multi-phase process.

### Hybrid skill

A skill with its own core workflow that also embeds or consumes building-block skills.

### Framework-aware skill

A skill tied to a specific framework or library, encoding its current patterns, APIs, and best practices.

### Version-aware skill

A skill that fetches or ships version-specific guidance so its advice does not go stale as the target technology evolves.

---

## Failure modes

### Sprawl

A skill that is too long, even if every line is live and unique. Hurts readability and attention. Cured by progressive disclosure and splitting.

### Sediment

Stale layers of content that accumulate because adding feels safe and removing feels risky. The slow erosion of relevance.

### Duplication

The same meaning expressed in more than one place. Costs maintenance, tokens, and inflates a concept's prominence.

### No-op instruction

A line that changes nothing because the model already does it by default. Test: does this change behavior versus the default?

### Hidden dependency

A tool, API, convention, or config a skill relies on without declaring it.

---

## Cognitive terms

### Context load

The cost a model-invoked skill imposes by keeping its description in the context window. Paid in tokens and attention.

### Cognitive load

The cost a user-invoked skill imposes on the human, who must remember it exists and when to use it.

### Relevance

Whether a line still bears on what the skill does. A line loses relevance by being off-topic, stale, or belonging to a branch the skill no longer handles. The lens for pruning.

### Shared language

A vocabulary that aligns how the user, the agent, and the codebase talk about a domain. Reduces friction and token use over time.

### Router skill

A user-invoked skill whose job is to point at other user-invoked skills — naming each and when to reach for it — so the human has one skill to remember instead of many. It cannot invoke the others; only the human can reach user-invoked skills.

### Mental model

The internal representation the agent builds of how a skill or domain works. A skill should shape the agent's mental model, not just issue commands.

### Priming

The effect of early words and framing on how the agent interprets the rest of the skill. The first sentence matters disproportionately.

### Decision fatigue

The degradation of decision quality as the number of decisions increases. A skill should reduce the decisions the agent must make, not multiply them.

---

## Evaluation and quality terms

### Eval-driven development

The practice of testing a skill against representative prompts, comparing with-skill and without-skill behavior, and iterating until the skill reliably improves outcomes.

### Trigger eval

A set of queries used to test whether a skill's description causes it to fire at the right times. Split into should-trigger and should-not-trigger cases.

### Should-trigger query

A realistic user prompt that should cause the agent to load the skill.

### Should-not-trigger query

A realistic user prompt that shares keywords or concepts with the skill but should *not* cause it to load. The most valuable cases are near-misses.

### With-skill run

A test where the agent has access to the skill and attempts the task.

### Baseline run

A test where the agent attempts the same task without the skill (or with an older version), used as a comparison point.

### Explain-the-why

A writing pattern that explains the reasoning behind a guideline rather than issuing a rigid command. Helps the agent generalize correctly.

### Negation pair

A writing pattern that pairs every "do not X" with a positive directive. Used because LLMs handle negation weakly.

### One-way pattern consistency

The practice of encoding exactly one canonical way to solve each recurring problem in a skill, reducing optionality and making agent output more deterministic.
