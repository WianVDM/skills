#!/usr/bin/env python3
"""
Tests for research-ticket.py.

Regression guards:
- the Jira request must ask for `issuetype` and `development`, and the
  normalizer must map them (previously `issue_type` was always "" and Jira
  could never return `status: complete` because the development gap note
  forced `partial`);
- acceptance-criteria inference must accept both the markdown heading form
  (`## Acceptance Criteria`) and the label form (`Acceptance Criteria:`);
- invalid JSON on stdin must print the error envelope to stdout and exit 2.

The HTTP layer is stubbed; no network calls are made.

Run with:
    python -m pytest skills/blocks/project/research-ticket/scripts/tests/
    python skills/blocks/project/research-ticket/scripts/tests/test_research_ticket.py
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "research-ticket.py"

_spec = importlib.util.spec_from_file_location("research_ticket", SCRIPT)
rt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rt)


def run_stdin(raw: str):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=raw,
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# HTTP stub
# ---------------------------------------------------------------------------

class _FakeResponse:
    def __init__(self, payload):
        self._body = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _jira_issue():
    return {
        "key": "OC-1",
        "fields": {
            "summary": "Auth guard race condition",
            "description": "## Acceptance Criteria\n- first works\n- second works\n\n## Notes\n- not a criterion",
            "status": {"name": "In Progress"},
            "priority": {"name": "High"},
            "issuetype": {"name": "Bug"},
            "assignee": {"displayName": "Ada"},
            "reporter": {"displayName": "Grace"},
            "labels": ["auth"],
            "components": [{"name": "Frontend"}],
            "created": "2026-07-01T10:00:00Z",
            "updated": "2026-07-03T08:42:00Z",
            "development": {
                "pullRequests": [{"url": "https://github.com/org/repo/pull/42"}],
                "branches": [{"name": "feature/OC-1"}],
                "commits": [{"id": "abc123"}],
            },
            "comment": {"comments": []},
            "attachment": [],
            "issuelinks": [],
            "subtasks": [],
            "worklog": {"worklogs": []},
        },
        "changelog": {"histories": []},
    }


# ---------------------------------------------------------------------------
# Jira normalization and requested fields (defects A and B)
# ---------------------------------------------------------------------------

def test_normalize_jira_maps_issuetype():
    result = rt.normalize_jira(_jira_issue(), ["core"], {})
    assert result["ticket"]["issue_type"] == "Bug"


def test_jira_adapter_requests_issuetype_and_development():
    captured = {}

    def fake_urlopen(req, timeout=0):
        captured["url"] = req.full_url
        return _FakeResponse(_jira_issue())

    original_urlopen = rt.urlopen
    saved_env_value = os.environ.get("JIRA_API_TOKEN")
    rt.urlopen = fake_urlopen
    os.environ["JIRA_API_TOKEN"] = "test-token"
    try:
        result = rt.jira_adapter(
            "OC-1",
            {"server_url": "https://jira.example.com", "token_env": "JIRA_API_TOKEN"},
            list(rt.DEFAULT_SCOPE),
        )
    finally:
        rt.urlopen = original_urlopen
        if saved_env_value is None:
            del os.environ["JIRA_API_TOKEN"]
        else:
            os.environ["JIRA_API_TOKEN"] = saved_env_value

    assert "issuetype" in captured["url"]
    assert "development" in captured["url"]
    assert result["status"] == "complete"
    assert result["ticket"]["issue_type"] == "Bug"
    assert result["dev_info"]["prs"] == ["https://github.com/org/repo/pull/42"]
    assert result["dev_info"]["branches"] == ["feature/OC-1"]
    assert result["dev_info"]["commits"] == ["abc123"]
    assert result["gaps"] == []


# ---------------------------------------------------------------------------
# acceptance-criteria inference (defect C)
# ---------------------------------------------------------------------------

def test_ac_markdown_heading_form():
    desc = "Some description.\n\n## Acceptance Criteria\n- first works\n- second works\n\n## Notes\n- not a criterion\n"
    assert rt.infer_acceptance_criteria(desc) == ["first works", "second works"]


def test_ac_markdown_heading_short_form():
    desc = "## AC\n* user can log in\n* errors are shown\n"
    assert rt.infer_acceptance_criteria(desc) == ["user can log in", "errors are shown"]


def test_ac_colon_form_still_works():
    desc = "Acceptance Criteria:\n- one\n- two\n\n## Other\n- ignored\n"
    assert rt.infer_acceptance_criteria(desc) == ["one", "two"]


# ---------------------------------------------------------------------------
# input validation and exit codes (defect D)
# ---------------------------------------------------------------------------

def test_invalid_json_exit_2():
    proc = run_stdin("not json")
    assert proc.returncode == 2
    out = json.loads(proc.stdout)
    assert out["status"] == "error"
    assert out["errors"]


def test_non_object_json_exit_2():
    proc = run_stdin("[1, 2, 3]")
    assert proc.returncode == 2
    assert json.loads(proc.stdout)["status"] == "error"


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
    print(f"All {len(tests)} tests passed.")


if __name__ == "__main__":
    main()
