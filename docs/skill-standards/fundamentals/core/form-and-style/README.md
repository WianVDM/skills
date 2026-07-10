# Form and style

A skill can be written as step-by-step instructions, as a set of guidelines and principles, or as a hybrid of both. The right form depends on what makes the agent more reliable for that specific domain.

There is no universal best form. The goal is predictability, not stylistic purity.

---

## Deeper topics

- [`completion-criteria.md`](./completion-criteria.md) — checkable step endings, premature completion, and legwork.
- [`leading-words.md`](./leading-words.md) — how to use the model's existing priors.
- [`anti-patterns.md`](./anti-patterns.md) — manual in disguise, guideline soup, over-constrained workflow, hidden hybrid.
- [`pruning.md`](./pruning.md) — single source of truth, relevance, and the no-op test.
- [`explain-the-why.md`](./explain-the-why.md) — giving the reasoning behind guidance.
- [`negation-handling.md`](./negation-handling.md) — pairing every prohibition with a positive directive.

---

## The three forms

### 1. Instruction-heavy

The skill lists ordered actions the agent should perform.

**Use when**

- Order matters.
- The agent would otherwise skip or reorder steps.
- The process has clear checkpoints.

**Example**

> 1. Read the current branch name.
> 2. Extract the ticket key, or ask the user for one.
> 3. Load the ticket report if it exists.
> 4. If it does not exist, create a skeleton report.

**Strengths**

- Hard to ignore or misinterpret.
- Good for sequential processes.
- Easy to validate: did the agent do step 3?

**Weaknesses**

- Can constrain the agent where reasoning would be better.
- Becomes brittle if the domain has many branches.

---

### 2. Guideline-heavy

The skill states principles, rules, and boundaries. The agent decides how to apply them.

**Use when**

- The agent's priors are strong for this domain.
- The task has many valid paths.
- The skill is shaping judgment, not enforcing sequence.

**Example**

> Design deep modules: a lot of behavior behind a small interface. Place the seam at a clean location. Test through the public interface.

**Strengths**

- Leaves room for the agent to reason.
- Compact.
- Works well as shared reference.

**Weaknesses**

- The agent may apply principles unevenly.
- Hard to validate without explicit criteria.

---

### 3. Hybrid

The skill uses steps for the process and guidelines for the decisions within each step.

**Use when**

- There is a clear sequence, but the decisions inside it need principles.
- The agent needs both guardrails and freedom.

**Example**

> ### 1. Planning
> Before writing code:
> - Confirm the public interface with the user.
> - Identify deep-module opportunities.
> - List the behaviors to test, not implementation steps.
>
> Tests should verify behavior through public interfaces, not implementation details.

Most real skills are hybrids.

---

## How to choose

Use this decision tree:

1. Does the agent already know the shape of the work?
   - **Yes** → lean toward guidelines.
   - **No** → lean toward instructions.
2. Does order matter?
   - **Yes** → use steps, at least for the sequence.
   - **No** → guidelines are usually enough.
3. Does the agent rush, skip, or vary on this task?
   - **Yes** → add explicit steps with completion criteria.
   - **No** → trust guidelines.
4. Are there many branches or valid paths?
   - **Yes** → guidelines scale better; use steps only for the shared skeleton.
   - **No** → steps are fine.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
