#!/usr/bin/env python3
"""Report applicable practices and optionally record a consumer decision."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set

import validate


OUTCOMES = {"applied", "already-compliant", "not-applicable", "deferred"}
PREFERENCE_VALUES = {"ask", "optout"}
STACK_SECTIONS = {"1c", "web", "common"}
CROSS_SECTIONS = {"tools", "anti-patterns", "prompts", "snippets"}


def detect_stacks(project: Path) -> Set[str]:
    stacks = {"common"}
    if (project / "package.json").is_file():
        stacks.add("web")
    if any(project.rglob("*.bsl")) or any(project.rglob("*.os")):
        stacks.add("1c")
    return stacks


def select_sections(project: Path, explicit: Optional[Iterable[str]] = None) -> Set[str]:
    """Select stack sections plus cross-cutting sections that require review."""
    stacks = set(explicit) if explicit is not None else detect_stacks(project)
    return stacks | {"common"} | CROSS_SECTIONS


def load_practices(root: Path, sections: Iterable[str], include_trial: bool = False) -> List[Dict[str, str]]:
    allowed_statuses = {"accepted", "trial"} if include_trial else {"accepted"}
    practices: List[Dict[str, str]] = []
    for stack in sorted(set(sections) | {"common"}):
        for path in sorted((root / "practices" / stack).glob("PC-*.md")):
            fields, body, problems = validate.parse_frontmatter(path)
            if problems or fields.get("status") not in allowed_statuses:
                continue
            title = next(
                (line[2:].strip() for line in body.splitlines() if line.startswith("# ")),
                path.stem,
            )
            item = dict(fields)
            item["title"] = title
            item["path"] = str(path.relative_to(root))
            practices.append(item)
    return practices


def current_commit(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(root),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def practice_is_committed(root: Path, practice_path: str) -> bool:
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{practice_path}"],
        cwd=str(root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if exists.returncode != 0:
        return False
    unchanged = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", practice_path],
        cwd=str(root),
    )
    return unchanged.returncode == 0


def empty_manifest() -> Dict[str, object]:
    return {
        "schema_version": 2,
        "preferences": {"global": "ask", "sections": {}},
        "practices": {},
    }


def _validate_practice_decisions(practices: object, path: Path) -> Dict[str, object]:
    if not isinstance(practices, dict):
        raise ValueError(f"manifest practices must be an object: {path}")
    for practice_id, decision in practices.items():
        if not isinstance(practice_id, str) or not isinstance(decision, dict):
            raise ValueError(f"manifest practice decisions must be objects keyed by ID: {path}")
        outcome = decision.get("outcome")
        if outcome not in OUTCOMES:
            raise ValueError(f"unsupported outcome {outcome!r} for {practice_id}: {path}")
        for field in ("practice_path", "source_commit", "recorded_at", "notes"):
            if not isinstance(decision.get(field), str):
                raise ValueError(f"manifest decision {practice_id} requires string {field}: {path}")
        if not re.fullmatch(r"[0-9a-f]{40}", decision["source_commit"]):
            raise ValueError(f"manifest decision {practice_id} has invalid source_commit: {path}")
        try:
            date.fromisoformat(decision["recorded_at"])
        except ValueError as exc:
            raise ValueError(
                f"manifest decision {practice_id} has invalid recorded_at: {path}"
            ) from exc
    return practices


def normalize_manifest_data(data: object, path: Path) -> Dict[str, object]:
    if not isinstance(data, dict):
        raise ValueError(f"consumer manifest root must be an object: {path}")
    schema_version = data.get("schema_version")
    if schema_version == 1:
        allowed = {"schema_version", "practices", "optout"}
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise ValueError(f"unsupported schema 1 fields {', '.join(unknown)}: {path}")
        optout = data.get("optout", False)
        if not isinstance(optout, bool):
            raise ValueError(f"schema 1 optout must be boolean: {path}")
        practices = _validate_practice_decisions(data.get("practices", {}), path)
        return {
            "schema_version": 2,
            "preferences": {
                "global": "optout" if optout else "ask",
                "sections": {},
            },
            "practices": practices,
        }
    if schema_version != 2:
        raise ValueError(f"unsupported manifest schema: {path}")
    allowed = {"schema_version", "preferences", "practices"}
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValueError(f"unsupported schema 2 fields {', '.join(unknown)}: {path}")
    preferences = data.get("preferences")
    if not isinstance(preferences, dict):
        raise ValueError(f"schema 2 preferences must be an object: {path}")
    if set(preferences) - {"global", "sections"}:
        raise ValueError(f"schema 2 preferences contain unsupported fields: {path}")
    global_preference = preferences.get("global")
    sections = preferences.get("sections")
    if global_preference not in PREFERENCE_VALUES:
        raise ValueError(f"unsupported global preference {global_preference!r}: {path}")
    if not isinstance(sections, dict):
        raise ValueError(f"schema 2 preference sections must be an object: {path}")
    for section, preference in sections.items():
        if section not in validate.ALLOWED_STACKS:
            raise ValueError(f"unsupported preference section {section!r}: {path}")
        if preference not in PREFERENCE_VALUES:
            raise ValueError(f"unsupported preference {preference!r} for {section}: {path}")
    practices = _validate_practice_decisions(data.get("practices"), path)
    return {
        "schema_version": 2,
        "preferences": {"global": global_preference, "sections": dict(sections)},
        "practices": practices,
    }


def load_manifest(path: Path) -> Dict[str, object]:
    if not path.exists():
        return empty_manifest()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid consumer manifest JSON: {path}") from exc
    return normalize_manifest_data(data, path)


def record_outcome(
    manifest_path: Path,
    practice: Dict[str, str],
    outcome: str,
    source_commit: str,
    notes: str,
) -> None:
    if outcome not in OUTCOMES:
        raise ValueError(f"unsupported outcome: {outcome}")
    manifest = load_manifest(manifest_path)
    if manifest_path.exists():
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        if raw.get("schema_version") == 1:
            if raw.get("optout") is True:
                raise ValueError("schema 1 optout manifest must be migrated before recording")
            manifest = raw
    practices = manifest["practices"]
    practices[practice["id"]] = {
        "outcome": outcome,
        "practice_path": practice["path"],
        "source_commit": source_commit,
        "recorded_at": date.today().isoformat(),
        "notes": notes,
    }
    temporary_path = manifest_path.with_name(f".{manifest_path.name}.tmp")
    temporary_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(manifest_path)


def markdown_report(
    practices: List[Dict[str, str]], manifest: Dict[str, object], sections: Iterable[str]
) -> str:
    lines = [
        "# Best Practices applicability report",
        "",
        f"Sections reviewed: {', '.join(f'`{section}`' for section in sorted(sections))}.",
        "",
    ]
    preferences = manifest["preferences"]
    decisions = manifest.get("practices", {})
    if preferences["global"] == "optout":
        return "\n".join(lines + ["Consumer preference: global `optout`; practices are not offered."])
    if not practices:
        return "\n".join(lines + ["Применимых практик выбранной зрелости нет."])
    for practice in practices:
        previous = decisions.get(practice["id"], {}).get("outcome", "not-recorded")
        lines.extend(
            [
                f"## {practice['id']}: {practice['title']}",
                "",
                f"- Status: `{practice['status']}`; evidence: `{practice['evidence_level']}`.",
                f"- Section: `{practice['stack']}`.",
                f"- Applies to: {practice['applies_to']}",
                f"- Source: `{practice['path']}`; {practice['source']}.",
                f"- Consumer outcome: `{previous}`.",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def apply_preferences(
    practices: List[Dict[str, str]], manifest: Dict[str, object]
) -> List[Dict[str, str]]:
    preferences = manifest["preferences"]
    if preferences["global"] == "optout":
        return []
    section_preferences = preferences["sections"]
    return [
        practice
        for practice in practices
        if section_preferences.get(practice["stack"], "ask") != "optout"
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--stack", action="append", choices=sorted(validate.ALLOWED_STACKS))
    parser.add_argument(
        "--section",
        action="append",
        choices=sorted(validate.ALLOWED_STACKS),
        help="explicit stack section; cross-cutting sections are still included",
    )
    parser.add_argument("--include-trial", action="store_true")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--record", metavar="ID=OUTCOME")
    parser.add_argument("--notes", default="")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    project = args.project.resolve()
    if not project.is_dir():
        raise SystemExit(f"project directory does not exist: {project}")
    problems = validate.validate_repository(root)
    if problems:
        for problem in problems:
            print(problem.render(root))
        raise SystemExit("Best Practices repository validation failed")
    explicit = set(args.section or args.stack or []) or None
    stacks = (explicit & STACK_SECTIONS) if explicit else detect_stacks(project)
    sections = select_sections(project, explicit)
    manifest_path = project / ".best-practices.json"
    manifest = load_manifest(manifest_path)
    practices = apply_preferences(
        load_practices(root, sections, include_trial=args.include_trial), manifest
    )
    if args.record:
        try:
            practice_id, outcome = args.record.split("=", 1)
        except ValueError:
            raise SystemExit("--record must use ID=OUTCOME")
        if outcome not in OUTCOMES:
            raise SystemExit(f"unsupported outcome {outcome!r}")
        selected = next((item for item in practices if item["id"] == practice_id), None)
        if not selected:
            raise SystemExit(f"practice is not in the current report: {practice_id}")
        if not practice_is_committed(root, selected["path"]):
            raise SystemExit(
                f"practice must match committed HEAD before recording: {selected['path']}"
            )
        record_outcome(manifest_path, selected, outcome, current_commit(root), args.notes)
    manifest = load_manifest(manifest_path)
    if args.format == "json":
        print(
            json.dumps(
                {
                    "detected_stacks": sorted(stacks),
                    "stacks": sorted(stacks),
                    "sections": sorted(sections),
                    "preferences": manifest["preferences"],
                    "practices": practices,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(markdown_report(practices, manifest, sections))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
