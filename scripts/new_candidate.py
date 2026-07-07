#!/usr/bin/env python3
"""Create the next validated practice candidate from command-line metadata."""

from __future__ import annotations

import argparse
import json
import re
import secrets
from datetime import date
from pathlib import Path
from typing import Optional, Sequence

import validate


BODY_LABELS = {
    "1c": ("Контекст", "Проблема", "Решение"),
    "web": ("Контекст", "Проблема", "Решение"),
    "common": ("Контекст", "Проблема", "Решение"),
    "tools": ("Назначение", "Вердикт", "Настройка"),
    "anti-patterns": ("Контекст", "Почему плохо", "Что делать вместо"),
    "prompts": ("Когда применять", "Промпт / паттерн", "Почему работает"),
    "snippets": ("Контекст", "Сниппет", "Заметки"),
}


def new_id(root: Path, year: int) -> str:
    """Return a locally unique, collision-resistant candidate ID."""
    for _ in range(100):
        candidate_id = f"PC-{year}-{secrets.token_hex(6)}"
        pattern = f"{candidate_id}-*.md"
        candidate_exists = any((root / "candidates").glob(pattern))
        practice_exists = any((root / "practices").glob(f"*/{pattern}"))
        if not candidate_exists and not practice_exists:
            return candidate_id
    raise RuntimeError("could not allocate a unique candidate id")


def render_candidate(
    candidate_id: str,
    slug: str,
    title: str,
    stack: str,
    source: str,
    added_by: str,
    evidence: str,
    evidence_level: str,
    created: str,
) -> str:
    filename = f"{candidate_id}-{slug}.md"
    target = f"practices/{stack}/{filename}"
    labels = BODY_LABELS[stack]
    body = "\n".join(f"- **{label}:** <заполнить>" for label in labels)
    quoted_source = json.dumps(source, ensure_ascii=False)
    quoted_added_by = json.dumps(added_by, ensure_ascii=False)
    quoted_evidence = json.dumps(evidence, ensure_ascii=False)
    return f'''---
id: {candidate_id}
status: new
source: {quoted_source}
added_by: {quoted_added_by}
stack: {stack}
target: {target}
evidence_level: {evidence_level}
evidence: {quoted_evidence}
created: {created}
decided:
---

# {title}

{body}

## Notes

Укажите границы применимости и почему урок может повториться в другом проекте.
'''


def create_candidate(root: Path, args: argparse.Namespace) -> Path:
    candidates_dir = root / "candidates"
    candidate_id = new_id(root, args.year)
    filename = f"{candidate_id}-{args.slug}.md"
    path = candidates_dir / filename
    if path.exists():
        raise FileExistsError(path)
    content = render_candidate(
        candidate_id=candidate_id,
        slug=args.slug,
        title=args.title,
        stack=args.stack,
        source=args.source,
        added_by=args.added_by,
        evidence=args.evidence,
        evidence_level=args.evidence_level,
        created=args.created,
    )
    path.write_text(content, encoding="utf-8")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--slug", required=True, help="lowercase kebab-case slug")
    parser.add_argument("--title", required=True)
    parser.add_argument("--stack", required=True, choices=sorted(validate.ALLOWED_STACKS))
    parser.add_argument("--source", required=True)
    parser.add_argument("--added-by", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--evidence-level", choices=("E0", "E1"), default="E1")
    parser.add_argument("--year", type=int, default=date.today().year)
    parser.add_argument("--created", default=date.today().isoformat())
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
        raise SystemExit("--slug must use lowercase kebab-case")
    path = create_candidate(args.root.resolve(), args)
    print(path)
    print("Заполните placeholders в теле, затем запустите: make check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
