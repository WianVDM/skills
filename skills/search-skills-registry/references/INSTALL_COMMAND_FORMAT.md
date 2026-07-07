# Install command format

`search-skills-registry` normalizes every result into an `install_command` that can be passed to `install-skill`.

## Valid format

```json
{
  "install_command": "install-skill <name> --source <url>"
}
```

Example:

```json
{
  "install_command": "install-skill lint-ts --source https://skills.sh/skills/lint-ts"
}
```

## Invalid format (negative test case)

Any result that does not match the `install-skill <name> --source <url>` pattern is invalid and should be rejected by a conductor or validation step. The previous broken format used `--registry` instead of `--source`:

```json
{
  "install_command": "install-skill lint-ts --registry skills-sh"
}
```

This command does not work because `install-skill` does not accept a `--registry` argument.

## Validation rule

A valid `install_command` must:

1. Start with `install-skill`.
2. Include the skill name as the second argument.
3. Include the `--source` flag followed by the source URL.

If a registry result produces an `install_command` that violates this rule, the result should be treated as malformed.
