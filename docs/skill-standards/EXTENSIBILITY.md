# Extensibility

## At a glance

This document extends the core standard to **non-coding skills** and **multi-agent coordination**. It covers asset-heavy skills, output-format triggers, verification artifacts, subjective-output evaluation, and file-based handoffs.

**Read this if:** you are writing a design, writing, data, or visual skill, or coordinating multiple agents.

The core standard is intentionally focused on coding and general-purpose skills, but the same model extends to non-coding domains and multi-agent coordination. This document describes how the core standard applies to those domains and what additional considerations they introduce.

---

## Non-coding skills

A non-coding skill uses the same `SKILL.md` core as a coding skill. The differences are in the assets, outputs, and evaluation methods.

### Asset-heavy skills

Non-coding skills often ship large assets: fonts, images, templates, samples, color palettes, brand guidelines.

Use the `assets/` directory for these:

```text
brand-guidelines/
├── SKILL.md
├── README.md
├── assets/
│   ├── fonts/
│   ├── logos/
│   ├── color-palette.json
│   └── templates/
└── references/
    └── USAGE.md
```

Recommendations:

- Use relative paths from `SKILL.md` to reference assets.
- Provide integrity hashes for large assets when distribution matters.
- Lazy-loading and packaging are harness-specific; keep the skill layout portable.

### Output-format triggers

Non-coding skills often produce a specific output format: `.docx`, `.pptx`, `.xlsx`, `.png`, `.pdf`, `.svg`, etc. The `description` should include the output format as a trigger.

Example:

```yaml
description: Generate a PowerPoint presentation from an outline. Use when asked for "slides", "deck", "presentation", or "pptx".
```

### File I/O and binary artifacts

Non-coding skills should:

- Use a temporary workspace for intermediate rendering.
- Write final artifacts to user-requested paths.
- Clean up temporary files.
- Track outputs in the audit trail.

### Verification artifacts

Recommend producing verification artifacts for complex outputs:

- **Visual skills** — rendered previews or thumbnails.
- **Spreadsheet skills** — recalc logs or formula check reports.
- **Document skills** — XML validation reports or structure checks.
- **General** — a `qa-report.json` or equivalent.

### Subjective-output evaluation

Non-coding outputs are often evaluated subjectively. Use the subjective-output hierarchy from `EVALUATION.md`:

1. Deterministic checks.
2. Visual QA or reader testing.
3. Structured-rubric LLM judge.
4. Human review.

Individual verdicts are capped at medium-high confidence.

### Non-coding skill workflow

A typical non-coding skill follows the same structure as a coding skill:

1. Understand the request and constraints.
2. Load relevant templates, brand guidelines, or examples.
3. Generate intermediate drafts or renders.
4. Verify the output.
5. Present or save the final artifact.

The coordination patterns are the same; only the handoff artifacts differ.

---

## Multi-agent coordination

A skill can describe multi-agent coordination without depending on a specific harness's agent primitives. The standard supports this through **file-based handoffs** and a **coordination vocabulary**.

### Minimum viable coordination model

For small teams or single-agent harnesses, use **delegate-and-summarize**:

1. The conductor skill creates a task brief.
2. It dispatches the brief to a subagent or worker.
3. The worker returns a structured artifact.
4. The conductor reviews the artifact and decides what to do next.

If the harness does not support subagents, the conductor runs the worker logic inline.

### Coordination vocabulary

The standard defines three coordination patterns:

1. **Delegate-and-summarize** — one conductor delegates to one or more workers and integrates their outputs.
2. **Peer collaboration** — two or more agents work on the same task with a shared ledger or plan.
3. **Skill-driven workflow** — a conductor invokes building-block skills in sequence, using context reports to share state.

The exact peer-to-peer semantics (mailbox, task list, plan approval) are product-specific and are not part of the v1 core. The standard defines the vocabulary and handoff conventions; harnesses implement the primitives.

### File-based handoffs

Shared context between agents should use file-based handoffs and durable progress ledgers:

```text
.agents/context/
├── plan/
│   └── task-123-plan.md
├── task-briefs/
│   └── task-123-worker-a.md
├── results/
│   └── task-123-worker-a.md
└── ledgers/
    └── task-123-progress.md
```

Each handoff file should include:

- A clear task description.
- Required inputs and expected outputs.
- The current state of the work.
- Open questions or blockers.

This keeps agents loosely coupled and makes isolation easier to reason about.

### Shared context without breaking isolation

Agents should share context through files, not through shared mutable memory. Each agent should:

- Read the handoff file at the start of its task.
- Write its results to a new file.
- Not modify another agent's state files unless explicitly authorized.

Isolation details (processes, sandboxes, worktrees) are harness-specific.

### MCP dependency declaration

A skill that needs an MCP server declares it in `skills.json` by name and capability, not by host config path:

```json
{
  "requirements": {
    "mcp_servers": [
      {
        "name": "design-system",
        "capabilities": ["query_component", "fetch_asset"]
      }
    ]
  }
}
```

The harness maps this to its native MCP configuration.

### Non-coding multi-agent tasks

For design, writing, or data tasks, multi-agent coordination follows the same patterns but uses different handoff artifacts:

- Visual tasks — rendered previews, mockups, asset files.
- Writing tasks — drafts, outlines, reader feedback.
- Data tasks — structured data, validation reports, recalc logs.

The coordination model is the same; only the artifacts differ.

---

## Limitations

The following extensibility concerns are **limited** and are documented as such:

- Harness-specific agent envelopes are intentionally not standardized in v1.
- Experimental transports like "Skills Over MCP" are not a near-term target.
- Peer-to-peer agent-team semantics vary by product.
- Visual QA tooling and cultural/design bias elimination are not mature.
- Empirical multi-agent and non-coding benchmarks are limited.

---

## Key takeaways

- Non-coding skills use the **same `SKILL.md` core** as coding skills; differences are in assets, outputs, and evaluation.
- Ship large static resources in **`assets/`** and reference them with relative paths.
- Include **output-format triggers** in the `description` when the skill produces a specific file type.
- Produce **verification artifacts** (previews, recalc logs, validation reports) for complex outputs.
- Use the **subjective-output hierarchy** from `EVALUATION.md` for non-coding outputs.
- Coordinate agents through **file-based handoffs** and shared ledgers, not shared mutable memory.
- Declare **MCP dependencies** by name and capability, not by host config path.
- Agent envelopes and peer-to-peer semantics remain **harness-specific** and are intentionally not standardized in v1.

## Research basis

- The **non-coding skill** model is drawn from the Anthropic skills repository examples (`brand-guidelines`, `docx`, `pptx`, `xlsx`, `canvas-design`, `algorithmic-art`) and the research synthesis.
- **Asset-heavy skill layout** (`assets/`, `templates/`, `fonts/`, `samples/`) is supported by the Anthropic `canvas-design` skill and similar examples.
- **Output-format triggers** and **file I/O conventions** are our own practices, aligned with the research observation that non-coding skills need clear format signals and safe temp-file handling.
- **Verification artifacts** and **subjective-output hierarchy** are drawn from the research evaluation framework.
- The **multi-agent coordination** vocabulary and **file-based handoff** pattern are drawn from the research on multi-agent coordination, obra/superpowers durable progress ledgers, and Claude Code worktree isolation.
- The recommendation to leave **agent envelopes** (tools, model, MCP, sandbox) harness-specific is drawn from the research finding that no convergence exists on a shared subagent format.
- **MCP dependency declaration** is drawn from the research on MCP governance and the dependency model in `PACKAGE.md`.

---

## Related documents

- [`FORMAT.md`](./FORMAT.md) — the `SKILL.md` core and sibling directories.
- [`PACKAGE.md`](./PACKAGE.md) — dependency declaration.
- [`EVALUATION.md`](./EVALUATION.md) — evaluation framework, including subjective-output hierarchy and multi-agent evaluation.
- [`GOVERNANCE.md`](./GOVERNANCE.md) — provenance and audit.
- [`patterns/conductor.md`](./patterns/conductor.md) — coordination and delegation.
- [`patterns/conductor-implementer-split.md`](./patterns/conductor-implementer-split.md) — reasoning/execution split.
- [`patterns/context-reports.md`](./patterns/context-reports.md) — structured shared artifacts.
