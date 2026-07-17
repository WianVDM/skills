#!/usr/bin/env python3
"""
Tests for initialize.py and load-skill-config.py.

CLI behavior is tested via subprocess because exit codes and the stdin
contract are part of the interface. Pure helpers are imported directly.

Run with:
    python -m pytest skills/blocks/project/initialize-skill/scripts/tests/
    python skills/blocks/project/initialize-skill/scripts/tests/test_initialize.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parents[1]
INITIALIZE = SCRIPT_DIR / "initialize.py"
LOADER = SCRIPT_DIR / "load-skill-config.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_init(*cli, stdin: str = "", cwd: Path | None = None):
    """Run initialize.py. Returns (exit_code, parsed_json_or_none, raw_stdout)."""
    proc = subprocess.run(
        [sys.executable, str(INITIALIZE), *cli, "--json"],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    try:
        return proc.returncode, json.loads(proc.stdout), proc.stdout
    except json.JSONDecodeError:
        return proc.returncode, None, proc.stdout + proc.stderr


def run_loader(payload: dict):
    proc = subprocess.run(
        [sys.executable, str(LOADER)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    return proc.returncode, json.loads(proc.stdout)


def propose(marker: Path, skill: str, **kwargs):
    """Run a proposal and return (exit_code, report)."""
    cli = ["--marker-dir", str(marker), "--skill-name", skill]
    if "defaults" in kwargs:
        cli += ["--defaults", json.dumps(kwargs["defaults"])]
    if "skill_dir" in kwargs:
        cli += ["--skill-dir", str(kwargs["skill_dir"])]
    if "schema_version" in kwargs:
        cli += ["--schema-version", kwargs["schema_version"]]
    code, report, raw = run_init(*cli, stdin=kwargs.get("stdin", ""))
    assert report is not None, f"no JSON output: {raw}"
    return code, report


def write_config_yaml(directory: Path, body: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "config.yaml"
    path.write_text(body, encoding="utf-8")
    return directory


def make_workspace(root: Path) -> Path:
    marker = root / ".agents"
    (marker / "config").mkdir(parents=True)
    return marker


# ---------------------------------------------------------------------------
# Fail-closed and invalid input
# ---------------------------------------------------------------------------

def test_missing_marker_dir_fails_closed(tmp_path):
    code, report = propose(tmp_path / "nope", "x", defaults={"a": 1})
    assert code == 1
    assert report["status"] == "error"
    assert "detect-project-context" in report["errors"][0]
    assert not (tmp_path / "nope").exists()


def test_missing_defaults_source_is_invalid_input(tmp_path):
    marker = make_workspace(tmp_path)
    code, report = propose(marker, "x")
    assert code == 2
    assert report["status"] == "error"
    assert "skill-dir or --defaults" in report["errors"][0]


def test_invalid_defaults_json(tmp_path):
    marker = make_workspace(tmp_path)
    code, report, _ = run_init(
        "--marker-dir", str(marker), "--skill-name", "x", "--defaults", "{bad"
    )
    assert code == 2
    assert report["status"] == "error"


def test_invalid_stdin_json(tmp_path):
    marker = make_workspace(tmp_path)
    code, report, _ = run_init(
        "--marker-dir", str(marker), "--skill-name", "x", stdin="not json"
    )
    assert code == 2
    assert report["status"] == "error"


def test_stdin_approve_rejected(tmp_path):
    marker = make_workspace(tmp_path)
    payload = json.dumps({
        "marker_dir": str(marker),
        "skill_name": "x",
        "defaults": {"a": 1},
        "approve": True,
    })
    code, report, _ = run_init(stdin=payload)
    assert code == 2
    assert "approve" in report["errors"][0]
    assert not (marker / "config" / "x.yaml").exists()


def test_prefix_validation_rejects_unprefixed_nested_key(tmp_path):
    marker = make_workspace(tmp_path)
    skill_dir = write_config_yaml(
        tmp_path / "fakeskill",
        "skill:\n  - key: tools.pr.provider\n    default: auto\n",
    )
    code, report = propose(marker, "fakeskill", skill_dir=skill_dir)
    assert code == 2
    assert "tools.pr.provider" in report["errors"][0]
    assert "fakeskill." in report["errors"][0]


# ---------------------------------------------------------------------------
# Proposal and approval flow
# ---------------------------------------------------------------------------

def test_propose_does_not_write(tmp_path):
    marker = make_workspace(tmp_path)
    code, report = propose(marker, "my-skill", defaults={"timeout": 30})
    assert code == 0
    assert report["status"] == "needs_approval"
    assert report["proposal_hash"]
    assert "timeout" in report["changes"]["added"]
    assert not (marker / "config" / "my-skill.yaml").exists()


def test_approve_writes_with_correct_hash(tmp_path):
    marker = make_workspace(tmp_path)
    _, proposal = propose(marker, "my-skill", defaults={"timeout": 30})
    code, report, _ = run_init(
        "--marker-dir", str(marker), "--skill-name", "my-skill",
        "--defaults", json.dumps({"timeout": 30}),
        "--approve", proposal["proposal_hash"],
    )
    assert code == 0
    assert report["status"] == "written"
    written = yaml.safe_load((marker / "config" / "my-skill.yaml").read_text())
    assert written == {"timeout": 30}


def test_approve_rejects_stale_hash(tmp_path):
    marker = make_workspace(tmp_path)
    _, proposal = propose(marker, "my-skill", defaults={"timeout": 30})
    config = marker / "config" / "my-skill.yaml"
    config.write_text("timeout: 60\n", encoding="utf-8")
    code, report, _ = run_init(
        "--marker-dir", str(marker), "--skill-name", "my-skill",
        "--defaults", json.dumps({"timeout": 30}),
        "--approve", proposal["proposal_hash"],
    )
    assert code == 1
    assert report["status"] == "error"
    assert "proposal changed" in report["errors"][0]
    assert config.read_text() == "timeout: 60\n"


def test_shared_edit_does_not_invalidate_hash(tmp_path):
    # The hash covers write_set only; shared.yaml is a read-only layer.
    marker = make_workspace(tmp_path)
    _, proposal = propose(marker, "my-skill", defaults={"timeout": 30})
    (marker / "config" / "shared.yaml").write_text("agents:\n  context_dir: .agents/context\n")
    code, report, _ = run_init(
        "--marker-dir", str(marker), "--skill-name", "my-skill",
        "--defaults", json.dumps({"timeout": 30}),
        "--approve", proposal["proposal_hash"],
    )
    assert code == 0
    assert report["status"] == "written"


def test_unchanged_when_nothing_to_write(tmp_path):
    marker = make_workspace(tmp_path)
    _, proposal = propose(marker, "my-skill", defaults={"timeout": 30})
    run_init(
        "--marker-dir", str(marker), "--skill-name", "my-skill",
        "--defaults", json.dumps({"timeout": 30}),
        "--approve", proposal["proposal_hash"],
    )
    code, report = propose(marker, "my-skill", defaults={"timeout": 30})
    assert code == 0
    assert report["status"] == "unchanged"


def test_approve_unchanged_writes_nothing_and_no_backup(tmp_path):
    marker = make_workspace(tmp_path)
    config = marker / "config" / "my-skill.yaml"
    config.write_text("timeout: 30\n", encoding="utf-8")
    _, proposal = propose(marker, "my-skill", defaults={"timeout": 30})
    code, report, _ = run_init(
        "--marker-dir", str(marker), "--skill-name", "my-skill",
        "--defaults", json.dumps({"timeout": 30}),
        "--approve", proposal["proposal_hash"],
    )
    assert code == 0
    assert report["status"] == "unchanged"
    assert "backup_path" not in report
    assert list((marker / "config").glob("*.backup.*")) == []


# ---------------------------------------------------------------------------
# Merge semantics
# ---------------------------------------------------------------------------

def test_shared_keys_never_written(tmp_path):
    marker = make_workspace(tmp_path)
    (marker / "config" / "shared.yaml").write_text("agents:\n  context_dir: .agents/context\n")
    _, proposal = propose(marker, "my-skill", defaults={"timeout": 30})
    assert proposal["proposed"]["agents"]["context_dir"] == ".agents/context"
    run_init(
        "--marker-dir", str(marker), "--skill-name", "my-skill",
        "--defaults", json.dumps({"timeout": 30}),
        "--approve", proposal["proposal_hash"],
    )
    written = yaml.safe_load((marker / "config" / "my-skill.yaml").read_text())
    assert written == {"timeout": 30}


def test_shared_updates_not_shadowed(tmp_path):
    marker = make_workspace(tmp_path)
    shared = marker / "config" / "shared.yaml"
    shared.write_text("agents:\n  context_dir: .agents/context\n")
    _, proposal = propose(marker, "my-skill", defaults={"timeout": 30})
    run_init(
        "--marker-dir", str(marker), "--skill-name", "my-skill",
        "--defaults", json.dumps({"timeout": 30}),
        "--approve", proposal["proposal_hash"],
    )
    shared.write_text("agents:\n  context_dir: .agents/NEW\n")
    code, loaded = run_loader({
        "marker_dir": str(marker), "skill_name": "my-skill",
        "defaults": {"timeout": 30},
    })
    assert code == 0
    assert loaded["config"]["agents"]["context_dir"] == ".agents/NEW"


def test_shadowed_shared_reported(tmp_path):
    marker = make_workspace(tmp_path)
    (marker / "config" / "shared.yaml").write_text("agents:\n  context_dir: .agents/context\n")
    (marker / "config" / "my-skill.yaml").write_text("agents:\n  context_dir: .agents/old\n")
    _, report = propose(marker, "my-skill", defaults={"timeout": 30})
    assert "agents.context_dir" in report["changes"]["shadowed_shared"]
    code, loaded = run_loader({"marker_dir": str(marker), "skill_name": "my-skill"})
    assert "agents.context_dir" in loaded["shadowed_shared"]


def test_user_edits_preserved(tmp_path):
    marker = make_workspace(tmp_path)
    (marker / "config" / "my-skill.yaml").write_text("timeout: 60\n")
    defaults = {"timeout": 30, "retries": 3}
    _, report = propose(marker, "my-skill", defaults=defaults)
    assert report["proposed"]["timeout"] == 60
    assert "timeout" in report["changes"]["preserved"]
    assert "retries" in report["changes"]["added"]
    _, written_report, _ = run_init(
        "--marker-dir", str(marker), "--skill-name", "my-skill",
        "--defaults", json.dumps(defaults),
        "--approve", report["proposal_hash"],
    )
    written = yaml.safe_load((marker / "config" / "my-skill.yaml").read_text())
    assert written["timeout"] == 60
    assert written["retries"] == 3
    assert "backup_path" in written_report


def test_backfill_missing_keys(tmp_path):
    marker = make_workspace(tmp_path)
    (marker / "config" / "my-skill.yaml").write_text("timeout: 60\n")
    defaults = {"timeout": 30, "tools": {"pr": {"provider": "auto"}}}
    _, report = propose(marker, "my-skill", defaults=defaults)
    assert "tools.pr.provider" in report["changes"]["added"]
    assert report["proposed"]["tools"]["pr"]["provider"] == "auto"
    assert report["proposed"]["timeout"] == 60


def test_prefixed_keys_extracted(tmp_path):
    marker = make_workspace(tmp_path)
    skill_dir = write_config_yaml(
        tmp_path / "fakeskill",
        "skill:\n"
        "  - key: fakeskill.tools.pr.provider\n    default: auto\n"
        "  - key: timeout\n    default: 30\n",
    )
    _, report = propose(marker, "fakeskill", skill_dir=skill_dir)
    assert report["proposed"]["tools"]["pr"]["provider"] == "auto"
    assert report["proposed"]["timeout"] == 30


def test_schema_migration(tmp_path):
    marker = make_workspace(tmp_path)
    (marker / "config" / "my-skill.yaml").write_text("timeout: 60\nschema_version: 1.0.0\n")
    _, report = propose(
        marker, "my-skill", defaults={"timeout": 30}, schema_version="2.0.0"
    )
    assert report["changes"]["migrated_from"] == "1.0.0"
    assert "schema_version" in report["changes"]["updated"]
    assert report["write_set"]["schema_version"] == "2.0.0"


def test_missing_required_reported(tmp_path):
    marker = make_workspace(tmp_path)
    skill_dir = write_config_yaml(
        tmp_path / "fakeskill",
        "skill:\n"
        "  - key: fakeskill.endpoint\n    required: true\n"
        "  - key: timeout\n    required: true\n    default: 30\n",
    )
    _, report = propose(marker, "fakeskill", skill_dir=skill_dir)
    assert report["missing_required"] == ["endpoint"]


# ---------------------------------------------------------------------------
# load-skill-config.py
# ---------------------------------------------------------------------------

def test_loader_merges_layers(tmp_path):
    marker = make_workspace(tmp_path)
    (marker / "config" / "shared.yaml").write_text("a: shared\nb: shared\n")
    (marker / "config" / "my-skill.yaml").write_text("b: skill\nc: skill\n")
    code, loaded = run_loader({
        "marker_dir": str(marker), "skill_name": "my-skill",
        "defaults": {"a": "default", "b": "default", "c": "default", "d": "default"},
    })
    assert code == 0
    assert loaded["status"] == "ready"
    assert loaded["config"] == {"a": "shared", "b": "skill", "c": "skill", "d": "default"}


def test_loader_missing(tmp_path):
    marker = make_workspace(tmp_path)
    code, loaded = run_loader({"marker_dir": str(marker), "skill_name": "ghost"})
    assert code == 1
    assert loaded["status"] == "missing"


def test_loader_type_mismatch(tmp_path):
    marker = make_workspace(tmp_path)
    (marker / "config" / "my-skill.yaml").write_text("timeout: not-a-number\n")
    code, loaded = run_loader({
        "marker_dir": str(marker), "skill_name": "my-skill",
        "defaults": {"timeout": 30},
    })
    assert code == 1
    assert loaded["status"] == "error"
    assert any("timeout must be an integer" in e for e in loaded["errors"])


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
        for test in tests:
            with tempfile.TemporaryDirectory() as inner:
                test(Path(inner))
        print(f"All {len(tests)} tests passed.")


if __name__ == "__main__":
    main()
