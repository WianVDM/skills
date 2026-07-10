# Bloat

Bloat is the class of mistakes that make a skill too large or too repetitive. The agent has to wade through excess, or the same meaning is repeated in multiple places.

---

## Sprawl

A skill that is simply too long. Even if every line is live and unique, the agent has to process too much before it can act. Attention thins across the excess.

**Causes**

- Reference material left in `SKILL.md`.
- Multiple unrelated concerns merged into one skill.
- Examples that explain more than they illustrate.

**Cure**

Push reference behind context pointers. Split by branch or sequence so each path carries only what it needs.

---

## Sediment

Stale layers of content that accumulate because adding feels safe and removing feels risky. The skill slowly drifts out of alignment with its actual behavior.

**Causes**

- No pruning discipline.
- Notes and examples added for one-off cases and never reviewed.
- Version changes that leave old guidance in place.

**Cure**

Review the skill after any significant behavior change. Delete guidance that no longer applies.

---

## Duplication

The same meaning expressed in more than one place. It costs maintenance, tokens, and inflates a concept's prominence beyond its real rank.

**Causes**

- Shared conventions copied into every skill.
- The same example repeated in `SKILL.md` and `references/EXAMPLES.md`.
- Synonyms restating the same branch in the description.

**Cure**

Maintain a single source of truth. Extract shared reference into a building-block skill or shared reference file.

See [pruning.md][pruning] for the discipline that prevents duplication.

---

## Premature extraction

Extracting a capability into a separate skill before it has multiple consumers is a form of bloat. It creates an extra identity, an extra dependency edge, and extra context load for a module that is still owned by one skill.

**Symptoms**

- The skill's description names another skill as its primary consumer (e.g., "for the pr-report conductor").
- Only one skill depends on it.
- The skill's interface is shaped by one consumer's contract rather than its own domain.
- The justification for extraction is "it might be useful someday."

**Cure**

Colocate the capability inside the consuming skill. Extract it only when a second consumer appears or when the capability is genuinely cross-cutting.

See the [building-block pattern][building-block] and the [architecture manifesto][architecture] for the extraction criteria.

---

## Research basis

See [sources.md][sources].

[sources]: ../../../reference/sources.md
[building-block]: ../../../patterns/building-block.md
[architecture]: ../../../../manifestos/architecture.md
[pruning]: ../form-and-style/pruning.md
