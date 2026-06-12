import tempfile
import unittest
from pathlib import Path

from modules.notes import NotesManager


class NotesManagerTests(unittest.TestCase):
    def test_add_and_get_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            notes_path = Path(tmp) / "notes.json"
            manager = NotesManager(notes_path)
            manager.add_note("first")
            manager.add_note("second")

            notes = manager.get_notes()
            self.assertEqual(2, len(notes))
            self.assertEqual("first", notes[0]["content"])
            self.assertEqual("second", notes[1]["content"])


if __name__ == "__main__":
    unittest.main()

