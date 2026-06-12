import tempfile
import unittest
from pathlib import Path

from core.file_manager import FileManager


class FileManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fm = FileManager()
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_organize_by_type(self) -> None:
        (self.base / "a.txt").write_text("x", encoding="utf-8")
        (self.base / "b.jpg").write_text("x", encoding="utf-8")

        result = self.fm.organize(self.base, mode="type")

        self.assertEqual(result["documents"], 1)
        self.assertEqual(result["images"], 1)
        self.assertTrue((self.base / "documents" / "a.txt").exists())
        self.assertTrue((self.base / "images" / "b.jpg").exists())

    def test_search_by_name(self) -> None:
        (self.base / "invoice_2026.txt").write_text("abc", encoding="utf-8")
        matches = self.fm.search(self.base, "invoice")
        self.assertEqual(len(matches), 1)
