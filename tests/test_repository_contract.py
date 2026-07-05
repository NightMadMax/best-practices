import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_workflow_uses_read_only_permissions_and_pinned_actions(self):
        workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read", workflow)
        uses = re.findall(r"^\s*uses:\s*([^\s#]+)", workflow, flags=re.MULTILINE)
        self.assertTrue(uses)
        for action in uses:
            self.assertRegex(action, r"^[^@]+@[0-9a-f]{40}$")

    def test_codeowners_protects_governance_and_content(self):
        codeowners = (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8")
        self.assertRegex(codeowners, r"(?m)^/\.github/\s+@\S+")
        self.assertRegex(codeowners, r"(?m)^/candidates/\s+@\S+")
        self.assertRegex(codeowners, r"(?m)^/practices/common/\s+@\S+")

    def test_pull_request_template_requires_local_check(self):
        template = (ROOT / ".github/pull_request_template.md").read_text(encoding="utf-8")
        self.assertIn("`make check`", template)
        self.assertIn("`source`", template)
        self.assertIn("`evidence`", template)

    def test_claude_skill_metadata_matches_canonical_skills(self):
        canonical_root = ROOT / ".agents/skills"
        claude_root = ROOT / ".claude/skills"
        for canonical_path in canonical_root.glob("*/SKILL.md"):
            claude_path = claude_root / canonical_path.parent.name / "SKILL.md"
            self.assertTrue(claude_path.is_file(), f"missing Claude pointer for {canonical_path}")
            canonical = canonical_path.read_text(encoding="utf-8")
            pointer = claude_path.read_text(encoding="utf-8")
            for field in ("name", "description"):
                pattern = rf"(?m)^{field}:\s*(.+)$"
                canonical_value = re.search(pattern, canonical)
                pointer_value = re.search(pattern, pointer)
                self.assertIsNotNone(canonical_value)
                self.assertIsNotNone(pointer_value)
                self.assertEqual(canonical_value.group(1), pointer_value.group(1))
            self.assertIn("../../../.agents/skills/", pointer)


if __name__ == "__main__":
    unittest.main()
