"""Regressões portáveis do gate de qualidade do repositório."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check.py"
SPEC = importlib.util.spec_from_file_location("repo_check", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class CheckTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for folder in ("scripts", "tests", "skills", ".github", ".claude-plugin"):
            (self.root / folder).mkdir()
        for name in ("LICENSE", "README.md", "CONTRIBUTING.md", "SECURITY.md",
                     "CODEOWNERS", "CHANGELOG.md", "AGENTS.md",
                     "skills/web-search-openrouter-agent-skill/SKILL.md"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("ok\n", encoding="utf-8")
        self.patcher = patch.object(module, "ROOT", self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_clean(self):
        self.assertEqual(module.check(), [])

    def test_ast_rejects_invalid_python(self):
        (self.root / "scripts/bad.py").write_text("if :\n", encoding="utf-8")
        self.assertTrue(any("bad.py" in error for error in module.check()))

    def test_action_requires_sha(self):
        (self.root / ".github/test.yml").write_text("uses: actions/checkout@v4\n", encoding="utf-8")
        self.assertTrue(any("fixada" in error for error in module.check()))

    def test_markdown_missing_link(self):
        (self.root / "README.md").write_text("[fonte](missing.md)\n", encoding="utf-8")
        self.assertTrue(any("link inexistente" in error for error in module.check()))

    def test_examples_not_link_checked(self):
        (self.root / "README.md").write_text("```text\n[x](missing.md)\n```\n", encoding="utf-8")
        self.assertEqual(module.check(), [])

    def test_version_portable_paths(self):
        (self.root / "version.txt").write_text("0.1.0\n", encoding="utf-8")
        (self.root / ".claude-plugin/plugin.json").write_text(json.dumps({"version": "0.1.0"}) + "\n", encoding="utf-8")
        (self.root / ".release-please-manifest.json").write_text(json.dumps({".": "0.1.0"}) + "\n", encoding="utf-8")
        self.assertEqual(module.check(), [])

    def test_version_disagreement(self):
        (self.root / "version.txt").write_text("0.1.0\n", encoding="utf-8")
        self.assertTrue(any("divergem" in error for error in module.check()))


if __name__ == "__main__":
    unittest.main()
