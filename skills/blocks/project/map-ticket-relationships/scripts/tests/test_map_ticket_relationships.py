#!/usr/bin/env python3
"""
Tests for map-ticket-relationships.py.

Regression guards:
- multi-dot filenames (auth.guard.ts, styles.module.css) must be extracted as
  affected files; plain prose must not be over-matched.
- the behavior-complete-01 eval scenario must actually pass.
- invalid JSON and a missing ticket_key must print the standard error
  envelope to stdout and exit 2.

Run with:
    python -m pytest skills/blocks/project/map-ticket-relationships/scripts/tests/
    python skills/blocks/project/map-ticket-relationships/scripts/tests/test_map_ticket_relationships.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "map-ticket-relationships.py"


def run(payload):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.returncode, {"_raw": proc.stdout + proc.stderr}


def ticket_data(**overrides):
    base = {
        "key": "OC-4644",
        "summary": "Auth guard race condition",
        "description": "",
        "labels": [],
        "related_tickets": {},
        "dev_info": {"prs": [], "branches": [], "commits": []},
        "attachments": [],
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# affected-file extraction (regression: multi-dot filenames never matched)
# ---------------------------------------------------------------------------

def test_multi_dot_filenames_extracted(tmp_path):
    guard = tmp_path / "src" / "app" / "guards" / "auth.guard.ts"
    guard.parent.mkdir(parents=True)
    guard.write_text("// guard\n", encoding="utf-8")
    styles = tmp_path / "src" / "app" / "styles.module.css"
    styles.write_text("/* styles */\n", encoding="utf-8")
    code, out = run(
        {
            "ticket_key": "OC-4644",
            "ticket_data": ticket_data(
                description="Fix in src/app/guards/auth.guard.ts and src/app/styles.module.css."
            ),
            "codebase_root": str(tmp_path),
            "infer_by_file": True,
        }
    )
    assert code == 0
    affected = out["relationships"]["affected_files"]
    assert "src/app/guards/auth.guard.ts" in affected
    assert "src/app/styles.module.css" in affected


def test_plain_text_not_over_matched(tmp_path):
    code, out = run(
        {
            "ticket_key": "OC-4644",
            "ticket_data": ticket_data(
                description=(
                    "Login fails sometimes. Reopen the app. Then it works. "
                    "Contact the team and/or the on-call engineer. "
                    "It broke after version 1.2.3 shipped."
                )
            ),
            "codebase_root": str(tmp_path),
            "infer_by_file": True,
        }
    )
    assert code == 0
    assert out["relationships"]["affected_files"] == []


# ---------------------------------------------------------------------------
# eval behavior-complete-01 scenario must pass
# ---------------------------------------------------------------------------

def test_eval_behavior_complete_scenario_passes(tmp_path):
    guard = tmp_path / "src" / "app" / "guards" / "auth.guard.ts"
    guard.parent.mkdir(parents=True)
    guard.write_text("// guard\n", encoding="utf-8")
    code, out = run(
        {
            "ticket_key": "OC-4644",
            "ticket_data": ticket_data(
                description="Fix in src/app/guards/auth.guard.ts",
                related_tickets={"parent": "OC-4000", "linked": ["OC-4500"]},
            ),
            "codebase_root": str(tmp_path),
            "infer_by_file": True,
        }
    )
    assert code == 0
    rel = out["relationships"]
    assert rel["parent"] == "OC-4000"
    assert "OC-4500" in rel["linked"]
    assert "src/app/guards/auth.guard.ts" in rel["affected_files"]


# ---------------------------------------------------------------------------
# input validation and exit codes
# ---------------------------------------------------------------------------

def test_invalid_json_exit_2():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input="not json",
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    out = json.loads(proc.stdout)
    assert out["status"] == "error"
    assert isinstance(out["errors"], list) and out["errors"]


def test_missing_ticket_key_exit_2():
    code, out = run({"ticket_data": ticket_data()})
    assert code == 2
    assert out["status"] == "error"
    assert any("ticket_key" in e for e in out["errors"])


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        if "tmp_path" in test.__code__.co_varnames:
            with tempfile.TemporaryDirectory() as inner:
                test(Path(inner))
        else:
            test()
    print(f"All {len(tests)} tests passed.")


if __name__ == "__main__":
    main()
