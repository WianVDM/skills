# Evaluation

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

See [structure/frontmatter.md](../core/structure/frontmatter.md) for description optimization guidance.

For user-invoked skills, the description is primarily human-facing, but a clarity eval still helps: collect realistic prompts that should and should not lead a human to reach for the skill. The 10/10 numeric target is most critical for model-invoked skills.

### What to watch for

- The skill makes the agent *worse* by over-constraining it.
- The agent ignores parts of the skill.
- The skill triggers on the wrong tasks.
- The skill fails to trigger on the right tasks.
- Outputs vary significantly across similar prompts.
- The skill uses a weaker tool when a better one was available without disclosing it.
- The skill reports a source as “unavailable” while a configured tool could fulfill the same capability.

### Tooling-awareness behavioral evals

Test the skill's behavior with realistic scenarios, not just the presence of guidance. Add cases that exercise tooling awareness and degradation disclosure:

- A better tool is available alongside the skill's adapter. The with-skill output should use the better tool or disclose it.
- A configured tool can fill a gap left by a failing adapter. The skill should offer to use it before accepting degraded data.
- A degraded source is used. The skill should name the better tool and explain the impact.

See [tooling-awareness.md](./tooling-awareness.md) for the capability-first approach to tool selection.

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
- [ ] The skill detects and prefers the best available tool for each capability (see [tooling-awareness.md](./tooling-awareness.md)).
- [ ] If the skill uses a degraded source, it discloses the better tool that was available and obtains user consent.

---

## Per-type checklists

### Building block

- [ ] The task is narrow and well-bounded.
- [ ] The skill has a clear, stable interface.
- [ ] The output is structured enough for other skills to act on.
- [ ] The skill does not contain presentation, coordination, or workflow logic that belongs in a wrapper or conductor.
- [ ] Dependencies are declared explicitly.

### Conductor

- [ ] The skill delegates deep work rather than doing it inline.
- [ ] State is tracked across phases and survives context compaction.
- [ ] Subagent prompts are focused and include scope, tools, and return format.
- [ ] The skill integrates findings before deciding what to do next.
- [ ] The skill checks for tools outside its own adapter set before invoking adapters.
- [ ] User interaction is owned by the conductor or its wrapper, not leaked to workers.

### Wrapper

- [ ] The skill is user-invoked.
- [ ] Its job is prompts, presentation, or confirmation.
- [ ] Core logic lives in a building block or conductor.
- [ ] Destructive actions are confirmed.
- [ ] The user receives a clear summary of results.

### Multi-layer / hybrid

- [ ] The primary layer is clear.
- [ ] The workflow and reference are clearly separated.
- [ ] Steps have checkable completion criteria.
- [ ] Embedded principles do not overwhelm the process.
- [ ] Building-block skills are referenced rather than duplicated.
- [ ] The skill is not using "hybrid" to avoid a clear boundary.

---

## Review questions

### Does this skill need to exist?

- Is the task repeated?
- Does the agent vary without guidance?
- Could a script, MCP server, or prompt template solve it instead?

See [when-to-create-a-skill/](../core/when-to-create-a-skill/).

### Is it the right type?

- Does it solve one narrow, well-bounded problem? → Building block.
- Does it coordinate multiple skills or tools through phases? → Conductor.
- Does it adapt another skill for human interaction? → Wrapper.
- Does it combine layers with a clear primary role? → Multi-layer / hybrid.

See [types/](../core/types/).

### Is every line load-bearing?

- If I remove this sentence, does behavior change?
- Does this instruction merely restate the default?
- Is this detail needed on every invocation, or can it be disclosed?

See [common-mistakes/](../core/common-mistakes/).

### Is the form right?

- Does the agent need steps, guidelines, or both?
- Are completion criteria checkable?
- Are leading words used where they add precision?

See [form-and-style/](../core/form-and-style/).

### Is it reusable?

- Are shared conventions duplicated?
- Are dependencies declared?
- Would this skill work in a project the author has never seen?

See [building-block.md](../../patterns/building-block.md).

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

---

## Research basis

See [SOURCES.md](../../reference/sources.md).
