# Baseline Examples

Replace placeholders with values detected or confirmed for the project.

---

## Example 1: bug reproduction baseline

### Input

- Scope: `OC-4644` auth guard race condition
- Related context: a report describing the race condition
- Method: `ui-browser` (detected)
- Branch: `main`
- Commit: `abc1234`
- Target URL: detected from project

### Generated report

`.agents/context/baseline/OC-4644-main.md`:

```markdown
---
skill: baseline
version: 1.0.0
scope: OC-4644
branch: main
commit: abc1234
type: bug
reproducible: true
method: ui-browser
consumed_context:
  - .agents/context/<skill>/OC-4644.md
baselined_at: 2026-06-26T08:42:00Z
artifacts_dir: OC-4644-main
summary: "Auth guard redirects to login during token refresh when navigating to /dashboard before the token refresh completes."
---

# Baseline: OC-4644 — Auth guard race condition

## Environment
- Branch: main
- Commit: abc1234
- Target URL: <detected-url>
- Method: ui-browser
- Scope: OC-4644

## Authentication
- Method: session-file
- Session: `.agents/context/baseline/sessions/default.json`

## Reproduction steps
1. Navigate to `/login`.
2. Enter valid credentials and submit.
3. Quickly navigate to `/dashboard` before the token refresh completes.

## Screenshots
- `OC-4644-main/screenshots/initial.png`: Login page loaded.
- `OC-4644-main/screenshots/final.png`: Redirected to login instead of dashboard.

## Findings
The bug is reproducible. Navigating to `/dashboard` during token refresh causes the auth guard to redirect back to `/login`.

## Deviation from consumed context
None.
```

### Generated artifacts

```text
.agents/context/baseline/
├── OC-4644-main.md
├── OC-4644-main.html
└── OC-4644-main/
    ├── screenshots/
    ├── logs/
    ├── dom-snapshot.json
    └── session/
```

---

## Example 2: feature baseline

### Input

- Scope: `OC-3075` rewards dashboard
- Method: `project-test` (detected)
- Branch: `main`
- Commit: `def5678`

### Generated report frontmatter

```yaml
---
skill: baseline
version: 1.0.0
scope: OC-3075
branch: main
commit: def5678
type: feature
method: test-runner
consumed_context:
  - .agents/context/<skill>/OC-3075.md
baselined_at: 2026-06-26T09:00:00Z
artifacts_dir: OC-3075-main
summary: "Rewards dashboard current layout, empty and loading states captured before upcoming redesign."
---
```

### Key sections

- Current dashboard layout.
- Existing rewards components.
- Empty and loading states.
- UI elements that will change.

---

## Example 3: API baseline

### Generated report frontmatter

```yaml
---
skill: baseline
version: 1.0.0
scope: user-profile-endpoint
branch: main
commit: def5678
type: api
method: api-http
consumed_context: []
baselined_at: 2026-06-26T09:00:00Z
artifacts_dir: user-profile-endpoint-main
summary: "User profile endpoint returns 200 with the expected profile payload."
---
```

---

## Example 4: code snapshot baseline

### Generated report frontmatter

```yaml
---
skill: baseline
version: 1.0.0
scope: auth-guard-module
branch: main
commit: def5678
type: module
method: code-snapshot
consumed_context: []
baselined_at: 2026-06-26T09:00:00Z
artifacts_dir: auth-guard-module-main
summary: "Snapshot of the auth guard module before refactoring."
---
```

---

## Example 5: manual fallback baseline

```markdown
---
skill: baseline
version: 1.0.0
scope: OC-5000
branch: main
commit: 789abcd
type: bug
method: manual
consumed_context: []
baselined_at: 2026-06-26T08:42:00Z
artifacts_dir: OC-5000-main
summary: "Checkout 'Complete Purchase' button is unresponsive based on user-provided screenshot and description."
---

# Baseline: OC-5000 — Checkout button unresponsive

## Environment
- Branch: main
- Commit: 789abcd
- Method: manual (user-provided screenshots)
- Target URL: https://staging.example.com/checkout

## User-provided screenshots
- `OC-5000-main/screenshots/checkout-page.png`: Checkout page with unresponsive button.

## User description
> The "Complete Purchase" button does nothing when clicked. No console errors are visible.

## Findings
Unable to reproduce with automation. Manual baseline captured from user evidence.
```

---

## Example 6: config after first run

`.agents/config/baseline.yaml`:

```yaml
preferences:
  verification_method: auto
  scope:
    default: ask
    feature: null
  branch:
    use_current: true
    target: null
  runtime:
    url: null
    auto_start: ask
    start_command: null
  viewport: null
  auth:
    method: none
  output:
    default_format: md
    naming: scope-branch

notes:
  - text: "Default verification method is auto-detection."
    category: decision
  - text: "Runtime URL and start command are detected per project."
    category: gotcha
```
