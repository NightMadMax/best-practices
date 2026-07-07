import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/migrate_consumer_manifest.py"
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("migrate_consumer_manifest", MODULE_PATH)
assert SPEC and SPEC.loader
migration = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = migration
SPEC.loader.exec_module(migration)


class ConsumerManifestMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="consumer-manifest-migration-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project"
        self.project.mkdir()
        subprocess.run(["git", "init", "-b", "main", str(self.project)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.project), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(self.project), "config", "user.email", "test@example.invalid"], check=True)

    def commit_manifest(self, data):
        path = self.project / ".best-practices.json"
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.project), "add", ".best-practices.json"], check=True)
        subprocess.run(["git", "-C", str(self.project), "commit", "-m", "fixture"], check=True, capture_output=True)
        return path

    def decision(self):
        return {
            "outcome": "applied",
            "practice_path": "practices/common/example.md",
            "source_commit": "a" * 40,
            "recorded_at": "2026-07-07",
            "notes": "fixture",
        }

    def test_plan_is_read_only_and_preserves_outcomes(self):
        path = self.commit_manifest({"schema_version": 1, "practices": {"PC-2026-001": self.decision()}})
        before = path.read_bytes()
        plan = migration.build_plan(self.project)
        self.assertEqual("ready", plan.status)
        self.assertTrue(plan.fingerprint)
        desired = json.loads(plan.desired_text)
        self.assertEqual(2, desired["schema_version"])
        self.assertEqual(self.decision(), desired["practices"]["PC-2026-001"])
        self.assertEqual(before, path.read_bytes())

    def test_apply_is_atomic_reviewed_and_idempotent(self):
        path = self.commit_manifest({"schema_version": 1, "practices": {"PC-2026-001": self.decision()}})
        plan = migration.build_plan(self.project)
        applied = migration.apply_plan(self.project, plan.fingerprint)
        self.assertEqual("applied", applied.status)
        self.assertEqual(2, json.loads(path.read_text(encoding="utf-8"))["schema_version"])
        self.assertIn(".best-practices.json", subprocess.run(
            ["git", "-C", str(self.project), "status", "--porcelain"],
            check=True, capture_output=True, text=True,
        ).stdout)
        subprocess.run(["git", "-C", str(self.project), "add", ".best-practices.json"], check=True)
        subprocess.run(["git", "-C", str(self.project), "commit", "-m", "migrate"], check=True, capture_output=True)
        self.assertEqual("up_to_date", migration.build_plan(self.project).status)

    def test_global_optout_migrates_to_preferences(self):
        self.commit_manifest({"schema_version": 1, "optout": True})
        desired = json.loads(migration.build_plan(self.project).desired_text)
        self.assertEqual("optout", desired["preferences"]["global"])
        self.assertEqual({}, desired["practices"])

    def test_unknown_applied_requires_manual_review(self):
        self.commit_manifest({"schema_version": 1, "applied": ["common"]})
        plan = migration.build_plan(self.project)
        self.assertEqual("manual_review_required", plan.status)
        self.assertIn("applied", "\n".join(plan.blockers))

    def test_dirty_tree_blocks_plan(self):
        path = self.commit_manifest({"schema_version": 1, "practices": {}})
        path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        self.assertEqual("blocked", migration.build_plan(self.project).status)

    def test_fingerprint_mismatch_does_not_write(self):
        path = self.commit_manifest({"schema_version": 1, "practices": {}})
        before = path.read_bytes()
        result = migration.apply_plan(self.project, "0" * 64)
        self.assertEqual("blocked", result.status)
        self.assertEqual(before, path.read_bytes())

    def test_stale_preimage_blocks_old_fingerprint(self):
        path = self.commit_manifest({"schema_version": 1, "practices": {}})
        plan = migration.build_plan(self.project)
        path.write_text('{"schema_version": 1, "optout": true}\n', encoding="utf-8")
        result = migration.apply_plan(self.project, plan.fingerprint)
        self.assertEqual("blocked", result.status)
        self.assertNotEqual(2, json.loads(path.read_text(encoding="utf-8"))["schema_version"])

    def test_symlink_manifest_is_blocked(self):
        outside = Path(self.temp.name) / "outside.json"
        outside.write_text('{"schema_version": 1, "practices": {}}\n', encoding="utf-8")
        link = self.project / ".best-practices.json"
        try:
            link.symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"symlink unavailable: {exc}")
        subprocess.run(["git", "-C", str(self.project), "add", ".best-practices.json"], check=True)
        subprocess.run(["git", "-C", str(self.project), "commit", "-m", "fixture"], check=True, capture_output=True)
        self.assertEqual("blocked", migration.build_plan(self.project).status)

    def test_cli_requires_confirmation_and_fingerprint(self):
        self.commit_manifest({"schema_version": 1, "practices": {}})
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--project", str(self.project), "--apply"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, result.returncode)

    def test_cli_defaults_to_read_only_plan(self):
        path = self.commit_manifest({"schema_version": 1, "practices": {}})
        before = path.read_bytes()
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--project", str(self.project)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("status=ready", result.stdout)
        self.assertEqual(before, path.read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
