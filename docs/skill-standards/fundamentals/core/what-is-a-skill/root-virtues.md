# The root virtues of a skill

**Layer:** universal fundamentals. **Mode:** rule.

Every skill should be judged against these five virtues. Predictability is the root; the others are levers on it.

---

## 1. Predictability

The agent should behave the same *way* every time the skill runs. The output may vary — a brainstorming skill should produce different ideas — but the process should be stable.

A skill exists to wrangle determinism out of a stochastic system.

A `debrief` skill that reads different files on every run but always produces the same report shape is predictable. One that skips the code-exploration phase whenever the ticket "looks easy" is not — same input class, different process.

The **predictability test**: imagine running the skill ten times on similar inputs. Would the agent follow the same process each time? If the answer is no, the skill is too vague.

---

## 2. Load-bearing minimalism

Every sentence, example, and instruction must earn its place. If removing it does not change behavior, it should go.

Minimalism is not about word count. It is about **signal density**. A one-line skill that anchors the right behavior is better than a fifty-line skill that says the same thing in more words.

"Write failing tests before implementation code" is load-bearing. "Testing is an important part of software quality and should be taken seriously" is many words of zero signal.

---

## 3. Fit for purpose

The shape of the skill should match the shape of the problem. A sequential process needs steps. A domain vocabulary needs definitions. A coordination task needs delegation rules. Forcing every skill into the same format weakens it.

A release pipeline fits ordered steps; a design-review skill forced into "step 1, step 2, step 3" just hides the judgment it was meant to encode.

---

## 4. Composability

A skill should work alone and fit cleanly into a larger set. It should declare what it needs from other skills and produce outputs that other skills can consume.

A `research-ticket` skill that writes its findings as a structured context report can feed `debrief`, `orchestrate`, and `pr-report` without any of them re-fetching the ticket.

---

## 5. Explicitness

A skill must be explicit about failure, ambiguity, assumptions, and dependencies. It should not silently skip problems or proceed on guesses.

A skill must also be explicit about **tooling choices**: what tool fulfilled each capability, what alternatives were available, and why a degraded source was accepted. See [`../../architecture/tooling-awareness.md`](../../architecture/tooling-awareness.md).

"Jira adapter unavailable; fell back to manual input, which lacks attachments" is explicit. Silently returning a thinner report is not.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
