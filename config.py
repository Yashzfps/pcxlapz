from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    project_root: Path = Path(__file__).resolve().parent
    data_dir: Path = project_root / "data"
    templates_dir: Path = data_dir / "templates"
    preferences_file: Path = data_dir / "preferences.json"
    tasks_file: Path = data_dir / "tasks.json"
    email_templates_file: Path = templates_dir / "emails.json"
    usage_db_file: Path = data_dir / "usage.sqlite3"
    log_file: Path = data_dir / "rias.log"
    smtp_host: str = os.getenv("RIAS_SMTP_HOST", "")
    smtp_port: int = int(os.getenv("RIAS_SMTP_PORT", "587"))
    smtp_user: str = os.getenv("RIAS_SMTP_USER", "")
    smtp_password: str = os.getenv("RIAS_SMTP_PASSWORD", "")
    smtp_sender: str = os.getenv("RIAS_SMTP_SENDER", "")


settings = Settings()
