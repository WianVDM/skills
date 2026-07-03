# Glossary

Definitions for the terms used across `write-a-skill` and the skills it produces. Precise vocabulary makes the skill more predictable and easier to maintain.

## Skill terms

### Skill

A compact contract that tells an agent what matters, what to watch for, and what shape the work should take for a specific domain. It is not a script, manual, or one-off prompt.

### Leading word

A compact concept already present in the model's pretraining, used to anchor behavior in the fewest tokens. Example: `grill`, `red`, `tight`, `deep`. It is used in the skill description and body to recruit the same behavior every time.

### Completion criterion

A checkable condition that tells the agent a step or unit of work is done. Strong criteria are both clear and, where it matters, exhaustive.

### Branch

A distinct way a skill can be invoked. In `write-a-skill`, the branches are New, Quick, Review, and Upgrade. Each branch may take a different path through the skill.

### Context pointer

A reference in the agent's context that names out-of-context material and encodes when to reach for it. The `description` is the top-level context pointer; links to `references/` files are disclosed pointers. Wording matters more than the target.

### Progressive disclosure

Moving reference material out of `SKILL.md` and behind a context pointer so the top level stays legible. Inline what every branch needs; disclose what only some branches need.

### Information hierarchy

A ranking of a skill's content by how immediately the agent needs it: in-skill steps, in-skill reference, disclosed reference, external reference.

### Co-location

Keeping related concepts — definition, rules, and caveats — under one heading so reading one part brings its neighbors with it.

## Execution terms

### Legwork

The digging the agent does within a step: reading files, exploring the codebase, testing assumptions. It is raised by strong completion criteria and leading words, not by adding extra steps.

### Premature completion

Ending a step before it is genuinely done because the agent's attention slips toward being finished. Cured by sharpening the completion criterion first; hiding later steps by splitting is the fallback.

### Post-completion steps

The steps that follow the current step. When visible, they tempt the agent toward premature completion. Hiding them by splitting or delegating reduces the pull.

## Pruning terms

### No-op line

A line that changes nothing because the model already does it by default. The test: does this line change behavior versus the default? If not, delete it or replace it with a stronger leading word or completion criterion.

### Relevance

Whether a line still bears on what the skill does. A line loses relevance by being off-topic, stale, or belonging to a branch the skill no longer handles.

### Duplication

The same meaning expressed in more than one place. It costs maintenance, tokens, and inflates a concept's prominence beyond its real rank.

### Sediment

Stale layers of content that accumulate because adding feels safe and removing feels risky. The slow erosion of relevance.

### Sprawl

A skill that is simply too long, even if every line is live and unique. Cured by progressive disclosure and splitting by branch or sequence.

## Domain terms

### Global skill

A skill designed to work in any project, harness, or user context. It detects the environment, declares all assumptions, and fails closed when required capabilities are missing.

### Project-specific skill

A skill that lives inside one project and may assume project-specific tools, paths, or conventions. It still declares its assumptions and follows structural standards.

### Pluggability

The ability of a global skill to drop into an unknown environment and behave correctly. It is not the absence of assumptions; it is the explicit handling of assumptions.

### Global readiness

The degree to which a project-specific skill can become global. Blockers include hardcoded paths, tool names, APIs, and missing dependency declarations.

### Self-audit

A lightweight check against the fundamentals before presenting a design to the user. If the check fails, the design is fixed or the user overrides with a recorded reason.

### Skill-standards fundamentals

The project standards that define predictability, load-bearing minimalism, fit for purpose, composability, and explicitness as the root virtues of a skill.
