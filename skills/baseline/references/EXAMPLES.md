# Baseline Examples

## Example 1: bug reproduction baseline

### Input

- Scope: `OC-4644` auth guard race condition
- Debrief: describes the race condition.
- Method: Playwright MCP.
- Branch: `main`
- Commit: `abc1234`
- Dev server: `http://localhost:4200`.

### Generated report

`.agents/context/baseline/OC-4644-main.md`:

```markdown
---
skill: baseline
version: 3
scope: OC-4644
branch: main
commit: abc1234
type: bug
reproducible: true
method: playwright-mcp
consumed_context:
  - .agents/context/debrief/OC-4644.md
baselined_at: 2026-06-26T08:42:00Z
artifacts_dir: OC-4644-main
summary: "Auth guard redirects to login during token refresh."
---

# Baseline: OC-4644 — Auth guard race condition

## Environment
- Branch: main
- Commit: abc1234
- Dev server: http://localhost:4200
- Browser viewport: 1280x720
- Method: Playwright MCP

## Authentication
- Method: session-file
- Session: `.agents/context/baseline/sessions/default.json`

## Reproduction steps
1. Navigate to `/login`.
2. Enter valid credentials and submit.
3. Quickly navigate to `/dashboard` before the token refresh completes.

## Screenshots
- [initial](OC-4644-main/screenshots/initial.png): Login page loaded.
- [step-1](OC-4644-main/screenshots/step-1.png): After submitting credentials.
- [final](OC-4644-main/screenshots/final.png): Redirected to login instead of dashboard.

## Console errors
```
No errors.
```

## Network errors
```
No errors.
```

## Findings
The bug is reproducible. Navigating to `/dashboard` during token refresh causes the auth guard to redirect back to `/login`.
```

### Generated artifacts

```text
.agents/context/baseline/
├── OC-4644-main.md
├── OC-4644-main.html
└── OC-4644-main/
    ├── screenshots/
    │   ├── initial.png
    │   ├── step-1.png
    │   └── final.png
    ├── logs/
    │   ├── console.log
    │   └── network.log
    ├── dom-snapshot.json
    └── session/
        └── cookies.json
```

---

## Example 2: feature baseline

### Input

- Scope: `OC-3075` rewards dashboard
- Debrief: describes the new dashboard.
- Method: project test.
- Branch: `main`
- Commit: `def5678`

### Generated report frontmatter

```yaml
---
skill: baseline
version: 3
scope: OC-3075
branch: main
commit: def5678
type: feature
reproducible: n/a
method: project-test
consumed_context:
  - .agents/context/debrief/OC-3075.md
baselined_at: 2026-06-26T09:00:00Z
artifacts_dir: OC-3075-main
summary: "Rewards dashboard: current layout, empty and loading states."
---
```

### Key sections

- Current dashboard layout.
- Existing rewards components.
- Empty and loading states.
- UI elements that will change.

---

## Example 3: config after first run

`.agents/config/baseline.yaml`:

```yaml
preferences:
  verification_method: playwright-mcp
  dev_server:
    url: http://localhost:4200
    auto_start: true
    start_command: npm run start
  viewport: 1280x720
  auth:
    method: session-file
    session_file: .agents/context/baseline/sessions/default.json
  output:
    default_format: html-both

notes:
  - text: "Playwright MCP is the verified UI tool in this project."
    category: decision
  - text: "Dev server runs on port 4200 via `npm run start`."
    category: gotcha
  - text: "User prefers HTML galleries alongside Markdown reports."
    category: preference
  - text: "Auth session persisted to baseline/sessions/default.json after manual sign-in."
    category: workaround
```

---

## Example 4: manual fallback baseline

When no automation is available, the skill still produces a structured report based on user-provided screenshots and descriptions.

```markdown
---
skill: baseline
version: 3
scope: OC-5000
branch: main
commit: 789abcd
type: bug
reproducible: unknown
method: manual
consumed_context: []
baselined_at: 2026-06-26T08:42:00Z
artifacts_dir: OC-5000-main
summary: "Checkout button unresponsive; captured from user evidence."
---

# Baseline: OC-5000 — Checkout button unresponsive

## Environment
- Branch: main
- Commit: 789abcd
- Method: manual (user-provided screenshots)
- Target URL: https://staging.example.com/checkout

## User-provided screenshots
- [checkout-page](OC-5000-main/screenshots/checkout-page.png): Checkout page with unresponsive button.

## User description
> The "Complete Purchase" button does nothing when clicked. No console errors are visible.

## Findings
Unable to reproduce with automation. Manual baseline captured from user evidence.
```
