#!/usr/bin/env python3
"""Report applicable practices and optionally record a consumer decision."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set

import validate


OUTCOMES = {"applied", "already-compliant", "not-applicable", "deferred"}
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


def load_manifest(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {"schema_version": 1, "practices": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("practices"), dict):
        raise ValueError(f"unsupported manifest schema: {path}")
    return data


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
    decisions = manifest.get("practices", {})
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
    practices = load_practices(root, sections, include_trial=args.include_trial)
    manifest_path = project / ".best-practices.json"
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
