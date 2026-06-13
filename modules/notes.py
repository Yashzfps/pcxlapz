import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from config import NOTES_FILE


class NotesManager:
    def __init__(self, notes_file: Path = NOTES_FILE):
        self.notes_file = notes_file
        self.notes_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.notes_file.exists():
            self._write_notes([])

    def _read_notes(self) -> List[Dict[str, str]]:
        try:
            with self.notes_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, OSError):
            pass
        return []

    def _write_notes(self, notes: List[Dict[str, str]]) -> None:
        with self.notes_file.open("w", encoding="utf-8") as file:
            json.dump(notes, file, ensure_ascii=False, indent=2)

    def add_note(self, text: str) -> None:
        if not text.strip():
            return

        notes = self._read_notes()
        notes.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "text": text.strip(),
            }
        )
        self._write_notes(notes)

    def get_notes(self) -> str:
        notes = self._read_notes()
        if not notes:
            return "No notes yet. Tell me 'note this down ...' and I'll save it!"

        formatted_lines = []
        for idx, note in enumerate(notes, start=1):
            formatted_lines.append(
                f"{idx}. [{note.get('timestamp', 'unknown time')}] {note.get('text', '')}"
            )

        return "\n".join(formatted_lines)
