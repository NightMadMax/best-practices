import tempfile
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
import validate  # noqa: E402


VALID_CANDIDATE = """---
id: PC-2026-001
status: triaged
source: "sample: docs/quality/DEFECTS.md #1"
added_by: "test"
stack: common
target: practices/common/PC-2026-001-check-input.md
evidence_level: E1
evidence: "test-case"
created: 2026-07-05
decided:
---

# Проверять входные данные

- **Контекст:** обработка внешних данных.
- **Проблема:** невалидный ввод приводит к ошибкам.
- **Решение:** валидировать данные на границе.
"""

VALID_PRACTICE = """---
id: PC-2026-001
status: trial
source: "sample: docs/quality/DEFECTS.md #1"
added_by: "test"
stack: common
tags: "validation, boundary"
applies_to: "обработка внешнего ввода"
does_not_apply_to: "полностью доверенные внутренние константы"
evidence_level: E1
evidence: "test-case"
owner: "@maintainer"
created: 2026-07-05
last_verified: 2026-07-05
review_by: 2026-10-05
supersedes:
conflicts_with:
candidate: candidates/PC-2026-001-check-input.md
---

# Проверять входные данные

- **Контекст:** обработка внешних данных.
- **Проблема:** невалидный ввод приводит к ошибкам.
- **Решение:** валидировать данные на границе.
- **Проверка:** негативный тест отклоняет неверный ввод.
"""


class RepositoryFixture:
    def __enter__(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "candidates").mkdir()
        (self.root / "practices/common").mkdir(parents=True)
        (self.root / "practices/common/README.md").write_text("# Common\n", encoding="utf-8")
        return self.root

    def __exit__(self, *args):
        self.temp_dir.cleanup()


class CandidateValidationTests(unittest.TestCase):
    def test_valid_candidate_passes(self):
        with RepositoryFixture() as root:
            path = root / "candidates/PC-2026-001-check-input.md"
            path.write_text(VALID_CANDIDATE, encoding="utf-8")
            self.assertEqual([], validate.validate_repository(root, check_links=False))

    def test_id_must_match_filename(self):
        with RepositoryFixture() as root:
            path = root / "candidates/PC-2026-002-check-input.md"
            path.write_text(VALID_CANDIDATE, encoding="utf-8")
            messages = [p.message for p in validate.validate_repository(root, check_links=False)]
            self.assertTrue(any("does not match filename" in message for message in messages))

    def test_duplicate_ids_are_rejected(self):
        with RepositoryFixture() as root:
            first = root / "candidates/PC-2026-001-first.md"
            second = root / "candidates/PC-2026-001-second.md"
            first.write_text(VALID_CANDIDATE, encoding="utf-8")
            second.write_text(VALID_CANDIDATE, encoding="utf-8")
            messages = [p.message for p in validate.validate_repository(root, check_links=False)]
            self.assertTrue(any("duplicate id" in message for message in messages))

    def test_decided_is_required_for_terminal_status(self):
        with RepositoryFixture() as root:
            path = root / "candidates/PC-2026-001-check-input.md"
            content = VALID_CANDIDATE.replace("status: triaged", "status: accepted")
            path.write_text(content, encoding="utf-8")
            messages = [p.message for p in validate.validate_repository(root, check_links=False)]
            self.assertTrue(any("requires decided" in message for message in messages))

    def test_unknown_status_and_wrong_target_are_rejected(self):
        with RepositoryFixture() as root:
            path = root / "candidates/PC-2026-001-check-input.md"
            content = VALID_CANDIDATE.replace("status: triaged", "status: published")
            content = content.replace("practices/common/PC-2026-001-check-input.md", "practices/web/PC-2026-001-check-input.md")
            path.write_text(content, encoding="utf-8")
            messages = [p.message for p in validate.validate_repository(root, check_links=False)]
            self.assertTrue(any("unsupported status" in message for message in messages))
            self.assertTrue(any("target must be" in message for message in messages))

    def test_tools_candidate_requires_tool_fields(self):
        with RepositoryFixture() as root:
            (root / "practices/tools").mkdir()
            (root / "practices/tools/README.md").write_text("# Tools\n", encoding="utf-8")
            path = root / "candidates/PC-2026-001-check-input.md"
            content = VALID_CANDIDATE.replace("stack: common", "stack: tools")
            content = content.replace("practices/common/PC-2026-001-check-input.md", "practices/tools/PC-2026-001-check-input.md")
            path.write_text(content, encoding="utf-8")
            messages = [p.message for p in validate.validate_repository(root, check_links=False)]
            self.assertTrue(any("body field 'Назначение'" in message for message in messages))

    def test_secret_and_machine_path_are_rejected(self):
        with RepositoryFixture() as root:
            path = root / "candidates/PC-2026-001-check-input.md"
            content = VALID_CANDIDATE + "\nToken: ghp_abcdefghijklmnopqrstuvwxyz123456\n/Users/alice/project\n"
            path.write_text(content, encoding="utf-8")
            messages = [p.message for p in validate.validate_repository(root, check_links=False)]
            self.assertTrue(any("GitHub token" in message for message in messages))
            self.assertTrue(any("machine-specific path" in message for message in messages))

    def test_broken_wikilink_is_rejected(self):
        with RepositoryFixture() as root:
            note = root / "README.md"
            note.write_text("See [[missing/note]].\n", encoding="utf-8")
            messages = [p.message for p in validate.validate_repository(root)]
            self.assertTrue(any("broken wikilink" in message for message in messages))

    def test_escaped_wikilink_alias_is_supported(self):
        with RepositoryFixture() as root:
            (root / "candidates/README.md").write_text("# Candidates\n", encoding="utf-8")
            note = root / "README.md"
            note.write_text("See [[candidates/README\\|candidates/]].\n", encoding="utf-8")
            self.assertEqual([], validate.validate_repository(root))

    def test_accepted_candidate_can_create_trial_practice(self):
        with RepositoryFixture() as root:
            candidate = root / "candidates/PC-2026-001-check-input.md"
            accepted = VALID_CANDIDATE.replace("status: triaged", "status: accepted")
            accepted = accepted.replace("decided:\n", "decided: 2026-07-05\n")
            candidate.write_text(accepted, encoding="utf-8")
            practice = root / "practices/common/PC-2026-001-check-input.md"
            practice.write_text(VALID_PRACTICE, encoding="utf-8")
            self.assertEqual([], validate.validate_repository(root, check_links=False))

    def test_accepted_practice_requires_e2(self):
        with RepositoryFixture() as root:
            candidate = root / "candidates/PC-2026-001-check-input.md"
            accepted = VALID_CANDIDATE.replace("status: triaged", "status: accepted")
            accepted = accepted.replace("decided:\n", "decided: 2026-07-05\n")
            candidate.write_text(accepted, encoding="utf-8")
            practice = root / "practices/common/PC-2026-001-check-input.md"
            practice.write_text(VALID_PRACTICE.replace("status: trial", "status: accepted"), encoding="utf-8")
            messages = [p.message for p in validate.validate_repository(root, check_links=False)]
            self.assertTrue(any("requires evidence_level E2" in message for message in messages))

    def test_invalid_calendar_date_is_rejected(self):
        with RepositoryFixture() as root:
            path = root / "candidates/PC-2026-001-check-input.md"
            path.write_text(VALID_CANDIDATE.replace("2026-07-05", "2026-02-30"), encoding="utf-8")
            messages = [p.message for p in validate.validate_repository(root, check_links=False)]
            self.assertTrue(any("created must use" in message for message in messages))

    def test_expired_review_date_is_reported(self):
        with RepositoryFixture() as root:
            candidate = root / "candidates/PC-2026-001-check-input.md"
            accepted = VALID_CANDIDATE.replace("status: triaged", "status: accepted")
            accepted = accepted.replace("decided:\n", "decided: 2026-07-05\n")
            candidate.write_text(accepted, encoding="utf-8")
            practice = root / "practices/common/PC-2026-001-check-input.md"
            practice.write_text(VALID_PRACTICE.replace("2026-10-05", "2026-01-01"), encoding="utf-8")
            stale = validate.find_stale_practices(root, today=date(2026, 7, 5))
            self.assertEqual(1, len(stale))
            self.assertIn("review_by expired", stale[0].message)


if __name__ == "__main__":
    unittest.main()
