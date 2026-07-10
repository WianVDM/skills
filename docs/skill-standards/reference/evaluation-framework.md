# Evaluation Framework

## At a glance

This document defines the **harness-neutral evaluation framework** built around `evals/evals.json` and a pluggable runner interface. It covers eval-driven development, trigger/behavior/composition/pressure/security tests, deterministic assertions, and minimal-harness runs.

**Read this if:** you are testing a skill, choosing baselines, or setting up a CI evaluation pipeline.

A skill is not finished when it is written. It is finished when it reliably improves the agent's behavior. This document specifies the evaluation framework for skills in this library.

The framework is built around a harness-neutral `evals/evals.json` schema and a pluggable runner interface. Each harness adapts its native traces into the common envelope, so tests can be reused across environments.

---

## Eval-driven development

The basic loop:

1. **Draft** the skill.
2. **Write test prompts** — 2–3 realistic tasks a user would actually ask.
3. **Run with-skill and baseline** in parallel:
   - **With-skill**: the agent has access to the skill.
   - **Baseline**: the agent has no skill (or the old version, if improving an existing skill).
4. **Evaluate** the outputs qualitatively and with objective assertions where possible.
5. **Iterate** on the skill based on what fails.
6. **Expand** the test set once the skill is stable.

---

## `evals/evals.json`

The evaluation artifact is a JSON file at `evals/evals.json` in the skill package. A formal JSON Schema is maintained in `schemas/evals.json.schema.json` and summarized in `PACKAGE.md`. The artifact schema version is `1`.

```json
{
  "version": "1",
  "skill": "review-ui",
  "tests": [
    {
      "id": "trigger-01",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "Review my UI for accessibility issues.",
      "expected": "review-ui"
    },
    {
      "id": "behavior-01",
      "type": "behavior",
      "prompt": "Review this React component for design system compliance.",
      "baseline_type": "no_skill",
      "assertions": [
        {
          "type": "file_read",
          "path": "src/components/Button.tsx"
        },
        {
          "type": "output_contains",
          "value": "design-system"
        }
      ]
    },
    {
      "id": "composition-01",
      "type": "composition",
      "available_skills": ["review-ui", "generate-component", "design-vocabulary"],
      "prompt": "Create a new accessible button component that follows our design system.",
      "expected_selection": ["generate-component", "design-vocabulary"]
    }
  ]
}
```

### Test types

| Type | Purpose |
|------|---------|
| `trigger` | Does the description fire at the right times? |
| `behavior` | Does the skill improve the agent's output? |
| `composition` | Does the skill select, follow, and compose correctly with other skills? |
| `pressure` | Does a discipline skill resist rationalization? |
| `security` | Does the skill avoid unsafe behavior? (separate audit dimension) |

### Baseline types

| Type | Use when |
|------|------|
| `no_skill` | The skill is new; compare against the agent's default behavior. |
| `previous_version` | Improving an existing skill; compare against the prior version. |
| `failure_documentation` | The no-skill case is trivially non-compliant; compare against the documented failure pattern. |

The `failure_documentation` baseline is especially important for **discipline skills** where the agent without the skill would naturally take the wrong path.

---

## Runner interface

Each harness implements a `Runner` that adapts native traces into a normalized envelope:

```json
{
  "events": [...],
  "tool_calls": [...],
  "text": "...",
  "token_counts": { ... },
  "duration_seconds": 12.3
}
```

The runner is harness-specific, but the assertions are harness-neutral. This is modeled after the AWS `sample-agent-skill-eval` approach, which defines an `AgentRunner` interface.

---

## Deterministic checks first

Prefer deterministic assertions over LLM-as-judge:

1. **File read/write checks** — did the agent read or write the expected files?
2. **Command checks** — did the agent run a specific command?
3. **Output format checks** — does the output match the expected schema?
4. **String/regex checks** — does the output contain or exclude specific content?

Only fall back to an LLM judge when deterministic checks are impossible.

---

## Subjective-output hierarchy

For skills with subjective outputs (style, design, prose), use this hierarchy:

1. **Deterministic checks** first.
2. **Golden/reference comparison** — compare against a known-good example.
3. **Structured-rubric LLM judge** — score against explicit criteria with confidence scores.
4. **Independent reader/viewer testing** — have a human or separate process evaluate the output.
5. **Human review** as the final arbiter.

Individual subjective verdicts are capped at **medium-high** confidence. The methodology itself is high confidence.

---

## Trigger evals

Trigger evals test whether the skill description causes it to load at the right times.

- **10 should-trigger queries** — realistic prompts that should load the skill. Include varied phrasing, casual speech, and cases where the user does not name the skill explicitly.
- **10 should-not-trigger queries** — near-miss prompts that share keywords but should *not* load the skill. These are the most valuable cases.

For user-invoked skills, the description is primarily human-facing, but a clarity eval still helps. The 10/10 target is most critical for model-invoked skills.

---

## Composition testing

Composable skills need composition tests. A composition test specifies an `available_skills` array and checks:

- **Selection** — did the agent choose the right skills for the task?
- **Following** — did the selected skills follow their contracts?
- **Composition** — did the skills integrate correctly?
- **Distractor resistance** — did the agent ignore irrelevant skills?
- **Reflection** — did the agent revise its selection when the task changed?

Composition testing is required for building blocks and conductors. It is recommended for other skills.

---

## Pressure testing

Discipline skills need **pressure tests** that try to make the agent rationalize its way around the rule. The baseline is the documented failure pattern, not a successful no-skill run.

For example, a TDD discipline skill should be tested with prompts like:

- "Add this feature quickly."
- "The test is obvious, just implement it."
- "Can you skip the test and come back to it?"

The skill should either refuse, produce the required evidence, or escalate to the user.

---

## Multi-agent evaluation

Skills that involve multi-agent coordination should be tested on:

- **Communication correctness** — do agents exchange the right information?
- **Task-assignment accuracy** — is work delegated to the right agent?
- **Conflict avoidance** — do agents avoid duplicate or conflicting work?
- **Ledger fidelity** — are shared task lists, plans, or reports accurate?
- **Distractor resistance** — do agents stay focused under irrelevant input?

See `patterns/conductor-implementer-split.md` for the conductor/implementer pattern and its handoff contract.

---

## Agent-authored skill tests

Agent-authored skills need the same functional tests as human-authored skills, plus:

- **Anti-rationalization test** — the skill does not undermine its own rules.
- **Scope test** — the skill stays within its declared scope.
- **Mutation test** — the skill does not try to modify itself or other skills without approval.
- **Consolidation test** — the skill does not silently merge or replace human-authored content.

See `GOVERNANCE.md` for the agent-authored skills governance model.

---

## Security scanning

Security scanning is a separate audit dimension from functional evaluation. It checks for:

- Secrets in files, references, or config.
- Undeclared network access or external dependencies.
- Unsafe code execution or script injection.
- Inappropriate permissions or sandbox escapes.

Security scanning is required for distributed skills and recommended for local skills. Results are reported in `audit/security-report.json`.

---

## Minimal-harness run

For skills intended to be portable, run a **minimal-harness test** to verify that the degraded experience is still useful. For example, test the skill in Aider with only the plain-markdown body and no YAML parsing, subagents, or scripts.

The minimal-harness run should document what features are lost and whether the core guidance still produces correct behavior.

---

## Limitations

The following evaluation concerns are **limited** and are documented as such:

- Exact empirical trigger thresholds and false-positive rates are not published by any harness.
- Broad composition and multi-agent benchmarks do not yet exist.
- Individual subjective verdicts are inherently uncertain.
- LLM judges require confidence scoring and should not be treated as ground truth.

---

## Key takeaways

- A skill is finished when it **reliably improves the agent's behavior**, not when it is written.
- Prefer **deterministic assertions** (file read/write, commands, output contains/excludes, format) over LLM-as-judge.
- **Trigger evals** are essential for model-invoked skills: aim for 10 should-trigger and 10 should-not-trigger queries.
- **Composition tests** are required for building blocks and conductors; they check selection, following, composition, and distractor resistance.
- **Pressure tests** try to make discipline skills rationalize their way around the rule.
- **Discipline skills** use the documented failure pattern as a baseline, not a successful no-skill run.
- **Agent-authored skills** need extra tests: anti-rationalization, scope, mutation, and consolidation.
- **Security scanning** is a separate audit dimension from functional evaluation.
- Run a **minimal-harness test** for portable skills to confirm degraded behavior is still useful.

## Research basis

- The **eval-driven development** loop and **trigger evals** are our own practices, strongly supported by the research finding that skills only become reliable through empirical testing.
- The **`evals/evals.json` schema** and **runner interface** are design choices synthesized from the AWS `sample-agent-skill-eval` project and the research on cross-harness evaluation.
- **Baseline types** (`no_skill`, `previous_version`, `failure_documentation`) and the **guardrail baseline** are drawn from the research evaluation framework, particularly for discipline skills.
- The **deterministic checks first** rule and **subjective-output hierarchy** are drawn from the research evaluation framework.
- **Composition testing** and **multi-agent evaluation dimensions** are drawn from the research on multi-agent coordination and skill composition.
- **Agent-authored-specific tests** are drawn from the research on agent-authored skills governance.
- **Security scanning as a separate audit dimension** is drawn from the research on governance and enterprise skill libraries.
- **Minimal-harness run** is drawn from the research on Aider compatibility and minimal-harness skill injection.
- The **limitations** are drawn from the research gaps checklist and are explicitly documented.

---

## Related documents

- [`fundamentals/architecture/evaluation.md`](../fundamentals/architecture/evaluation.md) — the fundamental evaluation checklists and review questions.
- [`PACKAGE.md`](./package.md) — formal `evals.json`, `skills.json`, and lock-file schemas.
- [`GOVERNANCE.md`](./governance.md) — verification levels and agent-authored skills.
- [`PORTABILITY.md`](../patterns/portability.md) — minimal-harness degradation and portable core.
- [`patterns/discipline-skill.md`](../patterns/discipline-skill.md) — pressure testing and guardrail baselines.
- [`patterns/conductor-implementer-split.md`](../patterns/conductor-implementer-split.md) — multi-agent handoff patterns.
