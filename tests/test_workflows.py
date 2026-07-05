import json
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import new_candidate  # noqa: E402
import practice_report  # noqa: E402
import validate  # noqa: E402


class WorkflowTests(unittest.TestCase):
    def test_generator_allocates_next_id_and_escapes_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "candidates").mkdir()
            (root / "candidates/PC-2026-004-old.md").write_text("old", encoding="utf-8")
            args = Namespace(
                year=2026,
                slug="safe-boundaries",
                title="Безопасные границы",
                stack="common",
                source='project: docs/"quoted"',
                added_by="test",
                evidence="test-case",
                evidence_level="E1",
                created="2026-07-05",
            )
            path = new_candidate.create_candidate(root, args)
            self.assertEqual("PC-2026-005-safe-boundaries.md", path.name)
            fields, body, problems = validate.parse_frontmatter(path)
            self.assertEqual([], problems)
            self.assertEqual('project: docs/"quoted"', fields["source"])
            self.assertEqual(
                "practices/common/PC-2026-005-safe-boundaries.md",
                fields["target"],
            )
            self.assertIn("<заполнить>", body)

    def test_stack_detection_always_includes_common(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "package.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual({"common", "web"}, practice_report.detect_stacks(project))

    def test_manifest_records_explicit_outcome(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / ".best-practices.json"
            practice = {
                "id": "PC-2026-001",
                "path": "practices/common/PC-2026-001-example.md",
            }
            practice_report.record_outcome(
                manifest,
                practice,
                "applied",
                "a" * 40,
                "verified by test",
            )
            data = json.loads(manifest.read_text(encoding="utf-8"))
            record = data["practices"]["PC-2026-001"]
            self.assertEqual("applied", record["outcome"])
            self.assertEqual("a" * 40, record["source_commit"])

    def test_manifest_source_must_match_committed_practice(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            path = root / "practice.md"
            path.write_text("committed\n", encoding="utf-8")
            subprocess.run(["git", "add", "practice.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)
            self.assertTrue(practice_report.practice_is_committed(root, "practice.md"))
            path.write_text("changed\n", encoding="utf-8")
            self.assertFalse(practice_report.practice_is_committed(root, "practice.md"))

    def test_report_excludes_trial_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            common = root / "practices/common"
            common.mkdir(parents=True)
            practice = """---
id: PC-2026-001
status: trial
source: test
added_by: test
stack: common
tags: test
applies_to: all projects
does_not_apply_to:
evidence_level: E1
evidence: test
owner: test
created: 2026-07-05
last_verified: 2026-07-05
review_by: 2026-10-05
supersedes:
conflicts_with:
candidate: candidates/PC-2026-001-example.md
---
# Trial practice
"""
            (common / "PC-2026-001-example.md").write_text(practice, encoding="utf-8")
            self.assertEqual([], practice_report.load_practices(root, {"common"}))
            included = practice_report.load_practices(root, {"common"}, include_trial=True)
            self.assertEqual(["PC-2026-001"], [item["id"] for item in included])


if __name__ == "__main__":
    unittest.main()
