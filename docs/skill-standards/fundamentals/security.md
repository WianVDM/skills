# Security

A skill should be safe to use in an untrusted project by default. Security is not a separate concern; it shapes how a skill handles secrets, destructive actions, external access, and required capabilities.

---

## Secrets

Never store secrets in skill files, reference files, or config files.

| Bad | Good |
|-----|------|
| `api_key: abc123` in `.agents/config/{skill}.yaml` | `token_env: GITHUB_TOKEN` referencing an environment variable. |
| Embedding a service account key in a script. | Reading the key from a secure store or env var at runtime. |
| Recording a token in a context report. | Recording only that a token is required, not the value. |

If a skill needs credentials, it should:

- Reference an environment variable by name.
- Mention the required variable in `README.md` and `references/DEPENDENCIES.md`.
- Fail closed if the variable is missing, with a clear explanation.

---

## Destructive actions

A destructive action is anything that mutates state the user cannot trivially undo: writing files, deleting files, creating issues, posting comments, pushing commits, deploying, or changing configuration.

- Prefer read-only operations during investigation.
- Require explicit user confirmation before destructive actions.
- State clearly what will change and why.
- Offer a dry-run or preview when possible.

---

## External access

A skill must be explicit about what data leaves the local machine.

- If a skill calls an external API, document the endpoint and purpose.
- If a skill sends data to a remote model or service, document what is sent.
- If a skill uses an MCP server or extension, declare it as a dependency.

---

## Required capabilities

A skill must declare the tools, APIs, MCP servers, extensions, and environment variables it requires.

Dependencies are not bad. Hidden dependencies are.

- List required skills in `SKILL.md` frontmatter or `references/DEPENDENCIES.md`.
- List external tools and environment variables in `README.md` and `references/DEPENDENCIES.md`.
- If a capability is missing, fail closed with a clear explanation.

---

## Project trust

A skill should not assume the project is trusted. Even in a project the user owns, the skill should:

- Avoid running arbitrary commands from project files without inspection.
- Avoid executing generated scripts before review.
- Treat external URLs, package registries, and API responses as potentially malicious.

---

## Fail closed

If a required security capability is missing, the skill stops. It does not silently degrade or guess.

Examples:

- A token is required but not set → stop and explain.
- A destructive action is requested but not confirmed → stop and ask.
- A required tool is not installed → stop and list the missing tool.

---

## Research basis

- The fundamental rule of **no secrets in skill files** is a common denominator across the research sources. Every harness and governance source treats credential storage as a critical risk.
- **Destructive action confirmation** and the preference for read-only investigation are supported by the research on governance, audit, and the safe operation of skills in untrusted projects.
- **Fail closed** is our own framing, aligned with the research emphasis on explicit dependency handling and safety.
- The **external access** and **project trust** sections are our own synthesis, supported by the research on MCP server governance, third-party tool risk, and audit requirements.
- The distinction between dependency declaration (what is needed) and runtime capability checking (whether it is present) is drawn from the research on governance and capability gates.


---

## Security checklist

Use this when designing or reviewing a skill.

- [ ] No secrets are stored in skill files, references, or config.
- [ ] Required environment variables are declared by name.
- [ ] Destructive actions require explicit user confirmation.
- [ ] The skill prefers read-only operations during investigation.
- [ ] External APIs, MCP servers, and extensions are declared as dependencies.
- [ ] The skill documents what data leaves the local machine.
- [ ] The skill fails closed when a required capability is missing.
- [ ] The skill is safe to run in an untrusted project by default.
