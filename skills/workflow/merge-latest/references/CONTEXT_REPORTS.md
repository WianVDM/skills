# Reports and Context

`merge-latest` produces structured merge reports and state files that follow the context-reports conventions. See the `context-reports` skill for the shared context-report schema and freshness rules.

## Produced reports

### Merge report

```text
.agents/context/merge-latest/{target}-merge-report.md
```

Full record of the merge attempt: result, commits, files, conflicts, resolutions, validation output, and next steps.

### State file

```text
.agents/context/merge-latest/{target}/state.md
```

Working memory: branch inference, phase checklist, conflict status, resolutions, validation result, decisions.

### Backup

```text
.agents/context/merge-latest/backups/{target}-{timestamp}/
```

Snapshot of current HEAD before the merge attempt.

## Key placeholder

`{target}` is the target branch name (sanitized if needed).

## Consumed context

| Source | Location | Use |
|--------|----------|-----|
| Git metadata | local `.git` | branch history, commits, blame |
| GitHub MCP | via harness | PR and commit context |
| Jira MCP | via harness | ticket context from branch names |
