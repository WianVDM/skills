# Dependencies

## Required skills

- `detect-project-context` — locate the project root and recommended config directory.
- `list-available-skills` — discover installed skills in the target scope.
- `install-skill` — copy approved skills into the target scope.
- `validate-skill-frontmatter` — validate the frontmatter of every installed skill after sync.

## Required tools

- `read`, `write`, `edit`, `bash` — core agent tools.

## Required binaries

- `git` (preferred) or `curl` (fallback) — fetch the source package.
- `diff` — detect local modifications.

## Required environment variables

None.

## Optional environment variables

- `GITHUB_TOKEN` — if `github.com/WianVDM/skills` is private or rate-limited.
