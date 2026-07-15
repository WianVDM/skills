# index-skill-capabilities

Generate a structured capability index from the skill bundle.

## What it does

This building block reads every skill's `SKILL.md`, `README.md`, `references/`, `subagents/`, `scripts/`, and `config.yaml`, extracts the capabilities each skill implements, and writes a machine-readable JSON index.

By default, the index is written to `.agents/skill-capability-index.json` in the detected project so it can be used as a project-local override. The path is configurable with `--output`; bundle CI typically uses `--output docs/skill-capability-index.json` to commit the index to the repository.

Other skills and conductors can use the index to:

- Find skills that implement a specific capability.
- Compare a new skill against the existing catalog.
- Detect overlap and extraction opportunities.
- Rank alternatives by shared capabilities.

## Usage

Generate the index (default project-local path):

```bash
python skills/blocks/authoring/index-skill-capabilities/scripts/index-skill-capabilities.py
```

Generate the index for the bundle repository (committed to `docs/`):

```bash
python skills/blocks/authoring/index-skill-capabilities/scripts/index-skill-capabilities.py --output docs/skill-capability-index.json
```

Validate an existing index:

```bash
python skills/blocks/authoring/index-skill-capabilities/scripts/index-skill-capabilities.py --check
```

Write to a custom path:

```bash
python skills/blocks/authoring/index-skill-capabilities/scripts/index-skill-capabilities.py --output /path/to/index.json
```

## Index schema

See [`references/INDEX_SCHEMA.md`](references/INDEX_SCHEMA.md) for the full JSON schema, taxonomy, and consumer rules.

## When to maintain or extend this skill

- The taxonomy needs new categories.
- The source extraction rules need to handle new `SKILL.md` section shapes.
- A new skill file type should be indexed (e.g., `assets/`).
- The schema version changes.

## Directory layout

```text
index-skill-capabilities/
├── SKILL.md
├── README.md
├── references/
│   ├── INDEX_SCHEMA.md
│   └── DEPENDENCIES.md
├── scripts/
│   ├── index-skill-capabilities.py
│   └── tests/
│       └── test_index_skill_capabilities.py
└── evals/
    └── evals.json
```

## Key conventions

- The index is deterministic and reproducible for the same skill files.
- The index is versioned and includes freshness metadata.
- The generator does not use LLMs; it uses structured parsing and keyword rules.
- User-scope and third-party skills are not indexed in v1, but the schema is designed to support them.

## Dependencies

- `parse-skill-frontmatter` (recommended)
- `context-reports` (recommended)
- `pyyaml`

## How to update

- Keep `SKILL.md` focused on purpose and workflow; push schema details into `INDEX_SCHEMA.md`.
- Update the taxonomy when a new cross-cutting capability appears in two or more skills.
- Bump the schema version when the index structure changes.
- Run `scripts/tests/test_index_skill_capabilities.py` after any change.
