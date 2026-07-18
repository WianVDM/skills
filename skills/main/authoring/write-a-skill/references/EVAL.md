# Evaluation and testing

This file keeps only the `write-a-skill`-specific test cases and scenarios. For the canonical methodology and the `evals/evals.json` schema, see:

- `eval-format` skill (located via the detected skills directory)
- `docs/skill-standards/reference/evaluation-framework.md`
- `docs/skill-standards/guides/trigger-evals.md`

## Trigger evals

`write-a-skill` is **user-invoked**, so the evals below test whether a human reader would correctly reach for the skill. They are not model-routing tests.

### Should-trigger queries

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

### Should-not-trigger queries

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

### Branch classification evals

These verify that the conductor classifies intent into the correct branch and gate:

- **Initialize branch:** *"I haven't configured write-a-skill yet."* → expected branch `initialize`.
- **Create branch, full gate:** *"I want to create a skill that helps me write ADRs."* → expected branch `create`, gate `full`.
- **Create branch, quick gate:** *"Give me a minimal skill for daily standup notes."* → expected branch `create`, gate `quick`.
- **Change branch, review gate:** *"Can you review my existing skill `triage`?"* → expected branch `change`, gate `review`.
- **Change branch, update gate:** *"Make my project-specific skill `triage` global-ready."* → expected branch `change`, gate `update`.

## Behavioral evals

1. **No drafting before confirmation.** Start the Create branch full gate and verify that the conductor does not write files until the user explicitly confirms the design.
2. **Self-audit blocks violations.** Present a design with two core objectives and verify that the self-audit fails and drafting is blocked.
3. **Path detection is used.** Run the skill in a project without `.agents/` and verify that it asks the user for the correct layout.
4. **Workers do not ask users.** Inspect subagent prompts and outputs to ensure all user questions flow through the conductor.
5. **Completion criteria exist.** Verify that every branch and gate in `SKILL.md` ends with a completion criterion.
6. **No `.agents/` hardcoding.** Search the skill files for `.agents/` and confirm that only detection rules and historical references contain it.
7. **Review is read-only.** Run the Change branch review gate and confirm that no files are modified unless the user explicitly asks for changes.
8. **Update confirms changes.** Run the Change branch update gate and confirm that every proposed change is approved before application.
9. **Branch workflow disclosure.** Verify that `SKILL.md` points to `references/BRANCH_WORKFLOWS.md` for detailed phase lists and stays under 300 lines.
10. **Invocation declaration.** Verify that `SKILL.md` frontmatter contains `invocation: user-invoked`.
11. **Initializer warns and persists config.** Run `write-a-skill` in a project without a `write-a-skill.yaml` config. Verify the conductor proposes paths, warns about missing canonical standards, and only writes `write-a-skill.yaml` after explicit approval.
12. **Degraded mode is consistently disclosed.** Remove the canonical standards path and trigger the `create` branch. Verify the degraded-mode warning appears during pattern adherence, audit, and review phases, and that the user's choice is recorded in the decision log.
13. **Audit/review catch token bloat.** Present a drafted skill with an unjustified reference section and verify that `audit-skill` or `review-skill` flags it as a token-economy warning or blocker.
14. **Audit/review catch pattern violations.** Present a drafted skill that deviates from a Layer 2 pattern without rationale and verify that the audit/review flags the deviation.
15. **Overlap detection flags a duplicate capability.** Present a design for a skill whose description overlaps with an existing building block (e.g., `parse-skill-frontmatter`) and verify that `detect-skill-overlap` flags the overlap before drafting proceeds.

## Tooling-awareness behavioral evals

1. **Better tool available.** Configure a better tool for a capability the drafted skill needs. Run the Create branch and verify the design either uses the better tool or discloses it and asks for consent.
2. **Adapter fallback.** Remove the preferred tool from the design. Verify the skill names the degraded source and explains the impact before proceeding.
3. **Lazy tool discovery.** Trigger a branch that uses a recommended tool. Verify the conductor checks for that tool only when the branch is selected, not at initialization.
4. **Capability matrix in draft.** Run the Create branch full gate and verify the design draft contains a capability-to-tool mapping for each load-bearing capability.

## Composition tests

These verify that the conductor composes building-block skills correctly and handles their outputs.

1. **Create branch invokes the expected sequence.** Given a request to create a skill, verify the conductor calls `detect-project-context` → `list-available-skills` → `search-skills-registry` → `detect-skill-overlap` → `decide-skill-shape` (or resolves shape internally) → `audit-skill` → `validate-skill-frontmatter` before writing any file.
2. **Change branch delegates to `review-skill`.** Given a request to review an existing skill, verify the conductor loads `review-skill` and does not attempt to run the audit inline.
3. **Failure in a building block stops the workflow.** Verify that if `audit-skill` returns blockers, the conductor does not proceed to file writing without an explicit user override.
4. **Dependency self-diagnostic gates startup.** Verify that if a required building-block skill is missing and the diagnostic reports `blocked`, the conductor stops and explains how to install the missing skill.
5. **Config-driven standards path is honored.** Verify that when `write-a-skill.standards_path` is configured, the conductor checks that directory before falling back to embedded fundamentals.
6. **Overlap detection gates shape decisions.** Verify that `detect-skill-overlap` is invoked during the alternatives phase and that its findings influence the colocation/extraction decision.

## Regression checklist

After any change to this skill, run:

- All 10 should-trigger queries lead to invoking `write-a-skill`.
- All 10 should-not-trigger queries do not lead to invoking `write-a-skill`.
- All five branch classification evals.
- All 15 behavioral evals.
- All 4 tooling-awareness behavioral evals.
- A self-review of `write-a-skill` using its own Change branch review gate.
- A self-update check of `write-a-skill` using its own Change branch update gate.
- Verify all reference links in `SKILL.md` and `README.md` resolve.
- Verify `detect-project-context` returns a valid result for the current project.

## Eval artifacts

Store eval results in `{context}/skill-eval/write-a-skill-eval-{date}.md` with the eval prompt, expected outcome, observed outcome, and pass/fail status.
