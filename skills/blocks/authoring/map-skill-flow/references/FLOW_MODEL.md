# Flow report schema

The flow report is a markdown context report. It follows the shared context-report envelope from the `context-reports` skill, plus the sections below.

**Location:** `{context}/skill-design/{skill-name}-flow.md` (design) or `{context}/skill-review/{skill-name}-flow.md` (review).

## Frontmatter

```yaml
---
skill: map-skill-flow
target: {name of the mapped skill}
source: {skill-directory | design-draft}
generated_at: {ISO-8601 timestamp}
---
```

## Sections

### Branches and gates

| Branch | Gates | Declared or inferred |
|---|---|---|

### Phases

| Branch | Phase | Completion criterion | Declared or inferred |
|---|---|---|---|

### Success paths

One short paragraph per branch: what "done" means.

### Break points

Sorted `silent` first, then `blocked`, `degraded`, `disclosed`.

| Cause | Detection | Handling | Confidence | Detail |
|---|---|---|---|---|

### Mermaid diagram

The rendered flow in a ` ```mermaid ` fence.
