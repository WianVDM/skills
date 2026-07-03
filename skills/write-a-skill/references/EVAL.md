# Evaluation and testing

This document defines how to test `write-a-skill` to ensure it behaves correctly across its four branches and does not drift from the fundamentals.

## Trigger evals

Even though `write-a-skill` is user-invoked, the description must make it obvious to a human when to reach for the skill and must not be confused with a model-facing trigger list. Test the description with realistic prompts.

### 10 should-trigger queries

These prompts should lead a human to invoke `write-a-skill`:

1. "I want to create a skill that helps me write ADRs."
2. "Can you help me design a new agent skill for code reviews?"
3. "Review my existing skill `triage` against the standards."
4. "Make my project-specific skill `triage` global-ready."
5. "I need a minimal skill for daily standup notes."
6. "Should I turn this repeated debugging process into a skill?"
7. "Audit the skill in `.agents/skills/verify-branch`."
8. "Upgrade `write-a-skill` so it works in any project."
9. "Give me a skill that drafts release notes from commit messages."
10. "Help me decide whether this problem needs a skill or a script."

### 10 should-not-trigger queries

These prompts share keywords but should *not* lead a human to invoke `write-a-skill`:

1. "Write a Python script that checks my PRs." — this is a script, not a skill design request.
2. "Change the system prompt for my agent." — this is a prompt change, not a skill.
3. "Fix this bug in the codebase." — this is implementation, not skill design.
4. "Write a README for the project." — this is documentation, not a skill.
5. "Create a GitHub Action workflow." — this is CI, not a skill.
6. "Refactor the `auth.service.ts` file." — this is code refactoring, not a skill review.
7. "Add a new MCP server for database queries." — this is an external tool, not a skill.
8. "Help me write a one-off prompt for summarizing text." — this is a prompt template, not a reusable skill.
9. "Update the skill-standards documentation." — this is documentation, not skill design.
10. "Install a new npm package." — this is dependency management, not a skill.

### Original branch trigger evals

These verify that the conductor classifies intent into the correct branch:

- **New branch:** *"I want to create a skill that helps me write ADRs."* → expected branch New.
- **Quick branch:** *"Give me a minimal skill for daily standup notes."* → expected branch Quick.
- **Review branch:** *"Can you review my existing skill `triage`?"* → expected branch Review.
- **Upgrade branch:** *"Make my project-specific skill `triage` global-ready."* → expected branch Upgrade.

## Behavioral evals

Behavioral evals verify that the skill follows its own rules.

1. **No drafting before confirmation.** Start the New branch and verify that the conductor does not write files until the user explicitly confirms the design.
2. **Self-audit blocks violations.** Present a design with two core objectives and verify that the self-audit fails and drafting is blocked.
3. **Path detection is used.** Run the skill in a project without `.agents/` and verify that it asks the user for the correct layout.
4. **Workers do not ask users.** Inspect subagent prompts and outputs to ensure all user questions flow through the conductor.
5. **Completion criteria exist.** Verify that every branch in `SKILL.md` ends with a completion criterion.
6. **No `.agents/` hardcoding.** Search the skill files for `.agents/` and confirm that only detection rules and historical references contain it.
7. **Review is read-only.** Run the Review branch and confirm that no files are modified unless the user explicitly asks for changes.
8. **Upgrade confirms changes.** Run the Upgrade branch and confirm that every proposed change is approved before application.
9. **Branch workflow disclosure.** Verify that `SKILL.md` points to `references/BRANCH_WORKFLOWS.md` for detailed phase lists and stays under 300 lines.
10. **Invocation declaration.** Verify that `SKILL.md` frontmatter contains both `invocation: user-invoked` and `disable-model-invocation: true`.

## Regression checklist

After any change to this skill, run:

- [ ] All 10 should-trigger queries lead to invoking `write-a-skill`.
- [ ] All 10 should-not-trigger queries do not lead to invoking `write-a-skill`.
- [ ] All four branch classification evals.
- [ ] All 10 behavioral evals.
- [ ] A self-review of `write-a-skill` using its own Review branch.
- [ ] A self-upgrade check of `write-a-skill` using its own Upgrade branch.
- [ ] Verify all reference links in `SKILL.md` and `README.md` resolve.
- [ ] Verify the detection script returns a valid result for the current project.

## Eval artifacts

Store eval results in `{context}/skill-eval/write-a-skill-eval-{date}.md` with the eval prompt, expected outcome, observed outcome, and pass/fail status.
