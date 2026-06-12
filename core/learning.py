from __future__ import annotations

import sqlite3
from pathlib import Path

from config import settings
from utils.helpers import load_json, save_json


class LearningEngine:
    def __init__(self) -> None:
        self.preferences_file = settings.preferences_file
        self.db_file = settings.usage_db_file
        self._init_db()

    def _init_db(self) -> None:
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS usage_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def set_preference(self, key: str, value: str) -> None:
        prefs = load_json(self.preferences_file, {})
        prefs[key] = value
        save_json(self.preferences_file, prefs)

    def get_preference(self, key: str, default: str | None = None) -> str | None:
        prefs = load_json(self.preferences_file, {})
        return prefs.get(key, default)

    def record_action(self, action: str, context: str = "") -> None:
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("INSERT INTO usage_events(action, context) VALUES (?, ?)", (action, context))

    def top_actions(self, limit: int = 5) -> list[tuple[str, int]]:
        with sqlite3.connect(self.db_file) as conn:
            rows = conn.execute(
                "SELECT action, COUNT(*) as c FROM usage_events GROUP BY action ORDER BY c DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [(row[0], row[1]) for row in rows]

    def suggestions(self) -> list[str]:
        actions = self.top_actions(3)
        suggestions: list[str] = []
        for action, _ in actions:
            suggestions.append(f"You use '{action}' frequently; consider creating a recurring automation.")
        if not suggestions:
            suggestions.append("No usage data yet. Start using commands to get personalized suggestions.")
        return suggestions
