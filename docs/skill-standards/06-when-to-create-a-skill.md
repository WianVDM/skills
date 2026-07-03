# 06 — When to create a skill

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

See [07-global-vs-project-skills.md](./07-global-vs-project-skills.md) for what pluggability requires.

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

## Skill vs script

A script is deterministic: same input, same output, no reasoning. A skill is judgment-shaped: it guides how the agent reasons.

| Use a script | Use a skill |
|--------------|-------------|
| Detect the project's package manager. | Decide which verification method fits a ticket. |
| Parse a ticket key from a branch name. | Investigate and synthesize ticket context. |
| Run the test suite and return results. | Decide whether the test suite's failure is blocking. |

A skill may call scripts. A script should not call a skill.

### Scripts-first rule

When designing a skill, default to scripts for any logic that is deterministic, repeatable, and stable. Only keep logic in `SKILL.md` when it requires judgment, context, or adaptation.

Signs that a script should exist:

- The agent repeatedly generates the same helper code across invocations.
- The operation has clear inputs and outputs.
- The operation can be tested independently.
- The logic is stable enough that regenerating it each time wastes tokens.

Scripts live in `scripts/`, are referenced from `SKILL.md`, and execute without loading their source into context. This is cheaper and more reliable than asking the agent to recreate the logic each time.

---

## Skill vs MCP server

An MCP server exposes a structured interface to an external system. A skill guides how the agent uses tools.

| Use an MCP server | Use a skill |
|-------------------|-------------|
| Query a database. | Decide what queries to run and how to interpret results. |
| Create a GitHub issue. | Decide how to break a plan into issues. |
| Read from a browser. | Decide what pages to visit and what to capture. |

A skill may invoke an MCP server. An MCP server should not contain skill logic.

---

## Skill vs prompt template

A prompt template is a reusable snippet of user input. A skill is reusable agent guidance.

| Use a prompt template | Use a skill |
|-----------------------|-------------|
| A fixed way to ask the agent to summarize something. | A repeatable process with scope, criteria, and outputs. |
| A reminder to use a specific format. | A contract about how to behave across invocations. |

If the user has to remember to paste it, it is a prompt template. If the agent can reach it, it is a skill.

---

## The litmus test

Before creating a skill, complete this sentence:

> This skill makes the agent more predictable at ______ by enforcing ______.

If you cannot fill in both blanks clearly, the skill is not well-defined enough.
