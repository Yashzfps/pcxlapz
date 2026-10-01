import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from modules.aura_assistant import AuraAssistant
from modules.notes import NotesManager


class TestAuraAssistant(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.notes = NotesManager(notes_file=self.workspace / "notes.json")
        self.gmail = MagicMock()
        self.assistant = AuraAssistant(
            notes_manager=self.notes,
            gmail_handler=self.gmail,
            workspace_root=self.workspace,
            ollama_client=MagicMock(generate=MagicMock(return_value=None)),
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("modules.aura_assistant.open_application")
    def test_dispatch_open_application(self, open_app):
        open_app.return_value = (True, "Opening notepad now~")
        reply = self.assistant.handle("open notepad")
        self.assertIn("Opening notepad", reply)
        open_app.assert_called_once()

    def test_delete_requires_confirmation_then_moves_to_trash(self):
        target = self.workspace / "sample.txt"
        target.write_text("hello", encoding="utf-8")

        first = self.assistant.handle(f"delete {target}")
        self.assertIn("Reply 'yes' or 'no'", first)
        self.assertTrue(target.exists())

        second = self.assistant.handle("yes")
        self.assertIn("Moved to trash", second)
        self.assertFalse(target.exists())

    def test_email_requires_confirmation(self):
        self.gmail.send_email.return_value = (True, "Email sent")
        reply = self.assistant.handle(
            "send email to test@example.com | Hello | Body content"
        )
        self.assertIn("Reply 'yes' to confirm", reply)
        self.gmail.send_email.assert_not_called()

        confirmed = self.assistant.handle("yes")
        self.assertIn("Email sent", confirmed)
        self.gmail.send_email.assert_called_once()

    def test_relative_path_is_resolved_to_workspace(self):
        reply = self.assistant.handle("create file notes/todo.txt | study")
        self.assertIn("File created", reply)
        created = self.workspace / "notes" / "todo.txt"
        self.assertTrue(created.exists())
        self.assertEqual(created.read_text(encoding="utf-8"), "study")

    @patch("modules.aura_assistant.open_application")
    def test_failure_reporting_for_missing_app(self, open_app):
        open_app.return_value = (False, "I couldn't find that app.")
        reply = self.assistant.handle("open imaginary-app")
        self.assertIn("Failed:", reply)


if __name__ == "__main__":
    unittest.main()
