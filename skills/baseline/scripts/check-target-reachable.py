#!/usr/bin/env python3
"""Check whether a target URL or file path is reachable.

Accepts a --url argument. For HTTP(S) URLs, performs a lightweight HEAD request
with a GET fallback. For file paths, checks existence.

Outputs JSON:
    {"reachable": true|false, "status": 200, "message": "..."}

The script is read-only, deterministic, and safe to run in any project.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_TIMEOUT = 10
USER_AGENT = "baseline-reachable-check/1.0"


def _check_http(url: str) -> dict:
    """Perform a lightweight HTTP reachability check."""
    def request(method: str):
        req = urllib.request.Request(
            url,
            method=method,
            headers={"User-Agent": USER_AGENT},
        )
        return urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT)

    try:
        with request("HEAD") as resp:
            status = resp.status
            return {
                "reachable": 200 <= status < 400,
                "status": status,
                "message": "HEAD request succeeded",
            }
    except urllib.error.HTTPError as exc:
        # Some servers do not allow HEAD; fall back to GET.
        if exc.code == 405:
            try:
                with request("GET") as resp:
                    status = resp.status
                    return {
                        "reachable": 200 <= status < 400,
                        "status": status,
                        "message": "GET request succeeded (HEAD not allowed)",
                    }
            except urllib.error.HTTPError as get_exc:
                return {
                    "reachable": False,
                    "status": get_exc.code,
                    "message": f"HTTP error: {get_exc.reason}",
                }
            except Exception as get_exc:
                return {
                    "reachable": False,
                    "status": 0,
                    "message": f"GET request failed: {get_exc}",
                }
        return {
            "reachable": False,
            "status": exc.code,
            "message": f"HTTP error: {exc.reason}",
        }
    except urllib.error.URLError as exc:
        return {
            "reachable": False,
            "status": 0,
            "message": f"URL error: {exc.reason}",
        }
    except Exception as exc:
        return {
            "reachable": False,
            "status": 0,
            "message": f"HEAD request failed: {exc}",
        }


def _check_file(target: str) -> dict:
    """Check whether a file path exists."""
    path = Path(target)
    if path.exists():
        return {
            "reachable": True,
            "status": 0,
            "message": f"path exists: {target}",
        }
    return {
        "reachable": False,
        "status": 0,
        "message": f"path not found: {target}",
    }


def check_target_reachable(url: str) -> dict:
    """Dispatch to the appropriate reachability checker."""
    stripped = url.strip()
    if not stripped:
        return {"reachable": False, "status": 0, "message": "target is empty"}

    if stripped.startswith(("http://", "https://")):
        return _check_http(stripped)

    # Treat as a file path
    return _check_file(stripped)


def main():
    parser = argparse.ArgumentParser(
        description="Check whether a target URL or file path is reachable."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="The URL or file path to check.",
    )
    args = parser.parse_args()

    result = check_target_reachable(args.url)
    print(json.dumps(result, indent=2))

    # Exit non-zero for hard failures only, not for unreachable targets.
    if "error" in result:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
