import json
from pathlib import Path
from typing import Any, Dict, Optional

from config import PREFERENCES_FILE


class PreferencesManager:
    def __init__(self, preferences_file: Path = PREFERENCES_FILE):
        self.preferences_file = preferences_file
        self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.preferences_file.exists():
            self._write({})

    def _read(self) -> Dict[str, Any]:
        try:
            with self.preferences_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            pass
        return {}

    def _write(self, payload: Dict[str, Any]) -> None:
        with self.preferences_file.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    def set_value(self, key: str, value: str) -> None:
        data = self._read()
        data[key] = value
        self._write(data)

    def get_value(self, key: str) -> Optional[str]:
        data = self._read()
        value = data.get(key)
        return value if isinstance(value, str) else None
