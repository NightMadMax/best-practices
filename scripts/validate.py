#!/usr/bin/env python3
"""Validate Best Practices repository content without third-party packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


ALLOWED_STATUSES = {"new", "triaged", "accepted", "rejected"}
ALLOWED_PRACTICE_STATUSES = {"trial", "accepted", "deprecated", "superseded"}
ALLOWED_EVIDENCE_LEVELS = {"E0", "E1", "E2", "E3"}
ALLOWED_STACKS = {
    "1c",
    "web",
    "common",
    "tools",
    "anti-patterns",
    "prompts",
    "snippets",
}
REQUIRED_FIELDS = (
    "id",
    "status",
    "source",
    "added_by",
    "stack",
    "target",
    "evidence_level",
    "evidence",
    "created",
    "decided",
)
FILENAME_RE = re.compile(
    r"^(?P<id>PC-(?P<year>\d{4})-(?P<number>\d{3}))-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WIKILINK_RE = re.compile(r"\[\[([^\]#|]+?)(?:#[^\]|]+)?(?:\\?\|[^\]]+)?\]\]")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[opsu]_[A-Za-z0-9]{20,}\b")),
    ("generic credential", re.compile(
        r"(?i)\b(?:password|passwd|api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}"
    )),
    ("private host", re.compile(r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b")),
    ("machine-specific path", re.compile(r"(?:/Users/[^/\s]+|/home/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+)")),
)
PRACTICE_REQUIRED_FIELDS = (
    "id",
    "status",
    "source",
    "added_by",
    "stack",
    "tags",
    "applies_to",
    "does_not_apply_to",
    "evidence_level",
    "evidence",
    "owner",
    "created",
    "last_verified",
    "review_by",
    "supersedes",
    "conflicts_with",
    "candidate",
)
BODY_FIELDS = {
    "1c": ("Контекст", "Проблема", "Решение"),
    "web": ("Контекст", "Проблема", "Решение"),
    "common": ("Контекст", "Проблема", "Решение"),
    "tools": ("Назначение", "Вердикт", "Настройка"),
    "anti-patterns": ("Контекст", "Почему плохо", "Что делать вместо"),
    "prompts": ("Когда применять", "Промпт / паттерн", "Почему работает"),
    "snippets": ("Контекст", "Сниппет", "Заметки"),
}


@dataclass(frozen=True)
class Problem:
    path: Path
    message: str

    def render(self, root: Path) -> str:
        try:
            display = self.path.relative_to(root)
        except ValueError:
            display = self.path
        return f"{display}: {self.message}"


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
        return decoded if isinstance(decoded, str) else value
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1]
    return value


def is_iso_date(value: str) -> bool:
    if not DATE_RE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def parse_frontmatter(path: Path) -> Tuple[Dict[str, str], str, List[Problem]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    problems: List[Problem] = []
    if not lines or lines[0].strip() != "---":
        return {}, text, [Problem(path, "missing opening frontmatter delimiter")]

    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}, text, [Problem(path, "missing closing frontmatter delimiter")]

    fields: Dict[str, str] = {}
    for line_number, raw in enumerate(lines[1:end], start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1].isspace() or ":" not in raw:
            problems.append(Problem(path, f"unsupported frontmatter syntax on line {line_number}"))
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[a-z_]+", key):
            problems.append(Problem(path, f"invalid frontmatter key {key!r} on line {line_number}"))
            continue
        if key in fields:
            problems.append(Problem(path, f"duplicate frontmatter field {key!r}"))
        fields[key] = _unquote(value)

    return fields, "\n".join(lines[end + 1 :]), problems


def validate_candidate(path: Path, root: Path) -> Tuple[str, List[Problem]]:
    problems: List[Problem] = []
    match = FILENAME_RE.fullmatch(path.name)
    if not match:
        problems.append(Problem(path, "filename must match PC-YYYY-NNN-kebab-case.md"))

    fields, body, frontmatter_problems = parse_frontmatter(path)
    problems.extend(frontmatter_problems)
    for field in REQUIRED_FIELDS:
        if field not in fields:
            problems.append(Problem(path, f"missing frontmatter field {field!r}"))

    candidate_id = fields.get("id", "")
    if match and candidate_id != match.group("id"):
        problems.append(Problem(path, f"id {candidate_id!r} does not match filename id {match.group('id')!r}"))
    if match and fields.get("created") and fields["created"][:4] != match.group("year"):
        problems.append(Problem(path, "created year does not match filename year"))

    status = fields.get("status", "")
    if status and status not in ALLOWED_STATUSES:
        problems.append(Problem(path, f"unsupported status {status!r}"))
    stack = fields.get("stack", "")
    if stack and stack not in ALLOWED_STACKS:
        problems.append(Problem(path, f"unsupported stack {stack!r}"))

    expected_target = f"practices/{stack}/{path.name}" if stack else ""
    target = fields.get("target", "")
    if target and target != expected_target:
        problems.append(Problem(path, f"target must be {expected_target!r} for stack {stack!r}"))
    if target and status == "accepted" and not (root / target).is_file():
        problems.append(Problem(path, f"target does not exist: {target}"))

    evidence_level = fields.get("evidence_level", "")
    if evidence_level and evidence_level not in ALLOWED_EVIDENCE_LEVELS:
        problems.append(Problem(path, f"unsupported evidence_level {evidence_level!r}"))
    if status == "accepted" and evidence_level not in {"E1", "E2", "E3"}:
        problems.append(Problem(path, "accepted candidate requires evidence_level E1 or higher"))

    for field in ("source", "added_by", "evidence"):
        if field in fields and not fields[field].strip():
            problems.append(Problem(path, f"frontmatter field {field!r} must not be empty"))
    created = fields.get("created", "")
    if created and not is_iso_date(created):
        problems.append(Problem(path, "created must use YYYY-MM-DD"))
    decided = fields.get("decided", "")
    if status in {"accepted", "rejected"} and not is_iso_date(decided):
        problems.append(Problem(path, f"status {status!r} requires decided in YYYY-MM-DD format"))
    if status in {"new", "triaged"} and decided:
        problems.append(Problem(path, f"status {status!r} requires an empty decided field"))

    if not re.search(r"^#\s+\S", body, flags=re.MULTILINE):
        problems.append(Problem(path, "body must contain a level-one title"))
    for label in BODY_FIELDS.get(stack, ()):
        if not re.search(rf"\*\*{re.escape(label)}:\*\*\s*\S", body, flags=re.IGNORECASE):
            problems.append(Problem(path, f"missing or empty body field {label!r}"))

    full_text = path.read_text(encoding="utf-8")
    if "<заполнить>" in body:
        problems.append(Problem(path, "body still contains <заполнить> placeholder"))
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(full_text):
            problems.append(Problem(path, f"possible {label} found"))

    return candidate_id, problems


def validate_practice(path: Path, root: Path) -> Tuple[str, List[Problem]]:
    problems: List[Problem] = []
    match = FILENAME_RE.fullmatch(path.name)
    if not match:
        return "", [Problem(path, "practice filename must match PC-YYYY-NNN-kebab-case.md")]

    fields, body, frontmatter_problems = parse_frontmatter(path)
    problems.extend(frontmatter_problems)
    for field in PRACTICE_REQUIRED_FIELDS:
        if field not in fields:
            problems.append(Problem(path, f"missing frontmatter field {field!r}"))

    practice_id = fields.get("id", "")
    if practice_id != match.group("id"):
        problems.append(Problem(path, f"id {practice_id!r} does not match filename id {match.group('id')!r}"))
    stack = fields.get("stack", "")
    if stack not in ALLOWED_STACKS:
        problems.append(Problem(path, f"unsupported stack {stack!r}"))
    elif path.parent != root / "practices" / stack:
        problems.append(Problem(path, f"practice must be stored under practices/{stack}/"))

    status = fields.get("status", "")
    if status not in ALLOWED_PRACTICE_STATUSES:
        problems.append(Problem(path, f"unsupported practice status {status!r}"))
    evidence_level = fields.get("evidence_level", "")
    if evidence_level not in ALLOWED_EVIDENCE_LEVELS:
        problems.append(Problem(path, f"unsupported evidence_level {evidence_level!r}"))
    if status == "trial" and evidence_level not in {"E1", "E2", "E3"}:
        problems.append(Problem(path, "trial practice requires evidence_level E1 or higher"))
    if status == "accepted" and evidence_level not in {"E2", "E3"}:
        problems.append(Problem(path, "accepted practice requires evidence_level E2 or E3"))

    for field in ("source", "added_by", "applies_to", "evidence", "owner"):
        if field in fields and not fields[field].strip():
            problems.append(Problem(path, f"frontmatter field {field!r} must not be empty"))
    for field in ("created", "last_verified", "review_by"):
        if fields.get(field) and not is_iso_date(fields[field]):
            problems.append(Problem(path, f"{field} must use YYYY-MM-DD"))

    candidate = fields.get("candidate", "")
    expected_candidate = f"candidates/{path.name}"
    if candidate != expected_candidate:
        problems.append(Problem(path, f"candidate must be {expected_candidate!r}"))
    elif not (root / candidate).is_file():
        problems.append(Problem(path, f"candidate does not exist: {candidate}"))

    if not re.search(r"^#\s+\S", body, flags=re.MULTILINE):
        problems.append(Problem(path, "body must contain a level-one title"))
    for label in BODY_FIELDS.get(stack, ()):
        if not re.search(rf"\*\*{re.escape(label)}:\*\*\s*\S", body, flags=re.IGNORECASE):
            problems.append(Problem(path, f"missing or empty body field {label!r}"))
    if not re.search(r"\*\*Проверка:\*\*\s*\S", body, flags=re.IGNORECASE):
        problems.append(Problem(path, "missing or empty body field 'Проверка'"))

    full_text = path.read_text(encoding="utf-8")
    if "<заполнить>" in body:
        problems.append(Problem(path, "body still contains <заполнить> placeholder"))
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(full_text):
            problems.append(Problem(path, f"possible {label} found"))
    return practice_id, problems


def _wikilink_target_exists(root: Path, target: str) -> bool:
    target_path = Path(target)
    candidates = [root / target_path, root / f"{target}.md"]
    if "/" not in target:
        candidates.extend(root.rglob(target_path.name))
        candidates.extend(root.rglob(f"{target_path.name}.md"))
    return any(candidate.is_file() for candidate in candidates)


def validate_links(root: Path) -> List[Problem]:
    problems: List[Problem] = []
    ignored_parts = {".git", ".venv", "node_modules"}
    for path in root.rglob("*.md"):
        if ignored_parts.intersection(path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        for target in WIKILINK_RE.findall(text):
            if not _wikilink_target_exists(root, target.strip()):
                problems.append(Problem(path, f"broken wikilink [[{target}]]"))
        for target in MARKDOWN_LINK_RE.findall(text):
            target = target.strip().split("#", 1)[0]
            if not target or re.match(r"^(?:https?://|mailto:)", target):
                continue
            decoded = target.replace("%20", " ")
            if not (path.parent / decoded).resolve().is_file():
                problems.append(Problem(path, f"broken Markdown link ({target})"))
    return problems


def validate_repository(root: Path, check_links: bool = True) -> List[Problem]:
    problems: List[Problem] = []
    seen_ids: Dict[str, Path] = {}
    candidates_dir = root / "candidates"
    for path in sorted(candidates_dir.glob("PC-*.md")):
        candidate_id, candidate_problems = validate_candidate(path, root)
        problems.extend(candidate_problems)
        if candidate_id:
            if candidate_id in seen_ids:
                problems.append(Problem(path, f"duplicate id {candidate_id!r}; first used by {seen_ids[candidate_id].name}"))
            else:
                seen_ids[candidate_id] = path
    for stack in sorted(ALLOWED_STACKS):
        for path in sorted((root / "practices" / stack).glob("PC-*.md")):
            practice_id, practice_problems = validate_practice(path, root)
            problems.extend(practice_problems)
            candidate_path = root / "candidates" / path.name
            if practice_id and candidate_path.is_file():
                candidate_fields, _, _ = parse_frontmatter(candidate_path)
                practice_fields, _, _ = parse_frontmatter(path)
                for field in ("id", "source", "added_by", "stack"):
                    if candidate_fields.get(field) != practice_fields.get(field):
                        problems.append(Problem(path, f"field {field!r} differs from accepted candidate"))
                if candidate_fields.get("status") != "accepted":
                    problems.append(Problem(path, "linked candidate must have status 'accepted'"))
                if candidate_fields.get("target") != str(path.relative_to(root)):
                    problems.append(Problem(path, "candidate target does not point to this practice"))
    if check_links:
        problems.extend(validate_links(root))
    return problems


def find_stale_practices(root: Path, today: Optional[date] = None) -> List[Problem]:
    today = today or date.today()
    stale: List[Problem] = []
    for stack in sorted(ALLOWED_STACKS):
        for path in sorted((root / "practices" / stack).glob("PC-*.md")):
            fields, _, problems = parse_frontmatter(path)
            if problems or not is_iso_date(fields.get("review_by", "")):
                continue
            if date.fromisoformat(fields["review_by"]) < today:
                stale.append(Problem(path, f"review_by expired on {fields['review_by']}"))
    return stale


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--no-links", action="store_true", help="skip Markdown and wikilink checks")
    parser.add_argument(
        "--strict-freshness",
        action="store_true",
        help="treat expired review_by dates as validation errors",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    problems = validate_repository(root, check_links=not args.no_links)
    stale = find_stale_practices(root)
    for warning in stale:
        print(f"WARNING: {warning.render(root)}", file=sys.stderr)
    if args.strict_freshness:
        problems.extend(stale)
    if problems:
        for problem in problems:
            print(problem.render(root), file=sys.stderr)
        print(f"Validation failed: {len(problems)} problem(s)", file=sys.stderr)
        return 1
    print("Validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
