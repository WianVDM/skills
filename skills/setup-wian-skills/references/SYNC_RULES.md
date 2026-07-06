# Sync rules

The sync plan compares the source package to the installed skills in the target scope.

## Statuses

| Status | Definition | Default action |
|---|---|---|
| `missing` | Skill exists in source but not in target scope. | Install after confirmation. |
| `changed` | Skill exists in both but content differs. | Update after confirmation. |
| `identical` | Skill exists in both and content is the same. | Skip. |
| `modified` | Target copy differs from source but source version is newer. | Ask: overwrite or keep local. |
| `older` | Target version is newer than source. | Warn and ask: downgrade or skip. |

## Content comparison

Compare skill directories using `diff -r` or equivalent. If any difference exists, the installed copy is treated as locally modified.

## Version comparison

Use the `version` frontmatter field when present. If absent, fall back to content comparison.
