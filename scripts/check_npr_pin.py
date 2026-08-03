#!/usr/bin/env python3
"""Watch the pinned new-project-rules revision this repository executes.

The governance audit here runs a script *from another repository*, pinned by
full commit SHA. The pin is the right call — an audit that silently follows
somebody else's `main` is not an audit — but a pin with no watcher is a pin that
rots. It did: the recorded revision sat 284 commits behind while the audited
script had since been fixed to stop reporting a bypass check it never performed.
Every night this repository printed that reassurance about itself.

The other side of the contract has had a watcher for its pin of this repository
from the start. This is the missing half.

Two questions, kept apart:

* Does the pin still resolve, and does it still contain the script the workflow
  runs? A no here is a broken audit, today.
* Is the pin behind the upstream default branch? That is a maintainer decision
  to make deliberately, so it is reported and does not fail. Failing on it would
  be worse than useless here: the two repositories pin *each other*, and
  refreshing either pin advances that repository's main and puts the other one
  behind — so a red build on behind-main means they can never both be current,
  and the report stays red no matter what anyone does. The sibling repository
  had already decided this class for its other upstream: a red build for drift
  teaches people to ignore the check.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = Path(".github/workflows/governance-audit.yml")
UPSTREAM = "NightMadMax/new-project-rules"
# What the workflow runs from the pinned checkout. If a refresh of the pin ever
# moves or renames it, the audit breaks on the next scheduled run and this check
# says so first.
REQUIRED_SCRIPT = "scripts/check_github_governance.py"
PIN_RE = re.compile(r"ref:\s*([0-9a-f]{40})")


class PinError(Exception):
    """The pin cannot be read or cannot be trusted."""


def pinned_commit(root: Path = ROOT) -> str:
    """The upstream revision the governance audit executes."""
    try:
        text = (root / WORKFLOW).read_text(encoding="utf-8")
    except OSError as exc:
        raise PinError(f"cannot read {WORKFLOW}: {exc}") from exc
    if UPSTREAM not in text:
        raise PinError(f"{WORKFLOW} no longer checks out {UPSTREAM}")
    match = PIN_RE.search(text)
    if not match:
        raise PinError(f"{WORKFLOW} does not pin {UPSTREAM} by a full commit SHA")
    return match.group(1)


def _git(args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                              text=True, encoding="utf-8", check=False)
    except OSError as exc:
        raise PinError(f"git is not runnable: {exc}") from exc


def check(upstream_root: Path, root: Path = ROOT, *, strict: bool = False) -> list[str]:
    """Problems with the pin, read against a checkout of the upstream repository."""
    commit = pinned_commit(root)
    problems: list[str] = []

    resolved = _git(["cat-file", "-e", f"{commit}^{{commit}}"], upstream_root)
    if resolved.returncode != 0:
        return [f"pinned revision {commit[:12]} does not exist in {UPSTREAM}"]

    listed = _git(["ls-tree", "--name-only", commit, REQUIRED_SCRIPT], upstream_root)
    if listed.returncode != 0 or not listed.stdout.strip():
        problems.append(
            f"pinned revision {commit[:12]} does not contain {REQUIRED_SCRIPT}, "
            "which the governance audit runs")

    head = _git(["rev-parse", "HEAD"], upstream_root)
    if head.returncode != 0:
        raise PinError(f"cannot read the upstream HEAD: {head.stderr.strip()}")
    upstream_head = head.stdout.strip()
    if upstream_head != commit:
        behind = _git(["rev-list", "--count", f"{commit}..{upstream_head}"], upstream_root)
        count = behind.stdout.strip() if behind.returncode == 0 else "?"
        message = (f"pin {commit[:12]} is {count} commit(s) behind {UPSTREAM} "
                   f"{upstream_head[:12]}; review and refresh it deliberately")
        # `strict` exists for a caller that genuinely wants the pin enforced —
        # nothing in this repository does, and the scheduled watcher must not.
        problems.append(message) if strict else print(f"NOTE: {message}")

    return problems


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream-root", type=Path, required=True,
                        help="checkout of new-project-rules to compare the pin against")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--strict-pin", action="store_true",
                        help="fail when the pin is behind main instead of reporting it")
    args = parser.parse_args(argv)
    try:
        problems = check(args.upstream_root.resolve(), args.root.resolve(),
                         strict=args.strict_pin)
    except PinError as error:
        print(f"pin check failed: {error}", file=sys.stderr)
        return 1
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    print(f"Pinned {UPSTREAM} revision is current and runnable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
