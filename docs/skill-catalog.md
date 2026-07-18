# Skill catalog

This page lists every skill in the bundle. Skills are grouped into user-facing skills and building blocks.

- **Main skills** are the ones you invoke directly.
- **Block skills** are reused by other skills. You can invoke them on their own, but they are usually composed into conductors.

For each skill, the entry shows the invocation, what it does, and its dependencies. For full behavior, read the linked `SKILL.md`.

## Main skills

### Workflow

#### `debrief`

Debrief a ticket before implementation. Use when the user asks to 'understand a ticket', 'debrief a ticket', 'scope this ticket', or 'what does this ticket need'.

- **Invocation:** `model-invoked`
- **Location:** `../skills/main/workflow/debrief/`
- **Dependencies:**
  - **Required:** checkpoint, research-ticket, challenge-assumptions, context-reports, worker-contract, detect-project-context, parse-skill-frontmatter, token-resolver
  - **Recommended:** map-ticket-relationships, explore-code, scan-context, baseline
- **Details:** [debrief/SKILL.md](../skills/main/workflow/debrief/SKILL.md)

#### `handoff`

Write a session handoff snapshot in multiple passes, from high-level overview to detailed context, so a fresh session can continue.

- **Invocation:** `/handoff`
- **Location:** `../skills/main/workflow/handoff/`
- **Dependencies:** **Recommended:** detect-project-context, context-reports
- **Details:** [handoff/SKILL.md](../skills/main/workflow/handoff/SKILL.md)

#### `merge-latest`

Merge the latest upstream branch into the correct target branch safely. Classifies conflicts as trivial, semantic, or review; resolves only trivial ones automatically; validates the merge with a user-configured command pipeline; and produces a report. Use when the user says '/merge-latest', 'merge latest', 'merge upstream', or wants to sync a feature branch before opening a PR.

- **Invocation:** `/merge-latest`
- **Location:** `../skills/main/workflow/merge-latest/`
- **Dependencies:** **Recommended:** context-reports, checkpoint
- **Details:** [merge-latest/SKILL.md](../skills/main/workflow/merge-latest/SKILL.md)

#### `orchestrate`

Move a ticket from context to completed implementation by running other skills as a conductor. Use when the user says 'orchestrate', 'run the workflow', 'execute the plan', or after debrief and baseline are complete and it is time to plan and implement.

- **Invocation:** `/orchestrate`
- **Location:** `../skills/main/workflow/orchestrate/`
- **Dependencies:** None.
- **Details:** [orchestrate/SKILL.md](../skills/main/workflow/orchestrate/SKILL.md)

#### `plan-next`

Analyze context, discover available skills, build deep skill capability profiles, and create a phased action plan with explicit dependencies. Evaluates skills not only on direct relevance but on how they ensure the plan is correct and prevent missed complexity. Interactively refines with the user before finalizing. Use when the user wants to know what to do next, which skills to run, how to address findings, or says 'plan-next', 'what should I do', 'recommend skills', or 'create a plan'.

- **Invocation:** `/plan-next`
- **Location:** `../skills/main/workflow/plan-next/`
- **Dependencies:** None.
- **Details:** [plan-next/SKILL.md](../skills/main/workflow/plan-next/SKILL.md)

#### `pr-report`

Build an actionable understanding of a pull request. Gather PR metadata, review feedback, inline comments, CI/build status, and static-analysis findings by selecting the best available tool for each capability. Normalize all feedback into a concise issue board where every comment is challenged against ticket scope and actual changes. Use when the user says '/pr-report', 'pr report', 'check PR status', 'review feedback', or wants to see what changed since the last look on a PR. Accepts a PR number, ticket key, or no input for auto-detection.

- **Invocation:** `model-invoked`
- **Location:** `../skills/main/workflow/pr-report/`
- **Dependencies:**
  - **Required:** detect-project-context, initialize-skill, artifact-freshness, context-reports, worker-contract, token-resolver, tool-discovery, identity-resolver, pr-adapter-contract
  - **Recommended:** github-pr-adapter, github-actions-adapter, sonarcloud-adapter, jira-adapter, manual-pr-adapter
  - **Optional:** baseline, debrief
- **Details:** [pr-report/SKILL.md](../skills/main/workflow/pr-report/SKILL.md)

#### `verify-branch`

Compare the current branch to the repository's default branch and verify that changed code will pass CI gates. Acts as a gatekeeper — it runs configured tests, audits, and standards checks, then delivers an unfiltered PASS or FAIL verdict. Reports only; does not fix. Use when the user says 'verify branch', 'check my PR', 'are there tests for this', or before completing implementation.

- **Invocation:** `/verify-branch`
- **Location:** `../skills/main/workflow/verify-branch/`
- **Dependencies:** None.
- **Details:** [verify-branch/SKILL.md](../skills/main/workflow/verify-branch/SKILL.md)

### Product

#### `to-issues`

Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues.

- **Invocation:** `/to-issues`
- **Location:** `../skills/main/product/to-issues/`
- **Dependencies:** None.
- **Details:** [to-issues/SKILL.md](../skills/main/product/to-issues/SKILL.md)

#### `to-prd`

Turn the current conversation context into a PRD and publish it to the project issue tracker. Use when user wants to create a PRD from the current context.

- **Invocation:** `/to-prd`
- **Location:** `../skills/main/product/to-prd/`
- **Dependencies:** None.
- **Details:** [to-prd/SKILL.md](../skills/main/product/to-prd/SKILL.md)

#### `triage`

Triage issues through a state machine driven by triage roles. Use when user wants to create an issue, triage issues, review incoming bugs or feature requests, prepare issues for an AFK agent, or manage issue workflow.

- **Invocation:** `/triage`
- **Location:** `../skills/main/product/triage/`
- **Dependencies:** **Optional:** grill-with-docs
- **Details:** [triage/SKILL.md](../skills/main/product/triage/SKILL.md)

### Engineering

#### `baseline`

Capture a reproducible snapshot of a feature, module, route, API, or bug. Invoked by baseline, reproduce, verify UI, check the app, capture state, or snapshot.

- **Invocation:** `model-invoked`
- **Location:** `../skills/main/engineering/baseline/`
- **Dependencies:** None.
- **Details:** [baseline/SKILL.md](../skills/main/engineering/baseline/SKILL.md)

#### `diagnose`

Disciplined diagnosis loop for hard bugs and performance regressions. Reproduce → minimise → hypothesise → instrument → fix → regression-test. Use when user says "diagnose this" / "debug this", reports a bug, says something is broken/throwing/failing, or describes a performance regression.

- **Invocation:** `/diagnose`
- **Location:** `../skills/main/engineering/diagnose/`
- **Dependencies:** None.
- **Details:** [diagnose/SKILL.md](../skills/main/engineering/diagnose/SKILL.md)

#### `improve-codebase-architecture`

Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the decisions in docs/adr/. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more testable and AI-navigable.

- **Invocation:** `/improve-codebase-architecture`
- **Location:** `../skills/main/engineering/improve-codebase-architecture/`
- **Dependencies:** None.
- **Details:** [improve-codebase-architecture/SKILL.md](../skills/main/engineering/improve-codebase-architecture/SKILL.md)

#### `prototype`

Build a throwaway prototype to flesh out a design before committing to it. Routes between two branches — a runnable terminal app for state/business-logic questions, or several radically different UI variations toggleable from one route. Use when the user wants to prototype, sanity-check a data model or state machine, mock up a UI, explore design options, or says "prototype this", "let me play with it", "try a few designs".

- **Invocation:** `/prototype`
- **Location:** `../skills/main/engineering/prototype/`
- **Dependencies:** None.
- **Details:** [prototype/SKILL.md](../skills/main/engineering/prototype/SKILL.md)

#### `tdd`

Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions "red-green-refactor", wants integration tests, or asks for test-first development.

- **Invocation:** `/tdd`
- **Location:** `../skills/main/engineering/tdd/`
- **Dependencies:** None.
- **Details:** [tdd/SKILL.md](../skills/main/engineering/tdd/SKILL.md)

### Modes

#### `grill-me`

Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".

- **Invocation:** `/grill-me`
- **Location:** `../skills/main/modes/grill-me/`
- **Dependencies:** None.
- **Details:** [grill-me/SKILL.md](../skills/main/modes/grill-me/SKILL.md)

#### `grill-with-docs`

Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. Use when user wants to stress-test a plan against their project's language and documented decisions.

- **Invocation:** `/grill-with-docs`
- **Location:** `../skills/main/modes/grill-with-docs/`
- **Dependencies:** None.
- **Details:** [grill-with-docs/SKILL.md](../skills/main/modes/grill-with-docs/SKILL.md)

#### `zoom-out`

Tell the agent to zoom out and give broader context or a higher-level perspective. Use when you're unfamiliar with a section of code or need to understand how it fits into the bigger picture.

- **Invocation:** `/zoom-out`
- **Location:** `../skills/main/modes/zoom-out/`
- **Dependencies:** None.
- **Details:** [zoom-out/SKILL.md](../skills/main/modes/zoom-out/SKILL.md)

### Authoring

#### `write-a-skill`

Design, review, and update skills that follow the skill standards. Coordinates creation, audit, remediation, and first-run initialization.

- **Invocation:** `/write-a-skill`
- **Location:** `../skills/main/authoring/write-a-skill/`
- **Dependencies:**
  - **Required:** detect-project-context, decide-skill-shape, audit-skill, validate-skill-frontmatter, review-skill, eval-format, worker-contract, context-reports, parse-skill-frontmatter
  - **Recommended:** list-available-skills, search-skills-registry, detect-skill-overlap, install-skill, run-trigger-evals, index-skill-capabilities, chainlog, artifact-freshness
  - **Optional:** prototype
- **Details:** [write-a-skill/SKILL.md](../skills/main/authoring/write-a-skill/SKILL.md)

## Building blocks

### Authoring

#### `audit-skill`

Check a skill against the skill fundamentals and report blockers, warnings, and suggestions with a structured remediation plan.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/authoring/audit-skill/`
- **Dependencies:** None.
- **Details:** [audit-skill/SKILL.md](../skills/blocks/authoring/audit-skill/SKILL.md)

#### `decide-skill-shape`

Help decide whether a problem should be solved by a new skill, an existing skill, a script, an MCP server, a context file, or a mode. Use when the user is unsure what shape to build, or when a conductor needs a shape recommendation.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/authoring/decide-skill-shape/`
- **Dependencies:**
  - **Recommended:** list-available-skills
  - **Optional:** search-skills-registry
- **Details:** [decide-skill-shape/SKILL.md](../skills/blocks/authoring/decide-skill-shape/SKILL.md)

#### `detect-skill-overlap`

Detect when a skill overlaps with existing building blocks or contains capabilities that should be extracted as a generic building block. Use when reviewing, auditing, or designing a skill.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/authoring/detect-skill-overlap/`
- **Dependencies:** None.
- **Details:** [detect-skill-overlap/SKILL.md](../skills/blocks/authoring/detect-skill-overlap/SKILL.md)

#### `eval-format`

Provide the canonical schema and conventions for skill evaluation artifacts stored in evals/evals.json. Use when authoring, validating, or referencing trigger, behavior, composition, pressure, or security evals.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/authoring/eval-format/`
- **Dependencies:** None.
- **Details:** [eval-format/SKILL.md](../skills/blocks/authoring/eval-format/SKILL.md)

#### `index-skill-capabilities`

Generate a structured, deterministic capability index from skill files so other skills can discover, rank, and compare capabilities across the skill catalog.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/authoring/index-skill-capabilities/`
- **Dependencies:** None.
- **Details:** [index-skill-capabilities/SKILL.md](../skills/blocks/authoring/index-skill-capabilities/SKILL.md)

#### `parse-skill-frontmatter`

Extract canonical frontmatter fields from a SKILL.md file.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/authoring/parse-skill-frontmatter/`
- **Dependencies:** None.
- **Details:** [parse-skill-frontmatter/SKILL.md](../skills/blocks/authoring/parse-skill-frontmatter/SKILL.md)

#### `review-skill`

Audit an existing skill against the skill standards, apply the review principles, and produce a verdict-led report or remediation plan after explicit approval. Use when reviewing or updating a skill.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/authoring/review-skill/`
- **Dependencies:** **Required:** audit-skill, validate-skill-frontmatter
- **Details:** [review-skill/SKILL.md](../skills/blocks/authoring/review-skill/SKILL.md)

#### `run-trigger-evals`

Generate and update trigger evals for model-invoked skills in evals/evals.json.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/authoring/run-trigger-evals/`
- **Dependencies:** **Recommended:** parse-skill-frontmatter
- **Details:** [run-trigger-evals/SKILL.md](../skills/blocks/authoring/run-trigger-evals/SKILL.md)

#### `validate-skill-frontmatter`

Validate SKILL.md YAML frontmatter against the skill-frontmatter JSON schema with line-level error reporting.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/authoring/validate-skill-frontmatter/`
- **Dependencies:** None.
- **Details:** [validate-skill-frontmatter/SKILL.md](../skills/blocks/authoring/validate-skill-frontmatter/SKILL.md)

### Project

#### `artifact-freshness`

Check whether a context report or chainlog entry is fresh enough to reuse. Evaluates branch, commit, source timestamp, schema version, and age dimensions and returns a structured reason for any staleness.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/artifact-freshness/`
- **Dependencies:** **Required:** worker-contract, context-reports
- **Details:** [artifact-freshness/SKILL.md](../skills/blocks/project/artifact-freshness/SKILL.md)

#### `chainlog`

Append-only storage for observations collected by tools. Lets skills reuse prior work, build reports as views over observations, and check freshness per capability rather than per report.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/chainlog/`
- **Dependencies:**
  - **Required:** worker-contract, context-reports
  - **Recommended:** artifact-freshness
- **Details:** [chainlog/SKILL.md](../skills/blocks/project/chainlog/SKILL.md)

#### `challenge-assumptions`

Stress-test a list of assumptions by searching for disproof signals across provided evidence. Use when a skill needs to avoid confirmation bias.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/challenge-assumptions/`
- **Dependencies:** None.
- **Details:** [challenge-assumptions/SKILL.md](../skills/blocks/project/challenge-assumptions/SKILL.md)

#### `checkpoint`

Maintain phase checklists, current focus, and resume state for long-running conductor skills. Use when a skill needs to survive context compaction, track progress across phases, or resume from a previous session.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/checkpoint/`
- **Dependencies:** **Required:** context-reports
- **Details:** [checkpoint/SKILL.md](../skills/blocks/project/checkpoint/SKILL.md)

#### `context-reports`

Provide the canonical vocabulary for shared context reports. Use when a skill produces or consumes context reports, defines report schemas, or needs freshness rules and missing-report handling.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/context-reports/`
- **Dependencies:** **Recommended:** artifact-freshness
- **Details:** [context-reports/SKILL.md](../skills/blocks/project/context-reports/SKILL.md)

#### `detect-project-context`

Detect the project root, skill/context/config directories, and the skill-standards path for any workspace.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/detect-project-context/`
- **Dependencies:** None.
- **Details:** [detect-project-context/SKILL.md](../skills/blocks/project/detect-project-context/SKILL.md)

#### `explore-code`

Search the codebase for evidence related to a specific question, ticket, or ambiguity. Find mentioned files, similar patterns, relevant tests, ADRs, and docs. Use when a skill needs code context to resolve uncertainty.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/explore-code/`
- **Dependencies:** None.
- **Details:** [explore-code/SKILL.md](../skills/blocks/project/explore-code/SKILL.md)

#### `git-worktree-inspector`

Check out a branch or commit in a git worktree, inspect changed files, run scoped checks, and clean up without disturbing the user's current branch.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/git-worktree-inspector/`
- **Dependencies:** None.
- **Details:** [git-worktree-inspector/SKILL.md](../skills/blocks/project/git-worktree-inspector/SKILL.md)

#### `github-actions-adapter`

CI source adapter that fetches GitHub Actions check runs and job-log summaries and returns the normalized ci-source shape.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/github-actions-adapter/`
- **Dependencies:** **Required:** pr-adapter-contract, worker-contract, token-resolver
- **Details:** [github-actions-adapter/SKILL.md](../skills/blocks/project/github-actions-adapter/SKILL.md)

#### `github-pr-adapter`

GitHub PR source adapter that fetches PR metadata, changed files, reviews, and inline review threads via the GitHub API and returns the normalized pr-source shape.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/github-pr-adapter/`
- **Dependencies:** **Required:** pr-adapter-contract, worker-contract, token-resolver
- **Details:** [github-pr-adapter/SKILL.md](../skills/blocks/project/github-pr-adapter/SKILL.md)

#### `identity-resolver`

Resolve a work item from user input. Given a number, URL, branch, ticket key, or arbitrary text, returns a normalized identity with type, key, repo, branch, base, commit, url, and project.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/identity-resolver/`
- **Dependencies:** **Required:** worker-contract, context-reports, detect-project-context, tool-discovery
- **Details:** [identity-resolver/SKILL.md](../skills/blocks/project/identity-resolver/SKILL.md)

#### `initialize-skill`

First-run config initializer for any skill. Detects the project environment, loads skill-level defaults, merges them with existing project config, handles schema migration, proposes the result to the user, and persists it only after explicit approval.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/initialize-skill/`
- **Dependencies:** **Required:** detect-project-context
- **Details:** [initialize-skill/SKILL.md](../skills/blocks/project/initialize-skill/SKILL.md)

#### `jira-adapter`

Issue-tracker source adapter that resolves Jira tickets and fetches ticket scope with acceptance criteria, returning the normalized issue-tracker shape.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/jira-adapter/`
- **Dependencies:** **Required:** pr-adapter-contract, worker-contract, token-resolver
- **Details:** [jira-adapter/SKILL.md](../skills/blocks/project/jira-adapter/SKILL.md)

#### `manual-pr-adapter`

Manual PR source adapter that collects PR metadata, changed files, and review feedback from user input, CSV, JSON, or markdown files and returns the normalized pr-source shape.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/manual-pr-adapter/`
- **Dependencies:** **Required:** pr-adapter-contract, worker-contract
- **Details:** [manual-pr-adapter/SKILL.md](../skills/blocks/project/manual-pr-adapter/SKILL.md)

#### `map-ticket-relationships`

Map all relationships surrounding a ticket: parent, children, siblings, duplicates, linked tickets, blocked-by/blocks, implementation PRs/branches, original feature for bugs, attachments, and affected files. Use when a skill needs to anchor a ticket in its full context.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/map-ticket-relationships/`
- **Dependencies:** **Required:** context-reports, worker-contract, research-ticket
- **Details:** [map-ticket-relationships/SKILL.md](../skills/blocks/project/map-ticket-relationships/SKILL.md)

#### `pr-adapter-contract`

Defines the normalized adapter interface contract for conductor skills that consume PR metadata, reviews, CI status, static-analysis findings, issue-tracker scope, notifications, and context reports. Use when authoring or reviewing an adapter, implementing the adapter envelope, or mapping a new source into the normalized shape.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/pr-adapter-contract/`
- **Dependencies:** **Required:** worker-contract, context-reports, token-resolver
- **Details:** [pr-adapter-contract/SKILL.md](../skills/blocks/project/pr-adapter-contract/SKILL.md)

#### `research-ticket`

Fetch and normalize all data about a ticket from a configured issue tracker, including core fields, comments, attachments, history, development info, and related tickets. Use when a skill needs ticket context before making decisions or recommendations.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/research-ticket/`
- **Dependencies:** None.
- **Details:** [research-ticket/SKILL.md](../skills/blocks/project/research-ticket/SKILL.md)

#### `scan-context`

Discover related context reports in a project's context directory by ticket key, project, branch, or report type. Use when a skill needs to find prior baselines, handoffs, debriefs, or other shared reports.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/scan-context/`
- **Dependencies:** None.
- **Details:** [scan-context/SKILL.md](../skills/blocks/project/scan-context/SKILL.md)

#### `scope-checker`

Challenge a list of findings against a scope (ticket acceptance criteria, changed files, PR intent, or project conventions) and classify each one as in-scope, out-of-scope, or ambiguous. Use when a conductor needs to triage findings by whether they belong to the current work item.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/scope-checker/`
- **Dependencies:** **Required:** worker-contract
- **Details:** [scope-checker/SKILL.md](../skills/blocks/project/scope-checker/SKILL.md)

#### `sonarcloud-adapter`

Static-analysis source adapter that fetches SonarCloud findings and returns the normalized static-analysis shape.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/sonarcloud-adapter/`
- **Dependencies:** **Required:** pr-adapter-contract, worker-contract, token-resolver
- **Details:** [sonarcloud-adapter/SKILL.md](../skills/blocks/project/sonarcloud-adapter/SKILL.md)

#### `tool-discovery`

Discover and rank available tools for a given capability. Given a capability like pr-source or ci-source, returns a ranked list of available tools with confidence, source category, and fallback ordering.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/tool-discovery/`
- **Dependencies:** None.
- **Details:** [tool-discovery/SKILL.md](../skills/blocks/project/tool-discovery/SKILL.md)

#### `worker-contract`

Provide the canonical worker/subagent return contract for conductors to embed in subagent prompts. Use when composing a worker, standardizing subagent output, or referencing the shared return format, forbidden actions, and scope boundaries.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/project/worker-contract/`
- **Dependencies:** None.
- **Details:** [worker-contract/SKILL.md](../skills/blocks/project/worker-contract/SKILL.md)

### Registry

#### `find-skills`

Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/registry/find-skills/`
- **Dependencies:** None.
- **Details:** [find-skills/SKILL.md](../skills/blocks/registry/find-skills/SKILL.md)

#### `install-skill`

Install a skill from a local path or archive URL into the project or user scope.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/registry/install-skill/`
- **Dependencies:** **Recommended:** detect-project-context
- **Details:** [install-skill/SKILL.md](../skills/blocks/registry/install-skill/SKILL.md)

#### `list-available-skills`

Discover skills already available in the project and user scope by scanning canonical skill directories.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/registry/list-available-skills/`
- **Dependencies:** **Recommended:** parse-skill-frontmatter
- **Details:** [list-available-skills/SKILL.md](../skills/blocks/registry/list-available-skills/SKILL.md)

#### `search-skills-registry`

Search configured skill registries for third-party skills that could cover a given need.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/registry/search-skills-registry/`
- **Dependencies:** **Recommended:** parse-skill-frontmatter, install-skill
- **Details:** [search-skills-registry/SKILL.md](../skills/blocks/registry/search-skills-registry/SKILL.md)

### Tokens

#### `token-resolver`

Resolve secure tokens for adapters from environment variables, MCP config files, or a one-time user prompt. Return a reference without exposing the secret value.

- **Invocation:** `model-invoked`
- **Location:** `../skills/blocks/tokens/token-resolver/`
- **Dependencies:** None.
- **Details:** [token-resolver/SKILL.md](../skills/blocks/tokens/token-resolver/SKILL.md)

## Setup

#### `setup-wian-skills`

Set up or update Wian's skills in the workspace. Use the Vercel skills CLI to install or update the WianVDM/skills bundle, then resolve shared configuration once and present the initialization checklist.

- **Invocation:** `/setup-wian-skills`
- **Location:** `../skills/setup/setup-wian-skills/`
- **Dependencies:** **Required:** detect-project-context, list-available-skills, validate-skill-frontmatter
- **Details:** [setup-wian-skills/SKILL.md](../skills/setup/setup-wian-skills/SKILL.md)
