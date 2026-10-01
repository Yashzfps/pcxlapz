from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NOTES_FILE = DATA_DIR / "notes.json"
PREFERENCES_FILE = DATA_DIR / "preferences.json"
TRASH_DIR = DATA_DIR / "trash"
GMAIL_CREDENTIALS_FILE = BASE_DIR / "credentials.json"
GMAIL_TOKEN_FILE = BASE_DIR / "token.json"

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

WEB_SEARCH_MAX_RESULTS = 5
WEB_SEARCH_SNIPPET_LIMIT = 2

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_TIMEOUT_SECONDS = 20

DATA_DIR.mkdir(parents=True, exist_ok=True)
TRASH_DIR.mkdir(parents=True, exist_ok=True)
