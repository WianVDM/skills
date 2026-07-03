#!/usr/bin/env python3
"""Detect available CI gates and tools for the current project.

Inspects the project to decide which gates can be executed and which adapters
or commands are available for each. The script is read-only, deterministic, and
safe to run in any project.

Outputs JSON:
    {
      "project_type": "web-app",
      "sources": { ... },
      "gates": {
        "test": { "available": true, "confidence": "high", "commands": [...] },
        "spec-coverage": { "available": true, "confidence": "medium", ... },
        "standards": { "available": false, "confidence": "low", ... },
        "static-analysis": { "available": true, "confidence": "medium", "sub_gates": {...} }
      }
    }

Usage:
    python detect-gates.py
    python detect-gates.py --cwd /path/to/project
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Priority order for selecting the best package.json test script.
TEST_SCRIPT_PRIORITY = [
    "test:ci",
    "test-headless",
    "test:unit",
    "test:unit:ci",
    "test",
]

TEST_KEYWORDS = [
    "test", "tests", "jest", "vitest", "mocha", "jasmine", "karma",
    "pytest", "py.test", "unittest", "go test", "cargo test", "mvn test",
    "gradle test", "dotnet test", "npm test", "yarn test", "pnpm test",
]

SHELL_NOISE_PREFIXES = (
    "echo ", "printf ", "if ", "elif ", "else", "fi", "then ",
    "for ", "while ", "done ", "case ", "esac", "export ", "set ",
    "unset ", "local ", "declare ", "typeset ",
)

FRONTEND_DEPS = {
    "react", "react-dom", "vue", "@vue/runtime-dom", "@angular/core",
    "@angular/common", "svelte", "solid-js", "preact", "next", "nuxt",
    "vite", "@vitejs/plugin-react", "@vitejs/plugin-vue", "webpack", "parcel",
    "html-webpack-plugin",
}

BACKEND_DEPS = {
    "express", "fastify", "koa", "@nestjs/core", "hapi", "restify", "sails",
    "connect", "flask", "fastapi", "django", "tornado", "bottle", "pyramid",
}

PYTHON_BACKEND_FRAMEWORKS = [
    "flask", "fastapi", "django", "tornado", "bottle", "pyramid",
]

GO_HTTP_INDICATORS = [
    "net/http", "github.com/gin-gonic/gin", "github.com/labstack/echo",
    "github.com/gorilla/mux", "github.com/go-chi/chi", "github.com/fasthttp",
]

STATIC_ANALYSIS_ADAPTERS = {
    "dead-code": {
        "knip": ["knip.json", "knip.jsonc", "knip.config.js", "knip.config.ts"],
        "depcheck": [".depcheckrc", ".depcheckrc.json", ".depcheckrc.js", ".depcheckrc.yaml", ".depcheckrc.yml"],
        "ts-unused": ["tsconfig.json"],
    },
    "complexity": {
        "eslint-sonarjs": [".eslintrc", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yaml", ".eslintrc.yml", "eslint.config.js", "eslint.config.mjs"],
    },
    "duplication": {
        "jscpd": [".jscpd.json", "jscpd.json"],
    },
    "security": {
        "npm-audit": ["package.json"],
        "snyk": [".snyk"],
    },
    "style": {
        "eslint": [".eslintrc", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yaml", ".eslintrc.yml", "eslint.config.js", "eslint.config.mjs"],
        "biome": ["biome.json", "biome.jsonc"],
    },
    "architecture": {
        # Architecture checks are typically project-specific.
    },
}


STANDARDS_DOC_CANDIDATES = [
    "docs/coding-standards.md",
    "docs/testing-standards.md",
    "docs/standards.md",
    "docs/development-standards.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    ".agents/AGENTS.md",
    ".agents/config/standards.yaml",
    ".agents/config/standards.yml",
]


def _read_text(path: Path) -> str:
    """Read text safely, returning an empty string on failure."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _load_json(path: Path) -> Any:
    """Load JSON safely, returning None on failure."""
    try:
        return json.loads(_read_text(path))
    except (json.JSONDecodeError, OSError):
        return None


def _exists_any(cwd: Path, names: List[str]) -> str:
    """Return the first existing path name from a list of candidates."""
    for name in names:
        if (cwd / name).exists():
            return name
    return None


def _rel_path(path: Path, cwd: Path) -> str:
    """Return a POSIX-style path relative to the cwd."""
    return str(path.relative_to(cwd)).replace("\\", "/")


def _load_package_json(cwd: Path) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Load package.json and return (scripts, deps) or (None, None) on failure."""
    path = cwd / "package.json"
    if not path.exists():
        return None, None
    data = _load_json(path)
    if data is None:
        return None, None
    scripts = data.get("scripts", {}) or {}
    deps = set(data.get("dependencies", {}).keys())
    deps.update(data.get("devDependencies", {}).keys())
    deps.update(data.get("peerDependencies", {}).keys())
    return scripts, deps


def _is_dummy_script(script: str) -> bool:
    """Return True if a script is a placeholder that does not run tests."""
    if not script:
        return True
    s = script.lower()
    return (
        'echo "error: no test specified"' in s
        or ('exit 1' in s and len(s) < 50)
        or 'echo "no test' in s
        or 'echo "not implemented"' in s
    )


def _might_hang(script: str) -> bool:
    """Return True if a script is likely to run in watch/development mode."""
    if not script:
        return False
    if re.search(r"\bng\s+test", script) and not re.search(r"--watch\s*=\s*false", script):
        return True
    if re.search(r"\bjest\s", script) and not re.search(r"--watch(All)?\s*=\s*false", script):
        return True
    return False


def _detect_project_type(cwd: Path) -> Tuple[str, str, str]:
    """Return (project_type, confidence, source) for the given directory."""
    # Mobile
    mobile_files = ["pubspec.yaml", "Podfile", "AppDelegate.swift", "AppDelegate.m", "AppDelegate.mm"]
    mobile_dirs = ["android", "ios"]
    source = _exists_any(cwd, mobile_files)
    if source:
        return "mobile-app", "high", f"mobile indicator file: {source}"
    source = _exists_any(cwd, mobile_dirs)
    if source:
        return "mobile-app", "high", f"mobile indicator directory: {source}/"

    # Node.js
    scripts, deps = _load_package_json(cwd)
    if deps is not None:
        has_html = _has_html_entry(cwd) or _has_frontend_files(cwd)
        has_frontend = bool(deps & FRONTEND_DEPS)
        has_backend = bool(deps & BACKEND_DEPS)
        if has_html or has_frontend:
            return "web-app", "high", "package.json with HTML entry or frontend dependencies"
        if has_backend:
            return "api-service", "high", "package.json with backend dependencies"
        return "library", "medium", "package.json without clear frontend/backend signals"

    # Python
    python_files = ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg"]
    source = _exists_any(cwd, python_files)
    if source:
        text = ""
        for name in python_files:
            text += _read_text(cwd / name).lower()
        if any(fw in text for fw in PYTHON_BACKEND_FRAMEWORKS):
            return "api-service", "medium", "Python project with backend framework"
        return "library", "low", "Python project without clear backend indicators"

    # Go
    if (cwd / "go.mod").exists():
        if _go_has_main_or_http(cwd):
            return "api-service", "medium", "Go module with main package or HTTP imports"
        return "library", "low", "Go module without main package or HTTP imports"

    return "unknown", "low", "no recognized project indicators"


def _has_html_entry(cwd: Path) -> bool:
    """Check for an HTML entry point commonly used by web apps."""
    candidates = ["index.html", "public/index.html", "src/index.html", "static/index.html"]
    return _exists_any(cwd, candidates) is not None


def _has_frontend_files(cwd: Path) -> bool:
    """Check for typical frontend source files in the root and one subdir level."""
    frontend_exts = {".jsx", ".tsx", ".vue", ".svelte", ".html"}
    for entry in sorted(cwd.iterdir()):
        if entry.is_file() and entry.suffix in frontend_exts:
            return True
        if entry.is_dir():
            try:
                for child in sorted(entry.iterdir()):
                    if child.is_file() and child.suffix in frontend_exts:
                        return True
            except OSError:
                continue
    return False


def _go_has_main_or_http(cwd: Path) -> bool:
    """Scan a bounded number of Go files for main package or HTTP imports."""
    go_files = sorted(cwd.rglob("*.go"))
    for path in go_files[:200]:
        text = _read_text(path)
        if "package main" in text:
            return True
        if any(indicator in text for indicator in GO_HTTP_INDICATORS):
            return True
    return False


def _detect_package_json_test_commands(cwd: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    """Detect test commands from package.json scripts and monorepo subdirectories."""
    commands = []
    sources = []
    scripts, _ = _load_package_json(cwd)
    if scripts:
        best = _pick_best_test_command(scripts)
        if best:
            commands.append({
                "name": "root",
                "cwd": ".",
                "command": f"npm run {best['scriptName']}",
                "script": best["script"],
            })
            sources.append(f"package.json script: {best['scriptName']}")

    subdir_patterns = ["server", "backend", "api", "middleware", "packages/*"]
    for pattern in subdir_patterns:
        for dir_path in _expand_pattern_dirs(cwd, pattern):
            sub_scripts, _ = _load_package_json(dir_path)
            if sub_scripts:
                sub_best = _pick_best_test_command(sub_scripts)
                if sub_best:
                    rel = _rel_path(dir_path, cwd)
                    commands.append({
                        "name": rel or ".",
                        "cwd": rel or ".",
                        "command": f"npm run {sub_best['scriptName']}",
                        "script": sub_best["script"],
                    })
                    sources.append(f"package.json script in {rel}: {sub_best['scriptName']}")
    return commands, sources


def _pick_best_test_command(scripts: Dict[str, str]) -> Dict[str, str]:
    """Pick the highest-priority non-dummy test script."""
    for candidate in TEST_SCRIPT_PRIORITY:
        script = scripts.get(candidate)
        if not script:
            continue
        if _is_dummy_script(script):
            continue
        return {"scriptName": candidate, "script": script}
    return None


def _expand_pattern_dirs(cwd: Path, pattern: str) -> List[Path]:
    """Expand a directory pattern like packages/* into concrete directories."""
    if "*" not in pattern:
        candidate = cwd / pattern
        return [candidate] if candidate.is_dir() else []

    parts = pattern.split("/*")
    parent = cwd / parts[0]
    if not parent.is_dir():
        return []
    try:
        return [entry for entry in sorted(parent.iterdir()) if entry.is_dir()]
    except OSError:
        return []


def _detect_ci_test_commands(cwd: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    """Detect test commands referenced in CI configuration files."""
    commands = []
    sources = []

    github_workflows = cwd / ".github" / "workflows"
    if github_workflows.is_dir():
        try:
            for wf in sorted(github_workflows.glob("*.yml")) + sorted(github_workflows.glob("*.yaml")):
                text = _read_text(wf)
                extracted = _extract_test_commands_from_text(text)
                if extracted:
                    workflow_name = wf.stem
                    for idx, cmd in enumerate(extracted, start=1):
                        commands.append({
                            "name": f"github-workflow-{workflow_name}-{idx}",
                            "cwd": ".",
                            "command": cmd,
                        })
                    sources.append(f"GitHub workflow: {_rel_path(wf, cwd)}")
        except OSError:
            pass

    ci_files = {
        ".gitlab-ci.yml": "GitLab CI",
        "azure-pipelines.yml": "Azure Pipelines",
        "azure-pipelines.yaml": "Azure Pipelines",
        ".circleci/config.yml": "CircleCI",
        "Jenkinsfile": "Jenkins",
    }
    for filename, label in ci_files.items():
        path = cwd / filename
        if path.exists():
            text = _read_text(path)
            extracted = _extract_test_commands_from_text(text)
            if extracted:
                label_slug = label.lower().replace(" ", "-")
                for idx, cmd in enumerate(extracted, start=1):
                    commands.append({
                        "name": f"{label_slug}-{idx}",
                        "cwd": ".",
                        "command": cmd,
                    })
                sources.append(f"{label}: {filename}")

    return commands, sources


def _extract_test_commands_from_text(text: str) -> List[str]:
    """Heuristically extract likely test commands from CI YAML or Groovy text.

    Extracts actual command lines from common CI formats (GitHub Actions `run:`
    blocks, GitLab CI / Azure Pipelines `script:` list items, and Jenkins `sh`
    blocks) and filters out YAML metadata keys such as `name:` or `runs-on:`.
    """
    commands = []
    block_scalar_indicators = {"|", ">", "|-", ">-", "|+", ">+"}
    lines = text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        # GitHub Actions / CircleCI run: command or run: | block
        run_match = re.match(r"^(\s*)run:\s*(.*)$", line)
        if run_match:
            run_indent = len(run_match.group(1))
            content = run_match.group(2).strip()
            if content in block_scalar_indicators:
                # Block scalar: collect following indented lines
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if not next_line.strip():
                        i += 1
                        continue
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent > run_indent:
                        next_stripped = next_line.strip()
                        if next_stripped and not next_stripped.startswith("#"):
                            commands.append(next_stripped)
                        i += 1
                    else:
                        break
                continue
            elif content and not _is_metadata_line(content):
                commands.append(content)
            i += 1
            continue

        # List items (GitLab CI / Azure Pipelines script steps, CircleCI command)
        item_match = re.match(r"^\s*-\s*(.*)$", line)
        if item_match:
            content = item_match.group(1).strip()
            if content and not _is_metadata_line(content):
                commands.append(content)
            i += 1
            continue

        # Jenkins sh '...' / sh "..." blocks
        jenkins_match = re.search(r"\bsh\s+['\"](.+?)['\"]", line)
        if jenkins_match:
            commands.append(jenkins_match.group(1))

        i += 1

    # Filter out shell-only noise (echo, if/fi, etc.) then test-related commands
    commands = [cmd for cmd in commands if not _is_shell_noise(cmd)]
    test_commands = [
        cmd for cmd in commands
        if any(_is_test_command_keyword(kw, cmd) for kw in TEST_KEYWORDS)
    ]

    return list(dict.fromkeys(test_commands))[:20]  # dedupe, bounded


def _is_metadata_line(line: str) -> bool:
    """Return True if a line is a YAML/Jenkins metadata key, not a command."""
    metadata_keys = {
        "name", "uses", "needs", "with", "if", "env", "runs-on", "on",
        "jobs", "steps", "defaults", "strategy", "matrix", "branches",
        "permissions", "concurrency", "container", "services", "outputs",
        "description", "group", "working-directory", "shell", "timeout-minutes",
        "continue-on-error", "fail-fast", "max-parallel", "type", "stage",
        "when", "only", "except", "allow_failure", "artifacts", "cache",
        "variables", "image", "before_script", "after_script", "parameters",
        "trigger", "include", "extends", "dependencies", "resource_pool",
    }
    match = re.match(r"^([a-zA-Z0-9_-]+)\s*:", line)
    if match and match.group(1).lower() in metadata_keys:
        return True
    return False


def _is_shell_noise(command: str) -> bool:
    """Return True for shell-only lines that are not test commands."""
    cmd_lower = command.strip().lower()
    return any(cmd_lower.startswith(prefix) for prefix in SHELL_NOISE_PREFIXES)


def _is_test_command_keyword(keyword: str, command: str) -> bool:
    """Return True if keyword appears as a test-related term in the command.

    Handles whole-word and known-tool matching while avoiding matches inside
    unrelated words like "testing" or "testimonial" when possible.
    """
    command_lower = command.lower()
    if keyword in command_lower:
        if keyword == "test":
            return bool(re.search(r"(?:^|[\s\-:])test(?:[\s\-:]|$)", command_lower))
        return True
    return False


def _detect_task_runner_test_commands(cwd: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    """Detect test targets from Makefile, justfile, and Taskfile.yml."""
    commands = []
    sources = []

    # Makefile
    make_path = cwd / "Makefile"
    if make_path.exists():
        targets = _parse_makefile_targets(make_path)
        test_targets = [t for t in targets if any(kw in t.lower() for kw in TEST_KEYWORDS)]
        if test_targets:
            for target in test_targets[:10]:
                commands.append({
                    "name": f"make-{target}",
                    "cwd": ".",
                    "command": f"make {target}",
                })
            sources.append(f"Makefile targets: {', '.join(test_targets[:5])}")

    # justfile
    just_path = cwd / "justfile"
    if just_path.exists():
        targets = _parse_justfile_targets(just_path)
        test_targets = [t for t in targets if any(kw in t.lower() for kw in TEST_KEYWORDS)]
        if test_targets:
            for target in test_targets[:10]:
                commands.append({
                    "name": f"just-{target}",
                    "cwd": ".",
                    "command": f"just {target}",
                })
            sources.append(f"justfile targets: {', '.join(test_targets[:5])}")

    # Taskfile.yml / Taskfile.yaml
    taskfile_path = None
    for name in ["Taskfile.yml", "Taskfile.yaml"]:
        if (cwd / name).exists():
            taskfile_path = cwd / name
            break
    if taskfile_path:
        targets = _parse_taskfile_targets(taskfile_path)
        test_targets = [t for t in targets if any(kw in t.lower() for kw in TEST_KEYWORDS)]
        if test_targets:
            for target in test_targets[:10]:
                commands.append({
                    "name": f"task-{target}",
                    "cwd": ".",
                    "command": f"task {target}",
                })
            sources.append(f"Taskfile targets: {', '.join(test_targets[:5])}")

    return commands, sources


def _parse_makefile_targets(path: Path) -> List[str]:
    """Parse target names from a Makefile."""
    targets = []
    target_re = re.compile(r"^([a-zA-Z0-9_.-]+)\s*:")
    for line in _read_text(path).splitlines():
        match = target_re.match(line)
        if match and not line.startswith("\t"):
            targets.append(match.group(1))
    return targets


def _parse_justfile_targets(path: Path) -> List[str]:
    """Parse recipe names from a justfile."""
    targets = []
    recipe_re = re.compile(r"^([a-zA-Z0-9_-]+)\s*[:@\[]")
    for line in _read_text(path).splitlines():
        match = recipe_re.match(line)
        if match:
            targets.append(match.group(1))
    return targets


def _parse_taskfile_targets(path: Path) -> List[str]:
    """Parse task names from a Taskfile YAML."""
    targets = []
    task_re = re.compile(r"^\s+([a-zA-Z0-9_-]+):\s*$")
    in_tasks = False
    for line in _read_text(path).splitlines():
        if line.strip() == "tasks:":
            in_tasks = True
            continue
        if in_tasks:
            # Heuristic: tasks are indented under the top-level tasks key
            match = task_re.match(line)
            if match and not line.strip().startswith("#"):
                targets.append(match.group(1))
    return targets


def _detect_python_test_commands(cwd: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    """Detect Python test commands from project files."""
    commands = []
    sources = []
    pyproject = cwd / "pyproject.toml"
    if pyproject.exists():
        text = _read_text(pyproject).lower()
        if "pytest" in text or "[tool.pytest" in text:
            commands.append({"name": "python-pytest", "cwd": ".", "command": "pytest"})
            sources.append("pyproject.toml: pytest")
    pytest_ini = cwd / "pytest.ini"
    if pytest_ini.exists():
        commands.append({"name": "python-pytest", "cwd": ".", "command": "pytest"})
        sources.append("pytest.ini")
    setup_py = cwd / "setup.py"
    if setup_py.exists():
        text = _read_text(setup_py).lower()
        if "pytest" in text or "unittest" in text:
            commands.append({"name": "python-pytest", "cwd": ".", "command": "python -m pytest"})
            sources.append("setup.py")
    return commands, sources


def _detect_go_test_commands(cwd: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    """Detect Go test commands."""
    if (cwd / "go.mod").exists():
        return [{"name": "go-test", "cwd": ".", "command": "go test ./..."}], ["go.mod"]
    return [], []


def _detect_rust_test_commands(cwd: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    """Detect Rust test commands."""
    if (cwd / "Cargo.toml").exists():
        return [{"name": "cargo-test", "cwd": ".", "command": "cargo test"}], ["Cargo.toml"]
    return [], []


def _detect_test_gate(cwd: Path) -> Dict[str, Any]:
    """Detect the test gate availability and commands."""
    all_commands = []
    all_sources = []

    pkg_commands, pkg_sources = _detect_package_json_test_commands(cwd)
    all_commands.extend(pkg_commands)
    all_sources.extend(pkg_sources)

    ci_commands, ci_sources = _detect_ci_test_commands(cwd)
    all_commands.extend(ci_commands)
    all_sources.extend(ci_sources)

    task_commands, task_sources = _detect_task_runner_test_commands(cwd)
    all_commands.extend(task_commands)
    all_sources.extend(task_sources)

    py_commands, py_sources = _detect_python_test_commands(cwd)
    all_commands.extend(py_commands)
    all_sources.extend(py_sources)

    go_commands, go_sources = _detect_go_test_commands(cwd)
    all_commands.extend(go_commands)
    all_sources.extend(go_sources)

    rust_commands, rust_sources = _detect_rust_test_commands(cwd)
    all_commands.extend(rust_commands)
    all_sources.extend(rust_sources)

    if all_commands:
        # Normalize entries to have at least name and command
        normalized = []
        for cmd in all_commands:
            name = cmd.get("name") or cmd.get("command", "").split()[0] or "detected"
            normalized.append({
                "name": name,
                "cwd": cmd.get("cwd", "."),
                "command": cmd.get("command", cmd.get("script", "")),
            })
        return {
            "available": True,
            "confidence": "high" if pkg_commands else "medium",
            "commands": normalized,
        }

    return {
        "available": False,
        "confidence": "low",
        "reason": "no test commands detected in package.json, CI configs, task runners, or project files",
        "suggested_sources": ["package.json", ".github/workflows/*.yml", "Makefile", "justfile", "Taskfile.yml"],
    }


def _detect_spec_coverage_gate(cwd: Path) -> Dict[str, Any]:
    """Detect the spec-coverage gate based on common project layouts."""
    sources = []
    mappings = []

    common_layouts = [
        ("src/**", "tests/**/*.test.{js,ts,jsx,tsx}", "js/ts tests"),
        ("src/**", "src/**/*.test.{js,ts,jsx,tsx}", "co-located js/ts tests"),
        ("src/**", "__tests__/**/*.{js,ts,jsx,tsx}", "__tests__ layout"),
        ("src/**", "spec/**/*.spec.{js,ts}", "spec layout"),
        ("*.py", "tests/**/*.py", "python tests"),
        ("src/**/*.py", "tests/**/*.py", "python src/tests"),
        ("*.go", "*_test.go", "go tests"),
    ]

    for source_pattern, spec_pattern, label in common_layouts:
        if _pattern_matches_files(cwd, source_pattern, spec_pattern):
            mappings.append({
                "source_pattern": source_pattern,
                "spec_pattern": spec_pattern,
                "area": label,
            })
            sources.append(label)

    if mappings:
        return {
            "available": True,
            "confidence": "medium",
            "suggested_mappings": mappings,
        }

    return {
        "available": False,
        "confidence": "low",
        "reason": "no common source/spec layout detected",
        "suggested_mappings": [
            {"source_pattern": "src/**", "spec_pattern": "tests/**/*.test.{js,ts}", "area": "frontend"},
            {"source_pattern": "*.py", "spec_pattern": "tests/**/*.py", "area": "backend"},
        ],
    }


def _pattern_matches_files(cwd: Path, source_pattern: str, spec_pattern: str) -> bool:
    """Heuristically check whether source and spec patterns have matching files."""
    # Simplified glob matching: look for any files with the given extensions/prefixes.
    source_ext = _extract_extension_from_pattern(source_pattern)
    spec_ext = _extract_extension_from_pattern(spec_pattern)
    if not spec_ext:
        return False

    # Find any file matching the spec extension under root and one level of subdirs.
    spec_dirs = ["tests", "test", "__tests__", "spec", "specs"]
    for dir_name in spec_dirs:
        d = cwd / dir_name
        if d.is_dir():
            if _find_files_with_extension(d, spec_ext, max_files=5):
                return True
    # Co-located specs
    if _find_files_with_extension(cwd, spec_ext, max_files=5):
        return True
    return False


def _extract_extension_from_pattern(pattern: str) -> str:
    """Extract a concrete extension like .js from a glob pattern."""
    match = re.search(r"\{([a-z,]+)\}", pattern)
    if match:
        extensions = match.group(1).split(",")
        return f".{extensions[0]}"
    match = re.search(r"\*\_test\.(\w+)", pattern)
    if match:
        return f".{match.group(1)}"
    match = re.search(r"\.(\w+)$", pattern)
    if match:
        return f".{match.group(1)}"
    return ""


def _find_files_with_extension(cwd: Path, ext: str, max_files: int = 5) -> bool:
    """Return True if at least one file with the given extension exists (bounded)."""
    count = 0
    for entry in sorted(cwd.iterdir()):
        if entry.is_file() and entry.suffix == ext:
            return True
        if entry.is_dir():
            try:
                for child in sorted(entry.iterdir()):
                    if child.is_file() and child.suffix == ext:
                        return True
                    count += 1
                    if count >= max_files:
                        break
            except OSError:
                continue
    return False


def _detect_standards_gate(cwd: Path) -> Dict[str, Any]:
    """Detect standards documents and configuration."""
    sources = []
    for candidate in STANDARDS_DOC_CANDIDATES:
        path = cwd / candidate
        if not path.exists():
            continue
        if candidate in ("AGENTS.md", ".agents/AGENTS.md", "CONTRIBUTING.md"):
            text = _read_text(path).lower()
            if any(kw in text for kw in ["standard", "coding standard", "testing standard", "convention"]):
                sources.append({
                    "path": candidate,
                    "type": "markdown",
                    "confidence": "medium",
                })
        else:
            ext = path.suffix.lower()
            doc_type = "yaml" if ext in {".yaml", ".yml"} else "markdown"
            sources.append({
                "path": candidate,
                "type": doc_type,
                "confidence": "high",
            })

    if sources:
        return {
            "available": True,
            "confidence": "high" if any(s["confidence"] == "high" for s in sources) else "medium",
            "sources": sources,
        }

    return {
        "available": False,
        "confidence": "low",
        "reason": "no standards docs found",
        "suggested_sources": STANDARDS_DOC_CANDIDATES,
    }


def _detect_static_analysis_gate(cwd: Path) -> Dict[str, Any]:
    """Detect static analysis tools and sub-gates."""
    sub_gates = {}
    available_count = 0

    for sub_gate, adapters in STATIC_ANALYSIS_ADAPTERS.items():
        available_adapters = []
        for adapter_name, marker_files in adapters.items():
            if any((cwd / marker).exists() for marker in marker_files):
                available_adapters.append(adapter_name)
        if available_adapters:
            available_count += 1
        sub_gates[sub_gate] = {
            "available": bool(available_adapters),
            "adapters": available_adapters,
        }

    available = available_count > 0
    confidence = "high" if available_count >= 3 else ("medium" if available else "low")

    return {
        "available": available,
        "confidence": confidence,
        "sub_gates": sub_gates,
    }


def detect_gates(cwd: Path = None) -> Dict[str, Any]:
    """Return the full gate detection result for the given directory."""
    if cwd is None:
        cwd = Path.cwd()

    project_type, project_confidence, project_source = _detect_project_type(cwd)

    test_gate = _detect_test_gate(cwd)
    spec_gate = _detect_spec_coverage_gate(cwd)
    standards_gate = _detect_standards_gate(cwd)
    static_analysis_gate = _detect_static_analysis_gate(cwd)

    return {
        "project_type": project_type,
        "sources": {
            "project_type": {
                "confidence": project_confidence,
                "source": project_source,
            },
            "test_gate": test_gate.get("commands", []),
            "spec_coverage_gate": spec_gate.get("suggested_mappings", []),
            "standards_gate": standards_gate.get("sources", []),
            "static_analysis_gate": static_analysis_gate.get("sub_gates", {}),
        },
        "gates": {
            "test": test_gate,
            "spec-coverage": spec_gate,
            "standards": standards_gate,
            "static-analysis": static_analysis_gate,
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect available CI gates and tools for the current project."
    )
    parser.add_argument(
        "--cwd",
        help="Override the working directory to inspect. Default: current directory.",
    )
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    try:
        result = detect_gates(cwd)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
