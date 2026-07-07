# Reports and Context

## Produced reports

### Merge report

```text
.agents/context/merge-latest/{target}-merge-report.md
```

Full record of the merge attempt: result, commits, files, conflicts, resolutions, build output, next steps.

### State file

```text
.agents/context/merge-latest/{target}/state.md
```

Working memory: branch inference, phase checklist, conflict status, resolutions, build result, decisions.

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
