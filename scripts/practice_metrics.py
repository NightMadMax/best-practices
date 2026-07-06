#!/usr/bin/env python3
"""Summarize practice maturity and recorded consumer outcomes."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, Optional, Sequence

import practice_report
import validate


def collect_metrics(root: Path, consumers: Iterable[Path], today: Optional[date] = None) -> Dict[str, object]:
    today = today or date.today()
    candidate_statuses: Counter[str] = Counter()
    practice_statuses: Counter[str] = Counter()
    practice_sections: Counter[str] = Counter()
    evidence_levels: Counter[str] = Counter()

    for path in sorted((root / "candidates").glob("PC-*.md")):
        fields, _, problems = validate.parse_frontmatter(path)
        if not problems:
            candidate_statuses[fields.get("status", "unknown")] += 1

    for section in sorted(validate.ALLOWED_STACKS):
        for path in sorted((root / "practices" / section).glob("PC-*.md")):
            fields, _, problems = validate.parse_frontmatter(path)
            if problems:
                continue
            practice_statuses[fields.get("status", "unknown")] += 1
            practice_sections[section] += 1
            evidence_levels[fields.get("evidence_level", "unknown")] += 1

    consumer_outcomes: Counter[str] = Counter()
    manifests_found = 0
    consumer_paths = [path.resolve() for path in consumers]
    for consumer in consumer_paths:
        manifest_path = consumer / ".best-practices.json"
        if not manifest_path.is_file():
            continue
        manifests_found += 1
        manifest = practice_report.load_manifest(manifest_path)
        for decision in manifest["practices"].values():
            if isinstance(decision, dict):
                consumer_outcomes[str(decision.get("outcome", "unknown"))] += 1

    stale = validate.find_stale_practices(root, today=today)
    recorded = sum(consumer_outcomes.values())
    adopted = consumer_outcomes["applied"] + consumer_outcomes["already-compliant"]
    return {
        "candidate_statuses": dict(sorted(candidate_statuses.items())),
        "practice_statuses": dict(sorted(practice_statuses.items())),
        "practice_sections": dict(sorted(practice_sections.items())),
        "evidence_levels": dict(sorted(evidence_levels.items())),
        "stale_practices": [problem.render(root) for problem in stale],
        "consumers_scanned": len(consumer_paths),
        "consumer_manifests_found": manifests_found,
        "consumer_outcomes": dict(sorted(consumer_outcomes.items())),
        "recorded_decisions": recorded,
        "adoption_rate": (adopted / recorded) if recorded else None,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--consumer", action="append", type=Path, default=[])
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    problems = validate.validate_repository(root)
    if problems:
        for problem in problems:
            print(problem.render(root))
        raise SystemExit("Best Practices repository validation failed")
    missing = [path for path in args.consumer if not path.is_dir()]
    if missing:
        raise SystemExit(f"consumer directory does not exist: {missing[0]}")
    print(json.dumps(collect_metrics(root, args.consumer), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
