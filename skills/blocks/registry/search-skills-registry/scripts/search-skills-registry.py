#!/usr/bin/env python3
"""
search-skills-registry.py

Search configured skill registries for third-party skills that could cover a
user's need. This script is read-only and does not install anything.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

DEFAULT_CONFIG = {
    "write-a-skill": {
        "registries": [
            {
                "name": "skills-sh",
                "source_type": "skills_sh",
                "search_url": "https://skills.sh/api/search",
            },
            {
                "name": "github",
                "source_type": "github",
                "search_url": "https://api.github.com/search/repositories",
            },
            {
                "name": "npm",
                "source_type": "npm",
                "search_command": "npm search",
            },
        ]
    }
}


def load_config(project_root: Path) -> list[dict]:
    config_path = project_root / ".agents" / "config" / "write-a-skill.yaml"
    if not config_path.is_file():
        config_path = project_root / ".pi" / "config" / "write-a-skill.yaml"
    if not config_path.is_file():
        config_path = project_root / "agents" / "config" / "write-a-skill.yaml"

    if config_path.is_file():
        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return data.get("write-a-skill", {}).get("registries", [])
        except Exception:
            return DEFAULT_CONFIG["write-a-skill"]["registries"]
    return DEFAULT_CONFIG["write-a-skill"]["registries"]


def http_get_json(url: str, timeout: int = 10) -> Optional[dict]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "search-skills-registry/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"_error": str(e)}


def parse_skill_frontmatter(skill_md: Path) -> dict:
    """Load the shared frontmatter parser and parse a SKILL.md file."""
    parser_path = (
        Path(__file__).resolve().parent.parent.parent
        / "parse-skill-frontmatter"
        / "scripts"
        / "parse-skill-frontmatter.py"
    )
    spec = importlib.util.spec_from_file_location(
        "parse_skill_frontmatter", parser_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_frontmatter(skill_md)


def search_local(registry: dict, query: str) -> list[dict]:
    search_path = Path(registry.get("search_path", ".")).expanduser().resolve()
    if not search_path.is_dir():
        return []
    results = []
    for entry in search_path.iterdir():
        if not entry.is_dir():
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.is_file():
            continue
        try:
            data = parse_skill_frontmatter(skill_md)
            desc = data.get("description", "")
            if query.lower() in f"{entry.name} {desc}".lower():
                results.append({
                    "name": data.get("name") or entry.name,
                    "description": desc,
                    "source": registry["name"],
                    "url": str(entry),
                    "trust_signals": {"local": True},
                })
        except Exception:
            continue
    return results


def search_url(registry: dict, query: str) -> list[dict]:
    base_url = registry.get("search_url", "")
    if not base_url:
        return []
    url = f"{base_url}?q={urllib.parse.quote(query)}" if "?" not in base_url else f"{base_url}&q={urllib.parse.quote(query)}"
    data = http_get_json(url)
    if data is None or "_error" in data:
        return []
    # Assume the response is either a list of results or an object with a results key
    items = data if isinstance(data, list) else data.get("results", data.get("items", []))
    results = []
    for item in items:
        if not isinstance(item, dict):
            continue
        results.append({
            "name": item.get("name", item.get("package_name", "unknown")),
            "description": item.get("description", ""),
            "source": registry["name"],
            "url": item.get("url", item.get("html_url", "")),
            "trust_signals": item.get("trust_signals", {}),
        })
    return results


def search_skills_sh(registry: dict, query: str) -> list[dict]:
    return search_url(registry, query)


def search_github(registry: dict, query: str) -> list[dict]:
    base_url = registry.get("search_url", "https://api.github.com/search/repositories")
    url = f"{base_url}?q={urllib.parse.quote(query + ' topic:agent-skill')}"
    data = http_get_json(url)
    if data is None or "_error" in data:
        return []
    results = []
    for item in data.get("items", []):
        results.append({
            "name": item.get("name", "unknown"),
            "description": item.get("description", ""),
            "source": registry["name"],
            "url": item.get("html_url", ""),
            "trust_signals": {
                "stars": item.get("stargazers_count"),
                "forks": item.get("forks_count"),
            },
        })
    return results


def search_npm(registry: dict, query: str) -> list[dict]:
    cmd = registry.get("search_command", "npm search")
    try:
        base = shlex.split(cmd)
        proc = subprocess.run(
            base + [query, "--json"],
            shell=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        data = json.loads(proc.stdout)
        results = []
        for item in data:
            if not isinstance(item, dict):
                continue
            pkg = item.get("package", item)
            results.append({
                "name": pkg.get("name", "unknown"),
                "description": pkg.get("description", ""),
                "source": registry["name"],
                "url": pkg.get("links", {}).get("npm", ""),
                "trust_signals": {
                    "score": item.get("score", {}).get("final"),
                },
            })
        return results
    except Exception as e:
        return [{"_error": str(e)}]


def normalize_result(r: dict, registry_name: str) -> dict:
    return {
        "source": r.get("source", registry_name),
        "name": r.get("name", "unknown"),
        "description": r.get("description", ""),
        "url": r.get("url", ""),
        "trust_signals": r.get("trust_signals", {}),
        "install_command": f"install-skill {r.get('name', 'unknown')} --source {r.get('url', '')}",
    }


def search_registry(registry: dict, query: str) -> tuple[list[dict], Optional[str]]:
    source_type = registry.get("source_type", "url")
    handlers = {
        "local": search_local,
        "url": search_url,
        "skills_sh": search_skills_sh,
        "github": search_github,
        "npm": search_npm,
    }
    handler = handlers.get(source_type)
    if not handler:
        return [], f"Unknown source_type: {source_type}"
    try:
        results = handler(registry, query)
        if results and "_error" in results[0]:
            return [], results[0]["_error"]
        return [normalize_result(r, registry["name"]) for r in results if isinstance(r, dict) and "_error" not in r], None
    except Exception as e:
        return [], str(e)


def main():
    parser = argparse.ArgumentParser(description="Search skill registries for third-party skills.")
    parser.add_argument("query", help="Natural-language search query.")
    parser.add_argument("--project-root", default=".", help="Project root for config loading.")
    parser.add_argument("--registry", help="Limit search to one registry by name.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    registries = load_config(project_root)
    if args.registry:
        registries = [r for r in registries if r.get("name") == args.registry]

    all_results = []
    errors = []
    for registry in registries:
        results, err = search_registry(registry, args.query)
        if err:
            errors.append({"registry": registry.get("name", "unknown"), "error": err})
        else:
            all_results.extend(results)

    # Deduplicate by name + source
    seen = set()
    unique = []
    for r in all_results:
        key = (r["name"], r["source"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    report = {
        "query": args.query,
        "registries": [r.get("name") for r in registries],
        "results": unique,
        "errors": errors,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Query: {args.query}")
        print(f"Registries searched: {len(registries)}")
        print("Results:")
        for r in unique:
            print(f"  - {r['name']} ({r['source']})")
            print(f"    {r['description']}")
        if errors:
            print("Errors:")
            for e in errors:
                print(f"  - {e['registry']}: {e['error']}")


if __name__ == "__main__":
    main()
