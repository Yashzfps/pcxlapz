from __future__ import annotations

from config import settings
from ui.cli import cli
from utils.helpers import ensure_dir, save_json


def bootstrap() -> None:
    ensure_dir(settings.data_dir)
    ensure_dir(settings.templates_dir)
    if not settings.preferences_file.exists():
        save_json(settings.preferences_file, {"theme": "light", "organize_mode": "type"})
    if not settings.tasks_file.exists():
        save_json(settings.tasks_file, [])
    if not settings.email_templates_file.exists():
        save_json(
            settings.email_templates_file,
            {
                "welcome": {
                    "subject": "Welcome {name}",
                    "body": "Hi {name},\n\nWelcome to Rias local assistant.\n",
                }
            },
        )


if __name__ == "__main__":
    bootstrap()
    cli()
