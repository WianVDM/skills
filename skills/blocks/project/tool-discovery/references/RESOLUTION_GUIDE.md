# Resolution guide

How a conductor turns a *capability* into a working, cached, per-project recipe. This guide replaces provider-specific adapters: the model derives the recipe with whatever tools exist, validates it against the contract, and caches it so the derivation happens once per project.

## The flow

```
name the capability → detect candidates (model-first) → pick one →
derive the recipe → validate against the contract → cache it →
re-validate cheaply on later runs
```

### 1. Name the capability, not the tool

State the outcome first: "I need PR metadata, changed files, reviews, threads, and conversation comments in the `pr-source` shape." Never start from a tool and work backward.

### 2. Detect candidates, model-first

In order of sensor quality:

1. **In-session tools.** The model can see connected MCP tools and harness tools directly. Match tool names and schemas against the capability (`github_get_pull_request`, `mcp_gitlab_merge_request`, …). This is the strongest signal — these tools are *connected and working now*.
2. **Platform detection.** `git remote get-url origin` names the hosting platform (github.com, gitlab.com, dev.azure.com, bitbucket.org, or a self-hosted host). This single fact prunes most of the search space.
3. **CLI probes.** `which gh glab bb az` (or platform equivalents), then an auth probe (`gh auth status`, `glab auth status`). An installed-but-unauthenticated CLI is a late failure; catch it here.
4. **API + token.** When nothing else exists, a REST API with a token from `token-resolver` works for every major platform.
5. **The script.** `discover-tools.py` is the offline fallback when in-session detection is impossible (script-only contexts, unattended runs). It searches known MCP config locations and probes CLIs; it knows less than the model, so its output is a floor, not a ceiling.

### 3. Pick one

Prefer, in order: working MCP tool > authenticated CLI > API with token > manual. User config (`{capability}.provider`) overrides. Record the choice and why.

### 4. Derive the recipe

Write down the exact steps that fill the contract: which tool calls or commands, with which arguments, in which order, and how each output maps to contract fields. Use the concept mappings and known quirks below — they carry the non-obvious provider knowledge.

### 5. Validate against the contract

Fetch one real item and check coverage: can the recipe fill every required field of the contract shape? A recipe that cannot fill a required surface (e.g., conversation comments) is **partial** — disclose the gap, decide with the user whether to accept it, and record the limitation in the cache entry. Do not silently cache a thin recipe.

### 6. Cache per project

Store the validated recipe via `discover-tools.py cache-put` in `{config_dir}/tool-recipes.yaml`. One entry per capability.

### 7. Re-validate cheaply, invalidate on failure

On later runs: load the cache entry, run its `revalidate` probe (a single cheap call). If the probe fails or the tool is gone, re-derive. Invalidate also on user request or when the project platform changes. Never re-derive a recipe that still validates.

## Concept mappings

| Generic | GitHub | GitLab | Azure DevOps | Bitbucket |
|---|---|---|---|---|
| pull request | pull request | merge request | pull request | pull request |
| CI run | check suite / workflow run | pipeline | pipeline / build | pipeline |
| review comment surface | reviews + review threads + issue comments | discussions + notes | threads | comments + inline |
| approval state | review decision / reviews | approvals | reviewers vote | approvals |
| issue | issue | issue | work item | issue |

## Known provider quirks

- **GitHub has three comment surfaces.** Reviews (top-level), review threads (inline), and issue comments (conversation, where bots post). A recipe covering only two of them has a hole — deferrals and bot decorations live in the third.
- **GitHub thread resolution state** is only available via GraphQL (`reviewThread.isResolved`); REST needs heuristics.
- **GitLab resolution state** lives on discussions, not individual notes.
- **Azure DevOps** threads carry status (`active`, `fixed`, `closed`, `won't fix`) — map `won't fix` and `by design` closures to the settled disposition.
- **Bitbucket** has no native thread-resolution; treat author replies as the only settlement signal.
- **Self-hosted instances** (GitHub Enterprise, GitLab self-managed) change the API base URL, not the recipe shape. Record the base URL in the cache entry.

## Manual fallback

Manual is a recipe too: prompt the user for the specific contract fields that no tool could fill, or accept pasted JSON/CSV/marker text. It always validates (the user is the source) and never needs auth. It is the last resort per capability, not a default.

## Recipe cache format

`{config_dir}/tool-recipes.yaml`:

```yaml
pr-source:
  tool: github-mcp
  platform: github
  derived_at: "2026-07-20T14:32:00Z"
  validated: true
  coverage: complete            # complete | partial (disclose what is missing)
  missing: []                   # e.g. [conversation_comments]
  steps:
    - call: github_get_pull_request
      args: ["owner", "repo", "pullNumber"]
      yields: metadata
    - call: github_get_pull_request_files
      yields: changed_files
    - call: github_get_pull_request_reviews
      yields: reviews
    - call: github_get_pull_request_review_comments
      yields: threads
    - call: GET /repos/{owner}/{repo}/issues/{pr}/comments
      via: gh api
      yields: conversation_comments
  revalidate: "github_get_pull_request on the current PR; expect success"
ci-source:
  tool: gh-cli
  platform: github
  derived_at: "2026-07-20T14:33:00Z"
  validated: true
  coverage: complete
  missing: []
  steps:
    - call: gh pr checks {pr}
      yields: check_runs
  revalidate: "gh auth status"
```

Manage entries with `discover-tools.py` operations `cache-get`, `cache-put`, and `cache-invalidate`. Never hand-edit while a run is active.
