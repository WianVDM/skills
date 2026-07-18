# Sources and research basis

**Layer:** universal fundamentals. **Mode:** reference.

This document consolidates the research basis and attribution notes for the skill standards. The individual fundamental files reference this document instead of repeating the same notes.

## Primary sources

The claims below draw on these works. Credit where credit is due:

- [Claude Code skills documentation](https://code.claude.com/docs/en/skills) — skill structure, description-as-routing, context load.
- [Cursor rules documentation](https://cursor.com/docs/rules) — always-on vs. dynamic rules and the rules-to-skills boundary.
- [Codex](https://github.com/openai/codex) — `AGENTS.md` as project context; skill loader behavior confirmed in source.
- [Aider documentation](https://aider.chat/docs/) — minimal-harness surfaces (`/run`, `--read`) that inform the plain-markdown export path.
- [Hermes agent](https://github.com/NousResearch/hermes-agent) — frontmatter parsing and skill utilities, confirmed in source.
- [Agent Skills specification](https://agentskills.io/specification) — the minimal frontmatter surface and package metadata.
- [Anthropic skills repository](https://github.com/anthropics/skills) — non-coding and asset-heavy skill examples (`docx`, `pptx`, `xlsx`, `canvas-design`).
- [obra/superpowers](https://github.com/obra/superpowers) — narrow reusable skills, conductor-like orchestration, durable progress ledgers.
- [mattpocock/skills](https://github.com/mattpocock/skills) — practitioner skill craft and daily-driver skill design.
- [aws-samples/sample-agent-skill-eval](https://github.com/aws-samples/sample-agent-skill-eval) — eval artifact shapes and runner design inputs.

## Common denominator research

The core concept of a **skill** as reusable process guidance injected into the agent's context is supported across Claude Code, Cursor, Codex, Aider, and Hermes (all linked above). Each treats a skill as a markdown file with a routing description and a body of guidance. The framing of a skill as a **delegation boundary** — a way for a team to encode "how this kind of work is done here" — is supported by the research synthesis across harness makers and practitioner sources.

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

The following practices are strongly supported by the research across harnesses and practitioner sources (see Primary sources):

- **Context load and routing reliability** — shorter, focused skills are more reliable; bloated or overlapping skills create "skill hell."
- **No secrets in skill files** — a common denominator across every harness and governance source.
- **Destructive-action confirmation** and **read-only investigation by default** in untrusted projects.
- **LLM weakness at negation** — every "do not X" should be paired with a positive directive.
- **Model theory of mind and generalization** — explaining why a rule exists improves adherence more than rigid commands alone.
- **Description quality as the primary determinant of skill routing** — poor descriptions cause false positives and false negatives.
- **Skills rot without attention** — maintenance and retirement are necessary.
- **Not every problem deserves a skill** — scripts, MCP servers, prompt templates, and documentation are often better.

## Harness-specific observations

- **Claude Code**, **Cursor**, and **Codex** support on-demand skill loading and composition, which motivates the building block and conductor types.
- **Cursor** distinguishes always-on rules from dynamic rules (see the [rules documentation](https://cursor.com/docs/rules)). This supports the boundary between context files and skills.
- **Claude Code** distinguishes skills from `CLAUDE.md` and `.claude/rules`.
- **Codex** uses `AGENTS.md` as a project-level context file.
- [mattpocock/skills](https://github.com/mattpocock/skills) and [obra/superpowers](https://github.com/obra/superpowers) emphasize narrow, reusable skills and conductor-like orchestration skills.

## Package and dependency models

The dependency taxonomy (required, recommended, optional) and transitive closure rules are a synthesis of common package models from [npm](https://docs.npmjs.com/), [Python packaging](https://packaging.python.org/), and agent-harness skill ecosystems. The explicit degradation contract (`full` / `degraded` / `blocked`) is our own adaptation to agent workflows, where missing a tool is often recoverable by asking the user.

## Per-document notes

- `dependencies-and-bundling.md` references [`package.md`](./package.md) and [`../patterns/building-block.md`](../patterns/building-block.md) for the machine-readable dependency surfaces.
- `tooling-awareness.md` is our own framework for capability-first tool selection, user-consented degradation, and the adapter tunnel vision failure mode.
- `evaluation.md` draws the guardrail baseline and subjective-output hierarchy from the research evaluation framework.
- `lifecycle/` synthesizes standard software lifecycle stages with the research emphasis on evaluation and governance.
- `security.md` draws the external-access and project-trust sections from research on MCP server governance, third-party tool risk, and audit requirements.
- `structure/` references the conventional layout observed across Claude Code, Cursor, Codex, and the agentskills.io ecosystem.
- `types/` references the cross-cutting patterns (discipline skill, context-file, mode, conductor/implementer split) documented as patterns rather than primary types.
- `when-to-create-a-skill/` frames the skill-vs-MCP distinction as: MCP exposes structured capabilities; skills decide how to use them.
- `common-mistakes/` and `failure-recovery/` synthesize failure modes from skill-review experience and the research on context load, routing reliability, and skill ecosystem quality.
- `form-and-style/` synthesizes the three forms (instruction-heavy, guideline-heavy, hybrid) from the research observation that agent behavior varies by whether the task has a clear sequence or many valid paths.
- `what-is-a-skill/README.md` anchors the standards in the predictability root virtue and the four axes / five virtues framework.
- `examples/` uses illustrative examples drawn from the common patterns observed across the research and our own design practice.

## Related documents

- [`../README.md`](../README.md) — the context stack and how skills fit into it.
- [`package.md`](./package.md) — skill packaging, dependencies, and versioning.
- [`evaluation-framework.md`](./evaluation-framework.md) — the full evaluation framework.
