import base64
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import GMAIL_CREDENTIALS_FILE, GMAIL_SCOPES, GMAIL_TOKEN_FILE


class GmailHandler:
    def __init__(
        self,
        credentials_file: Path = GMAIL_CREDENTIALS_FILE,
        token_file: Path = GMAIL_TOKEN_FILE,
    ):
        self.credentials_file = credentials_file
        self.token_file = token_file

    def _get_credentials(self) -> Optional[Credentials]:
        creds: Optional[Credentials] = None

        if self.token_file.exists():
            creds = Credentials.from_authorized_user_file(
                str(self.token_file),
                GMAIL_SCOPES,
            )

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self.token_file.write_text(creds.to_json(), encoding="utf-8")

        if not creds or not creds.valid:
            if not self.credentials_file.exists():
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_file),
                GMAIL_SCOPES,
            )
            creds = flow.run_local_server(port=0)
            self.token_file.write_text(creds.to_json(), encoding="utf-8")

        return creds

    def send_email(self, to_email: str, subject: str, message_text: str) -> Tuple[bool, str]:
        if not to_email.strip() or not subject.strip() or not message_text.strip():
            return False, "Recipient, subject, and message are all required."

        creds = self._get_credentials()
        if not creds:
            return False, "Missing credentials.json. Follow setup_gmail.md first."

        message = MIMEText(message_text)
        message["to"] = to_email
        message["subject"] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        try:
            service = build("gmail", "v1", credentials=creds)
            service.users().messages().send(
                userId="me",
                body={"raw": raw_message},
            ).execute()
        except HttpError as exc:
            return False, f"Gmail API error: {exc}"
        except Exception as exc:
            return False, f"Unexpected email error: {exc}"

        return True, f"Email sent to {to_email}!"
