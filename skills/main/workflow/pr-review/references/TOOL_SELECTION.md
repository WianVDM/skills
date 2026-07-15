# Tool selection

Capability-to-tool mapping and selection rules for `pr-review`.

## Capabilities

| Capability | Purpose |
|---|---|
| `pr-source` | PR metadata, changed files, reviews, threads. |
| `ci-source` | Check runs and failing job logs. |
| `static-analysis-source` | Code-quality findings (optional). |
| `issue-tracker-source` | Ticket scope and acceptance criteria. |
| `posting` | Posting a PR review or handing back a payload. |
| `checkout` | Local branch checkout without disturbing the current branch. |

## Selection hierarchy

1. **User-configured tool** — if the user set a provider in `pr-review.yaml`, prefer it.
2. **Best available tool** — highest confidence among detected tools.
3. **Local tool** — a CLI or script that does not require network tokens.
4. **Manual fallback** — user-provided input, used only when no automated tool is available.

## Provider defaults

| Capability | Preferred | Fallbacks | Manual fallback |
|---|---|---|---|
| `pr-source` | GitHub MCP, `github-pr-adapter` | `gh` CLI, GitHub REST API | `manual-pr-adapter` |
| `reviews` | GitHub MCP, `github-pr-adapter` | `gh` CLI, GraphQL | User-provided text |
| `changed-files` | `github-pr-adapter`, GitHub MCP | `gh` CLI, `git diff` | User-provided list |
| `ci-source` | GitHub MCP, `github-actions-adapter` | `gh` CLI, GitHub Checks API | User-provided summary |
| `issue-tracker-source` | `jira-adapter`, Jira MCP | Jira API, GitHub Issues | User-provided scope |
| `posting` | `post-github-pr-review`, GitHub MCP | `gh` CLI | Manual payload |
| `checkout` | `git-worktree-inspector` | `git checkout` in temp clone | Manual instructions |

## Degradation disclosure

When a fallback is used, record in state:

- Original capability.
- Preferred tool that was unavailable.
- Fallback tool used.
- Confidence level of the fallback.
- Whether the user accepted the degraded source.

## Degraded mode

- `ask` (default) — ask the user whether to accept, retry, or skip.
- `accept` — accept degraded sources without asking (recorded).
- `reject` — stop and ask the user for a better tool or input.
