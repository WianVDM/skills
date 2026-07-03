# 13 — Evaluation

Use these checklists and questions when designing or reviewing a skill. A skill does not have to pass every item perfectly, but it should fail knowingly, not accidentally.

---

## Eval-driven development

A skill is not finished when it is written. It is finished when it reliably improves the agent's behavior. Test the skill against representative prompts and iterate.

### The basic loop

1. **Draft** the skill.
2. **Write test prompts** — 2–3 realistic tasks a user would actually ask.
3. **Run with-skill and baseline** in parallel:
   - **With-skill**: the agent has access to the skill.
   - **Baseline**: the agent has no skill (or the old version, if improving an existing skill).
4. **Evaluate** the outputs qualitatively and with objective assertions where possible.
5. **Iterate** on the skill based on what fails.
6. **Expand** the test set once the skill is stable.

### Objective assertions

For skills with verifiable outputs, write assertions that check concrete behavior:

- The output uses the requested format.
- A specific command was run.
- A specific file was read or written.
- No internal function was mocked.

Subjective skills (writing style, design quality) are better evaluated qualitatively. Do not force numeric assertions onto judgment.

### Trigger evals

Test the description separately from the body:

- Collect 10 **should-trigger** queries that should cause the agent to load the skill.
- Collect 10 **should-not-trigger** queries that should not load it, focusing on near-misses.
- Run them and measure trigger accuracy.
- Rewrite the description if the wrong skills fire or the right skill does not fire.

See [04-structure.md](./04-structure.md) for description optimization guidance.

For user-invoked skills, the description is primarily human-facing, but a clarity eval still helps: collect realistic prompts that should and should not lead a human to reach for the skill. The 10/10 numeric target is most critical for model-invoked skills.

### What to watch for

- The skill makes the agent *worse* by over-constraining it.
- The agent ignores parts of the skill.
- The skill triggers on the wrong tasks.
- The skill fails to trigger on the right tasks.
- Outputs vary significantly across similar prompts.

---

## Universal checklist

Applies to every skill.

- [ ] The skill has one clear objective.
- [ ] The skill type matches the objective.
- [ ] Every line in `SKILL.md` is load-bearing.
- [ ] The description states what the skill does and when to use it.
- [ ] Out-of-scope items are explicit.
- [ ] Dependencies are declared.
- [ ] Security considerations are addressed: no secrets in files, destructive actions confirmed.
- [ ] The skill is explicit about failure, ambiguity, and assumptions.
- [ ] Reference links resolve.
- [ ] The skill uses harness-agnostic and project-agnostic language where required.

---

## Per-type checklists

### Standalone / Atomic

- [ ] The task is narrow and well-bounded.
- [ ] The skill needs no state or minimal state.
- [ ] The model's priors are strong enough that the skill does not over-specify.
- [ ] The skill is not secretly a workflow or conductor.

### Building-block / Vocabulary

- [ ] The concept is reused or will be reused by multiple skills.
- [ ] The skill is mostly reference, not a workflow.
- [ ] Definitions are precise and consistent.
- [ ] The skill does not drift into project-specific detail.

### Conductor / Orchestrator

- [ ] The skill delegates deep work rather than doing it inline.
- [ ] State is tracked across phases and survives context compaction.
- [ ] Subagent prompts are focused and include scope, tools, and return format.
- [ ] The skill integrates findings before deciding what to do next.
- [ ] User interaction is owned by the conductor, not leaked to workers.

### Hybrid

- [ ] The workflow and reference are clearly separated.
- [ ] Steps have checkable completion criteria.
- [ ] Embedded principles do not overwhelm the process.
- [ ] Building-block skills are referenced rather than duplicated.

---

## Review questions

### Does this skill need to exist?

- Is the task repeated?
- Does the agent vary without guidance?
- Could a script, MCP server, or prompt template solve it instead?

See [06-when-to-create-a-skill.md](./06-when-to-create-a-skill.md).

### Is it the right type?

- Does it solve one narrow job? → Standalone.
- Does it provide shared language? → Building-block.
- Does it coordinate phases? → Conductor.
- Does it need both workflow and principles? → Hybrid.

See [02-skill-types.md](./02-skill-types.md).

### Is every line load-bearing?

- If I remove this sentence, does behavior change?
- Does this instruction merely restate the default?
- Is this detail needed on every invocation, or can it be disclosed?

See [05-common-mistakes.md](./05-common-mistakes.md).

### Is the form right?

- Does the agent need steps, guidelines, or both?
- Are completion criteria checkable?
- Are leading words used where they add precision?

See [03-form-and-style.md](./03-form-and-style.md).

### Is it reusable?

- Are shared conventions duplicated?
- Are dependencies declared?
- Would this skill work in a project the author has never seen?

See [12-reusability.md](./12-reusability.md).

### Does it fail well?

- Does it stop and explain when something is missing?
- Does it ask before overwriting config or state?
- Does it fail closed when a required capability is missing?

---

## The predictability test

Imagine running the skill ten times on similar inputs. Would the agent follow the same process each time? If the answer is no, the skill is too vague.

## The minimalism test

Remove one paragraph at a time from `SKILL.md`. If the skill still works, that paragraph was sediment. Prune it.

## The litmus test

Complete this sentence:

> This skill makes the agent more predictable at ______ by enforcing ______.

If both blanks are hard to fill, the skill is not yet well-defined.
