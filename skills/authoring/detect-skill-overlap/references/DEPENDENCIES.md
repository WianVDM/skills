# Dependencies

## Required skills

- **list-available-skills** — provides the catalog of existing skills in the project and user scope.
- **parse-skill-frontmatter** — extracts canonical fields from `SKILL.md` files.

## Recommended skills

- **detect-project-context** — optional, used to locate the project and user skill directories when the catalog is not already known.

## Required tools and capabilities

- **Read files** — to inspect the target skill and catalog skills.
- **Search / grep** — to find references and dependencies across skill files.

## Required binaries

- `python3` — required by the `list-available-skills` and `parse-skill-frontmatter` scripts.

## Required MCP servers

None.

## Environment variables

None.

## Consumed references

- `docs/skill-standards/fundamentals/architecture/dependencies-and-bundling.md` — colocation vs extraction rules.
