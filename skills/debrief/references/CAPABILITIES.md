# Capability Detection

The `debrief` skill gathers context from multiple sources. It detects what is available and asks the user when the choice is ambiguous.

---

## Deterministic helper scripts

The skill uses small, deterministic scripts to avoid guessing:

- `scripts/detect-project-layout.py` — find the project marker directory (`.agents`, `.pi`, `agents`, or user-specified).
- `scripts/detect-issue-tracker.py` — lists available trackers (MCP servers, env vars) with confidence.
- `scripts/extract-ticket-key.py` — extracts a ticket key from a branch name or arbitrary text.
- `scripts/infer-ticket-type.py` — classifies the ticket type (`code`, `ui`, `docs`, `process`, `unknown`).
- `scripts/detect-verifiable-state.py` — decides whether baseline is relevant for the ticket.
- `scripts/scan-related-context.py` — scans `{context_dir}/` for reports related to the current ticket or branch.
- `scripts/check-debrief-freshness.py` — compares an existing debrief report with the current branch/commit and ticket update time.
- `scripts/find-related-prs.py` — finds PRs related to the ticket or files.
- `scripts/trace-bug-origin.py` — traces a bug to its original feature commit.

---

## Issue tracker detection

Detection is automatic by default (`preferences.issue_tracker: auto`). The script checks for configured issue trackers in this order:

1. **Jira** — `jira` MCP server available or Jira env vars present.
2. **GitHub Issues** — `github` MCP server available or GitHub token present.
3. **Linear** — `linear` MCP server available or Linear token present.
4. **Manual** — no tracker available; user provides context.

The first viable option is pre-selected, but the user can choose another.

---

## Development info sources

Beyond the issue tracker, the skill may gather:

| Source | What it provides | Detection |
|--------|------------------|-----------|
| Linked PRs/branches | Work already started or related | Issue tracker development info |
| Open PRs in repo | Active work in same area | GitHub MCP or git remote |
| Recent commits | Recent changes to related files | Git log |
| Related tickets | Parent, child, linked, duplicates | Issue tracker links |

---

## Codebase access

The skill assumes it can read the project codebase. It uses targeted searches to resolve ambiguities, not broad architecture reviews.

Code exploration is time-boxed per ambiguity (default 5 minutes, configurable).

---

## Baseline capability

The `baseline` skill is a **soft default building block**. `debrief` invokes it as a separate workflow when `baseline_mode` is `required` or `optional` and the ticket involves verifiable state. The debrief skill does not directly operate browsers; it delegates to the baseline skill. If baseline is unavailable, the user must explicitly approve proceeding without it.

---

## Selection prompt

When multiple issue trackers are available, ask:

> "I found several ways to fetch ticket details:
> 1. Jira (already configured)
> 2. GitHub Issues
> 3. Manual input
> Which should I use?"

Store the choice in `{marker_dir}/config/debrief.yaml`.

---

## Fallback behavior

If the selected tracker fails during execution:

1. Document the failure in state.
2. Ask the user whether to:
   - Retry with the same tracker,
   - Try the next best tracker,
   - Switch to manual input,
   - Abort.
3. Update notes with the failure and workaround if one is found.

---

## Missing tracker setup

If no tracker is configured and the user wants to set one up, provide per-tracker setup instructions from `references/trackers/`.

Do not write harness-specific config files without user confirmation.
