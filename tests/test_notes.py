import tempfile
import unittest
from pathlib import Path

from modules.notes import NotesManager


class TestNotesManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.notes_path = Path(self.temp_dir.name) / "notes.json"
        self.manager = NotesManager(notes_file=self.notes_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_note_and_get_notes(self):
        self.manager.add_note("Buy groceries")
        self.manager.add_note("Call friend")

        output = self.manager.get_notes()

        self.assertIn("Buy groceries", output)
        self.assertIn("Call friend", output)
        self.assertIn("1.", output)
        self.assertIn("2.", output)

    def test_get_notes_when_empty(self):
        output = self.manager.get_notes()
        self.assertIn("No notes yet", output)


if __name__ == "__main__":
    unittest.main()
