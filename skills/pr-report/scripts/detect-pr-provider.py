#!/usr/bin/env python3
"""Detect the PR provider from git remote URLs, environment variables, or config.

Outputs a JSON object:
    {"provider": "github|gitlab|azure-devops|bitbucket|unknown", "source": "<description>"}

Detection order:
    1. Explicit config file value.
    2. Environment variable PR_REPORT_PR_PROVIDER.
    3. Git remote URL of the current repository.
    4. Environment variables that indicate a CI/provider context.

This script is read-only and safe to run in any project.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CONFIG_CANDIDATES = [
    ".agents/config/pr-report.yaml",
    ".agents/config/shared.yaml",
]

PROVIDER_PATTERNS = {
    "github": [
        r"github\.com",
        r"github\.com[:/]",
        r"gh:\s*",
        r"^https://[^/]+github\.com/",
        r"^git@github\.com:",
    ],
    "gitlab": [
        r"gitlab\.com",
        r"gitlab\.com[:/]",
        r"^https://[^/]+gitlab\.com/",
        r"^git@gitlab\.com:",
    ],
    "azure-devops": [
        r"dev\.azure\.com",
        r"visualstudio\.com",
        r"^https://[^/]+\.visualstudio\.com/",
        r"^https://dev\.azure\.com/",
    ],
    "bitbucket": [
        r"bitbucket\.org",
        r"bitbucket\.org[:/]",
        r"^https://[^/]+bitbucket\.org/",
        r"^git@bitbucket\.org:",
    ],
}


def _classify_url(url):
    """Classify a remote URL into a provider name."""
    url_lower = url.lower()
    for provider, patterns in PROVIDER_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url_lower, re.IGNORECASE):
                return provider
    return None


def _read_config_provider():
    """Read pr_provider from known config files without heavy dependencies."""
    for candidate in CONFIG_CANDIDATES:
        path = Path(candidate)
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.exists():
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            # Look for a line like: pr_provider: github
            match = re.search(
                r"^\s*pr_provider\s*[:=]\s*['\"]?([a-z0-9-]+)['\"]?",
                text,
                re.IGNORECASE | re.MULTILINE,
            )
            if match:
                return match.group(1).lower(), str(path)
        except OSError:
            continue

    return None


def _get_git_remotes():
    """Return a list of remote URLs from the current git repository."""
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if result.returncode != 0:
            return []

        urls = []
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[1] not in urls:
                urls.append(parts[1])
        return urls
    except (OSError, subprocess.TimeoutExpired):
        return []


def _detect_from_env():
    """Check environment variables that indicate the PR provider."""
    env = os.environ

    explicit = env.get("PR_REPORT_PR_PROVIDER")
    if explicit:
        return explicit.lower(), "PR_REPORT_PR_PROVIDER environment variable"

    if env.get("GITHUB_ACTIONS") == "true" or env.get("GITHUB_TOKEN"):
        return "github", "GitHub Actions / GITHUB_TOKEN environment variable"

    if env.get("GITLAB_CI") or env.get("CI_SERVER_URL"):
        return "gitlab", "GitLab CI environment variable"

    if env.get("AZURE_DEVOPS") or env.get("SYSTEM_TEAMFOUNDATIONSERVERURI"):
        return "azure-devops", "Azure DevOps environment variable"

    if env.get("BITBUCKET_BUILD_NUMBER") or env.get("BITBUCKET_WORKSPACE"):
        return "bitbucket", "Bitbucket CI environment variable"

    return None


def detect_pr_provider(config_path=None):
    """Return (provider, source) or None."""
    # 1. Explicit config
    config_result = _read_config_provider()
    if config_result:
        return config_result

    # 2. Environment
    env_result = _detect_from_env()
    if env_result:
        return env_result

    # 3. Git remotes
    for url in _get_git_remotes():
        provider = _classify_url(url)
        if provider:
            return provider, f"git remote URL: {url}"

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Detect the PR provider from git remotes, environment, or config."
    )
    parser.add_argument(
        "--config",
        help="Path to a config file to read pr_provider from.",
    )
    args = parser.parse_args()

    result = detect_pr_provider(config_path=args.config)
    if result is None:
        output = {"provider": "unknown", "source": "no provider detected"}
    else:
        provider, source = result
        output = {"provider": provider, "source": source}

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
