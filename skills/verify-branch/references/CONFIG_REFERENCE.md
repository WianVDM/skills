# Config Reference: verify-branch

Quick reference for `.agents/config/verify-branch.yaml`. See [CONFIG_PATTERN.md](CONFIG_PATTERN.md) for narrative docs.

---

## Global preferences

| Field | Type | Options | Default | Description |
|-------|------|---------|---------|-------------|
| `preferences.execution_mode` | string | `full` | `quick`, `full`, `security-audit` | Which gates to run based on tags. |
| `preferences.tags` | list of strings | `[]` | any tags | Only include gates that have all listed tags. |
| `preferences.dry_run` | boolean | `false` | `true`, `false` | Report the execution plan without running gates. |
| `preferences.fail_fast` | boolean | `true`, `false` | `false` | Stop after the first required gate fails. |
| `preferences.max_concurrent_gates` | integer | `>=1` | `1` | Maximum gates to run in parallel. |
| `preferences.report_template` | string | `default`, `compact`, `detailed`, `custom` | `default` | Report template to use. |
| `preferences.report_template_path` | string or null | path | `null` | Path to a custom report template. |
| `preferences.include_uncommitted` | boolean | `true`, `false` | `true` | Include uncommitted files in the verification set. |
| `preferences.default_branch` | string or null | any branch | `null` | Override default branch; auto-detected if null. |
| `preferences.base_ref` | string or null | any ref | `null` | Override diff base; uses default branch if null. |
| `preferences.adapter_paths` | list of strings | paths | `[]` | Extra directories to search for custom adapters. |

---

## Gate-level preferences

All gates live under `preferences.gates`. The gate registry is open: any gate name can be defined as long as it has a valid `type` and the required config for that type. The skill ships common defaults and ecosystem templates, but no gate is mandatory.

| Field | Type | Options | Default | Description |
|-------|------|---------|---------|-------------|
| `preferences.gates.{gate}.enabled` | boolean or string | `true`, `false`, `auto` | `auto` | Whether the gate runs. |
| `preferences.gates.{gate}.type` | string | `command`, `mapper`, `standards`, `custom` | required | Which subagent fulfills the gate. |
| `preferences.gates.{gate}.importance` | string | `required`, `optional` | `optional` | Whether a failed gate fails the overall verdict. |
| `preferences.gates.{gate}.fail_fast` | boolean | `true`, `false` | `false` | Stop the gate at the first internal failure. |
| `preferences.gates.{gate}.tags` | list of strings | `[]` | any tags | Used by execution modes to filter gates. |
| `preferences.gates.{gate}.depends_on` | list of strings | `[]` | gate names | Gates that must run before this gate. |

### Gate type: `command`

Command gates run shell commands. Fulfilled by `test-gate`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `commands` | list | `[]` | Commands to run. |
| `detect_commands` | list | `[]` | Detection hints for bootstrap. |

Per-command fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `commands[].name` | string | detected | Human-readable label. |
| `commands[].command` | string | detected | Shell command to execute. |
| `commands[].cwd` | string | `.` | Working directory. |
| `commands[].timeout` | integer | `300` | Timeout in seconds. |
| `commands[].env` | map | `{}` | Environment variables. |
| `commands[].importance` | string | inherits gate | Importance for this command. |
| `commands[].run_when` | list of globs | `**/*` | Run when changed files match. |

### Gate type: `mapper`

Mapper gates map source files to expected spec files. Fulfilled by `spec-coverage-gate`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mappings` | list | `[]` | Source-to-spec mappings. |
| `default_mappings` | list | `[]` | Mappings proposed by the ecosystem template. |
| `exemptions` | list | `[]` | Exempt patterns. |

Per-mapping fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mappings[].source_pattern` | glob | required | Pattern matching source files. |
| `mappings[].spec_pattern` | glob | required | Pattern matching expected spec files. |
| `mappings[].area` | string | inferred | Reporting label. |
| `exemptions[].pattern` | glob | required | Pattern matching exempt files. |
| `exemptions[].reason` | string | required | Why the exemption exists. |

### Gate type: `standards`

Standards gates apply project rules. Fulfilled by `standards-gate`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sources` | list | `[]` | External standards sources. |
| `ai_inference.enabled` | boolean | `false` | Infer rules from markdown docs. |
| `ai_inference.source_paths` | list | `[]` | Markdown files to infer from. |
| `ai_inference.edit_before_use` | boolean | `true` | Present inferred rules for editing. |
| `overrides` | list | `[]` | Rule overrides. |

Per-source fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sources[].type` | string | `yaml` | `yaml` or `markdown-frontmatter`. |
| `sources[].path` | string | required | Path to the standards file. |
| `sources[].name` | string | inferred | Reporting label. |

Per-override fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `overrides[].id` | string | required | Rule ID to override. |
| `overrides[].severity` | string | rule default | `violation`, `consideration`, `warning`, `disabled`. |
| `overrides[].threshold` | number | rule default | New threshold if supported. |
| `overrides[].reason` | string | required | Why the override exists. |

### Gate type: `custom`

Custom gates run a single adapter through `scripts/run-gate.js`. Fulfilled by `custom-gate`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `adapter` | string | best detected | Primary adapter to use. |
| `fallback_adapters` | list | detected | Ordered fallback adapters. |
| `command` | string | adapter default | Optional command override. |
| `cwd` | string | `.` | Working directory. |
| `timeout` | integer | adapter default | Timeout in seconds. |
| `detect_marker` | list | `[]` | Files that indicate this adapter is applicable. |

### Legacy `static-analysis` gate

Configs from v3.x may still use the `static-analysis` gate with `sub_gates`. The `static-analysis-gate` subagent remains available for backwards compatibility. New configs should define each sub-gate as a separate `custom` gate.

---

## Notes

| Field | Type | Description |
|-------|------|-------------|
| `notes[].text` | string | Note content. |
| `notes[].category` | string | `workaround`, `preference`, `gotcha`, `decision`, `assumption`. |

---

## Example open-registry config

```yaml
preferences:
  fail_fast: false
  max_concurrent_gates: 1
  report_template: default
  include_uncommitted: true
  default_branch: null
  base_ref: null
  adapter_paths:
    - ".agents/verify-branch/adapters"

  gates:
    test:
      enabled: auto
      importance: required
      type: command
      fail_fast: false
      commands:
        - name: "Unit tests"
          command: "npm test"
          cwd: "."
          timeout: 300
          env: {}
          importance: required
          run_when:
            - "src/**/*"
            - "tests/**/*"

    spec-coverage:
      enabled: auto
      importance: required
      type: mapper
      fail_fast: false
      mappings:
        - source_pattern: "src/**/*.js"
          spec_pattern: "src/**/*.test.js"
          area: "frontend"
      exemptions:
        - pattern: "src/**/*.config.js"
          reason: "Configuration files contain no logic to test."

    standards:
      enabled: auto
      importance: required
      type: standards
      fail_fast: false
      sources:
        - type: yaml
          path: ".agents/config/standards.yaml"
          name: "Project standards"
      ai_inference:
        enabled: false
        source_paths: []
        edit_before_use: true
      overrides: []

    security:
      enabled: auto
      importance: optional
      type: custom
      adapter: npm-audit
      fallback_adapters: [snyk]
      cwd: "."
      timeout: 300

    my-custom-gate:
      enabled: true
      importance: optional
      type: custom
      adapter: my-custom-adapter
      cwd: "."
      timeout: 300

notes:
  - text: "Open-registry verify-branch config."
    category: decision
```
