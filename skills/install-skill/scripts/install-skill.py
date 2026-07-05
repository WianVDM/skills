#!/usr/bin/env python3
"""
install-skill.py

Install a skill from a local path or URL into the project or user scope,
and confirm before overwriting.
"""

from __future__ import annotations

import argparse
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path


def detect_target_dir(project_root: Path, scope: str) -> Path:
    if scope == "user":
        return Path.home() / ".agents" / "skills"

    script = (
        Path(__file__).resolve().parent.parent.parent
        / "detect-project-context"
        / "scripts"
        / "detect-project-context.py"
    )
    result = subprocess.run(
        [sys.executable, str(script), "--start", str(project_root), "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    return Path(data["recommended_skills_dir"])


def copy_local(source: Path, dest: Path):
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest, ignore=shutil.ignore_patterns("*.pyc", "__pycache__"))


def download_archive(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "install-skill/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def extract_archive(data: bytes, dest: Path):
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        if zipfile.is_zipfile(io.BytesIO(data)):
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                zf.extractall(tmp_path)
        elif data.startswith(b"\x1f\x8b") or tarfile.is_tarfile(io.BytesIO(data)):
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
                tf.extractall(tmp_path)
        else:
            raise ValueError("Unsupported archive format. Only .zip and .tar.gz are supported.")

        # Find the single top-level directory if present
        entries = [e for e in tmp_path.iterdir() if e.is_dir()]
        if len(entries) == 1:
            shutil.copytree(entries[0], dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.pyc", "__pycache__"))
        else:
            for e in tmp_path.iterdir():
                if e.is_dir():
                    shutil.copytree(e, dest / e.name, dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.pyc", "__pycache__"))
                else:
                    shutil.copy2(e, dest / e.name)


def install(skill_name: str, source: str, scope: str, project_root: Path, yes: bool) -> dict:
    target_dir = detect_target_dir(project_root, scope)
    target_dir.mkdir(parents=True, exist_ok=True)
    dest = target_dir / skill_name
    existing = dest.exists()

    if existing and not yes:
        return {
            "installed": False,
            "skill_name": skill_name,
            "target_scope": scope,
            "installed_path": str(dest),
            "reason": "Skill already exists. Pass --yes to overwrite, or confirm the overwrite with the user.",
        }

    source_path = Path(source).expanduser().resolve()
    if source_path.is_dir():
        copy_local(source_path, dest)
    elif source.startswith("http://") or source.startswith("https://"):
        data = download_archive(source)
        extract_archive(data, dest)
    else:
        return {
            "installed": False,
            "skill_name": skill_name,
            "target_scope": scope,
            "installed_path": str(dest),
            "reason": "Source must be a local directory or an archive URL.",
        }

    return {
        "installed": True,
        "skill_name": skill_name,
        "target_scope": scope,
        "installed_path": str(dest),
    }


def main():
    parser = argparse.ArgumentParser(description="Install a skill from a local path or URL.")
    parser.add_argument("skill_name", help="Name of the skill to install.")
    parser.add_argument("--source", required=True, help="Local path or archive URL to install from.")
    parser.add_argument("--scope", choices=["project", "user"], default="project", help="Target scope.")
    parser.add_argument("--project-root", default=".", help="Project root for scope detection.")
    parser.add_argument("--yes", action="store_true", help="Confirm overwrite without prompting.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    report = install(args.skill_name, args.source, args.scope, project_root, args.yes)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if report["installed"]:
            print(f"Installed {report['skill_name']} to {report['installed_path']}")
        else:
            print(f"Not installed: {report['reason']}")

    sys.exit(0 if report["installed"] else 1)


if __name__ == "__main__":
    main()
