#!/usr/bin/env python3
"""Search the practice catalog by section, status, tag, or free text."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import validate


def load_catalog(root: Path) -> List[Dict[str, str]]:
    catalog: List[Dict[str, str]] = []
    for section in sorted(validate.ALLOWED_STACKS):
        for path in sorted((root / "practices" / section).glob("PC-*.md")):
            fields, body, problems = validate.parse_frontmatter(path)
            if problems:
                continue
            title = next(
                (line[2:].strip() for line in body.splitlines() if line.startswith("# ")),
                path.stem,
            )
            item = dict(fields)
            item.update(
                {
                    "title": title,
                    "path": path.relative_to(root).as_posix(),
                    "search_text": f"{title}\n{body}".casefold(),
                }
            )
            catalog.append(item)
    return catalog


def search_catalog(
    catalog: List[Dict[str, str]],
    sections: Optional[Sequence[str]] = None,
    statuses: Optional[Sequence[str]] = None,
    tags: Optional[Sequence[str]] = None,
    query: Optional[str] = None,
) -> List[Dict[str, str]]:
    section_filter = set(sections or [])
    status_filter = set(statuses or [])
    tag_filter = {tag.casefold() for tag in tags or []}
    query_filter = query.casefold() if query else None
    results: List[Dict[str, str]] = []
    for item in catalog:
        item_tags = {tag.strip().casefold() for tag in item.get("tags", "").split(",") if tag.strip()}
        if section_filter and item.get("stack") not in section_filter:
            continue
        if status_filter and item.get("status") not in status_filter:
            continue
        if tag_filter and not tag_filter.issubset(item_tags):
            continue
        if query_filter and query_filter not in item["search_text"]:
            continue
        results.append({key: value for key, value in item.items() if key != "search_text"})
    return results


def markdown_catalog(items: List[Dict[str, str]]) -> str:
    lines = ["# Practice catalog", ""]
    if not items:
        return "\n".join(lines + ["Практики по заданным фильтрам не найдены."])
    lines.extend(["| ID | Section | Status | Evidence | Practice |", "|---|---|---|---|---|"])
    for item in items:
        title = item["title"].replace("\\", "\\\\").replace("|", "\\|").replace("]", "\\]")
        lines.append(
            f"| `{item['id']}` | `{item['stack']}` | `{item['status']}` | "
            f"`{item['evidence_level']}` | [{title}]({item['path']}) |"
        )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--section", action="append", choices=sorted(validate.ALLOWED_STACKS))
    parser.add_argument("--status", action="append", choices=sorted(validate.ALLOWED_PRACTICE_STATUSES))
    parser.add_argument("--tag", action="append")
    parser.add_argument("--query")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    problems = validate.validate_repository(root)
    if problems:
        for problem in problems:
            print(problem.render(root))
        raise SystemExit("Best Practices repository validation failed")
    items = search_catalog(
        load_catalog(root),
        sections=args.section,
        statuses=args.status,
        tags=args.tag,
        query=args.query,
    )
    if args.format == "json":
        print(json.dumps(items, ensure_ascii=False, indent=2))
    else:
        print(markdown_catalog(items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
