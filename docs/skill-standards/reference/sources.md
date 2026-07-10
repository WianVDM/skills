# Sources and research basis

This document consolidates the research basis and attribution notes for the skill standards. The individual fundamental files reference this document instead of repeating the same notes.

## Common denominator research

The core concept of a **skill** as reusable process guidance injected into the agent's context is supported across Claude Code, Cursor, Codex, Aider, and Hermes. Each treats a skill as a markdown file with a routing description and a body of guidance. The framing of a skill as a **delegation boundary** — a way for a team to encode "how this kind of work is done here" — is supported by the research synthesis across harness makers and practitioner sources.

## Our own framework

Many of the concepts in these standards are our own analytical framework, synthesized from the research and from skill-review practice:

- **Predictability** as the root virtue.
- **The four axes**: invocation, information hierarchy, steering, pruning.
- **The five root virtues**: predictability, load-bearing minimalism, fit for purpose, composability, explicitness.
- **The "opposing truths" framing** for capturing tensions in skill design.
- **Completion criteria**, **premature completion**, and **legwork** as analytical tools.
- **Leading words** as a technique for recruiting strong model priors.
- **The no-op test**, **single source of truth**, and **relevance** pruning disciplines.
- **The information hierarchy** and **co-location** principles.
- **Description-as-context-pointer** and **progressive disclosure**.
- **Trigger evals** and the **10 should-trigger / 10 should-not-trigger** target.
- **The predictability test**, **minimalism test**, and **litmus test**.
- **The full / degraded / blocked self-diagnostics contract**.
- **Capability bundles**.
- **The scripts-first rule**.
- **The skill-vs-script-vs-MCP-vs-prompt-template decision tree**.

## Research-supported practices

The following practices are strongly supported by the research across harnesses and practitioner sources:

- **Context cost and routing reliability** — shorter, focused skills are more reliable; bloated or overlapping skills create "skill hell."
- **No secrets in skill files** — a common denominator across every harness and governance source.
- **Destructive-action confirmation** and **read-only investigation by default** in untrusted projects.
- **LLM weakness at negation** — every "do not X" should be paired with a positive directive.
- **Model theory of mind and generalization** — explaining why a rule exists improves adherence more than rigid commands alone.
- **Description quality as the primary determinant of skill routing** — poor descriptions cause false positives and false negatives.
- **Skills rot without attention** — maintenance and retirement are necessary.
- **Not every problem deserves a skill** — scripts, MCP servers, prompt templates, and documentation are often better.

## Harness-specific observations

- **Claude Code**, **Cursor**, and **Codex** support on-demand skill loading and composition, which motivates the building block and conductor types.
- **Cursor** distinguishes always-on rules from dynamic rules, with a `/migrate-to-skills` command that migrates only dynamic rules. This supports the boundary between context files and skills.
- **Claude Code** distinguishes skills from `CLAUDE.md` and `.claude/rules`.
- **Codex** uses `AGENTS.md` as a project-level context file.
- **Matt Pocock's** skill work and **obra/superpowers** emphasize narrow, reusable skills and conductor-like orchestration skills.

## Package and dependency models

The dependency taxonomy (required, recommended, optional) and transitive closure rules are a synthesis of common package models from npm, Python packaging, and agent-harness skill ecosystems. The explicit degradation contract (`full` / `degraded` / `blocked`) is our own adaptation to agent workflows, where missing a tool is often recoverable by asking the user.

## Per-document notes

- `dependencies-and-bundling.md` references `PACKAGE.md` and `patterns/building-block.md` for the machine-readable dependency surfaces.
- `tooling-awareness.md` is our own framework for capability-first tool selection, user-consented degradation, and the adapter tunnel vision failure mode.
- `evaluation.md` draws the guardrail baseline and subjective-output hierarchy from the research evaluation framework.
- `lifecycle/` synthesizes standard software lifecycle stages with the research emphasis on evaluation and governance.
- `security.md` draws the external-access and project-trust sections from research on MCP server governance, third-party tool risk, and audit requirements.
- `structure/` references the conventional layout observed across Claude Code, Cursor, Codex, and the agentskills.io ecosystem.
- `types/` references the cross-cutting patterns (discipline skill, context-file, mode, conductor/implementer split) documented as patterns rather than primary types.
- `when-to-create-a-skill/` frames the skill-vs-MCP distinction as: MCP exposes structured capabilities; skills decide how to use them.
- `common-mistakes/` and `failure-recovery/` synthesize failure modes from skill-review experience and the research on context cost, routing reliability, and skill ecosystem quality.
- `form-and-style/` synthesizes the three forms (instruction-heavy, guideline-heavy, hybrid) from the research observation that agent behavior varies by whether the task has a clear sequence or many valid paths.
- `what-is-a-skill/README.md` anchors the standards in the predictability root virtue and the four axes / five virtues framework.
- `examples/` uses illustrative examples drawn from the common patterns observed across the research and our own design practice.

## Related documents

- [`../README.md`](../README.md) — the context stack and how skills fit into it.
- [`package.md`](./package.md) — skill packaging, dependencies, and versioning.
- [`evaluation-framework.md`](./evaluation-framework.md) — the full evaluation framework.
