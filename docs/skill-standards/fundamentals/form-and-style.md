# Form and style

A skill can be written as step-by-step instructions, as a set of guidelines and principles, or as a hybrid of both. The right form depends on what makes the agent more reliable for that specific domain.

There is no universal best form. The goal is predictability, not stylistic purity.

When a skill has steps, each step should end on a **completion criterion**: a checkable condition that tells the agent the step is done. A vague criterion invites **premature completion** — the agent declares the step done and rushes toward the next one. A strong criterion forces the right amount of **legwork** — the digging the agent does within the step.

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

## Completion criteria

Whenever a skill has steps, each step should end on a **completion criterion**: a checkable condition that tells the agent the step is done.

A strong criterion is:

- **Checkable** — can the agent tell done from not-done?
- **Exhaustive** — where it matters, does it demand all the work?

| Weak | Strong |
|------|--------|
| Understand the ticket. | The ticket key, summary, acceptance criteria, and current status are recorded in the ticket report. |
| Write tests. | A failing test exists for the first behavior, and it fails for the expected reason. |
| Capture current state. | The report contains the branch, commit, scope, method, and at least one artifact. |

A vague criterion invites **premature completion** — ending a step before it is genuinely done because the agent's attention slips toward being finished. The cure is to sharpen the criterion first. Only if the criterion is irreducibly fuzzy and you actually observe the rush should you hide the later steps by splitting the skill.

### Premature completion

**Premature completion** happens when visible **post-completion steps** pull the agent forward. The agent sees the next steps and rushes the current one. Two defenses:

1. Sharpen the completion criterion. This is local and cheap.
2. Hide the later steps by splitting the skill or delegating them. This works only when the later steps leave the agent's context entirely (a subagent dispatch or a user-invoked hand-off).

### Legwork

**Legwork** is the work the agent does within a step without being told explicitly how to do it — reading files, exploring the code, testing assumptions. A demanding completion criterion raises legwork. A weak criterion lets it stay thin.

Legwork is never written as its own step. It is latent in the wording of the step and its completion criterion.

---

## Leading words and priors

A **leading word** is a compact concept already present in the model's pretraining. Using it anchors behavior in fewer tokens.

| Instead of | Leading word |
|------------|--------------|
| fast, deterministic, low-overhead | tight |
| a loop you believe in | red |
| interview relentlessly until nothing is unclear | grill |
| hide complexity behind a simple interface | deep |

Leading words work because they recruit priors the model already holds. They improve predictability while keeping the skill short.

A leading word must be reinforced by context. If the skill uses `deep`, it must define what deep means in this domain at least once, then rely on the word thereafter.

A leading word can also anchor **invocation**: when the same word appears in the user's prompts, docs, and codebase, the agent links that shared language to the skill and fires it more reliably. Front-load the leading word in the skill's description.

A weak leading word that does not beat the default is a **no-op**. The fix is a stronger word, not a different technique.

---

## Anti-patterns

### Manual in disguise

A skill that lists every keystroke and command. The agent becomes a slow script executor.

> Bad: “Run `git status`, then `git diff`, then `git log --oneline -5`.”
>
> Better: “Understand the current working state before making changes.”

### Vague guideline soup

A skill that says many true things but gives the agent no purchase point. Often caused by weak or missing leading words and completion criteria.

> Bad: “Be thorough. Consider edge cases. Write good tests.”
>
> Better: “For each public behavior, write one test through the public interface. Stop when the user confirms the listed behaviors are covered.”

### Over-constrained workflow

A skill that forces a rigid sequence where the domain has no natural sequence.

> Bad: A security review skill with ten mandatory steps in order.
>
> Better: A security review skill with a checklist the agent applies as it explores.

### Hidden hybrid

A skill that mixes steps and guidelines without signaling which is which. The agent cannot tell what is mandatory and what is advisory.

Use headings, numbering, and explicit wording to separate the two.

### No-op lines

A line that changes nothing because the agent already does it by default. Common examples:

- “Be thorough.” The agent is already thorough-ish.
- “Think carefully.” The agent already reasons.
- “Consider all options.” Too vague to change behavior.

Run the **no-op test**: does this line change behavior versus the default? If not, delete it or replace it with a stronger leading word or completion criterion.

---

## Pruning

A skill should be kept lean. Three disciplines help:

### Single source of truth

Each meaning should live in exactly one authoritative place. If a convention appears in multiple skills, extract it into a building-block skill or shared reference. Duplication inflates a concept's prominence and makes maintenance harder.

### Relevance

Does this line still bear on what the skill does? If a line is stale, off-topic, or belongs to a branch the skill no longer handles, remove it. A shorter skill is easier to keep relevant.

### No-op test

Run the **no-op test** on every line: *does this change behavior versus the default?* If the answer is no, the line is a no-op and should be deleted or replaced with a stronger leading word or completion criterion.

A line can be perfectly relevant and still a no-op. "Be thorough" is relevant but usually a no-op. "Relentless" is a stronger leading word that passes the test.

This is model-relative: if you disagree whether a line is a no-op, settle it by running the skill, not by debate.

---

## Research basis

- The three forms (instruction-heavy, guideline-heavy, hybrid) and the recommendation to match form to problem shape are our own framework, supported by the research observation that agent behavior varies by whether the task has a clear sequence or many valid paths.
- **Completion criteria**, **premature completion**, and **legwork** are our own analytical tools, synthesized from the research on predictability and the common failure mode of agents rushing steps.
- **Leading words** are our own technique, based on the observation that models have strong priors for compact concepts and that shorter, denser guidance is more reliable.
- The **explain-the-why** pattern is supported by the research on model theory of mind and generalization; rigid commands often fail when context changes.
- **Negation handling** is supported by the well-documented finding that LLMs handle negation weakly; the "pair prohibition with positive directive" rule is our own practice.
- The **no-op test**, **single source of truth**, and **relevance** pruning disciplines are our own, aligned with the research emphasis on minimalism and context cost.


---

## Explain the why

A skill should explain the reasoning behind its guidance, not just issue commands. Today's models have strong theory of mind and generalize better when they understand intent. This applies to steps and phases too: a one-line rationale for why a phase exists ("why this step before the next") reduces premature completion and helps the agent judge how much legwork is required.

| Rigid command | Explain-the-why |
|---------------|-----------------|
| NEVER mock internal functions. | Mocking internal functions couples tests to implementation. Prefer mocking at seams where the implementation can change without breaking the test. |
| ALWAYS write one test per behavior. | One test per behavior keeps failures diagnostic: a failing test points to one capability, not many. |

If you find yourself writing `ALWAYS`, `NEVER`, or `MUST` in all caps, treat it as a yellow flag. Reframe the instruction by explaining why the rule exists. The agent will apply it more reliably and adapt it better to edge cases.

Exceptions remain valid. Some safety or compliance rules are absolute. Mark those explicitly and explain why no exception is allowed.

---

## Negation handling

LLMs handle negation weakly. A rule that says "do not X" may still prime the agent toward X. Pair every prohibition with a positive directive.

| Weak | Strong |
|------|--------|
| Do not mock internal functions. | Mock at public seams. Internal functions stay unmocked. |
| Do not write all tests first. | Write one test, then the code to pass it, then repeat. |
| Do not skip the current-state capture. | Run the current-state capture for any ticket with verifiable UI, API, or code state. |

The positive directive tells the agent what *to* do. The negation only clarifies what to avoid.
