# Governance and Verification

## At a glance

This document specifies **verification, approval, audit, and signing** for skills, with special attention to agent-authored skills. It covers staging, immutability in-session, dependency parity, cryptographic signatures, and security scanning.

**Read this if:** you distribute skills, let agents write or modify skills, or need to meet trust and compliance requirements.

If agents can write skills, then **governance** is not optional. A skill that can be created, modified, or distributed by an agent must pass through approval gates and leave an audit trail. Without governance, agent-authored skills become untrusted artifacts that undermine the library.

This document specifies the governance model for skills in this library. It applies to all skills that are distributed beyond their origin project, and it is recommended for any skill that is created or modified by an agent.

## Agent-authored skills

An **agent-authored skill** is any skill where an agent wrote or materially modified the content. This includes skills generated autonomously in the background and skills generated interactively at the user's direction.

### Foreground vs. background creation

The standard distinguishes two origins for agent-authored skills:

- **Foreground user-directed creation** — the user explicitly asks the agent to create a skill. This is treated as user authorship, though the agent did the writing.
- **Background autonomous creation** — the agent creates or modifies a skill without direct user instruction. This is treated as agent-authored with stricter governance.

A harness may track this distinction via a context variable or explicit flag. Hermes, for example, uses a `skill_write_origin` `ContextVar` to distinguish these cases.

### Default personal scope

Agent-authored skills start in **personal scope**: they are local to the user or project and are not distributed until reviewed. Promotion to project, org, or public scope requires:

- Human review or approved CI attestation.
- Evaluation pass (see [reference/evaluation-framework.md](./evaluation-framework.md)).
- Security scan (separate from functional evaluation).
- Version bump if the schema or behavior changed and the skill is shared or consumed.

---

## Staging and approval

Agent-authored skills must go through **post-approval staging** before they are loaded or invoked. The default flow is:

1. The agent writes the skill to a **pending area** (e.g., `.agents/pending/skills/` or `~/.hermes/pending/skills/`).
2. The skill is **not loaded** and **not invoked** until reviewed.
3. A human reviewer or approved CI pipeline reviews the diff, runs evaluations, and approves or rejects.
4. On approval, the skill is promoted to the active skills directory.
5. On rejection, the skill is returned to the author with feedback or deleted.

For small teams, this can be as simple as `skills pending` and `skills approve` CLI commands. For enterprises, it scales to mandatory review, security scanning, and branch protection.

---

## Verification levels

A skill carries a verification level that tells consumers how much trust they can place in it. The level is set at bootstrap and is immutable for the session. If a skill is modified, it must be re-verified.

| Level | Meaning | Typical requirements |
|-------|---------|----------------------|
| `unverified` | Default. No review or evaluation. | human-in-the-loop (HITL) on every irreversible action. |
| `declared` | The author claims it meets the standard. | Checklist review by a human or tool. |
| `tested` | Evaluations pass. | Evaluation suite, security scan, adversarial pressure tests. |
| `formal` | Machine-checkable proof. | Aspirational; not practical for most skills today. |

The verification level is declared in `skills.json` or an audit ledger, not in `SKILL.md` frontmatter. It is a separate signal of evaluation rigor derived from evaluation, audit, and governance records.

---

## Audit events

Every significant action on a skill should produce an audit event. The minimum event envelope is:

| Field | Description |
|-------|-------------|
| `event_type` | `create`, `modify`, `approve`, `reject`, `invoke`, `distribute`, `retire`. |
| `session_id` | Identifier of the session. |
| `operator` | Human or agent responsible. |
| `skill_ids` | The skills involved. |
| `request_id` | Correlation ID for the request. |
| `capability` | The capability exercised. |
| `target` | The skill or resource affected. |
| `decision` | Approve, reject, defer, etc. |
| `outcome` | Success, failure, blocked, etc. |
| `rationale` | Why the decision was made. |
| `trace_id` | Link to the execution trace. |
| `verification_level` | Verification level of the skill at the time. |
| `risk_tier` | Risk assessment of the skill or action. |

Harnesses map their native traces into this envelope. For example:

- Codex provides a Compliance API.
- Claude Code supports OpenTelemetry and attribution settings.
- Enterprise agent-package managers produce lock files and SARIF security reports.
- Verifiable Artifacts proposes a hash-chain model.

---

## Immutability in-session

A skill that is loaded in a session is **immutable for that session**. If an agent tries to modify a loaded skill, the attempt is intercepted as an irreversible capability call, walked through human-in-the-loop approval, and audited with pre/post content hashes.

If the modification is approved, it produces a new skill artifact that must be re-verified before the next session. Verification levels are bootstrap-only; they cannot be promoted mid-session.

---

## Dependency parity

Agent-authored skills have no exemption from dependency policy. They must declare all required skills, tools, MCP servers, binaries, and environment variables in `skills.json`. Policy gates must approve them before the skill is loaded or invoked.

Undeclared dependencies are policy violations. This is especially important for MCP servers, which can leak data or execute actions outside the project.

---

## Cryptographic signatures

Before a skill is promoted beyond personal scope, a human reviewer or approved CI attestation pipeline should sign the approved manifest. The signature covers the manifest and content hashes.

Signatures are **recommended but not sufficient**. They provide integrity, not trust. A signed skill still needs evaluation and review.

---

## Agent-authored skill evaluation

Agent-authored skills use the same functional evaluation framework as human-authored skills (see [reference/evaluation-framework.md](./evaluation-framework.md)), plus additional tests:

- **Anti-rationalization test** — the skill does not quietly undermine its own rules.
- **Scope test** — the skill stays within its declared scope.
- **Mutation test** — the skill does not try to modify itself or other skills without approval.
- **Consolidation test** — the skill does not silently merge or replace human-authored content.

---

## Consolidation and self-improvement

Some agent systems support **background consolidation**: an agent reviews and refines skills over time. This is allowed only for personal skills by default. Shared, project, or org skills require human review before any consolidation or patch.

This prevents agent loops from quietly changing team-wide conventions without oversight.

---

## Security scanning

Security scanning is a separate audit dimension from functional evaluation. It checks for:

- Secrets in files or references.
- Undeclared network access or external dependencies.
- Unsafe code execution or script injection.
- Inappropriate permissions or sandbox escapes.

Security scanning is required for distributed skills and recommended for local skills. Results are reported in a separate `audit/security-report.json` artifact.

---

## Limitations

The following governance concerns are **limited** and are documented as such:

- Exact harness-specific approval UIs and staging directories vary by vendor.
- Cryptographic signing tooling maturity is not yet universal.
- Runtime mutation interception is not uniformly available across harnesses.
- Formal verification tooling is not practical for most skills today.

---

## Key takeaways

- **Agent-authored skills** start in personal scope and require review before promotion to project, org, or public scope.
- **Verification levels** (`unverified`, `declared`, `tested`, `formal`) are set at bootstrap and immutable for the session.
- A skill loaded in a session is **immutable in-session**; modification attempts are intercepted, approved, and audited.
- **Signatures** are recommended but not sufficient; combine them with evaluation and review.
- **Security scanning** is a separate audit dimension from functional evaluation.

## Research basis

- The governance model is drawn from the research on agent-authored skills, enterprise governance, and verifiable artifacts.
- **Hermes** provides a write-approval system (`tools/write_approval.py`) that informed the staging/approval model. https://github.com/NousResearch/hermes-agent
- **Claude Code** settings support attribution, OpenTelemetry, and managed plugin settings. https://code.claude.com/docs/en/skills
- **Codex** provides a Compliance API and managed configuration. https://developers.openai.com/codex/guides/agents-md
- **Agent Package Manager (APM)** and **Agent Skill Harbor** provide enterprise governance models that informed the small-team-to-enterprise scaling path.
- **Verifiable Artifacts** (arXiv 2605.00424) frames verification levels, immutability, mutation interception, and signed manifests. https://arxiv.org/abs/2605.00424
- The **foreground/background** distinction, **default personal scope**, and **post-approval staging** rules are our own design choices, synthesized from the research on agent authorship.
- The **verification level mapping** (`unverified` → HITL, `declared` → checklist, `tested` → evals + security scan, `formal` → machine proof) is our own operationalization of the Verifiable Artifacts levels.
- The **audit event schema** is our own minimum envelope, designed to be reconcilable with native harness traces.
- The **security scanning as separate audit dimension** rule is drawn from the research evaluation framework.

---

## Related documents

- [`reference/package.md`](./package.md) — package envelope, versioning, dependencies.
- [`reference/evaluation-framework.md`](./evaluation-framework.md) — evaluation framework and agent-authored skill tests.
- [`fundamentals/security.md`](../fundamentals/security.md) — security fundamentals.
