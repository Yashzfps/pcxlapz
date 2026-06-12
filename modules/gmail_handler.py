"""Gmail send-email integration with OAuth."""

import base64
from email.message import EmailMessage
from pathlib import Path
from typing import Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GmailHandler:
    """Handles Gmail authentication and sending messages."""

    def __init__(self, credentials_file: Path, token_file: Path, scopes):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes
        self.token_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_credentials(self) -> Credentials:
        creds = None
        if self.token_file.exists():
            creds = Credentials.from_authorized_user_file(
                str(self.token_file), self.scopes
            )
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif not creds or not creds.valid:
            if not self.credentials_file.exists():
                raise FileNotFoundError(
                    f"Missing OAuth file: {self.credentials_file}. "
                    "Follow setup_gmail.md to create it."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_file), self.scopes
            )
            creds = flow.run_local_server(port=0)
        self.token_file.write_text(creds.to_json(), encoding="utf-8")
        return creds

    def send_email(self, to_email: str, subject: str, message: str) -> Tuple[bool, str]:
        """Compose and send a Gmail message."""
        try:
            creds = self._load_credentials()
            service = build("gmail", "v1", credentials=creds)

            mime_message = EmailMessage()
            mime_message["To"] = to_email
            mime_message["Subject"] = subject
            mime_message.set_content(message)

            raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode("utf-8")
            sent = (
                service.users()
                .messages()
                .send(userId="me", body={"raw": raw})
                .execute()
            )
            return True, f"Email sent! Message id: {sent.get('id', 'unknown')}"
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

