---
name: pr-report-adapter-registry
description: Default adapter registry for the pr-report conductor. Maps built-in adapter names to their roles and source paths.
metadata:
  author: Wian van der Merwe
  tags: [pr-report, adapters, registry]
  version: "1.0.0"
---

# Adapter Registry

Default registry for the `pr-report` conductor. Users can extend or override it in project config. The registry format is documented in [CONFIG_PATTERN.md](CONFIG_PATTERN.md).

## Built-in adapters

```yaml
adapter_registry:
  github-pr-adapter:
    type: skill
    role: pr-source
    path: .agents/skills/adapters/github-pr-adapter
  github-actions-adapter:
    type: skill
    role: ci-source
    path: .agents/skills/adapters/github-actions-adapter
  sonarcloud-adapter:
    type: skill
    role: static-analysis-source
    path: .agents/skills/adapters/sonarcloud-adapter
  jira-adapter:
    type: skill
    role: issue-tracker-source
    path: .agents/skills/adapters/jira-adapter
  manual-pr-adapter:
    type: skill
    role: pr-source
    path: .agents/skills/adapters/manual-pr-adapter
  token-resolver:
    type: skill
    role: shared
    path: .agents/skills/core/token-resolver
```

## Community adapters

Additional adapters such as `gitlab-pr-adapter`, `azure-devops-pr-adapter`, `gitea-pr-adapter`, `azure-pipelines-adapter`, `sonarqube-adapter`, `codeql-adapter`, `linear-adapter`, `teams-adapter`, and `slack-adapter` can be registered in project config. Their interfaces are defined by the `pr-adapter-contract` building block.

## Override in project config

```yaml
# {config_dir}/pr-report.yaml
adapter_registry:
  my-custom-ci:
    type: script
    role: ci-source
    path: .agents/adapters/pr-report/my-custom-ci.py

adapters:
  ci:
    source: my-custom-ci
```

## References

- `pr-adapter-contract` — adapter interface contract
- [CONFIG_PATTERN.md](CONFIG_PATTERN.md) — config schema
- [CAPABILITIES.md](CAPABILITIES.md) — adapter discovery rules
