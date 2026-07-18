# Stateful

**Layer:** proposed architecture. **Mode:** rule.

Skills can be stateless or stateful. The choice depends on whether the skill needs memory across invocations, context compactions, or long-running processes.

---

## Stateless skills

A stateless skill produces the same behavior every time it runs, given the same input and environment. It does not read or write state files.

**When to use**

- The task completes in one shot.
- No memory is needed between invocations.
- The skill is a guideline, vocabulary, or simple atomic action.

**Examples**

- A compressed-response skill that replies in ultra-short form.
- An interview skill that questions the user until shared understanding is reached.
- A shared design-vocabulary skill with no session memory.

**Characteristics**

- Simpler to reason about.
- Easier to compose.
- No resumption logic needed.

---

## Stateful skills

A stateful skill maintains working memory across invocations, context compactions, or long-running phases. It reads and writes state files.

**When to use**

- The task spans multiple turns or sessions.
- Context may be compacted and must be recovered.
- The process has phases that need tracking.
- Output is produced incrementally.

**Examples**

- A ticket-research skill that tracks research phases and incremental report sections.
- A project-orchestration skill that maintains plan, decisions, and phase state across a ticket lifecycle.
- A multi-session teaching skill that remembers progress.

**Characteristics**

- Must document where state lives, its schema, and how to resume.
- Must avoid duplicating state on re-run.
- Must handle context compaction gracefully.

---

## State location

Project-level state lives in a well-known location:

```text
{project-root}/.agents/context/{skill-name}/
├── {key}/
│   ├── state.md              # working memory
│   ├── report.md             # final or incremental output
│   └── artifacts/            # supporting files
└── {key}-checkpoint.md       # latest checkpoint link
```

A skill must document its state layout. Do not scatter state across unrelated directories.

State files are private working memory for one skill. If observations need to be shared across skills, append them to a [`chainlog`](./chainlog.md) and generate reports or views from the chainlog as needed.

---

## State schema

A state file should have a predictable structure. Frontmatter plus markdown body is usually enough:

```yaml
---
skill: ticket-research
version: 1
key: OC-1234
created_at: 2026-06-26T08:00:00Z
updated_at: 2026-06-26T10:30:00Z
phase: research
focus: api-contract
---
```

The schema should include:

- Identifying metadata: skill name, version, key.
- Timestamps for freshness checks.
- Current phase or focus.
- Completion markers for tracked units.

---

## State lifecycle

Treat state as a living document:

1. **Skeleton** — create the state file with pending markers.
2. **Draft** — fill sections as work progresses.
3. **Refined** — update with findings, decisions, and assumptions.
4. **Checkpoint** — write a compact summary after major progress.
5. **Archive** — move old state to an archive location when it is no longer active.

Append important decisions rather than silently overwriting them. Define a pruning or archiving strategy so state files do not grow indefinitely.

---

## Incremental output

Stateful skills should write output incrementally, not only at the end.

Use status markers to track progress:

```markdown
<!-- STATUS: pending -->
```

Replace with:

```markdown
<!-- STATUS: completed -->
```

as sections finish.

Update state after every subagent return and after any context compaction. Re-read state before deciding the next action.

---

## Resumption after compaction

If the session context is compacted, the agent must not guess where it left off. Instead:

1. Read the state file.
2. Read the latest report or checkpoint.
3. Summarize completed work, pending work, current focus, and recommended next action.
4. Resume from the first pending unit.
5. Do not restart completed units unless new information contradicts them.

A skill must document its resumption routine.

---

## Avoiding duplicate work

On re-run, a stateful skill must:

- Check for existing state before creating new state.
- Reuse completed work when it is still valid.
- Surface to the user when restarting would overwrite prior decisions.

Never silently overwrite existing state without asking.

---

## Research basis

- The distinction between **stateless** and **stateful** skills is our own, but it is supported by the research on context compaction, multi-session work, and the need to recover state after context loss.
- The `.agents/context/{skill-name}/{key}/` layout is our own convention, aligned with the research emphasis on well-known locations for context and memory.
- The state lifecycle (skeleton → draft → refined → checkpoint → archive) and the use of status markers are our own practices.
- The **resumption after compaction** routine is our own, informed by the research finding that agents must not guess where they left off after context compaction.
- The rule to **never silently overwrite state** is our own safety practice, aligned with the security fundamentals.
