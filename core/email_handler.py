from __future__ import annotations

import smtplib
from email.message import EmailMessage
from pathlib import Path

from config import settings
from utils.helpers import load_json, save_json
from utils.logger import get_logger


logger = get_logger(__name__)


class EmailHandler:
    def __init__(self) -> None:
        self.templates = load_json(settings.email_templates_file, {})
        self.history_file = settings.data_dir / "email_history.json"

    def save_template(self, name: str, subject: str, body: str) -> None:
        self.templates[name] = {"subject": subject, "body": body}
        save_json(settings.email_templates_file, self.templates)

    def list_templates(self) -> dict[str, dict[str, str]]:
        return dict(self.templates)

    def render_template(self, name: str, **kwargs: str) -> tuple[str, str]:
        if name not in self.templates:
            raise KeyError(f"Template not found: {name}")
        template = self.templates[name]
        return template["subject"].format(**kwargs), template["body"].format(**kwargs)

    def compose(self, to_email: str, subject: str, body: str) -> EmailMessage:
        msg = EmailMessage()
        msg["From"] = settings.smtp_sender or settings.smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)
        return msg

    def send(self, to_email: str, subject: str, body: str) -> None:
        if not all([settings.smtp_host, settings.smtp_user, settings.smtp_password]):
            raise ValueError("SMTP settings are incomplete. Set env vars in .env")

        msg = self.compose(to_email, subject, body)
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            smtp.starttls()
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
        self._append_history(to_email, subject)
        logger.info("Email sent to %s", to_email)

    def send_from_template(self, template_name: str, to_email: str, **kwargs: str) -> None:
        subject, body = self.render_template(template_name, **kwargs)
        self.send(to_email, subject, body)

    def _append_history(self, to_email: str, subject: str) -> None:
        history = load_json(self.history_file, [])
        history.append({"to": to_email, "subject": subject})
        save_json(self.history_file, history)
