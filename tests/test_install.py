"""Testes offline da instalação global, sem tocar na home real."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install.py"
SPEC = importlib.util.spec_from_file_location("skill_installer", SCRIPT)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.source = self.home / "source"
        self.source.mkdir()
        (self.source / "SKILL.md").write_text("skill", encoding="utf-8")
        self.root = self.home / "skills"

    def test_core_roots(self):
        self.assertEqual(len(installer.skill_roots(self.home)), 4)

    def test_all_roots(self):
        roots = installer.skill_roots(self.home, True)
        self.assertGreaterEqual(len(roots), 11)
        self.assertIn(self.home / ".config/opencode/skill", roots)
        self.assertIn(self.home / ".config/opencode/skills", roots)

    def test_account_detection(self):
        (self.home / ".claude-extra").mkdir()
        roots = installer.skill_roots(self.home)
        self.assertIn(self.home / ".claude-extra" / "skills", roots)
        self.assertEqual(len(roots), len(set(roots)))

    def test_check_does_not_create(self):
        rows = installer.install(self.source, [self.root], check=True)
        self.assertEqual(rows[0]["status"], "missing")
        self.assertFalse(self.root.exists())

    def test_dry_run_does_not_create(self):
        rows = installer.install(self.source, [self.root], dry_run=True)
        self.assertEqual(rows[0]["status"], "would-link")
        self.assertFalse(self.root.exists())

    def test_directory_conflict_preserved(self):
        destination = self.root / installer.NAME
        destination.mkdir(parents=True)
        (destination / "keep.txt").write_text("preserve", encoding="utf-8")
        rows = installer.install(self.source, [self.root])
        self.assertEqual(rows[0]["status"], "conflict")
        self.assertEqual((destination / "keep.txt").read_text(), "preserve")

    def test_symlink_idempotent(self):
        rows = installer.install(self.source, [self.root])
        if rows[0]["status"] == "error":
            self.skipTest("sistema sem permissão para criar symlinks")
        self.assertEqual(rows[0]["status"], "linked")
        self.assertTrue((self.root / installer.NAME).is_symlink())
        self.assertEqual(installer.install(self.source, [self.root])[0]["status"], "ok")
        self.assertEqual(installer.install(self.source, [self.root], check=True)[0]["status"], "ok")

    def test_missing_skill_rejected(self):
        (self.source / "SKILL.md").unlink()
        with self.assertRaises(ValueError):
            installer.install(self.source, [self.root])


if __name__ == "__main__":
    unittest.main()
