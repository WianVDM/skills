# Structure

A skill is a directory. The structure should support the skill's purpose, not impose ceremony. Use only the files and directories that add value.

---

## Conventional layout

```
skill-name/
├── SKILL.md                 # required: identity, intent, core contract
├── README.md                # for human maintainers
├── references/              # disclosed detail: schemas, edge cases, examples
│   ├── REFERENCE.md
│   ├── CONFIG_PATTERN.md
│   ├── CONTEXT_REPORTS.md
│   └── EXAMPLES.md
├── subagents/               # worker personas for delegation
│   └── worker-name.md
├── scripts/                 # deterministic helpers
│   └── detect-env.py
└── assets/                  # templates and static resources
```

Principles:

- `SKILL.md` is required.
- Include `README.md` for non-trivial skills.
- Optional directories should contain content; do not include empty ones.
- Prefer a flat structure; avoid deep nesting.
- Reference links must resolve.

---

## SKILL.md

`SKILL.md` is the skill's public interface. It should contain only what the agent needs on every invocation.

A good `SKILL.md` answers:

- What does this skill do?
- When should it run?
- What is the core contract?
- What is in and out of scope?
- Where does detailed reference live?

Push deep detail into `references/`. Push worker prompts into `subagents/`. Push deterministic logic into `scripts/`.

---

## Frontmatter

A skill declares its identity in the frontmatter of `SKILL.md`. See [`../FORMAT.md`](../reference/format.md) for the full portable frontmatter schema and [`../PACKAGE.md`](../reference/package.md) for package-level metadata. The rest of this section covers the structural role of frontmatter and how to write a strong description.

```yaml
---
name: skill-name
description: What this skill does and when to trigger it.
metadata:
  author: your-name
invocation: model-invoked
---
```

`version` is optional; add it once the skill is shared, consumed, or versioned.

### Naming conventions

- **Skill names**: lowercase, hyphen-separated. Example: `review-code`.
- **Config keys**: lowercase, snake_case. Group related keys under namespaces.
- **Report types**: lowercase, hyphen-separated, matching the directory name.
- **Worker names**: lowercase, role-focused. Example: `investigator.md`.
- **Script names**: lowercase, hyphen-separated, descriptive. Example: `detect-env.py`.

### Requirements

- `name` matches the directory name.
- `description` is under 1024 characters.
- The description states what the skill does and when to use it, with trigger keywords.
- `version` is optional; if used, it should follow semantic meaning for schema or behavior changes once the skill is shared or consumed.

### Invocation mode

A skill is either **model-invoked** or **user-invoked**. The choice trades two loads:

- **Model-invoked**: the description stays in the agent's context, so the skill can fire autonomously and other skills can reach it. This pays **context load** on every turn. A model-invoked skill is still reachable by the user typing its name.
- **User-invoked**: the description is stripped or marked as human-facing. Only the user can invoke it by name. This pays **cognitive load** — the user must remember it exists. No other skill can reach it.

Choose model-invocation only when the agent or another skill must reach the skill on its own. If it only ever fires by hand, make it user-invoked and pay no context load.

When user-invoked skills multiply past what the user can remember, the cure is a **router skill**: a single user-invoked skill that names the others and when to reach for each. A router skill can only hint; it cannot invoke user-invoked skills on the user's behalf.

#### Declaring the invocation mode

The frontmatter should declare the invocation mode explicitly. Use `invocation: model-invoked` or `invocation: user-invoked`. For harnesses that only recognize the boolean flag, `disable-model-invocation: true` is equivalent to `invocation: user-invoked`. If both fields are present, they must agree. Model-invoked is the default when neither field is present. Declaring the mode is recommended by the portable core standard; omitting it leaves the default to the harness.

### Description as a context pointer

The `description` is not just metadata. It is the top-level **context pointer** that causes the agent to load the skill. Its wording, not just its content, decides when and how reliably the skill fires.

A good description:

- States what the skill does.
- Front-loads the **leading word** or domain.
- Lists one trigger per distinct branch. Synonyms that rename the same branch are duplication — collapse them.
- Includes a reach clause for when another skill needs it, if applicable.

Example:

```yaml
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
```

Weak example:

```yaml
description: Helps with UI reviews.
```

#### Trigger evals

Test the description with a trigger eval set before finalizing a skill:

- **10 should-trigger queries** — realistic prompts that should load the skill. Include varied phrasing, casual speech, and cases where the user does not name the skill explicitly.
- **10 should-not-trigger queries** — near-miss prompts that share keywords but should *not* load the skill. These are the most valuable cases.

Run the queries against the agent and check which trigger. If activation is unreliable, rewrite the description and test again. Save the eval set in `references/EVAL.md`.

Avoid easy negatives like "write a Fibonacci function" for a UI review skill. Test the boundary, not the obvious miss.

For user-invoked skills, the description is primarily human-facing, but a clarity eval still helps: collect realistic prompts that should and should not lead a human to reach for the skill. The 10/10 numeric target is most critical for model-invoked skills.

---

## README.md

`README.md` is for human maintainers. It should explain:

- What the skill does in plain language.
- When to use it.
- Directory layout.
- Key conventions.
- How to adapt or extend it.

Do not put operational detail in `README.md` that the agent needs. The agent reads `SKILL.md` and `references/`.

---

## Progressive disclosure and the information hierarchy

Progressive disclosure means putting detail where it belongs on the information hierarchy. The hierarchy ranks content by how immediately the agent needs it:

1. **In-skill step** — an ordered action in `SKILL.md`, the primary tier. What the agent does, in order. Each step ends on a **completion criterion**.
2. **In-skill reference** — a definition, rule, or fact in `SKILL.md`, consulted on demand. A flat peer-set of rules is a legitimate arrangement, not a smell.
3. **Disclosed reference** — material pushed out of `SKILL.md` into a sibling file, reached by a **context pointer**. Loaded only when the pointer fires.
4. **External reference** — shared reference outside the skill system, reachable by any skill. The only shared home two user-invoked skills can use, since neither can invoke the other.

Push too little down and the top of `SKILL.md` bloats. Push too much and you hide material the agent actually needs. The test is **branching**: inline what every branch needs, and disclose what only some branches reach. If a pointer to must-have material fires unreliably, sharpen the pointer wording before inlining.

When a skill has multiple branches with long step-by-step workflows, disclose the detailed workflows behind a pointer. Keep in `SKILL.md` only the branch summary, its completion criterion, and the pointer. This keeps the top-level contract legible while preserving the full process for the branch that needs it.

**Co-location** is the within-file companion to the hierarchy: keep a concept's definition, rules, and caveats under one heading rather than scattered, so reading one part brings its neighbours with it.

---

## Harness-agnostic and project-agnostic language

Skills must not assume a specific agent harness, tool name, slash command, or vendor API.

| Bad | Good |
|-----|------|
| Run `/ticket OC-1234`. | Invoke the ticket-research skill for ticket OC-1234. |
| Call the `Agent` tool. | Spawn a focused worker. |
| Use `git status`. | Check the current working state. |
| Open Jira ticket PROJ-123. | Open the configured issue tracker for ticket PROJ-123. |
| Run `npm test`. | Run the project's test command. |

The skill should detect the environment, consult config, or ask the user.

---

## Optional directories

### references/

Deep detail: schemas, edge cases, examples, config patterns, context report schemas. Every reference file should be reachable from `SKILL.md` or another reference file.

### subagents/

Worker personas for delegation. Each worker prompt must state role, scope, allowed tools, forbidden actions, and return format. Workers should not duplicate shared context.

### scripts/

Deterministic helpers. Scripts should be documented, safe, isolated, and failure-explicit. Prefer read-only inspection unless the script is explicitly designed to mutate state.

### assets/

Templates and static resources. Useful when a skill produces files from a fixed template.

---

## What to avoid

- Empty directories.
- Deep nesting that hides the skill's contract.
- Putting reference detail in `SKILL.md` that most invocations do not need.
- Duplicating the same convention explanation across multiple skills.

---

## Research basis

See [SOURCES.md](../reference/sources.md).
