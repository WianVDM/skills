# Baseline Reference

Checklists, templates, and artifact conventions for the `baseline` skill.

---

## Checklists

### Bug reproduction

- [ ] Resolve scope and confirm it is unambiguous.
- [ ] Confirm branch and record commit.
- [ ] Verify the capture method works.
- [ ] Start the target runtime if needed and allowed.
- [ ] Navigate to the route, endpoint, or code location.
- [ ] Execute the reproduction steps from consumed context or user input.
- [ ] Capture evidence of the initial, intermediate, and final/error states.
- [ ] Capture console, network, or response logs if applicable.
- [ ] Note deviations from consumed context.
- [ ] Document whether the bug is reproducible.

### Feature baseline

- [ ] Resolve scope and confirm it is unambiguous.
- [ ] Confirm branch and record commit.
- [ ] Verify the capture method works.
- [ ] Start the target runtime if needed and allowed.
- [ ] Capture the current state.
- [ ] Identify all elements that will change.
- [ ] Note existing similar functionality.
- [ ] Document current data and empty states.
- [ ] Capture errors or anomalies.

### API baseline

- [ ] Resolve scope and confirm the endpoint or contract.
- [ ] Confirm branch and record commit.
- [ ] Verify the HTTP client or API method works.
- [ ] Start the target runtime if needed and allowed.
- [ ] Capture the request and response.
- [ ] Document headers, status codes, and response bodies.
- [ ] Note authentication or environment requirements.
- [ ] Record deviations from the expected contract.

### Code snapshot

- [ ] Resolve scope and confirm the files or modules.
- [ ] Confirm branch and record commit.
- [ ] Capture the current state of the relevant files or directories.
- [ ] Include dependency or import relationships if relevant.
- [ ] Document any TODOs, FIXMEs, or known issues in scope.
- [ ] Record the reason for the snapshot.

### Hard stops

Stop immediately and flag if:

- Scope is ambiguous.
- The target branch is missing or unreachable.
- The target is unreachable.
- The capture method fails without a viable fallback.
- Authentication fails and no fallback is available.
- The reproduction steps do not match the described behavior and the user cannot clarify.

---

## Artifact directory structure

```text
.agents/context/baseline/
├── {scope}-{branch}.md
├── {scope}-{branch}.html        # optional
└── {scope}-{branch}/
    ├── screenshots/
    ├── logs/
    ├── requests/
    ├── code/
    ├── dom-snapshot.json
    └── session/
```

### Rules

- Name artifacts by step or purpose, not by timestamp.
- If the tool cannot save directly to the target path, capture to a temporary location and move the files afterward.
- Reference artifacts from the report using relative paths.
- Reuse existing artifacts when fresh; overwrite when re-capturing.
- Keep the artifact directory name consistent with the report filename.

---

## Markdown report template

```markdown
---
skill: baseline
version: 4
scope: <scope>
branch: <branch>
commit: <commit>
method: <detected-method>
consumed_context:
  - .agents/context/<skill>/<scope>.md
baselined_at: <timestamp>
type: <bug|feature|module|route|api|manual>
reproducible: true              # only when type is bug
artifacts_dir: <scope>-<branch>
summary: "<one-sentence synthesis of what was captured and the key finding>"
---

# Baseline: <scope> — <title>

## Environment
- Branch: <branch>
- Commit: <commit>
- Target URL/path: <detected-url-or-path>
- Method: <detected-method>
- Scope: <scope>

## Authentication
- Method: <auth-method>
- Session: <session-reference-if-applicable>

## Reproduction steps
1. <step one>
2. <step two>
3. <step three>

## Screenshots
- [initial](<scope>-<branch>/screenshots/initial.png): Initial state.
- [final](<scope>-<branch>/screenshots/final.png): Final or error state.

## Console errors
```
No errors.
```

## Network errors
```
No errors.
```

## Findings
<Synthesis of what was captured and the most important observations.>

## Deviation from consumed context
<Any differences from consumed context, or "None.">
```

### Template notes

- `scope` and `branch` are required in the filename and frontmatter.
- `commit` identifies the exact code state.
- `method` records the captured method, not a vendor tool name.
- `consumed_context` lists reports that informed the baseline; omit if none.
- `summary` is **required** and must be one sentence.
- `reproducible` only for `type: bug`.
- Keep the body focused on evidence, findings, and deviations.

---

## HTML gallery template

Generated alongside the Markdown report when `output.default_format` is `html-both`. The HTML is for human consumption only; other skills should read the `.md` report.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Baseline: <scope></title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
    h1 { font-size: 1.75rem; }
    h2 { font-size: 1.25rem; margin-top: 2rem; }
    figure { margin: 1rem 0; }
    img { max-width: 100%; border: 1px solid #ccc; }
    figcaption { font-size: 0.9rem; color: #555; margin-top: 0.25rem; }
    pre { background: #f5f5f5; padding: 1rem; overflow-x: auto; }
    .meta { color: #555; }
  </style>
</head>
<body>
  <h1>Baseline: <scope> — <title></h1>
  <p class="meta">
    <strong>Branch:</strong> <branch> ·
    <strong>Commit:</strong> <commit> ·
    <strong>Type:</strong> <type> ·
    <strong>Baselined at:</strong> <timestamp>
  </p>

  <h2>Environment</h2>
  <ul>
    <li>Branch: <branch></li>
    <li>Commit: <commit></li>
    <li>Target URL/path: <detected-url-or-path></li>
    <li>Method: <detected-method></li>
  </ul>

  <h2>Findings</h2>
  <p><one-sentence synthesis of the baseline finding></p>
</body>
</html>
```

---

## Versioning and migration

Reports include `version: 4` to match the skill's major version. Older reports may:

- Use `ticket` instead of `scope`.
- Omit `branch` or `commit`.
- Use `{ticket-key}-{slug}.md` filenames.
- Omit `summary`.
- Include `reproducible` on non-bug types.
- Use `dev_server` in config instead of `runtime`.

Treat older reports as potentially stale and prefer re-capturing. If re-capture is not possible, record the migration path in the report body and update the frontmatter where feasible.
