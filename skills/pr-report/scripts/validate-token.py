#!/usr/bin/env python3
"""Validate a token for a given PR/provider platform.

Usage:
    validate-token.py <provider> <token-or-env-ref>

The token argument may be:
    - A literal token string.
    - An environment variable reference like ${GITHUB_TOKEN} or $GITHUB_TOKEN.

Performs a lightweight validation call when a generic approach is available.
If no validation is implemented for the provider, returns:
    {"valid": null, "message": "validation not implemented"}

This script performs read-only network calls and never modifies state.
"""

import argparse
import json
import os
import re
import sys
import urllib.request

SUPPORTED_PROVIDERS = {"github", "gitlab", "azure-devops", "bitbucket"}


def _resolve_token(token_or_ref):
    """Resolve an env-var reference or literal token."""
    token_or_ref = token_or_ref.strip()
    match = re.match(r"^\$\{([^}]+)\}$|^\$([A-Za-z_][A-Za-z0-9_]*)$", token_or_ref)
    if match:
        var_name = match.group(1) or match.group(2)
        return os.environ.get(var_name), var_name
    return token_or_ref, None


def _github_validate(token):
    """Validate a GitHub token via the GraphQL viewer endpoint."""
    query = '{"query": "query { viewer { login } }"}'
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=query.encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "pr-report-validate-token",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            body = response.read().decode("utf-8", errors="ignore")
            if response.status == 200 and '"viewer"' in body:
                return True, "token authenticated successfully"
            return False, f"unexpected response: HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP error {exc.code}: authentication failed or token invalid"
    except urllib.error.URLError as exc:
        return False, f"network error: {exc.reason}"
    except Exception as exc:  # noqa: BLE001
        return False, f"validation error: {exc}"


def _gitlab_validate(token):
    """Validate a GitLab token via the user API endpoint."""
    req = urllib.request.Request(
        "https://gitlab.com/api/v4/user",
        headers={
            "PRIVATE-TOKEN": token,
            "User-Agent": "pr-report-validate-token",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                return True, "token authenticated successfully"
            return False, f"unexpected response: HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP error {exc.code}: authentication failed or token invalid"
    except urllib.error.URLError as exc:
        return False, f"network error: {exc.reason}"
    except Exception as exc:  # noqa: BLE001
        return False, f"validation error: {exc}"


def validate_token(provider, token):
    """Validate a token for the given provider."""
    provider = provider.lower().strip()

    if provider not in SUPPORTED_PROVIDERS:
        return {
            "valid": null_value(),
            "provider": provider,
            "message": "validation not implemented",
        }

    if not token:
        return {"valid": False, "provider": provider, "message": "token is empty or unset"}

    if provider == "github":
        valid, message = _github_validate(token)
    elif provider == "gitlab":
        valid, message = _gitlab_validate(token)
    else:
        return {
            "valid": null_value(),
            "provider": provider,
            "message": "validation not implemented",
        }

    return {"valid": valid, "provider": provider, "message": message}


def null_value():
    """Return a JSON null value."""
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Validate a provider token via lightweight API call."
    )
    parser.add_argument("provider", help="Provider name: github, gitlab, azure-devops, bitbucket")
    parser.add_argument(
        "token",
        help="Literal token or environment variable reference like ${TOKEN} or $TOKEN.",
    )
    args = parser.parse_args()

    token, env_var = _resolve_token(args.token)
    if env_var and token is None:
        print(
            json.dumps(
                {
                    "valid": False,
                    "provider": args.provider,
                    "message": f"environment variable {env_var} is not set",
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    result = validate_token(args.provider, token)
    print(json.dumps(result, indent=2))

    # Exit non-zero only on hard failures (network errors, empty token), not on
    # known-invalid tokens, so callers can still read {"valid": false}.
    if "validation error" in result.get("message", "") or "network error" in result.get("message", ""):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
