# Glossary

**Layer:** universal fundamentals. **Mode:** reference.

This glossary defines the terms used across the skill standards. Use consistent terminology when writing or reviewing skills. The model reads meaning from how words are used, so precision matters.

---

## Skill terms

### Skill

The smallest load-bearing shape that makes an agent reliably do the right thing for a specific domain. A contract between author and agent, not a script or manual.

### Delegation boundary

What a skill is: a contract that lets a team encode "how this kind of work is done here" and have that guidance travel with the agent across sessions and tasks. The skill sets the boundary; the agent still decides the exact actions inside it.

### Invocation mode

How a skill is reached. **Model-invoked** skills keep their description in the agent's context so the agent and other skills can route to them, paying context load on every turn. **User-invoked** skills are reachable only by name, paying cognitive load instead. Declared in frontmatter as `invocation`.

### Context stack

The layered context model a skill sits in: always-on context files (`AGENTS.md`), scoped rules, skills, MCP servers and tools, and subagents. A skill may call lower layers but must not blur into them.

### Determinism device

A mechanism that makes a stochastic system behave more predictably. A skill is a determinism device for an agent.

### Predictability

The degree to which a skill makes the agent follow the same *process* on every run. Output may vary; behavior should not. The root virtue every other concept serves.

### Root virtue

The single value that every other lever in a skill serves. For agent skills, the root virtue is **Predictability**.

### Load-bearing minimalism

Every line in a skill must earn its place. If removing a sentence does not change behavior, it should be removed. Not about word count; about signal density.

### Completion criterion

A checkable condition that tells the agent a step or unit of work is done. Strong criteria are clear and exhaustive.

### Leading word

A compact concept already present in the model's pretraining, used to anchor behavior in few tokens. Example: `deep`, `tight`, `red`, `grill`. Recruits priors the model already holds.

### Legwork

The work an agent does within a step or guideline — reading files, exploring code, testing assumptions — without being told explicitly how to do it.

### Premature completion

Ending a step before it is genuinely done because the agent's attention slips toward being finished. Caused by vague completion criteria or visible **post-completion steps** pulling attention forward. Cured by sharpening the criterion first; splitting or delegating is the fallback when the criterion cannot be made sharp and the rush is observed.

### Post-completion steps

The steps that follow the current step. When visible, they tempt the agent toward **premature completion**. Hiding them by splitting or delegating reduces the pull, but only if the later steps truly leave the agent's context.

### Progressive disclosure

Moving reference material out of `SKILL.md` and behind a pointer, so the top level stays legible. Inline what every path needs; disclose what only some branches need.

### Context pointer

A reference in the agent's context that names out-of-context material and encodes when to reach for it. The **description** of a model-invoked skill is the top-level context pointer. The wording of the pointer matters more than the target.

### Reach clause

The sentence in a skill's **description** that tells other skills when to reach for it. User triggers cover prompts; the reach clause covers consumers, naming the situation in which a conductor or building block should route to the skill. Example: "Lets adapters reference a token without exposing the secret value."

### Information hierarchy

A ranking of a skill's content by how immediately the agent needs it. The rungs are: in-skill steps, in-skill reference, disclosed reference (behind a context pointer), and external reference (outside the skill system). The hierarchy decides how far down a piece sits; co-location decides what sits beside it once there.

### Branch

A distinct way a skill can be invoked — a case or path that changes what the skill does.

---

## Skill types

### Building block

A narrow, reusable skill that provides one capability other skills can invoke and build on. Often model-invoked.

### Conductor

A skill that coordinates other skills, subagents, or tools through a multi-phase process to reach a larger goal.

### Wrapper

A thin skill that adapts a building block or conductor for human interaction, adding prompts, confirmation, and presentation.

### Multi-layer skill

A skill that participates in more than one layer of the architecture, with one clear primary role.

### Framework-aware skill

A skill tied to a specific framework or library, encoding its current patterns, APIs, and best practices.

### Version-aware skill

A skill that fetches or ships version-specific guidance so its advice does not go stale as the target technology evolves.

---

## Failure modes

### Sprawl

A skill that is too long, even if every line is live and unique. Hurts readability and attention. Cured by progressive disclosure and splitting.

### Skill hell

A degraded ecosystem where too many bloated, overlapping, or poorly triggered skills compete for attention and make the agent less reliable rather than more reliable.

### Sediment

Stale layers of content that accumulate because adding feels safe and removing feels risky. The slow erosion of relevance.

### Duplication

The same meaning expressed in more than one place. Costs maintenance, tokens, and inflates a concept's prominence.

### Guideline soup

A skill that says many true things but gives the agent no purchase point. Caused by weak or missing leading words and completion criteria. Cured by turning vague guidance into specific principles, leading words, or checkable criteria.

### No-op instruction

A line that changes nothing because the model already does it by default. Test: does this change behavior versus the default?

### Hidden dependency

A tool, API, convention, or config a skill relies on without declaring it.

---

## Cognitive terms

### Context load

The cost a model-invoked skill imposes by keeping its description in the context window. Paid in tokens and attention.

### Cognitive load

The cost a user-invoked skill imposes on the human, who must remember it exists and when to use it.

### Relevance

Whether a line still bears on what the skill does. A line loses relevance by being off-topic, stale, or belonging to a branch the skill no longer handles. The lens for pruning.

### Shared language

A vocabulary that aligns how the user, the agent, and the codebase talk about a domain. Reduces friction and token use over time.

### Router skill

A user-invoked skill whose job is to point at other user-invoked skills — naming each and when to reach for it — so the human has one skill to remember instead of many. It cannot invoke the others; only the human can reach user-invoked skills.

### Mental model

The internal representation the agent builds of how a skill or domain works. A skill should shape the agent's mental model, not just issue commands.

### Priming

The effect of early words and framing on how the agent interprets the rest of the skill. The first sentence matters disproportionately.

### Decision fatigue

The degradation of decision quality as the number of decisions increases. A skill should reduce the decisions the agent must make, not multiply them.

---

## Evaluation and quality terms

### Eval-driven development

The practice of testing a skill against representative prompts, comparing with-skill and without-skill behavior, and iterating until the skill reliably improves outcomes.

### Trigger eval

A set of queries used to test whether a skill's description causes it to fire at the right times. Split into should-trigger and should-not-trigger cases.

### Should-trigger query

A realistic user prompt that should cause the agent to load the skill.

### Should-not-trigger query

A realistic user prompt that shares keywords or concepts with the skill but should *not* cause it to load. The most valuable cases are near-misses.

### With-skill run

A test where the agent has access to the skill and attempts the task.

### Baseline run

A test where the agent attempts the same task without the skill (or with an older version), used as a comparison point.

### Explain-the-why

A writing pattern that explains the reasoning behind a guideline rather than issuing a rigid command. Helps the agent generalize correctly.

### Negation pair

A writing pattern that pairs every "do not X" with a positive directive. Used because LLMs handle negation weakly.

### One-way pattern consistency

The practice of encoding exactly one canonical way to solve each recurring problem in a skill, reducing optionality and making agent output more deterministic.

---

## Architecture and patterns

### Tool building block

A narrow, functional skill that performs one task and returns structured output. Distinguished from a vocabulary building block.

### Vocabulary building block

A skill that provides shared reference, language, or conventions that other skills consume. Distinguished from a tool building block.

### Discipline skill

A prescriptive skill that enforces a specific way of working and resists rationalization. Examples: test-driven development, verification-before-completion.

### Context-file

Always-on guidance that lives in the project context, not a skill. Examples: `AGENTS.md`, `CONVENTIONS.md`, `.cursorrules`.

### Mode

A transient behavior switch that changes how the agent behaves for a session or task. Not a skill.

### Chainlog

Append-only storage for observations collected by tools and skills. Producers append; consumers query. Lets skills reuse prior work, build reports as views over observations, and check freshness per capability rather than per report. See `patterns/chainlog.md` and `reference/chainlog-contract.md`.

### Context report

A structured, shared artifact that one skill produces and other skills consume: baselines, handoffs, debriefs, ticket research. Reports carry freshness metadata (branch, commit, timestamps) so consumers can tell whether they are safe to reuse. See `patterns/context-reports.md`.

### Standards path

The resolved location of the canonical skill-standards wiki. Skills must resolve it through configuration, project-context detection, or explicit user consent rather than hardcoding relative paths. See `fundamentals/architecture/standards-path.md`.

### Lazy dependency evaluation

Checking **recommended** and **optional** dependencies only when the feature or branch that needs them is selected, instead of checking everything at initialization. Required dependencies are still checked eagerly. Keeps skills lightweight in projects that exercise only a subset of their capabilities.

### Worker return contract

The fixed envelope a worker or subagent returns to its conductor: a `status` plus structured artifacts (summary, findings, decisions). Lets conductors integrate worker output without parsing free prose. See `schemas/worker-return-contract.schema.json`.

### Conductor/implementer split

The pattern of separating reasoning and orchestration (conductor) from execution (implementer).

---

## Tooling awareness

### Capability (tooling)

An outcome a skill needs, expressed independently of any specific tool. For example, "obtain full top-level review bodies" is a capability; "call the GitHub PR adapter" is one possible tool that fulfills it.

### Capability-first design

Designing a skill by naming the capabilities it needs before choosing the tools that fulfill them. The skill detects available tools, selects the best one for each capability, and discloses the choice.

### Tooling awareness

The practice of treating tool selection as part of a skill's contract. A tooling-aware skill declares capabilities, discovers available tools, selects the best one, discloses the choice, and obtains user consent before accepting degraded output.

### Adapter tunnel vision

A failure mode in which a skill treats its own built-in adapters, scripts, or preferred paths as the only way to fulfill a capability, ignoring better tools that are already configured or available.

### User-consented degradation

The rule that a skill must disclose a better available tool, explain the impact of using a weaker one, and obtain explicit user consent before accepting degraded output.

---

## Governance and verification

### Agent-authored skill

A skill written or materially modified by an agent. Requires stricter governance than human-authored skills.

### Staging

The practice of writing agent-authored skills to a pending area for review before they are loaded or invoked.

### Audit event

A recorded action taken on a skill, such as create, modify, approve, reject, invoke, distribute, or retire.

### Immutability in-session

The rule that a loaded skill cannot be modified during the session. Any modification attempt is intercepted and audited.

---

## Package and portability

### Portable core

The parts of a skill that are guaranteed to work across harnesses: the `SKILL.md` YAML frontmatter and markdown body, plus the optional sibling directories defined in `FORMAT.md`. The portable core is the only required part of a skill; everything else is envelope.

### Package envelope

The metadata, dependency, and distribution layer that sits around the portable core: `skills.json`, `skills.lock`, versioning, namespacing, and dependency declarations. Required when a skill has consumers, dependencies, or distribution; optional for a lone `SKILL.md`.

### Capability bundle

A named group of skills declared in a package's `skills.json` that installs together to enable a workflow.

### Namespacing

The practice of prefixing a skill name with its package name to avoid collisions: `package-name:skill-name`.

### Canonical install path

The preferred location for installed skills: `{project-root}/.agents/skills/` and `~/.agents/skills/`.

### Convention-file fallback

Using always-on context files such as `AGENTS.md` or `CONVENTIONS.md` for harnesses that do not support native skills.

### Plain-markdown export

A degraded form of a skill where YAML frontmatter is stripped or summarized so the body can be used by minimal harnesses.

### Degradation

The rules by which a skill preserves core behavior when the harness does not support its full feature set.

---

## Evaluation

### `evals.json`

The harness-neutral evaluation artifact that defines test cases for a skill.

### Runner

The harness-specific adapter that runs a test and produces a normalized trace envelope.

### Composition test

A test that checks whether a skill selects, follows, and composes correctly with other skills.

### Pressure test

A test that tries to make a discipline skill rationalize its way around the rule.

### Guardrail baseline

The baseline for a discipline skill: the documented failure pattern, not a successful no-skill run.

### Multi-agent evaluation

Testing dimensions for skills that involve coordination: communication correctness, task-assignment accuracy, conflict avoidance, ledger fidelity, distractor resistance.

---

## Implementation and runtime terms

### Harness

An agent runtime that loads, invokes, and executes skills. Examples include Claude Code, Cursor, Codex, Aider, and Hermes. The portable core should work across any harness; harness-specific envelope details may vary.

### Harness hint

A frontmatter field or config value that a harness may use for its own loading, scoping, or installation behavior. Harness hints are not part of the portable core; a portable skill should not rely on them for its core behavior. Examples include `allowed-tools`, `depends`, `disable-model-invocation`, `globs`, and `paths`.

### Harness-specific envelope

The parts of a skill implementation that are not part of the portable core: native harness discovery, exact tool scoping, MCP server wiring, sandbox configuration, and subagent spawning. The standard defines the boundary between the portable core and the envelope, not the envelope itself.

### YAML frontmatter

The YAML frontmatter block at the top of `SKILL.md`, delimited by `---`, that declares identity, routing, version, and harness hints. Also called simply **frontmatter**.

### Tool scoping

The runtime restriction of which tools a skill may use. Tool scoping is a harness-specific envelope concern; the portable standard declares dependencies in `skills.json` and lets harnesses map them to native scoping mechanisms such as `allowed-tools`.

### Capability

A feature or permission a skill requires from its runtime environment, such as a sandbox feature, a network endpoint, or a file-system access level. Distinct from a tool: a capability is what the runtime must allow, not what the skill directly calls.

### Sandbox

The isolated execution environment in which a skill or tool runs. A sandbox may limit file access, network access, or command execution. A skill should declare required sandbox features in `skills.json` and fail closed when they are missing.

### Loader index

A file that maps skill names or package identifiers to their locations on disk. Used when a harness cannot discover skills from canonical directories directly, or when native paths must point to a shared `.agents/skills/` tree.

### Subagent / worker

An isolated agent instance invoked by a conductor to perform a focused task. A **worker** is the prompt or contract that defines the subagent's role, scope, allowed tools, and return format for a specific invocation.

### Context compaction

The process by which a long-running agent session is summarized or truncated to fit within the context window. Skills that must survive compaction persist state to a file or report rather than relying on in-context memory.

### Trust layer

The concerns that make a skill trustworthy for distribution: evaluation and audit. The trust layer sits around the portable core and package envelope.

### Bootstrap routine

The load-detect-validate-resolve-persist-execute-curate sequence a configurable or global skill uses to initialize and adapt to a project. See `patterns/initialization.md` and `patterns/configurable.md`.

