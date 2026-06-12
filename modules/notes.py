"""Simple persistent note-taking module."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict


class NotesManager:
    """Manages notes persisted in a JSON file."""

    def __init__(self, notes_file: Path) -> None:
        self.notes_file = notes_file
        self.notes_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.notes_file.exists():
            self.notes_file.write_text("[]", encoding="utf-8")

    def _load(self) -> List[Dict[str, str]]:
        try:
            return json.loads(self.notes_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, notes: List[Dict[str, str]]) -> None:
        self.notes_file.write_text(
            json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def add_note(self, content: str) -> Dict[str, str]:
        note = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "content": content.strip(),
        }
        notes = self._load()
        notes.append(note)
        self._save(notes)
        return note

    def get_notes(self) -> List[Dict[str, str]]:
        return self._load()
