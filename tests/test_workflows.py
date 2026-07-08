import json
from unittest import mock
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
import practice_metrics  # noqa: E402
import search_practices  # noqa: E402
import validate  # noqa: E402


class WorkflowTests(unittest.TestCase):
    def _write_accepted_pair(self, root, stack, suffix, slug):
        candidate_id = f"PC-2026-{suffix}"
        filename = f"{candidate_id}-{slug}.md"
        (root / "candidates").mkdir(exist_ok=True)
        (root / "practices" / stack).mkdir(parents=True, exist_ok=True)
        labels = validate.BODY_FIELDS[stack]
        candidate_body = "\n".join(f"- **{label}:** verified {label.lower()}" for label in labels)
        practice_body = candidate_body + "\n- **Проверка:** automated fixture"
        candidate = f'''---
id: {candidate_id}
status: accepted
source: fixture
added_by: test
stack: {stack}
target: practices/{stack}/{filename}
evidence_level: E2
evidence: fixture-test
created: 2026-07-06
decided: 2026-07-06
---

# {stack} fixture

{candidate_body}
'''
        practice = f'''---
id: {candidate_id}
status: accepted
source: fixture
added_by: test
stack: {stack}
tags: fixture
applies_to: fixture projects
does_not_apply_to: none
evidence_level: E2
evidence: fixture-test
owner: test
created: 2026-07-06
last_verified: 2026-07-06
review_by: 2027-01-06
supersedes:
superseded_by:
conflicts_with:
candidate: candidates/{filename}
---

# {stack} fixture

{practice_body}
'''
        (root / "candidates" / filename).write_text(candidate, encoding="utf-8")
        (root / "practices" / stack / filename).write_text(practice, encoding="utf-8")

    @mock.patch("new_candidate.secrets.token_hex", return_value="a1b2c3d4e5f6")
    def test_generator_allocates_collision_resistant_id_and_escapes_metadata(self, _token_hex):
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
            self.assertEqual("PC-2026-a1b2c3d4e5f6-safe-boundaries.md", path.name)
            fields, body, problems = validate.parse_frontmatter(path)
            self.assertEqual([], problems)
            self.assertEqual('project: docs/"quoted"', fields["source"])
            self.assertEqual(
                "practices/common/PC-2026-a1b2c3d4e5f6-safe-boundaries.md",
                fields["target"],
            )
            self.assertIn("<заполнить>", body)

    @mock.patch("new_candidate.secrets.token_hex", side_effect=["a1b2c3d4e5f6", "deadbeefcafe"])
    def test_generator_retries_local_id_collision(self, _token_hex):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "candidates").mkdir()
            (root / "candidates/PC-2026-a1b2c3d4e5f6-existing.md").write_text("old", encoding="utf-8")
            self.assertEqual("PC-2026-deadbeefcafe", new_candidate.new_id(root, 2026))

    def test_stack_detection_always_includes_common(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "package.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual({"common", "web"}, practice_report.detect_stacks(project))

    def test_default_sections_include_every_cross_cutting_category(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            self.assertEqual(
                {"common", "tools", "anti-patterns", "prompts", "snippets"},
                practice_report.select_sections(project),
            )

    def test_explicit_stack_still_includes_cross_cutting_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            self.assertEqual(
                {"1c", "common", "tools", "anti-patterns", "prompts", "snippets"},
                practice_report.select_sections(project, {"1c"}),
            )

    def test_cli_report_includes_all_sections_end_to_end(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "base"
            project = Path(directory) / "consumer"
            root.mkdir()
            project.mkdir()
            sections = sorted(validate.ALLOWED_STACKS)
            for index, stack in enumerate(sections, start=1):
                suffix = f"{index:012d}"
                self._write_accepted_pair(root, stack, suffix, stack.replace("-", ""))
            command = [
                sys.executable,
                str(ROOT / "scripts/practice_report.py"),
                "--root",
                str(root),
                "--project",
                str(project),
                "--format",
                "json",
            ]
            for stack in sorted(practice_report.STACK_SECTIONS):
                command.extend(["--section", stack])
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            report = json.loads(result.stdout)
            self.assertEqual(set(validate.ALLOWED_STACKS), set(report["sections"]))
            self.assertEqual(set(practice_report.STACK_SECTIONS), set(report["stacks"]))
            self.assertEqual(report["stacks"], report["detected_stacks"])
            self.assertEqual(set(validate.ALLOWED_STACKS), {item["stack"] for item in report["practices"]})

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
            self.assertEqual(2, data["schema_version"])
            self.assertEqual({"global": "ask", "sections": {}}, data["preferences"])
            record = data["practices"]["PC-2026-001"]
            self.assertEqual("applied", record["outcome"])
            self.assertEqual("a" * 40, record["source_commit"])

    def test_metrics_aggregate_recorded_consumer_outcomes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "base"
            consumer = Path(directory) / "consumer"
            root.mkdir()
            consumer.mkdir()
            self._write_accepted_pair(root, "common", "000000000001", "fixture")
            manifest = {
                "schema_version": 1,
                "practices": {
                    "PC-2026-000000000001": {
                        "outcome": "applied",
                        "practice_path": "practices/common/PC-2026-000000000001-fixture.md",
                        "source_commit": "a" * 40,
                        "recorded_at": "2026-07-06",
                        "notes": "fixture",
                    },
                    "PC-2026-other": {
                        "outcome": "deferred",
                        "practice_path": "practices/common/PC-2026-other.md",
                        "source_commit": "b" * 40,
                        "recorded_at": "2026-07-06",
                        "notes": "fixture",
                    },
                },
            }
            (consumer / ".best-practices.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            metrics = practice_metrics.collect_metrics(root, [consumer], today=practice_metrics.date(2026, 7, 6))
            self.assertEqual(1, metrics["consumer_manifests_found"])
            self.assertEqual({"applied": 1, "deferred": 1}, metrics["consumer_outcomes"])
            self.assertEqual({"global:ask": 1}, metrics["consumer_preferences"])
            self.assertEqual(0.5, metrics["adoption_rate"])

    def test_missing_manifest_defaults_to_schema2(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = practice_report.load_manifest(Path(directory) / ".best-practices.json")
            self.assertEqual(2, manifest["schema_version"])
            self.assertEqual({"global": "ask", "sections": {}}, manifest["preferences"])
            self.assertEqual({}, manifest["practices"])

    def test_schema1_manifest_is_normalized_without_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".best-practices.json"
            original = '{"schema_version": 1, "practices": {}}\n'
            path.write_text(original, encoding="utf-8")
            manifest = practice_report.load_manifest(path)
            self.assertEqual(2, manifest["schema_version"])
            self.assertEqual("ask", manifest["preferences"]["global"])
            self.assertEqual(original, path.read_text(encoding="utf-8"))

    def test_schema1_global_optout_is_normalized(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".best-practices.json"
            path.write_text('{"schema_version": 1, "optout": true}\n', encoding="utf-8")
            manifest = practice_report.load_manifest(path)
            self.assertEqual("optout", manifest["preferences"]["global"])
            self.assertEqual([], practice_report.apply_preferences([{"stack": "common"}], manifest))

    def test_schema2_section_optout_filters_only_that_section(self):
        manifest = {
            "schema_version": 2,
            "preferences": {"global": "ask", "sections": {"web": "optout"}},
            "practices": {},
        }
        normalized = practice_report.normalize_manifest_data(manifest, Path("manifest.json"))
        practices = [{"stack": "common"}, {"stack": "web"}, {"stack": "tools"}]
        self.assertEqual(
            [{"stack": "common"}, {"stack": "tools"}],
            practice_report.apply_preferences(practices, normalized),
        )

    def test_cli_respects_schema2_global_optout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "base"
            project = Path(directory) / "consumer"
            root.mkdir()
            project.mkdir()
            self._write_accepted_pair(root, "common", "000000000001", "fixture")
            (project / ".best-practices.json").write_text(
                json.dumps({
                    "schema_version": 2,
                    "preferences": {"global": "optout", "sections": {}},
                    "practices": {},
                }),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/practice_report.py"),
                    "--root", str(root),
                    "--project", str(project),
                    "--format", "json",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            self.assertEqual("optout", report["preferences"]["global"])
            self.assertEqual([], report["practices"])

    def test_unknown_applied_field_requires_future_migration_review(self):
        with self.assertRaisesRegex(ValueError, "unsupported schema 1 fields applied"):
            practice_report.normalize_manifest_data(
                {"schema_version": 1, "applied": ["common"]}, Path("manifest.json")
            )

    def test_record_preserves_canonical_schema1_until_migration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".best-practices.json"
            path.write_text('{"schema_version": 1, "practices": {}}\n', encoding="utf-8")
            practice_report.record_outcome(
                path,
                {"id": "PC-2026-001", "path": "practices/common/example.md"},
                "applied",
                "a" * 40,
                "fixture",
            )
            self.assertEqual(1, json.loads(path.read_text(encoding="utf-8"))["schema_version"])

    def test_record_rejects_schema1_global_optout_without_implicit_migration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".best-practices.json"
            path.write_text('{"schema_version": 1, "optout": true}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be migrated"):
                practice_report.record_outcome(
                    path,
                    {"id": "PC-2026-001", "path": "practices/common/example.md"},
                    "applied",
                    "a" * 40,
                    "fixture",
                )

    def test_catalog_filters_by_section_status_tag_and_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_accepted_pair(root, "common", "000000000001", "fixture")
            path = root / "practices/common/PC-2026-000000000001-fixture.md"
            content = path.read_text(encoding="utf-8").replace("tags: fixture", "tags: security, fixture")
            path.write_text(content, encoding="utf-8")
            catalog = search_practices.load_catalog(root)
            found = search_practices.search_catalog(
                catalog,
                sections=["common"],
                statuses=["accepted"],
                tags=["security"],
                query="automated fixture",
            )
            self.assertEqual(["PC-2026-000000000001"], [item["id"] for item in found])

    def test_catalog_requires_all_requested_tags(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_accepted_pair(root, "common", "000000000001", "fixture")
            catalog = search_practices.load_catalog(root)
            self.assertEqual([], search_practices.search_catalog(catalog, tags=["fixture", "missing"]))

    def test_markdown_catalog_escapes_table_title(self):
        item = {
            "id": "PC-2026-001",
            "stack": "common",
            "status": "accepted",
            "evidence_level": "E2",
            "title": "A | B]",
            "path": "practices/common/example.md",
        }
        rendered = search_practices.markdown_catalog([item])
        self.assertIn(r"[A \| B\]]", rendered)

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
superseded_by:
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
