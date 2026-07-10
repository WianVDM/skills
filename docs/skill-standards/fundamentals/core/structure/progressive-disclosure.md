# Progressive disclosure

Progressive disclosure means putting detail where it belongs on the information hierarchy. The hierarchy ranks content by how immediately the agent needs it:

1. **In-skill step** — an ordered action in `SKILL.md`, the primary tier. What the agent does, in order. Each step ends on a **completion criterion**.
2. **In-skill reference** — a definition, rule, or fact in `SKILL.md`, consulted on demand. A flat peer-set of rules is a legitimate arrangement, not a smell.
3. **Disclosed reference** — material pushed out of `SKILL.md` into a sibling file, reached by a **context pointer**. Loaded only when the pointer fires.
4. **External reference** — shared reference outside the skill system, reachable by any skill. The only shared home two user-invoked skills can use, since neither can invoke the other.

Push too little down and the top of `SKILL.md` bloats. Push too much and you hide material the agent actually needs. The test is **branching**: inline what every branch needs, and disclose what only some branches reach. If a pointer to must-have material fires unreliably, sharpen the pointer wording before inlining.

When a skill has multiple branches with long step-by-step workflows, disclose the detailed workflows behind a pointer. Keep in `SKILL.md` only the branch summary, its completion criterion, and the pointer. This keeps the top-level contract legible while preserving the full process for the branch that needs it.

**Co-location** is the within-file companion to the hierarchy: keep a concept's definition, rules, and caveats under one heading rather than scattered, so reading one part brings its neighbours with it.

See [`../form-and-style/completion-criteria.md`](../form-and-style/completion-criteria.md) for completion criteria and [`../common-mistakes/bloat.md`](../common-mistakes/bloat.md) for sprawl as a failure mode.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
