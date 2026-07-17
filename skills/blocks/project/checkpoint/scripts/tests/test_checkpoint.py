#!/usr/bin/env python3
"""
Tests for checkpoint.py.

Round-trip tests are the regression guard for owner-section data loss:
arbitrary `##` sections an owner adds must survive every subsequent update.

Run with:
    python -m pytest skills/blocks/project/checkpoint/scripts/tests/
    python skills/blocks/project/checkpoint/scripts/tests/test_checkpoint.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "checkpoint.py"


def run(payload: dict):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.returncode, {"_raw": proc.stdout + proc.stderr}


def create(state: Path, phases=("research", "implement", "verify")):
    return run({
        "operation": "create", "state_path": str(state),
        "owner": "test-skill", "key": "OC-1", "phases": list(phases),
    })


# ---------------------------------------------------------------------------
# owner sections (regression: silent loss)
# ---------------------------------------------------------------------------

def test_owner_sections_survive_unrelated_updates(tmp_path):
    state = tmp_path / "state.md"
    create(state)
    run({"operation": "update", "state_path": str(state),
         "owner_sections": "My notes.\n\n## Custom Analysis\nThis must survive."})
    run({"operation": "update", "state_path": str(state), "completed_phase": "research"})
    run({"operation": "update", "state_path": str(state), "current_focus": "implement"})
    text = state.read_text(encoding="utf-8")
    assert "My notes." in text
    assert "## Custom Analysis" in text
    assert "This must survive." in text


def test_extra_sections_survive_owner_replacement(tmp_path):
    state = tmp_path / "state.md"
    create(state)
    run({"operation": "update", "state_path": str(state),
         "owner_sections": "v1 notes\n\n## Decisions\nChose A over B."})
    # Replace the owner blob; the standalone ## section must persist.
    run({"operation": "update", "state_path": str(state), "owner_sections": "v2 notes"})
    text = state.read_text(encoding="utf-8")
    assert "v2 notes" in text
    assert "## Decisions" in text
    assert "Chose A over B." in text


def test_resume_returns_owner_and_extra_sections(tmp_path):
    state = tmp_path / "state.md"
    create(state)
    run({"operation": "update", "state_path": str(state),
         "owner_sections": "notes\n\n## Custom\nextra content"})
    _, out = run({"operation": "resume", "state_path": str(state)})
    assert "notes" in out["owner_sections"]
    extras = dict(out.get("extra_sections") or [])
    assert "Custom" in extras


# ---------------------------------------------------------------------------
# core flow
# ---------------------------------------------------------------------------

def test_create_update_resume_roundtrip(tmp_path):
    state = tmp_path / "state.md"
    code, _ = create(state)
    assert code == 0
    run({"operation": "update", "state_path": str(state),
         "completed_phase": "research", "in_progress_phase": "implement",
         "last_action": "finished research"})
    _, out = run({"operation": "resume", "state_path": str(state)})
    assert out["completed_phases"] == ["research"]
    assert out["in_progress_phase"] == "implement"
    assert out["next_pending_phase"] == "verify"


def test_create_refuses_overwrite(tmp_path):
    state = tmp_path / "state.md"
    create(state)
    code, out = create(state)
    assert code == 1
    assert out["status"] == "blocked"


def test_validate_state(tmp_path):
    state = tmp_path / "state.md"
    create(state)
    code, out = run({"operation": "validate", "state_path": str(state)})
    assert code == 0
    assert out["valid"] is True


def test_history_pruning_archives(tmp_path):
    state = tmp_path / "state.md"
    create(state)
    for i in range(5):
        run({"operation": "update", "state_path": str(state),
             "last_action": f"action {i}", "max_history_rows": 3})
    text = state.read_text(encoding="utf-8")
    assert "action 4" in text and "action 0" not in text
    archive = Path(f"{state}.history.md")
    assert archive.exists()
    assert "action 0" in archive.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# input validation
# ---------------------------------------------------------------------------

def test_invalid_max_history_rows_exit_2(tmp_path):
    state = tmp_path / "state.md"
    create(state)
    code, out = run({"operation": "update", "state_path": str(state), "max_history_rows": "abc"})
    assert code == 2
    assert "max_history_rows" in out["errors"][0]


def test_missing_state_path_exit_2():
    code, out = run({"operation": "resume"})
    assert code == 2


def test_unknown_operation_exit_2():
    code, out = run({"operation": "explode"})
    assert code == 2


def test_invalid_json_exit_2():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        input="not json", capture_output=True, text=True,
    )
    assert proc.returncode == 2


def test_missing_state_file_fails_closed(tmp_path):
    code, out = run({"operation": "resume", "state_path": str(tmp_path / "nope.md")})
    assert code == 1
    assert "not found" in out["errors"][0]


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    with tempfile.TemporaryDirectory() as tmp:
        for test in tests:
            with tempfile.TemporaryDirectory() as inner:
                test(Path(inner))
        print(f"All {len(tests)} tests passed.")


if __name__ == "__main__":
    main()
