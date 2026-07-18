# Wrapper

**Layer:** proposed architecture. **Mode:** rule.

A wrapper skill is a thin layer that adapts a building block or conductor for human interaction. It adds prompts, presentation, confirmation, and user-facing language without containing the core logic of the wrapped skill.

Wrappers are the third layer of the architecture. They sit between the user and the reusable machinery underneath.

---

## When to use a wrapper

Use a wrapper when:

- A building block or conductor exists but needs user-facing prompts or confirmation.
- The user should see a curated summary rather than raw output.
- The workflow needs explicit human gates between phases.
- The same underlying capability must be presented differently to different audiences.

Do not use a wrapper when:

- The skill is doing real work that belongs in a building block.
- There is no underlying skill to wrap; the wrapper would become a bloated conductor.
- The user can invoke the underlying skill directly without confusion.

---

## What a wrapper is not

A wrapper is not:

- A conductor. It does not coordinate phases or maintain complex state.
- A building block. It does not provide reusable capability to other skills.
- A replacement for a good `description` in the underlying skill.

A wrapper's job is the interface. If you find yourself adding workflow logic, checkpoints, or deep orchestration, you are probably writing a conductor or a hybrid skill instead.

---

## Wrapper anatomy

```
wrapper-name/
├── SKILL.md                 # user-facing contract: prompts, confirmation, presentation
├── README.md                # for human maintainers
├── references/
│   └── EXAMPLES.md          # sample prompts and expected outputs
└── assets/                  # templates for user-facing output
    └── templates/
```

A wrapper is usually **user-invoked** because its primary consumer is the human. It may reference the underlying skill by name, but it cannot invoke model-invoked skills on the user's behalf unless the harness explicitly allows it.

---

## Core responsibilities

### 1. Prompt the user clearly

A wrapper should ask the user for what it needs in plain language. Each prompt should:

- State what the wrapper is about to do.
- Explain what information is needed and why.
- Offer sensible defaults when possible.
- Accept the user's answer and pass it to the underlying skill.

### 2. Confirm destructive actions

If the wrapped skill can mutate state, the wrapper must:

- State what will change.
- Explain the consequences.
- Require explicit confirmation before proceeding.
- Offer a dry-run or preview when possible.

See [`../fundamentals/architecture/security.md`](../fundamentals/architecture/security.md) for destructive-action rules.

### 3. Present results

A wrapper should translate raw output into a form the user can act on:

- Summarize long outputs.
- Highlight decisions or next steps.
- Preserve the original output in a reference or report when the user might need it.
- Avoid rephrasing in a way that loses precision.

### 4. Stay thin

A wrapper should not:

- Reimplement logic from the wrapped skill.
- Maintain complex state across phases.
- Delegate to many workers.
- Hide destructive actions behind friendly language.

If the wrapper is growing, reconsider whether the underlying skill should be split or the wrapper should become a conductor.

---

## Invocation mode

Wrappers are almost always **user-invoked**. Their descriptions are human-facing, so context load is low.

A wrapper may be used as a **router**: a single user-invoked skill that names several related skills and tells the user when to reach for each. A router cannot invoke the other skills; it can only guide the user.

```markdown
# Tools router

This router points to user-invoked tools for design, testing, and deployment. Use it when you need one of these but cannot remember the exact name.

- `review-ui` — review UI code for design-system compliance.
- `run-tests` — run the project's test command and report results.
- `deploy-preview` — deploy a preview build.
```

---

## Common wrapper patterns

### The prompt-and-pass wrapper

The wrapper collects missing inputs and passes them to the underlying skill.

**Example:** a `summarize` wrapper asks the user for the target length and format, then invokes the underlying `summarize-text` building block with those parameters.

### The confirm-and-proceed wrapper

The wrapper previews what the underlying skill will do and asks for confirmation.

**Example:** an `install-skill` wrapper lists the skills to be installed, their sources, and the files that will change, then asks the user to confirm before invoking the underlying `install-skill` building block.

### The summarize-and-present wrapper

The wrapper takes the output of a conductor and presents it in a human-readable form.

**Example:** a `debrief-report` wrapper takes the structured report from the `debrief` conductor and produces a concise summary for the user.

### The router wrapper

The wrapper does not invoke other skills; it names them and explains when to use each.

**Example:** a `tools` wrapper lists all available skills for a domain and asks the user which one to run.

---

## Anti-patterns

| Anti-pattern | Problem | Cure |
|---|---|---|
| Fat wrapper | The wrapper contains core logic that should live in a building block. | Move the logic down. |
| Hidden conductor | The wrapper coordinates multiple skills and phases. | Promote it to a conductor. |
| Silent destructive wrapper | The wrapper performs mutations without confirmation. | Add explicit confirmation. |
| Chatty wrapper | The wrapper asks too many questions or rephrases obvious outputs. | Cut prompts to the minimum. |
| Leaky wrapper | The wrapper exposes raw internal output that the user cannot act on. | Summarize and contextualize. |

---

## Research basis

- The **wrapper** as a thin user-facing adaptation layer is our own framing, but it is supported by the research observation that skills often need a distinct user-facing boundary (e.g., Cursor commands with `disable-model-invocation: true`, Claude Code user-invoked skills).
- The **prompt-and-pass**, **confirm-and-proceed**, **summarize-and-present**, and **router** wrapper patterns are our own taxonomy, derived from common user-interaction needs.
- The rule that a wrapper should not contain core logic is our own design choice, aligned with the building block / conductor / wrapper separation.
- The **router wrapper** concept (a user-invoked skill that names other user-invoked skills) is our own, supported by the research observation that users cannot remember many user-invoked skills and benefit from a single entry point.
- The **wrapper vs. conductor** promotion rule is our own, informed by the research on workflow skills and the need to separate presentation from orchestration.

---

## Wrapper checklist

- [ ] The wrapper is user-invoked.
- [ ] The wrapper's job is presentation, prompts, or confirmation.
- [ ] Core logic lives in a building block or conductor.
- [ ] Destructive actions are confirmed.
- [ ] The user sees a clear summary of results.
- [ ] The wrapper does not reimplement logic from the skill it wraps.
- [ ] The wrapper does not coordinate multiple phases or maintain complex state.

---

## Related documents

- [`building-block.md`](./building-block.md) — the layer a wrapper usually sits on top of.
- [`conductor.md`](./conductor.md) — the layer a wrapper should not become.
- [`../fundamentals/architecture/types/`](../fundamentals/architecture/types/) — choosing the right skill type.
- [`../fundamentals/architecture/security.md`](../fundamentals/architecture/security.md) — destructive actions and confirmation.
