# The root virtues of a skill

Every skill should be judged against these five virtues. Predictability is the root; the others are levers on it.

---

## 1. Predictability

The agent should behave the same *way* every time the skill runs. The output may vary — a brainstorming skill should produce different ideas — but the process should be stable.

A skill exists to wrangle determinism out of a stochastic system.

---

## 2. Load-bearing minimalism

Every sentence, example, and instruction must earn its place. If removing it does not change behavior, it should go.

Minimalism is not about word count. It is about **signal density**. A one-line skill that anchors the right behavior is better than a fifty-line skill that says the same thing in more words.

---

## 3. Fit for purpose

The shape of the skill should match the shape of the problem. A sequential process needs steps. A domain vocabulary needs definitions. A coordination task needs delegation rules. Forcing every skill into the same format weakens it.

---

## 4. Composability

A skill should work alone and fit cleanly into a larger set. It should declare what it needs from other skills and produce outputs that other skills can consume.

---

## 5. Explicitness

A skill must be explicit about failure, ambiguity, assumptions, and dependencies. It should not silently skip problems or proceed on guesses.

A skill must also be explicit about **tooling choices**: what tool fulfilled each capability, what alternatives were available, and why a degraded source was accepted. See [`../../architecture/tooling-awareness.md`](../../architecture/tooling-awareness.md).

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
