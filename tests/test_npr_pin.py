import subprocess
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_npr_pin  # noqa: E402


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=str(root), check=True,
                            capture_output=True, text=True, encoding="utf-8")
    return result.stdout.strip()


class NprPinTests(unittest.TestCase):
    """The pin this repository executes another repository's audit from.

    A pin without a watcher is a pin that rots, and this one did: 284 commits
    behind, running a version of the audit whose bypass check had already been
    fixed. These tests are about the watcher, not about the dictionary of what a
    pin looks like.
    """

    def _upstream(self, root: Path) -> tuple[str, str]:
        root.mkdir(parents=True, exist_ok=True)
        (root / "scripts").mkdir()
        (root / "scripts/check_github_governance.py").write_text("print('audit')\n", encoding="utf-8")
        for command in (["init", "-q"], ["config", "user.email", "t@example.com"],
                        ["config", "user.name", "t"], ["add", "-A"],
                        ["commit", "-q", "-m", "first"]):
            git(root, *command)
        first = git(root, "rev-parse", "HEAD")
        (root / "README.md").write_text("later\n", encoding="utf-8")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "second")
        return first, git(root, "rev-parse", "HEAD")

    def _repository(self, root: Path, commit: str) -> None:
        (root / ".github/workflows").mkdir(parents=True)
        (root / ".github/workflows/governance-audit.yml").write_text(
            "jobs:\n  audit:\n    steps:\n"
            "      - uses: actions/checkout@" + "a" * 40 + "\n"
            "        with:\n"
            "          repository: NightMadMax/new-project-rules\n"
            f"          ref: {commit}\n", encoding="utf-8")

    def test_current_pin_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            _, head = self._upstream(base / "upstream")
            self._repository(base / "repo", head)
            self.assertEqual([], check_npr_pin.check(base / "upstream", base / "repo"))

    def test_pin_behind_main_is_reported_without_failing(self):
        # The two repositories pin each other. Failing on behind-main means they
        # can never both be current: refreshing either pin advances that
        # repository's main and puts the other one behind. So drift is a note,
        # and the sibling repository had already decided this class the same way
        # for its other upstream.
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            first, _ = self._upstream(base / "upstream")
            self._repository(base / "repo", first)
            self.assertEqual([], check_npr_pin.check(base / "upstream", base / "repo"))

    def test_strict_pin_is_available_for_a_caller_that_wants_it(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            first, _ = self._upstream(base / "upstream")
            self._repository(base / "repo", first)
            problems = check_npr_pin.check(base / "upstream", base / "repo", strict=True)
            self.assertEqual(1, len(problems))
            self.assertIn("behind", problems[0])

    def test_missing_revision_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            self._upstream(base / "upstream")
            self._repository(base / "repo", "b" * 40)
            problems = check_npr_pin.check(base / "upstream", base / "repo")
            self.assertTrue(any("does not exist" in problem for problem in problems))

    def test_revision_without_the_audited_script_is_reported(self):
        # The workflow runs one named script out of the pinned checkout. A pin
        # that no longer carries it breaks the audit on its next scheduled run,
        # and the failure should be named here first.
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            upstream = base / "upstream"
            self._upstream(upstream)
            (upstream / "scripts/check_github_governance.py").unlink()
            git(upstream, "add", "-A")
            git(upstream, "commit", "-q", "-m", "remove the audit")
            self._repository(base / "repo", git(upstream, "rev-parse", "HEAD"))
            problems = check_npr_pin.check(upstream, base / "repo")
            self.assertTrue(any("check_github_governance.py" in problem for problem in problems))

    def test_a_workflow_that_stopped_pinning_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repo = base / "repo"
            (repo / ".github/workflows").mkdir(parents=True)
            (repo / ".github/workflows/governance-audit.yml").write_text(
                "jobs:\n  audit:\n    steps:\n"
                "      - uses: actions/checkout@" + "a" * 40 + "\n"
                "        with:\n"
                "          repository: NightMadMax/new-project-rules\n"
                "          ref: main\n", encoding="utf-8")
            with self.assertRaises(check_npr_pin.PinError):
                check_npr_pin.pinned_commit(repo)

    def test_the_real_workflow_pins_by_commit(self):
        self.assertRegex(check_npr_pin.pinned_commit(ROOT), r"^[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
