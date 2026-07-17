# Dependencies

## Required skills

None. `context-reports` is a standalone vocabulary building block.

## Recommended skills

- `artifact-freshness` — the operational freshness check for consumed reports. Evaluated lazily: only needed when a consumer validates freshness.

## Consumed references

- `references/context-report-schema.json` — embedded fallback mirror of the canonical context-report schema in the skill-standards wiki. When the standards are resolvable via the standards path, they take precedence.

## Required tools

- **Read filesystem** — consumers read this skill's contract and report files.
