# Capability Detection

Before orchestrating, detect what the environment can do.

## Capabilities to detect

| Capability | How to detect |
|------------|---------------|
| Issue tracker access | Check for Jira, GitHub Issues, or manual ticket context in `.agents/context/debrief/`. |
| Source control | Check for `.git` and available remotes. |
| Test runners | Check `package.json`, `pyproject.toml`, or similar for test scripts. |
| UI verification | Check for Playwright, Cypress, or manual baseline capability. |
| Available skills | Scan user and built-in skill directories for `SKILL.md` files. |

## Skill availability mapping

For each role category in config, check whether at least one mapped skill is installed. If a required category has no available skill, stop and ask the user.

## Dynamic role resolution

Config stores role categories, not hardcoded names. At runtime:

1. Read the role category list from config.
2. For each skill in the list, check if it is installed.
3. Use the first installed skill for the role.
4. If none are installed, fall back to the generic subagent for that role (e.g., `implementer` for implementation).
