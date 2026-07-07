# Configuration and Notes

The `verify-branch` skill adapts to each project through config and notes stored in `.agents/config/verify-branch.yaml`.

---

## Config location

Config is loaded from four locations, in merge order:

1. `~/.agents/config/shared.yaml` — user-level shared defaults.
2. `~/.agents/config/verify-branch.yaml` — user-level verify-branch defaults.
3. `{project-root}/.agents/config/shared.yaml` — project shared config.
4. `{project-root}/.agents/config/verify-branch.yaml` — project-specific config.

Later values override earlier ones. Project config always wins over user-level config.

```text
{project-root}/.agents/config/verify-branch.yaml
{project-root}/.agents/config/shared.yaml
~/.agents/config/verify-branch.yaml
~/.agents/config/shared.yaml
```

The skill reads these shared keys when present:

| Shared key | Used for |
|------------|----------|
| `preferences.default_branch` | Fallback default branch. |
| `preferences.report_template` | Shared default report template. |
| `notes` | Shared operational memory, appended, not replaced. |

User-level config is supported under `~/.agents/config/`. Use it for personal defaults such as `default_branch`, `report_template`, or `execution_mode`. Project config always overrides user-level config, so team decisions still take precedence.

---

## Config schema

```yaml
preferences:
  fail_fast: false
  max_concurrent_gates: 1
  report_template: default
  include_uncommitted: true
  default_branch: null
  base_ref: null

  gates:
    test:
      enabled: auto
      importance: required
      fail_fast: false
      commands: []
      detect_ci_jobs: true

    spec-coverage:
      enabled: auto
      importance: required
      fail_fast: false
      mappings: []
      exemptions: []

    standards:
      enabled: auto
      importance: required
      fail_fast: false
      sources: []
      ai_inference:
        enabled: false
        source_paths: []
        edit_before_use: true
      overrides: []

    dead-code:
      enabled: auto
      importance: optional
      type: custom
      adapter: null
      fallback_adapters: []
      cwd: "."
      timeout: 300

    complexity:
      enabled: auto
      importance: optional
      type: custom
      adapter: null
      fallback_adapters: []
      cwd: "."
      timeout: 300

    duplication:
      enabled: auto
      importance: optional
      type: custom
      adapter: null
      fallback_adapters: []
      cwd: "."
      timeout: 300

    security:
      enabled: auto
      importance: optional
      type: custom
      adapter: null
      fallback_adapters: []
      cwd: "."
      timeout: 300
      tags: [security]

    style:
      enabled: auto
      importance: optional
      type: custom
      adapter: null
      fallback_adapters: []
      cwd: "."
      timeout: 300

    architecture:
      enabled: auto
      importance: optional
      type: custom
      adapter: null
      fallback_adapters: []
      cwd: "."
      timeout: 300

    security-audit:
      enabled: auto
      importance: optional
      fail_fast: false
      type: command
      commands: []

    style-format:
      enabled: auto
      importance: optional
      fail_fast: false
      commands: []

notes:
  - text: "Default gate behavior is auto-detection; nothing is assumed."
    category: decision
```

---

## Global preferences

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `fail_fast` | boolean | `false` | Stop after the first required gate fails. |
| `max_concurrent_gates` | integer | `1` | Maximum gates to run in parallel. |
| `report_template` | string | `default` | `default`, `compact`, `detailed`, `custom` — Report template to use. |
| `report_template_path` | string or null | `null` | Path to a custom report template. |
| `execution_mode` | string | `full` | `quick`, `full`, `security-audit` — Which gates to run. |
| `tags` | list of strings | `[]` | Only include gates that have all listed tags. |
| `dry_run` | boolean | `false` | Report the planned gates without running them. |
| `include_uncommitted` | boolean | `true` | Include staged, unstaged, and untracked files in the verification set. |
| `default_branch` | string or null | `null` | Override default branch; auto-detected if null. |
| `base_ref` | string or null | `null` | Override diff base; uses default branch if null. |
| `adapter_paths` | list of strings | `[]` | Extra directories to search for custom adapters. |

---

## Execution modes and planning

`preferences.execution_mode` controls which gates are included in a run:

- `full` — include all enabled gates. This is the default.
- `quick` — include required gates and any gate tagged `fast` or `quick`.
- `security-audit` — include only gates tagged `security`.

`preferences.tags` provides an additional filter: only gates that have all of the listed tags are included.

`preferences.dry_run` reports the planned gates and stops without executing them.

### Gate dependencies

Any gate may declare `depends_on` with a list of gate names. The skill orders gates so that dependencies run first. Circular dependencies and references to unknown gates are reported as planning errors.

Example:

```yaml
preferences:
  execution_mode: quick
  tags: []
  dry_run: false

  gates:
    test:
      enabled: true
      importance: required
      tags: [fast]

    deploy-preview:
      enabled: true
      importance: optional
      tags: [slow]
      depends_on: [test]
```

In `quick` mode, `test` runs but `deploy-preview` is skipped because it is optional and has no `fast`/`quick` tag.

All gates live under `preferences.gates`. Each gate has the same common fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean or string | `auto` | Whether the gate runs. `auto` detects tools and treats missing tools as optional. `false` disables the gate; disabled required gates are treated as `NOT_APPLICABLE` for verdict purposes. |
| `importance` | string | gate-specific | `required` gates fail the overall verdict; `optional` gates do not. |
| `fail_fast` | boolean | `false` | Stop the gate at the first internal failure. |
| `tags` | list of strings | `[]` | Tags used by execution modes and tag filters. |
| `depends_on` | list of strings | `[]` | Gate names that must run before this gate. |

### Gate: `test`

Runs the project test suite. Supports multiple commands, each with its own settings.

- `enabled` — `auto` detects test commands; `true` always runs; `false` skips.
- `importance` — defaults to `required`.
- `detect_ci_jobs` — scan CI files for additional test commands.
- `commands` — list of command objects:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | detected | Human-readable label. |
| `command` | string | detected | Shell command to execute. |
| `cwd` | string | `.` | Working directory relative to project root. |
| `timeout` | integer | `300` | Timeout in seconds. |
| `env` | map | `{}` | Environment variables for the command. |
| `importance` | string | inherits gate | `required` or `optional` for this command. |
| `run_when` | list of globs | `**/*` | Run only when changed files match. |

Commands are run in order. A command with `run_when` is skipped if no changed file matches.

### Gate: `spec-coverage`

Verifies that changed source files have corresponding spec files that exist and were modified.

- `mappings` — list of source-to-spec mappings:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source_pattern` | glob | required | Pattern matching source files. |
| `spec_pattern` | glob | required | Pattern matching expected spec files. |
| `area` | string | inferred | Reporting label, e.g. `frontend`, `backend`. |

- `exemptions` — list of patterns that do not need spec coverage:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `pattern` | glob | required | Pattern matching exempt files. |
| `reason` | string | required | Why the exemption exists. |

Example:

```yaml
mappings:
  - source_pattern: "src/**/*.js"
    spec_pattern: "src/**/*.test.js"
    area: "frontend"
exemptions:
  - pattern: "src/**/*.config.js"
    reason: "Configuration files contain no logic to test."
```

### Gate: `standards`

Applies project standards rules to changed files.

- `sources` — list of standards files to load:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | string | `yaml` | `yaml` or `markdown-frontmatter`. |
| `path` | string | required | Path to the standards file relative to project root. |
| `name` | string | inferred | Reporting label. |

- `ai_inference` — infer rules from markdown docs when no YAML sources exist:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable inference. |
| `source_paths` | list | `[]` | Markdown files to infer from. |
| `edit_before_use` | boolean | `true` | Present inferred rules for editing before persisting. |

- `overrides` — project-specific rule adjustments:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | string | required | Rule ID to override. |
| `severity` | string | rule default | `violation`, `consideration`, `warning`, or `disabled`. |
| `threshold` | number | rule default | New threshold if the rule supports one. |
| `reason` | string | required | Why the override exists. |

Example override:

```yaml
overrides:
  - id: "nesting-depth"
    severity: "consideration"
    threshold: 4
    reason: "Legacy widget tree makes deeper nesting unavoidable until refactor."
```

### Gate: `custom` (static-analysis, security, style, dead-code, etc.)

The open gate registry lets you define any tool-backed gate as a `custom` gate under `preferences.gates`. Each `custom` gate runs a single adapter through `scripts/run-gate.js`.

Common examples:

| Gate purpose | Typical adapter |
|--------------|---------------|
| `dead-code` | `knip`, `depcheck`, `ts-unused` |
| `complexity` | `eslint-sonarjs` |
| `duplication` | `jscpd` |
| `security` | `npm-audit`, `snyk` |
| `style` | `eslint`, `biome` |
| `architecture` | project-specific adapter |

Per-gate fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `adapter` | string | detected | Primary adapter to use. |
| `fallback_adapters` | list | `[]` | Ordered fallback adapters. |
| `command` | string | adapter default | Optional command override. |
| `cwd` | string | `.` | Working directory. |
| `timeout` | integer | adapter default | Timeout in seconds. |
| `detect_marker` | list | `[]` | Files that indicate this adapter is applicable. |

If a custom gate is enabled but no adapter is available, it is marked `SKIPPED` if optional, or `ERROR` if required.

Example:

```yaml
gates:
  dead-code:
    enabled: auto
    importance: optional
    type: custom
    adapter: knip
    fallback_adapters: [depcheck, ts-unused]
    cwd: "."
    timeout: 300

  security:
    enabled: auto
    importance: optional
    type: custom
    adapter: npm-audit
    fallback_adapters: [snyk]
    cwd: "."
    timeout: 300
    tags: [security]
```

### Legacy `static-analysis` gate

v3 configs may still use the `static-analysis` gate with `sub_gates`. The `static-analysis-gate` subagent remains available for backwards compatibility. New configs should define each sub-gate as a separate `custom` gate.

---

## Verdict policy

`preferences.verdict_policy` controls how gate results are aggregated into the overall verdict.

| Mode | Behavior |
|------|----------|
| `all_required` (default) | All required gates must pass. Any required failure or error fails the verdict. A required gate that is explicitly disabled (`enabled: false`) is treated as `NOT_APPLICABLE` rather than `SKIPPED`. |
| `any_required` | Pass if at least one required gate passes cleanly and no required gate errors. |
| `threshold` | Pass if required failures, errors, and total violations are within configured limits. |

Example `threshold` policy:

```yaml
preferences:
  verdict_policy:
    mode: threshold
    threshold:
      max_failures: 0
      max_errors: 0
      max_violations: 3
```

---

## Bootstrap behavior

If `.agents/config/verify-branch.yaml` does not exist, or if required fields are missing, the skill enters bootstrap mode:

1. **Load** — Read `shared.yaml` and any existing `verify-branch.yaml`.
2. **Detect** — Run detection scripts to propose defaults:
   - Project type and available tools.
   - Test commands from `package.json`, `pyproject.toml`, `go.mod`, etc.
   - CI job commands from workflow files.
   - Source-to-spec conventions.
   - Standards docs such as `STANDARDS.md`, `CONTRIBUTING.md`, or `ARCHITECTURE.md`.
   - Static-analysis tools such as ESLint, Knip, jscpd, etc.
3. **Build proposal** — The `bootstrap` subagent constructs a proposed config.
4. **Consult** — Present the proposal to the user. Pre-populate questions with detected values. Always offer "Other" or "Ask me later."
5. **Persist** — Write the resolved config to `.agents/config/verify-branch.yaml`.
6. **Proceed** — Continue the verification run using the resolved config.

If the user is unavailable or declines input, required gates with missing tools are marked `ERROR` and the overall verdict is `FAIL`. Optional gates are marked `SKIPPED`.

---

## Overriding detected defaults

Detected defaults are proposals, not decisions. To override them:

1. Edit `.agents/config/verify-branch.yaml` directly.
2. Answer differently during bootstrap.
3. Provide a value on the fly when the skill asks for missing config during a run.

The skill never silently overwrites an existing config value. If a detection result conflicts with a stored value, the skill reports the conflict and asks which to keep.

---

## Config on-the-fly

If a gate is enabled but missing a required value during execution (for example, a `command` or `source_pattern`):

1. The skill pauses the current gate.
2. It asks the user for the missing value.
3. It writes the value back to `.agents/config/verify-branch.yaml`.
4. It resumes the gate using the updated config.

If the user declines, the gate is marked `ERROR` if required, or `SKIPPED` if optional.

If the user updates config manually during a run, the skill completes the current gate with the original config, then re-reads config before the next gate. Changes are recorded in the report notes and checkpoint state.

---

## Note categories

Notes capture operational memory. They should be concise and future-facing. Use the categories from the `write-a-skill` framework:

| Category | Example |
|----------|---------|
| `workaround` | "Knip reports false positives for barrel files; ignore them via `exemptions` in `verify-branch.yaml`." |
| `preference` | "User prefers `fail_fast: true` for quick pre-push checks." |
| `gotcha` | "Security audit adapter times out on the first run if the registry is slow; increase timeout to 600." |
| `decision` | "Spec-coverage gate is required because the team does not trust coverage without it." |
| `assumption` | "Assuming `main` is the default branch until `origin/HEAD` is configured." |

Notes are appended, never replaced. If a new note contradicts an existing one, the skill asks the user before adding it.

---

## User consultation rules

- Never silently overwrite existing config values.
- Pre-populate every question with detected values and previous preferences.
- Always offer an "Other" or "Ask me later" option.
- Do not skip a required gate without user confirmation.
- Do not modify code during bootstrap or config resolution.
- Explain why a value is needed before asking for it.
- When detection conflicts with stored config, present the diff and ask.
