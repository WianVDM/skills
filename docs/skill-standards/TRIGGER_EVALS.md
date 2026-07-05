# Trigger Evaluation Guide

A trigger eval tests whether a skill's `description` causes it to load at the right times. A weak description makes a skill invisible; a strong description front-loads the leading words and domain signals the agent should match against.

This guide covers how to write and run trigger evals in practice.

---

## When trigger evals matter

Trigger evals are **essential** for model-invoked skills. They are useful but optional for user-invoked skills, where the description is mainly human-facing.

Run trigger evals:

- Before finalizing a new skill.
- After rewriting a description.
- When the agent harness or model changes.
- When merging skills that might compete for the same keywords.

---

## The 10/10 rule

Aim for at least:

- **10 should-trigger queries** — realistic prompts that should load the skill.
- **10 should-not-trigger queries** — near-miss prompts that share keywords but should *not* load the skill.

The should-not-trigger cases are usually more valuable. They expose false positives before users do.

---

## Writing should-trigger queries

A good should-trigger query is realistic and varied:

- Use the exact leading word or domain.
- Use casual phrasing the user might actually type.
- Include cases where the user does **not** name the skill explicitly.
- Include synonyms for the same intent, but only if they map to a distinct branch.

Examples for a UI review skill:

- "Review my UI for accessibility issues."
- "Check this component against the design system."
- "Audit the UX of this page."
- "Is this responsive layout okay?"

Avoid trivial positives like "run the UI review skill." They do not test routing.

---

## Writing should-not-trigger queries

A good should-not-trigger query is a near-miss. It shares keywords with the skill but points to a different domain or intent.

Examples for a UI review skill:

- "Review my backend API." — shares "review" but wrong domain.
- "Write a UI test." — shares "UI" but wrong task.
- "Check the accessibility of my PDF." — shares "accessibility" but wrong target.
- "Summarize the design system docs." — shares "design system" but wrong action.

Avoid easy negatives like "write a Fibonacci function." They test the obvious miss, not the boundary.

---

## Running trigger evals

### Option 1: manual run

1. Paste each query into the agent as if you were the user.
2. Observe whether the skill loads (e.g., the harness shows it in the context, mentions it by name, or acts on its rules).
3. Record the result in a spreadsheet or `references/EVAL.md`.
4. For false negatives, rewrite the description and re-test.
5. For false positives, narrow the description or add negative examples to the eval set.

### Option 2: evals.json

Add trigger tests to `evals/evals.json`. Each harness provides a runner that checks whether the skill loaded for each prompt.

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
      "id": "trigger-02",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "Check this page against our design system.",
      "expected": "review-ui"
    },
    {
      "id": "trigger-03",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "Review my backend API endpoints.",
      "expected": ""
    },
    {
      "id": "trigger-04",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "Write a UI test for this component.",
      "expected": ""
    }
  ]
}
```

The `expected` field is the skill name for should-trigger cases and empty for should-not-trigger cases. The runner checks whether the loaded skill set matches.

### Option 3: side-by-side comparison

Run the queries with and without the skill available. If a query only triggers the skill when it is present, the description is doing the work. If it triggers a different skill or the default agent, the description is too weak or too broad.

---

## Template: trigger eval set

Use this as a starting point for any model-invoked skill. Replace the bracketed sections.

```json
{
  "version": "1",
  "skill": "[skill-name]",
  "tests": [
    {
      "id": "trigger-should-01",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "[realistic prompt using the leading word]",
      "expected": "[skill-name]"
    },
    {
      "id": "trigger-should-02",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "[casual phrasing, no skill name]",
      "expected": "[skill-name]"
    },
    {
      "id": "trigger-should-03",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "[synonym for the same intent]",
      "expected": "[skill-name]"
    },
    {
      "id": "trigger-should-04",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "[specific scenario the skill handles]",
      "expected": "[skill-name]"
    },
    {
      "id": "trigger-should-05",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "[another realistic prompt]",
      "expected": "[skill-name]"
    },
    {
      "id": "trigger-should-06",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "[another realistic prompt]",
      "expected": "[skill-name]"
    },
    {
      "id": "trigger-should-07",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "[another realistic prompt]",
      "expected": "[skill-name]"
    },
    {
      "id": "trigger-should-08",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "[another realistic prompt]",
      "expected": "[skill-name]"
    },
    {
      "id": "trigger-should-09",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "[another realistic prompt]",
      "expected": "[skill-name]"
    },
    {
      "id": "trigger-should-10",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "[another realistic prompt]",
      "expected": "[skill-name]"
    },
    {
      "id": "trigger-not-01",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "[near-miss: shares a keyword but wrong domain]",
      "expected": ""
    },
    {
      "id": "trigger-not-02",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "[near-miss: shares a keyword but wrong task]",
      "expected": ""
    },
    {
      "id": "trigger-not-03",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "[near-miss: shares a keyword but wrong target]",
      "expected": ""
    },
    {
      "id": "trigger-not-04",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "[near-miss: same domain, different action]",
      "expected": ""
    },
    {
      "id": "trigger-not-05",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "[near-miss: same action, different domain]",
      "expected": ""
    },
    {
      "id": "trigger-not-06",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "[near-miss: related but out of scope]",
      "expected": ""
    },
    {
      "id": "trigger-not-07",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "[near-miss: related but out of scope]",
      "expected": ""
    },
    {
      "id": "trigger-not-08",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "[near-miss: related but out of scope]",
      "expected": ""
    },
    {
      "id": "trigger-not-09",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "[near-miss: related but out of scope]",
      "expected": ""
    },
    {
      "id": "trigger-not-10",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "[obvious negative, useful for sanity]",
      "expected": ""
    }
  ]
}
```

---

## Interpreting results

| Result | Meaning | Action |
|--------|---------|--------|
| Should-trigger fails | Description is too weak or missing keywords. | Add leading words, synonyms, or scenario phrases. |
| Should-not-trigger fails | Description is too broad. | Remove vague terms, split into narrower skills, or add negative constraints. |
| Both pass | Description is well-calibrated. | Keep the eval set and move on. |
| Inconsistent | The model is sensitive to phrasing. | Test more variants; consider a reach clause. |

---

## Iteration tips

- **Rewrite one variable at a time.** Change the leading word, the reach clause, or the trigger list separately so you know what helped.
- **Front-load the domain.** The first few words of the description matter most.
- **Use quotes for trigger phrases.** Phrases like `"review my UI"` can anchor the model better than prose.
- **Avoid generic verbs.** "Help with" or "assist with" do not tell the agent when to load the skill.
- **Add a reach clause** if other skills need to invoke this one: "Use when another skill needs to know the available skills."

---

## Common pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Description is a title | Skill rarely fires | Rewrite as a when-to-use sentence. |
| Description lists every feature | False positives | Collapse synonyms; keep one trigger per branch. |
| Description is too long | Context budget waste | Trim to under 1024 chars; move detail to references. |
| No should-not-trigger cases | Surprise false positives | Write near-misses before shipping. |
| Testing only exact skill name | Routing fails in real use | Test realistic, unnamed prompts. |

---

## Saving and sharing evals

Store the final eval set in `evals/evals.json` and reference it from `skills.json`:

```json
{
  "verification": {
    "level": "tested",
    "evals": "evals/evals.json"
  }
}
```

Keep a human-readable summary in `references/EVAL.md` for reviewers who do not run the harness themselves.

---

## Related documents

- [`EVALUATION.md`](./EVALUATION.md) — full evaluation framework, baselines, and composition tests.
- [`fundamentals/evaluation.md`](./fundamentals/evaluation.md) — review checklists and fundamentals.
- [`fundamentals/form-and-style.md`](./fundamentals/form-and-style.md) — leading words, completion criteria, and description craft.
- [`FORMAT.md`](./FORMAT.md) — the `description` field and frontmatter schema.
