"""Configuration for the Rias desktop assistant."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NOTES_FILE = DATA_DIR / "notes.json"

# DuckDuckGo doesn't require API keys for the library used in this project.
WEB_SEARCH_RESULTS = 5

# Gmail OAuth settings
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = DATA_DIR / "token.json"

