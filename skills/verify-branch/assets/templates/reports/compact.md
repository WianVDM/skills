---
skill: verify-branch
version: 4
branch: {{branch}}
base: {{base}}
commit: {{commit}}
generated_at: {{generated_at}}
verdict: {{verdict}}
---

# {{branch}} — {{verdict}}

{{#gate_results}}
- {{gate}} ({{importance}}): {{status}}{{#has_findings}} — {{finding_count}} finding(s){{/has_findings}}
{{/gate_results}}

{{#has_any_findings}}
## Failures
{{#gate_results}}
{{#has_findings}}
{{#findings}}
- `{{gate}}` | {{file}}:{{line}} | {{rule}} | {{severity}} | {{message}}
{{/findings}}
{{/has_findings}}
{{/gate_results}}
{{/has_any_findings}}
