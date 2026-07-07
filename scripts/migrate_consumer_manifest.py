#!/usr/bin/env python3
"""Plan or apply an atomic consumer manifest migration to schema 2."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

import practice_report


@dataclass(frozen=True)
class MigrationPlan:
    project: Path
    manifest: Path
    status: str
    summary: str
    blockers: tuple[str, ...]
    preimage_sha256: str
    desired_text: str
    fingerprint: str


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def git_state(project: Path) -> tuple[bool, bool, str]:
    git = shutil.which("git")
    if not git:
        return False, False, "Git is unavailable"
    top = subprocess.run(
        [git, "-C", str(project), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != project.resolve():
        return False, False, "Project must be a Git repository root"
    status = subprocess.run(
        [git, "-C", str(project), "status", "--porcelain"],
        capture_output=True,
        text=True,
    )
    if status.returncode != 0:
        return True, False, "Cannot inspect Git working tree"
    return True, not status.stdout.strip(), ""


def _blocked(project: Path, manifest: Path, summary: str, *blockers: str) -> MigrationPlan:
    return MigrationPlan(project, manifest, "blocked", summary, tuple(blockers), "", "", "")


def build_plan(project: Path) -> MigrationPlan:
    project = project.resolve()
    manifest = project / ".best-practices.json"
    if not project.is_dir():
        return _blocked(project, manifest, "Consumer manifest migration is blocked.", "Project directory does not exist")
    repository, clean, git_problem = git_state(project)
    if not repository:
        return _blocked(project, manifest, "Consumer manifest migration is blocked.", git_problem)
    if not clean:
        return _blocked(project, manifest, "Consumer manifest migration is blocked.", "Git working tree must be clean")
    if manifest.is_symlink():
        return _blocked(project, manifest, "Consumer manifest migration is blocked.", "Consumer manifest must not be a symlink")
    if not manifest.exists():
        return MigrationPlan(project, manifest, "up_to_date", "Consumer manifest does not exist; nothing to migrate.", (), "", "", "")
    if not manifest.is_file():
        return _blocked(project, manifest, "Consumer manifest migration is blocked.", "Consumer manifest is not a regular file")

    preimage = manifest.read_bytes()
    preimage_sha256 = sha256_bytes(preimage)
    try:
        raw = json.loads(preimage.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _blocked(project, manifest, "Consumer manifest migration is blocked.", "Consumer manifest is not valid UTF-8 JSON")
    if not isinstance(raw, dict):
        return _blocked(project, manifest, "Consumer manifest migration is blocked.", "Consumer manifest root must be an object")
    if raw.get("schema_version") == 2:
        try:
            practice_report.normalize_manifest_data(raw, manifest)
        except ValueError as exc:
            return _blocked(project, manifest, "Consumer manifest migration is blocked.", str(exc))
        return MigrationPlan(project, manifest, "up_to_date", "Consumer manifest already uses schema 2.", (), preimage_sha256, "", "")
    if raw.get("schema_version") != 1:
        return _blocked(project, manifest, "Consumer manifest migration is blocked.", "Unsupported consumer manifest schema")
    unknown = sorted(set(raw) - {"schema_version", "practices", "optout"})
    if unknown:
        return MigrationPlan(
            project,
            manifest,
            "manual_review_required",
            "Consumer manifest contains unknown legacy state.",
            (f"Unknown schema 1 fields require manual review: {', '.join(unknown)}",),
            preimage_sha256,
            "",
            "",
        )
    try:
        desired = practice_report.normalize_manifest_data(raw, manifest)
    except ValueError as exc:
        return _blocked(project, manifest, "Consumer manifest migration is blocked.", str(exc))
    desired_text = json.dumps(desired, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    payload = {
        "project": str(project),
        "manifest": ".best-practices.json",
        "preimage_sha256": preimage_sha256,
        "desired_sha256": sha256_bytes(desired_text.encode("utf-8")),
        "from_schema": 1,
        "to_schema": 2,
    }
    fingerprint = sha256_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return MigrationPlan(
        project,
        manifest,
        "ready",
        "Migrate consumer manifest schema 1 -> 2 without changing recorded outcomes.",
        (),
        preimage_sha256,
        desired_text,
        fingerprint,
    )


def format_plan(plan: MigrationPlan) -> str:
    lines = [
        f"status={plan.status}",
        f"project={plan.project}",
        f"manifest={plan.manifest}",
        plan.summary,
    ]
    if plan.preimage_sha256:
        lines.append(f"preimage_sha256={plan.preimage_sha256}")
    if plan.fingerprint:
        lines.append(f"fingerprint={plan.fingerprint}")
    if plan.blockers:
        lines.append("blocking_issues:")
        lines.extend(f"- {blocker}" for blocker in plan.blockers)
    lines.append("No files were changed.")
    return "\n".join(lines)


def atomic_write(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def apply_plan(project: Path, fingerprint: str) -> MigrationPlan:
    plan = build_plan(project)
    if plan.status != "ready":
        return plan
    if fingerprint != plan.fingerprint:
        return MigrationPlan(
            plan.project,
            plan.manifest,
            "blocked",
            "Consumer manifest migration is blocked.",
            ("Fingerprint mismatch; rebuild and review the plan",),
            plan.preimage_sha256,
            "",
            "",
        )
    if sha256_bytes(plan.manifest.read_bytes()) != plan.preimage_sha256:
        return _blocked(plan.project, plan.manifest, "Consumer manifest migration is blocked.", "Consumer manifest changed after planning")
    atomic_write(plan.manifest, plan.desired_text)
    normalized = practice_report.load_manifest(plan.manifest)
    if normalized["schema_version"] != 2:
        raise RuntimeError("postcondition failed: consumer manifest is not schema 2")
    return MigrationPlan(
        plan.project,
        plan.manifest,
        "applied",
        "Consumer manifest migration applied and verified; changes remain unstaged.",
        (),
        plan.preimage_sha256,
        "",
        plan.fingerprint,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--fingerprint")
    parser.add_argument("--yes", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.apply:
        if not args.yes or not args.fingerprint:
            print("Apply requires --fingerprint and --yes.", file=sys.stderr)
            return 2
        plan = apply_plan(args.project, args.fingerprint)
        print(format_plan(plan).replace("No files were changed.", "File changed only when status=applied."))
        return 0 if plan.status in {"applied", "up_to_date"} else 1
    if args.fingerprint or args.yes:
        print("Plan mode does not accept --fingerprint or --yes.", file=sys.stderr)
        return 2
    plan = build_plan(args.project)
    print(format_plan(plan))
    return 0 if plan.status in {"ready", "up_to_date"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
