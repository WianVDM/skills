# When to create a skill

Not every problem deserves a skill. A skill is one option among several. Choose the right tool for the job.

---

## The decision tree

Ask these questions in order:

### 1. Is this a repeated judgment or process?

If the task only happens once and will never repeat, plain inference or a one-off prompt is probably enough. A skill only earns its maintenance cost if it is used repeatedly.

### 2. Is the judgment subtle enough that the agent varies without guidance?

If the agent reliably does the right thing without a skill, do not create one. A skill is needed when the agent's default behavior is inconsistent or wrong for your domain.

### 3. Is there a deterministic tool, script, MCP server, or extension that already does this?

If yes, use that. A skill should not replicate deterministic logic that a script or tool handles better.

| Approach | Best for |
|----------|----------|
| **Script** | Deterministic, repeatable logic with clear inputs and outputs. |
| **MCP server** | External data or actions that need a structured interface. |
| **Extension / tool** | Tight integration with a specific harness or editor. |
| **Plain inference** | One-off questions or tasks where the agent's priors are sufficient. |
| **Skill** | Repeated, judgment-heavy work where consistency matters. |

### 4. Does this need to be reusable across projects?

If yes, design it as a global skill. It must be harness-agnostic and project-agnostic.

If no, a project-specific skill may be fine, but it should still follow the same structural standards.

See [`../../../patterns/global-pluggable.md`](../../../patterns/global-pluggable.md) for what pluggability requires.

### 5. Does this only make sense alongside other skills?

If the value appears only when combined with other skills, it may be a building block or a conductor, not a standalone skill.

---

## When a skill is the right choice

Create a skill when:

- The task repeats and consistency matters.
- The agent's default behavior is unreliable for this domain.
- The work involves judgment, sequencing, or coordination that a script cannot encode.
- The output is consumed by other skills or future sessions.
- A shared vocabulary or decision framework would reduce friction across sessions.

---

## When not to create a skill

Do not create a skill when:

- A script or MCP server already solves it deterministically.
- The task is a one-off question or exploration.
- The agent's priors are already strong enough.
- The real problem is missing documentation, not missing skill guidance. Fix the docs first.
- The skill would just wrap a single command with no added judgment.

---

## Deeper comparisons

- [`skill-vs-script.md`](./skill-vs-script.md) — scripts-first rule and how skills use scripts.
- [`skill-vs-mcp-server.md`](./skill-vs-mcp-server.md) — skills decide how to use capabilities; MCP servers expose them.
- [`skill-vs-prompt-template.md`](./skill-vs-prompt-template.md) — reusable user input vs. reusable agent guidance.

---

## The litmus test

Before creating a skill, complete this sentence:

> This skill makes the agent more predictable at ______ by enforcing ______.

If you cannot fill in both blanks clearly, the skill is not well-defined enough.

---

## Related documents

- [`../types/`](../types/) — choosing the right skill type once you have decided a skill is the answer.
- [`../lifecycle/`](../lifecycle/) — the full skill lifecycle from decision to retirement.
- [`../common-mistakes/`](../common-mistakes/) — failure modes that often follow from choosing the wrong shape.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
