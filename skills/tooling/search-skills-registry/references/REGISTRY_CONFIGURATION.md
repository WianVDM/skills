# Registry configuration

Registries are declared in `.agents/config/write-a-skill.yaml` under `write-a-skill.registries`:

```yaml
write-a-skill:
  registries:
    - name: skills-sh
      source_type: skills_sh
      search_url: https://skills.sh/api/search
    - name: github
      source_type: github
      search_url: https://api.github.com/search/repositories
    - name: npm
      source_type: npm
      search_command: npm search
    - name: local
      source_type: local
      search_path: /path/to/local/registry
```

Supported `source_type` values:

- `skills_sh` — Uses a JSON search URL.
- `github` — Uses the GitHub repository search API.
- `npm` — Runs `npm search <query> --json`.
- `url` — Uses a generic JSON search URL.
- `local` — Scans a local directory containing skill subdirectories.

Each registry must include a `name` and `source_type`. Additional keys such as `search_url`, `search_command`, or `search_path` are required by the relevant handler.

If no configuration file exists, the skill uses built-in defaults that include the `skills-sh`, `github`, and `npm` registries.
