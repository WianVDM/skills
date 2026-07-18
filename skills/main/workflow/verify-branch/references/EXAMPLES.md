# Examples

Global examples for configuring and running `verify-branch` on different project types.

## Example 1: Node.js/TypeScript library

```yaml
# .agents/config/verify-branch.yaml
preferences:
  fail_fast: false
  include_uncommitted: true
  execution_mode: full

  gates:
    test:
      enabled: auto
      importance: required
      type: command
      fail_fast: false
      detect_ci_jobs: true
      commands:
        - name: "Unit tests"
          command: "npm run test:ci"
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
        - source_pattern: "src/**/*.ts"
          spec_pattern: "src/**/*.test.ts"
          area: "unit"
      exemptions:
        - pattern: "src/**/*.d.ts"
          reason: "Type declaration files contain no logic to test."

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

    dead-code:
      enabled: auto
      importance: optional
      type: custom
      adapter: knip
      fallback_adapters: [depcheck, ts-unused]
      cwd: "."
      timeout: 300

    complexity:
      enabled: auto
      importance: optional
      type: custom
      adapter: eslint-sonarjs
      cwd: "."
      timeout: 300

    duplication:
      enabled: auto
      importance: optional
      type: custom
      adapter: jscpd
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

    style:
      enabled: auto
      importance: optional
      type: custom
      adapter: eslint
      fallback_adapters: [biome]
      cwd: "."
      timeout: 300

notes:
  - text: "Initial verify-branch config for a Node.js library using the open gate registry."
    category: decision
```

## Example 2: Python service

```yaml
# .agents/config/verify-branch.yaml
preferences:
  fail_fast: false
  include_uncommitted: true

  gates:
    test:
      enabled: auto
      importance: required
      type: command
      commands:
        - name: "pytest"
          command: "pytest"
          cwd: "."
          timeout: 300
          run_when:
            - "src/**/*.py"
            - "tests/**/*.py"

    spec-coverage:
      enabled: auto
      importance: required
      type: mapper
      mappings:
        - source_pattern: "src/**/*.py"
          spec_pattern: "tests/**/*.py"
          area: "unit"
      exemptions:
        - pattern: "src/**/__init__.py"
          reason: "Package init files usually contain no logic."

    standards:
      enabled: auto
      importance: required
      type: standards
      sources:
        - type: yaml
          path: ".agents/config/standards.yaml"
          name: "Project standards"

    dead-code:
      enabled: auto
      importance: optional
      type: custom
      command: "vulture ."
      cwd: "."
      timeout: 300

    complexity:
      enabled: auto
      importance: optional
      type: custom
      command: "radon cc -nc src"
      cwd: "."
      timeout: 300

    style:
      enabled: auto
      importance: optional
      type: custom
      command: "ruff check ."
      cwd: "."
      timeout: 300

notes: []
```

## Example 3: Go service

```yaml
# .agents/config/verify-branch.yaml
preferences:
  fail_fast: false
  include_uncommitted: true

  gates:
    test:
      enabled: auto
      importance: required
      type: command
      commands:
        - name: "go test"
          command: "go test ./..."
          cwd: "."
          timeout: 300
          run_when:
            - "**/*.go"

    spec-coverage:
      enabled: false
      importance: optional
      type: mapper

    standards:
      enabled: auto
      importance: required
      type: standards
      sources:
        - type: yaml
          path: ".agents/config/standards.yaml"
          name: "Project standards"

    dead-code:
      enabled: auto
      importance: optional
      type: custom
      command: "go vet ./..."
      cwd: "."
      timeout: 300

    style:
      enabled: auto
      importance: optional
      type: custom
      command: "gofmt -l ."
      cwd: "."
      timeout: 300

notes: []
```

## Example 4: Running with a branch override

```text
verify-branch feature/OC-1234
```

The skill verifies the branch `feature/OC-1234` against the detected default branch. If no default branch is detected and `preferences.default_branch` is not set, the skill asks the user.

## Example 5: Resume after interruption

If a previous run was interrupted, the state file `.agents/context/verify-branch/{branch-name}-state.md` records completed gates. The skill reads this file, invokes `checkpoint/resume`, and resumes from the first pending gate.

## Example 6: Fresh advisory context

A `baseline` report exists at `.agents/context/baseline/OC-1234-feature-x.md` with matching branch and commit. The `context-scout` classifies it as fresh. The report is passed to gate subagents as advisory context but does not influence the verdict.

A stale `debrief` report from an earlier commit is noted in the final report under `consumed_context.stale` with a reason such as "commit mismatch".

## Example 7: Adding a custom adapter

A project uses a custom lint tool called `lint-9000`. The project adds an adapter at `.agents/verify-branch/adapters/lint-9000.js` that implements the adapter contract in [ADAPTERS.md](ADAPTERS.md). Then the config references it:

```yaml
preferences:
  adapter_paths:
    - ".agents/verify-branch/adapters"

  gates:
    style:
      enabled: true
      importance: optional
      type: custom
      adapter: lint-9000
      cwd: "."
      timeout: 300
```

The adapter is registered in [GATE_REGISTRY.md](GATE_REGISTRY.md) and [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md) for discoverability.

## Example 8: Execution modes and tags

Run only fast gates in a pre-push check:

```yaml
preferences:
  execution_mode: quick

  gates:
    test:
      enabled: true
      importance: required
      tags: [fast]

    lint:
      enabled: true
      importance: optional
      type: custom
      adapter: eslint
      tags: [fast]

    security:
      enabled: true
      importance: optional
      type: custom
      adapter: npm-audit
      tags: [security]

    deploy-preview:
      enabled: true
      importance: optional
      tags: [slow]
      depends_on: [test]
```

In `quick` mode, `test` and `lint` run; `security` and `deploy-preview` are skipped. In `security-audit` mode, only `security` runs. In `full` mode, all enabled gates run, with `deploy-preview` waiting for `test` to finish.

## Example 9: Dry run

Report the planned execution without running any gates:

```text
verify-branch feature/OC-1234
# With config: preferences.dry_run: true
```

The skill writes the planned gate list to the report and exits with a PASS verdict, since no gates were executed.
