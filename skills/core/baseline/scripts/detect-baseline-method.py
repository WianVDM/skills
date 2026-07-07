#!/usr/bin/env python3
"""Detect available baseline capture methods for the current project.

Inspects the project and the environment to decide which baseline methods are
viable: ui-browser, api-http, test-runner, code-snapshot, or manual.

Outputs JSON:
    {
      "methods": [
        {
          "method": "ui-browser|api-http|test-runner|code-snapshot|manual",
          "available": true|false,
          "confidence": "high|medium|low",
          "source": "..."
        }
      ]
    }

The script is read-only, deterministic, and safe to run in any project.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


def _read_text(path: Path) -> str:
    """Read text safely, returning an empty string on failure."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _load_package_json(cwd: Path):
    """Load package.json and return its dependency names, or None."""
    path = cwd / "package.json"
    if not path.exists():
        return None
    try:
        data = json.loads(_read_text(path))
        deps = set(data.get("dependencies", {}).keys())
        deps.update(data.get("devDependencies", {}).keys())
        deps.update(data.get("peerDependencies", {}).keys())
        return deps
    except (json.JSONDecodeError, OSError):
        return None


def _detect_mcp_files(cwd: Path):
    """Vendor-agnostic detection of MCP configuration files.

    Searches for `mcp.json` in the project root and in immediate subdirectories
    (including hidden directories such as editor/harness config folders) without
    naming specific vendors. Also checks the project-agnostic
    `.agents/config/mcp.json` convention.
    """
    mcp_files = []
    skip_dirs = {"node_modules", ".git", "dist", "build", "out"}

    for entry in sorted(cwd.iterdir()):
        if entry.is_file() and entry.name == "mcp.json":
            mcp_files.append(entry)
        elif entry.is_dir() and entry.name not in skip_dirs:
            candidate = entry / "mcp.json"
            if candidate.exists():
                mcp_files.append(candidate)
            # Project-agnostic agents config convention
            if entry.name == ".agents":
                nested = entry / "config" / "mcp.json"
                if nested.exists():
                    mcp_files.append(nested)

    return mcp_files


def _detect_ui_browser(cwd: Path):
    """Detect browser automation tooling and MCP configurations."""
    sources = []
    deps = _load_package_json(cwd) or set()

    browser_deps = {
        "playwright": "Playwright project dependency",
        "@playwright/test": "Playwright test dependency",
        "playwright-core": "Playwright core dependency",
        "cypress": "Cypress project dependency",
        "puppeteer": "Puppeteer project dependency",
        "puppeteer-core": "Puppeteer core dependency",
        "@browserbasehq/stagehand": "Stagehand project dependency",
    }
    for dep, label in browser_deps.items():
        if dep in deps:
            sources.append(label)

    config_files = {
        "playwright.config.ts": "Playwright config",
        "playwright.config.js": "Playwright config",
        "playwright.config.mjs": "Playwright config",
        "cypress.config.js": "Cypress config",
        "cypress.config.ts": "Cypress config",
    }
    for name, label in config_files.items():
        if (cwd / name).exists():
            sources.append(label)

    mcp_keywords = [
        ("playwright", "Playwright MCP config"),
        ("stagehand", "Stagehand MCP config"),
        ("puppeteer", "Puppeteer MCP config"),
        ("browser-tools", "Browser-tools MCP config"),
        ("chrome-devtools", "Chrome DevTools MCP config"),
    ]
    for mcp_path in _detect_mcp_files(cwd):
        text = _read_text(mcp_path).lower()
        for keyword, label in mcp_keywords:
            if keyword in text:
                sources.append(f"{label}: {mcp_path}")

    # Fallback: npx tooling present in the project
    if not sources and shutil.which("npx"):
        if (cwd / "node_modules" / ".bin" / "playwright").exists():
            sources.append("npx playwright available")
        if (cwd / "node_modules" / ".bin" / "cypress").exists():
            sources.append("npx cypress available")

    if sources:
        return True, "high" if len(sources) >= 2 else "medium", "; ".join(sorted(set(sources)))
    return False, "low", "no browser automation tooling or MCP config detected"


def _detect_api_http(cwd: Path):
    """Detect available HTTP clients for API baselines."""
    clients = []
    for name, label in [
        ("curl", "curl"),
        ("http", "httpie"),
        ("httpx", "httpx"),
        ("wget", "wget"),
        ("python", "Python urllib"),
    ]:
        if shutil.which(name):
            clients.append(label)

    if clients:
        return True, "high", f"HTTP client(s) available: {', '.join(sorted(set(clients)))}"

    # Check for common API description files
    api_files = ["openapi.json", "openapi.yaml", "swagger.json", "swagger.yaml"]
    for name in api_files:
        if (cwd / name).exists():
            return True, "medium", f"API description file found: {name}"

    return False, "low", "no HTTP client found in PATH and no API description file"


def _detect_test_runner(cwd: Path):
    """Detect project test runners."""
    # JavaScript / TypeScript
    deps = _load_package_json(cwd) or set()
    test_scripts = []
    if "jest" in deps or (cwd / "jest.config.js").exists() or (cwd / "jest.config.ts").exists():
        test_scripts.append("jest")
    if "vitest" in deps or (cwd / "vitest.config.js").exists() or (cwd / "vitest.config.ts").exists():
        test_scripts.append("vitest")
    if "@playwright/test" in deps or any((cwd / name).exists() for name in ["playwright.config.ts", "playwright.config.js"]):
        test_scripts.append("playwright")
    if "cypress" in deps or (cwd / "cypress.config.js").exists() or (cwd / "cypress.config.ts").exists():
        test_scripts.append("cypress")
    if "mocha" in deps:
        test_scripts.append("mocha")
    if "jasmine" in deps:
        test_scripts.append("jasmine")

    if test_scripts:
        return True, "high", f"JavaScript/TypeScript test runner(s): {', '.join(sorted(set(test_scripts)))}"

    # Python
    python_configs = ["pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini"]
    for name in python_configs:
        path = cwd / name
        if not path.exists():
            continue
        text = _read_text(path).lower()
        if "pytest" in text or "[tool.pytest" in text:
            return True, "high", f"pytest configuration found: {name}"

    # Go
    if (cwd / "go.mod").exists():
        for go_file in sorted(cwd.rglob("*_test.go"))[:50]:
            return True, "high", f"Go tests found: {go_file.relative_to(cwd)}"

    return False, "low", "no test runner configuration detected"


def _detect_code_snapshot(cwd: Path):
    """Detect whether project source files are available for code snapshot baselines."""
    source_extensions = {
        ".js", ".ts", ".jsx", ".tsx",
        ".py", ".go", ".java", ".kt", ".swift",
        ".cs", ".cpp", ".c", ".h", ".rb", ".php",
        ".rs", ".scala", ".clj", ".elm",
    }
    # Bounded walk: root and one level of subdirectories keeps it cheap.
    for entry in sorted(cwd.iterdir()):
        if entry.is_file() and entry.suffix in source_extensions:
            return True, "high", "project source files available"
        if entry.is_dir() and not entry.name.startswith("."):
            try:
                for child in sorted(entry.iterdir()):
                    if child.is_file() and child.suffix in source_extensions:
                        return True, "high", "project source files available"
            except OSError:
                continue
    return False, "low", "no recognizable source files found"


def _detect_manual():
    """Manual fallback is always available."""
    return True, "high", "user-provided fallback"


def detect_methods(cwd: Path = None):
    """Return a list of method result dicts."""
    if cwd is None:
        cwd = Path.cwd()

    available, confidence, source = _detect_ui_browser(cwd)
    methods = [
        {"method": "ui-browser", "available": available, "confidence": confidence, "source": source},
    ]

    available, confidence, source = _detect_api_http(cwd)
    methods.append(
        {"method": "api-http", "available": available, "confidence": confidence, "source": source}
    )

    available, confidence, source = _detect_test_runner(cwd)
    methods.append(
        {"method": "test-runner", "available": available, "confidence": confidence, "source": source}
    )

    available, confidence, source = _detect_code_snapshot(cwd)
    methods.append(
        {"method": "code-snapshot", "available": available, "confidence": confidence, "source": source}
    )

    available, confidence, source = _detect_manual()
    methods.append(
        {"method": "manual", "available": available, "confidence": confidence, "source": source}
    )

    return methods


def main():
    parser = argparse.ArgumentParser(
        description="Detect available baseline capture methods for the current project."
    )
    parser.add_argument(
        "--cwd",
        help="Override the working directory to inspect. Default: current directory.",
    )
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    try:
        methods = detect_methods(cwd)
        print(json.dumps({"methods": methods}, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
