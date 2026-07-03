# 01 — What is a skill?

A skill is the **smallest load-bearing shape** that makes an agent reliably do the right thing for a specific domain.

It is not:

- A script the agent executes word for word.
- A manual the agent reads before acting.
- A prompt the user types every time.
- A configuration file.

A skill is a **contract**. It tells the agent what matters, what to watch for, and what shape the work should take. The agent still decides the exact actions.

---

## The root virtue: predictability

A skill exists to wrangle determinism out of a stochastic system. The root virtue is **predictability**: the agent should follow the same *process* every time the skill runs. The output may vary — a brainstorming skill should produce different ideas — but the behavior should be stable.

Every other concept in these standards serves predictability. Cost, maintainability, and clarity are symptoms of it, not rivals.

See [13-evaluation.md](./13-evaluation.md) for the predictability test.

---

## The four axes

Skill design is the deliberate tuning of four axes. Each axis is a set of levers that make the agent more predictable.

### 1. Invocation

How the skill is reached and the cost paid for that reach.

- **Model-invoked** skills keep their description, so the agent can fire them and other skills can reach them. They pay **context load**.
- **User-invoked** skills strip the description, so only the human can reach them by name. They pay **cognitive load**.

See [04-structure.md](./04-structure.md) for invocation mode.

### 2. Information hierarchy

How the skill's content is arranged and how far down the ladder each piece sits.

- **In-skill steps** — ordered actions in `SKILL.md`.
- **In-skill reference** — definitions, rules, and facts in `SKILL.md`.
- **Disclosed reference** — material behind a context pointer in a sibling file.
- **External reference** — shared reference outside the skill system, reachable by any skill.

See [04-structure.md](./04-structure.md) for progressive disclosure and the information hierarchy.

### 3. Steering

How the skill shapes the agent's runtime behavior.

- **Leading words** recruit priors the model already holds.
- **Completion criteria** tell the agent when a step is done.
- **Legwork** is the digging the agent does within a step.
- **Post-completion steps** are the later steps that tempt the agent to rush.

See [03-form-and-style.md](./03-form-and-style.md) for steering levers.

### 4. Pruning

How the skill is kept lean and relevant.

- **Single source of truth** — one authoritative place for each meaning.
- **No-op test** — does this line change behavior versus the default?
- **Relevance** — does this line still bear on what the skill does?
- **Sediment** and **duplication** are the failure modes pruning prevents.

See [05-common-mistakes.md](./05-common-mistakes.md) for failure modes and cures.

---

## The root virtues

Every skill should be judged against these five virtues. Predictability is the root; the others are levers on it.

### 1. Predictability

The agent should behave the same *way* every time the skill runs. The output may vary — a brainstorming skill should produce different ideas — but the process should be stable.

A skill exists to wrangle determinism out of a stochastic system.

### 2. Load-bearing minimalism

Every sentence, example, and instruction must earn its place. If removing it does not change behavior, it should go.

Minimalism is not about word count. It is about **signal density**. A one-line skill that anchors the right behavior is better than a fifty-line skill that says the same thing in more words.

### 3. Fit for purpose

The shape of the skill should match the shape of the problem. A sequential process needs steps. A domain vocabulary needs definitions. A coordination task needs delegation rules. Forcing every skill into the same format weakens it.

### 4. Composability

A skill should work alone and fit cleanly into a larger set. It should declare what it needs from other skills and produce outputs that other skills can consume.

### 5. Explicitness

A skill must be explicit about failure, ambiguity, assumptions, and dependencies. It should not silently skip problems or proceed on guesses.

---

## Opposing truths

Several tensions run through skill design. Both sides are true.

| Tension | Both are true |
|---------|---------------|
| Minimal vs complete | Cut to the bone, but not so far that the agent has to guess. |
| Explicit vs implicit | Give steps where the agent would vary; trust priors where the agent already knows the shape. |
| Standalone vs composable | A skill should work alone, but also play well with others. |
| Stable vs self-improving | A skill should have invariant principles, but adapt to project preferences through config and notes. |
| Author control vs agent freedom | The skill shapes behavior; the agent decides actions. |

The right answer in each case is: **it depends on the domain and on how the agent behaves without the guardrail.**

---

## When a skill stops being useful

A skill has failed when:

- The agent ignores it because it is too long or too vague.
- The agent follows it mechanically and produces worse results than it would have without it.
- It duplicates something a script, MCP server, or existing tool already does better.
- It tries to solve too many unrelated problems.
- It hides assumptions that later cause the agent to guess wrong.

If any of these are true, the skill needs to be pruned, split, or removed.
