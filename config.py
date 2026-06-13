from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NOTES_FILE = DATA_DIR / "notes.json"
GMAIL_CREDENTIALS_FILE = BASE_DIR / "credentials.json"
GMAIL_TOKEN_FILE = BASE_DIR / "token.json"

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

WEB_SEARCH_MAX_RESULTS = 5
WEB_SEARCH_SNIPPET_LIMIT = 2

DATA_DIR.mkdir(parents=True, exist_ok=True)
