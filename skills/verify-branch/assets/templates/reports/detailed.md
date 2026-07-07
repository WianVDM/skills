---
skill: verify-branch
version: 1.0.0
branch: {{branch}}
base: {{base}}
commit: {{commit}}
generated_at: {{generated_at}}
verdict: {{verdict}}
required_gates_passed: {{required_gates_passed}}
required_gates_total: {{required_gates_total}}
optional_gates_passed: {{optional_gates_passed}}
optional_gates_total: {{optional_gates_total}}
consumed_context:
  fresh:{{#fresh_context}}
    - path: {{path}}
      skill: {{skill}}
      summary: "{{summary}}"{{/fresh_context}}
  stale:{{#stale_context}}
    - path: {{path}}
      skill: {{skill}}
      reason: "{{reason}}"{{/stale_context}}
---

# Branch Verification: {{branch}}

**Verdict:** {{verdict}}  
**Reason:** {{verdict_reason}}  
**Base:** {{base}}  
**Commit:** {{commit}}  
**Generated:** {{generated_at}}

## Gate summary

| Gate | Importance | Status | Adapter | Findings |
|------|------------|--------|---------|----------|{{#gate_results}}
| {{gate}} | {{importance}} | {{status}} | {{adapter}} | {{finding_count}} |{{/gate_results}}

## Context consumed

{{#has_fresh}}
### Fresh
{{#fresh_context}}
- `{{path}}` ({{skill}}): {{summary}}
{{/fresh_context}}
{{/has_fresh}}
{{^has_fresh}}
_No fresh context reports consumed._
{{/has_fresh}}

{{#has_stale}}
### Stale
{{#stale_context}}
- `{{path}}` ({{skill}}): {{reason}}
{{/stale_context}}
{{/has_stale}}
{{^has_stale}}
_No stale context reports._
{{/has_stale}}

## Findings

{{#gate_results}}
{{#has_findings}}
### {{gate}}

| File | Line | Rule | Severity | Message |
|------|------|------|----------|---------|{{#findings}}
| {{file}} | {{line}} | {{rule}} | {{severity}} | {{message}} |{{/findings}}

{{/has_findings}}
{{^has_findings}}
### {{gate}}

No findings.

{{/has_findings}}
{{/gate_results}}

## Raw details

{{#gate_results}}
### {{gate}}

- Status: {{status}}
- Adapter: {{adapter}}
- Summary: {{summary}}
- Raw output:

```
{{raw_output}}
```

{{/gate_results}}

## Verdict policy details

```json
{{verdict_details_json}}
```
