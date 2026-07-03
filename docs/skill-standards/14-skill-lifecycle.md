# 14 — Skill lifecycle

A skill is a living document. It moves through distinct phases from initial idea to retirement. Treat each phase as intentional, not accidental.

---

## 1. Decide

Before writing anything, confirm that a skill is the right solution.

- Is the task repeated?
- Does the agent vary without guidance?
- Would a script, MCP server, prompt template, or documentation change solve it instead?

See [06-when-to-create-a-skill.md](./06-when-to-create-a-skill.md).

---

## 2. Design

Choose the skill type and form before writing files.

- **Type**: standalone, building-block, conductor, or hybrid. See [02-skill-types.md](./02-skill-types.md).
- **Form**: instruction-heavy, guideline-heavy, or hybrid. See [03-form-and-style.md](./03-form-and-style.md).
- **Invocation**: model-invoked or user-invoked. See [04-structure.md](./04-structure.md).
- **Scope**: what is in and what is out.
- **Dependencies**: other skills, tools, APIs, environment variables.

Write a one-sentence intent statement:

> This skill makes the agent more predictable at ______ by enforcing ______.

If both blanks are hard to fill, the design is not ready.

---

## 3. Draft

Write the minimal `SKILL.md` plus only the supporting files that are needed.

- Frontmatter with name, description, and metadata.
- Core contract in the body.
- Reference files for disclosed detail.
- Scripts for deterministic logic.
- Subagents only if delegation is clearly needed.

Keep `SKILL.md` under 500 lines. Under 300 is better. See [04-structure.md](./04-structure.md).

---

## 4. Validate

Check the draft against structure and style standards before testing behavior.

- Does the description include what and when?
- Are reference links resolvable?
- Is every line load-bearing?
- Are dependencies declared?
- Is the language harness-agnostic and project-agnostic where required?

See [13-evaluation.md](./13-evaluation.md) for checklists.

---

## 5. Test

Run the skill against representative prompts.

- **Trigger evals**: does the description fire at the right times?
- **Behavioral evals**: does the skill improve the agent's output compared to no skill?
- **Edge cases**: missing config, missing context report, ambiguous input, user rejection.

See [13-evaluation.md](./13-evaluation.md) for the eval-driven development loop.

---

## 6. Iterate

Improve the skill based on test results and real usage.

- Generalize from specific failures rather than overfitting to one prompt.
- Remove instructions that do not change behavior.
- Add scripts when the agent repeatedly generates the same helper code.
- Sharpen completion criteria if the agent rushes.
- Rewrite the description if triggering is unreliable.

---

## 7. Publish

Once the skill is stable, publish or install it.

- Bump the version if the schema, config, or behavior changed.
- Document breaking changes.
- Add or update `README.md` for human maintainers.
- Declare compatibility and dependencies clearly.

---

## 8. Maintain

Skills rot without attention. Maintenance tasks:

- Review after significant real-world usage.
- Remove sediment — guidance that no longer applies.
- Update framework-specific advice when the target technology changes.
- Add notes to config when user preferences or workarounds emerge.
- Re-run trigger evals if the agent harness or model changes.

---

## 9. Deprecate or split

Retire a skill when:

- It is no longer used.
- Its job is better handled by a script, MCP server, or another skill.
- It has grown too many unrelated concerns and should be split.
- A newer version replaces it.

When deprecating, document the replacement path and update any skills that depended on it.

---

## Lifecycle checklist

- [ ] Decided a skill is the right solution.
- [ ] Chosen type, form, invocation, and scope.
- [ ] Drafted a minimal `SKILL.md` and supporting files.
- [ ] Validated structure and style.
- [ ] Tested triggers and behavior against baselines.
- [ ] Iterated based on failures.
- [ ] Published with version and documentation.
- [ ] Scheduled maintenance review.
