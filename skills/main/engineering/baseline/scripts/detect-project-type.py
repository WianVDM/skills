#!/usr/bin/env python3
"""Detect the project type of the current working directory.

Inspects well-known files and directories to classify the project as one of:
    web-app, api-service, library, mobile-app, or unknown.

Outputs JSON:
    {"project_type": "...", "confidence": "high|medium|low", "source": "..."}

The script is read-only, deterministic, and safe to run in any project.
"""

import json
import re
import sys
from pathlib import Path


FRONTEND_DEPS = {
    "react",
    "react-dom",
    "vue",
    "@vue/runtime-dom",
    "@angular/core",
    "@angular/common",
    "svelte",
    "solid-js",
    "preact",
    "next",
    "nuxt",
    "vite",
    "@vitejs/plugin-react",
    "@vitejs/plugin-vue",
    "webpack",
    "parcel",
    "html-webpack-plugin",
}

BACKEND_DEPS = {
    "express",
    "fastify",
    "koa",
    "@nestjs/core",
    "hapi",
    "restify",
    "sails",
    "connect",
    "fastify",
    "flask",
    "fastapi",
    "django",
    "tornado",
    "bottle",
    "pyramid",
}

PYTHON_BACKEND_FRAMEWORKS = [
    "flask",
    "fastapi",
    "django",
    "tornado",
    "bottle",
    "pyramid",
]

GO_HTTP_INDICATORS = [
    "net/http",
    "github.com/gin-gonic/gin",
    "github.com/labstack/echo",
    "github.com/gorilla/mux",
    "github.com/go-chi/chi",
    "github.com/fasthttp",
]


def _exists_any(cwd: Path, names):
    """Return the first existing path from a list of candidate names."""
    for name in names:
        if (cwd / name).exists():
            return name
    return None


def _read_text(path: Path) -> str:
    """Read text safely, returning an empty string on failure."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _load_package_json(cwd: Path):
    """Load package.json and return a dependency name set, or None."""
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


def _has_html_entry(cwd: Path) -> bool:
    """Check for an HTML entry point commonly used by web apps."""
    candidates = [
        "index.html",
        "public/index.html",
        "src/index.html",
        "static/index.html",
    ]
    return _exists_any(cwd, candidates) is not None


def _has_frontend_files(cwd: Path) -> bool:
    """Check for typical frontend source files."""
    frontend_exts = {".jsx", ".tsx", ".vue", ".svelte", ".html"}
    # Only look in the root and one level of subdirectories to stay cheap.
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
    """Scan a limited number of Go files for main package or HTTP imports."""
    go_files = sorted(cwd.rglob("*.go"))
    for path in go_files[:200]:  # bounded for determinism and performance
        text = _read_text(path)
        if "package main" in text:
            return True
        if any(indicator in text for indicator in GO_HTTP_INDICATORS):
            return True
    return False


def _detect_mobile(cwd: Path):
    """Detect mobile app indicators."""
    mobile_files = ["pubspec.yaml", "Podfile", "AppDelegate.swift", "AppDelegate.m", "AppDelegate.mm"]
    mobile_dirs = ["android", "ios"]
    source = _exists_any(cwd, mobile_files)
    if source:
        return "mobile-app", "high", f"mobile indicator file: {source}"
    source = _exists_any(cwd, mobile_dirs)
    if source:
        return "mobile-app", "high", f"mobile indicator directory: {source}/"
    return None


def _detect_web_or_api(cwd: Path, deps: set):
    """Detect web-app or api-service from Node.js project."""
    has_html = _has_html_entry(cwd) or _has_frontend_files(cwd)
    has_frontend = bool(deps & FRONTEND_DEPS)
    has_backend = bool(deps & BACKEND_DEPS)

    if has_html or has_frontend:
        return "web-app", "high", "package.json with HTML entry or frontend dependencies"
    if has_backend:
        return "api-service", "high", "package.json with backend dependencies"
    return None


def _detect_python(cwd: Path):
    """Detect Python project type."""
    python_files = ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg"]
    source = _exists_any(cwd, python_files)
    if not source:
        return None

    text = ""
    for name in python_files:
        text += _read_text(cwd / name).lower()

    if any(fw in text for fw in PYTHON_BACKEND_FRAMEWORKS):
        return "api-service", "medium", "Python project with backend framework"
    return "library", "low", "Python project without clear backend indicators"


def _detect_go(cwd: Path):
    """Detect Go project type."""
    if not (cwd / "go.mod").exists():
        return None
    if _go_has_main_or_http(cwd):
        return "api-service", "medium", "Go module with main package or HTTP imports"
    return "library", "low", "Go module without main package or HTTP imports"


def detect_project_type(cwd: Path = None):
    """Return (project_type, confidence, source) for the given directory."""
    if cwd is None:
        cwd = Path.cwd()

    result = _detect_mobile(cwd)
    if result:
        return result

    deps = _load_package_json(cwd)
    if deps is not None:
        result = _detect_web_or_api(cwd, deps)
        if result:
            return result
        return "library", "medium", "package.json without clear frontend/backend signals"

    result = _detect_python(cwd)
    if result:
        return result

    result = _detect_go(cwd)
    if result:
        return result

    return "unknown", "low", "no recognized project indicators"


def main():
    try:
        project_type, confidence, source = detect_project_type()
        output = {
            "project_type": project_type,
            "confidence": confidence,
            "source": source,
        }
        print(json.dumps(output, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
