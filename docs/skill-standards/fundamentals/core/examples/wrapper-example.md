# Wrapper example

**Layer:** universal fundamentals. **Mode:** reference.

A wrapper skill that adapts a building block for human interaction.

```text
run-ui-review/
├── SKILL.md
└── README.md
```

## `SKILL.md`

```markdown
---
name: run-ui-review
invocation: user-invoked
description: Run a UI review for the user. Use when the user asks to "review my UI", "check my UI", or "audit the design of this page".
---

# Run UI review

Prompt the user for scope, run the `review-ui` building block, and present the results in a concise summary.

## In scope

- Ask which files, components, or pages to review.
- Invoke `review-ui` with the chosen scope.
- Summarize findings for the user.

## Out of scope

- Do not perform the UI review inline; delegate to `review-ui`.
- Do not make changes to files unless the user explicitly asks.

## Steps

1. Ask the user what to review.
2. Invoke `review-ui` with the selected scope.
3. Collect the review report.
4. Present a concise summary with action items.

## Dependencies

- `review-ui` — the building block that performs the actual review.

## Security

- Destructive actions require explicit user confirmation.
- The wrapper does not write files; it delegates to the building block.
```

## Why it works

- **User-invoked:** the wrapper is explicitly called by the user.
- **Thin adaptation layer:** it only handles prompts and presentation.
- **Core logic stays in the building block:** `review-ui` remains reusable.
- **Clear boundaries:** the user knows the wrapper is coordinating, not reviewing.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
