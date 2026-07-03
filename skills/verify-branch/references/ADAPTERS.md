# Adapter Contract and Registry

Adapters are the executable bridge between a gate and the underlying tool or command. Each adapter is a small script that receives structured input, invokes one tool, and returns structured output. The gate runner dispatches adapters and normalizes their output so the conductor can aggregate results without knowing tool internals.

## Adapter discovery

Adapters are resolved in the following order:

1. **Project adapters:** paths listed in `preferences.adapter_paths`, plus the default project directory `{project_root}/.agents/verify-branch/adapters`.
2. **Extension adapters:** global or harness-level extension directories (from config or `VERIFY_BRANCH_EXTENSION_DIR` env var).
3. **Skill built-in adapters:** the skill's own adapter directory, searched by adapter name (new flat layout) and then by legacy category layout.

This means projects can add custom adapters without editing the skill. They can also override built-in adapters by placing a same-named adapter in a project adapter path.

## Adapter contract

Adapters must follow the input and output schemas below. Adapters may be written in any language as long as they read and emit the expected JSON.

### Input

The gate runner passes the following input to every adapter. Adapters must accept it either as JSON on `stdin` or as a single JSON-encoded string argument named `--input`.

```json
{
  "changed_files": [
    "src/auth/guard.ts",
    "src/auth/guard.test.ts"
  ],
  "base_branch": "origin/main",
  "config": {
    "enabled": "auto",
    "adapter": "eslint",
    "command": null,
    "cwd": ".",
    "timeout": 300
  },
  "project_root": "/absolute/path/to/project"
}
```

| Field | Type | Description |
|---|---|---|
| `changed_files` | list of strings | Paths changed in the branch, relative to `project_root`. |
| `base_branch` | string | The base ref used for the diff. |
| `config` | object | The gate configuration from `verify-branch.yaml`. |
| `project_root` | string | Absolute path to the project root. |

Adapters should treat missing or empty `changed_files` as a signal to return `NOT_APPLICABLE` when the tool only makes sense for changed files, or to run the tool globally when the gate is designed for full scans.

### Output

Adapters must write a single JSON object to `stdout`. Extra lines on `stderr` are captured as `raw_output` but must not affect parsing.

```json
{
  "status": "PASS",
  "findings": [],
  "summary": "ESLint found no issues in 2 changed files.",
  "raw_output": ""
}
```

| Field | Type | Description |
|---|---|---|
| `status` | string | One of `PASS`, `FAIL`, `ERROR`, `NOT_APPLICABLE`, `SKIPPED`. |
| `findings` | list of objects | Zero or more findings produced by the tool. |
| `summary` | string | Human-readable summary of the result. |
| `raw_output` | string | Raw tool output, captured for debugging and reporting. |

### Optional adapter metadata

Adapters may include a `metadata` object in their output to declare capabilities:

```json
{
  "status": "PASS",
  "findings": [],
  "summary": "...",
  "metadata": {
    "fulfills": ["style", "lint"],
    "requires": ["eslint"],
    "detect_marker": [".eslintrc", "eslint.config.js"]
  }
}
```

| Field | Type | Description |
|---|---|---|
| `fulfills` | list of strings | Gate categories this adapter can fulfill. |
| `requires` | list of strings | External tools required by the adapter. |
| `detect_marker` | list of strings | Files that indicate this adapter is applicable. |

### Status values

| Status | Meaning | When to use |
|---|---|---|
| `PASS` | Tool ran and found no blocking issues. | The tool completed and reported no violations relevant to the gate. |
| `FAIL` | Tool ran and found blocking issues. | The tool completed but reported violations. |
| `ERROR` | Tool could not run. | Missing binary, crashed process, invalid config, or unreadable input. |
| `NOT_APPLICABLE` | No work to do. | No changed files match the tool's scope, or the gate has no relevant files. |
| `SKIPPED` | Tool not available and gate is optional. | The adapter detected it is unavailable and the gate should not be treated as an error. |

### Finding schema

Each finding must include the following fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | string or null | yes | Path to the file, relative to `project_root`. Use `null` for gate-level findings. |
| `line` | integer or null | no | Line number if known. Use `0` or `null` for gate-level findings. |
| `rule` | string | yes | Rule ID, category, or tool-specific identifier. |
| `severity` | string | yes | `violation`, `consideration`, `warning`, or `info`. |
| `message` | string | yes | Human-readable description of the finding. |
| `introduced` | boolean | no | `true` if the finding is believed to be introduced by the branch. |

Example:

```json
{
  "file": "src/auth/guard.ts",
  "line": 42,
  "rule": "complexity/cyclomatic",
  "severity": "violation",
  "message": "Function `canActivate` has cyclomatic complexity 18, exceeding threshold 10.",
  "introduced": true
}
```

### Exit behavior

Adapters must exit with code `0` when they run successfully, even if the tool they wrap reports violations. A non-zero exit code is reserved for hard adapter errors such as:

- The adapter script itself crashed.
- The adapter could not parse the input JSON.
- The adapter could not write output.
- An unexpected exception occurred.

The tool's own non-zero exit code must be mapped to `FAIL` or `ERROR` in the JSON output, with the adapter itself exiting `0`.

---

## Adding a new adapter

### Option A: Project-specific adapter

Create a file in your project:

```
{project-root}/.agents/verify-branch/adapters/my-adapter.js
```

Reference it in `.agents/config/verify-branch.yaml`:

```yaml
preferences:
  gates:
    my-gate:
      type: custom
      adapter: my-adapter
```

### Option B: Skill built-in adapter

1. Create a file in the skill's adapter directory. The new flat layout is preferred: `scripts/adapters/{adapter-name}.js`. The legacy category layout (`scripts/adapters/{category}/{adapter-name}.js`) is still supported for backwards compatibility.
2. Follow the input/output contract.
3. Keep it focused: one adapter should wrap one tool or one command pattern.
4. Register the adapter in `references/GATE_REGISTRY.md` and list it below.
5. Document the adapter's purpose, tool, and config expectations.
6. Test it manually with sample input and add a contract test if possible.

---

## Shipped adapters

### Command adapters

The `command` value can be either a string (executed through the shell) or an array of strings (executed directly without shell interpolation). **Array form is preferred** because it prevents shell injection from file paths and other variables. The string form is preserved for backwards compatibility and should only be used with trusted, hard-coded commands.

| Adapter | Tool / pattern | Description |
|---|---|---|
| `custom-command` | arbitrary shell command | Runs any command supplied in `config.command`. |
| `npm-test` | `npm test` / `npm run test` | Runs the standard npm test script. |
| `jest` | `jest` | Runs Jest with project configuration. |
| `vitest` | `vitest` | Runs Vitest with project configuration. |
| `pytest` | `pytest` | Runs pytest for Python projects. |
| `go-test` | `go test` | Runs Go tests for Go projects. |

### Mapper adapters

| Adapter | Tool / pattern | Description |
|---|---|---|
| `default-mapper` | glob mapping | Maps `source_pattern` to `spec_pattern` using configured mappings. |

### Standards adapters

| Adapter | Tool / pattern | Description |
|---|---|---|
| `yaml-standards` | YAML file | Reads rules from a YAML standards file and applies them. |
| `markdown-frontmatter` | Markdown frontmatter | Reads rules embedded in Markdown frontmatter. |

### Custom / analysis adapters

| Adapter | Tool / pattern | Description |
|---|---|---|
| `knip` | `knip` | Finds unused files, dependencies, and exports. |
| `depcheck` | `depcheck` | Finds unused npm dependencies. |
| `ts-unused` | `ts-unused-exports` | Finds unused TypeScript exports. |
| `eslint-sonarjs` | `eslint` with `eslint-plugin-sonarjs` | Uses SonarJS complexity rules. |
| `jscpd` | `jscpd` | Detects copy-paste code duplication. |
| `npm-audit` | `npm audit` | Reports known vulnerabilities in npm dependencies. |
| `snyk` | `snyk test` | Reports Snyk security findings. |
| `eslint` | `eslint` | Runs ESLint on changed files. |
| `biome` | `biome check` | Runs Biome lint and format checks. |

---

## Adapter selection and fallback

The gate runner selects an adapter using this order:

1. If `config.command` is set, use the `custom-command` adapter with the override.
2. If `config.adapter` is set and non-null, resolve it using the discovery paths.
3. If `config.adapter` is null or unavailable, try `config.fallback_adapters` in order.
4. If no adapter is available and the gate is optional, return `SKIPPED`.
5. If no adapter is available and the gate is required, return `ERROR`.

Adapters may declare themselves unavailable by returning `SKIPPED` with a summary such as `Binary 'knip' not found in PATH`. The gate runner then proceeds to the next fallback or escalates according to the gate's importance.

---

## Adapter debugging

When an adapter fails unexpectedly, inspect the following:

- The `raw_output` field in the gate report for the tool's stderr and stdout.
- The adapter's exit code in the gate runner logs (non-zero exit codes indicate adapter bugs, not tool violations).
- The input JSON passed to the adapter, including `changed_files` and `config`.
- The adapter discovery path to confirm which file was resolved.

To test an adapter manually, pipe sample input to it:

```bash
echo '{"changed_files":["src/example.ts"],"base_branch":"origin/main","config":{"adapter":"eslint"},"project_root":"."}' | node .agents/verify-branch/adapters/eslint.js
```

To test the gate runner's discovery, use:

```bash
echo '{"changed_files":[],"base_branch":"origin/main","config":{"adapter":"eslint"},"project_root":"."}' | node scripts/run-gate.js --gate style --adapter eslint
```
