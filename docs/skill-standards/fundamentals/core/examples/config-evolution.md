# Config evolution

A skill's config should adapt to what it learns.

## Initial config

```yaml
# .agents/config/example-skill.yaml

preferences:
  sonarqube:
    method: mcp

notes: []
```

## After first run

The agent discovers the MCP server cannot export issues. It asks the user, then updates:

```yaml
# .agents/config/example-skill.yaml

preferences:
  sonarqube:
    method: api
    url: https://sonar.example.com
    token_env: SONAR_TOKEN

notes:
  - text: "MCP server lacks issue-export scope. Use web API with SONAR_TOKEN instead."
    category: workaround
    added: "2026-06-26"
```

## Why it works

- The skill adapts to the actual environment.
- Future invocations skip the discovery step.
- The reasoning is recorded, not just the setting.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
