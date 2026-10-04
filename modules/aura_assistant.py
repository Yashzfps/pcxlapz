import re
import shutil
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple

from config import TRASH_DIR
from modules.app_control import close_application, open_application
from modules.notes import NotesManager
from modules.ollama_client import OllamaClient
from modules.preferences import PreferencesManager

SUPPORTED_TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".py",
    ".json",
    ".csv",
    ".log",
    ".yaml",
    ".yml",
    ".ini",
}

YES_WORDS = {"yes", "y", "confirm", "ok", "do it", "haan", "ha", "kar do"}
NO_WORDS = {"no", "n", "cancel", "stop", "mat", "nah"}
CONSEQUENTIAL_HINTS = ("send email", "purchase", "buy", "publish", "submit", "delete account")


@dataclass
class PendingAction:
    prompt: str
    callback: Callable[[], str]


class AuraAssistant:
    def __init__(
        self,
        notes_manager: NotesManager,
        gmail_handler: Any,
        workspace_root: Optional[Path] = None,
        ollama_client: Optional[OllamaClient] = None,
        preferences: Optional[PreferencesManager] = None,
    ):
        self.notes_manager = notes_manager
        self.gmail_handler = gmail_handler
        self.workspace_root = workspace_root or Path.cwd()
        self.ollama_client = ollama_client or OllamaClient()
        self.preferences = preferences or PreferencesManager()
        self.pending_action: Optional[PendingAction] = None

    def available_tools(self) -> List[str]:
        return [
            "open_application",
            "close_application",
            "list_directory",
            "search_files",
            "create_folder",
            "create_file",
            "read_file",
            "summarize_file",
            "copy_path",
            "move_path",
            "rename_path",
            "trash_path",
            "open_file",
            "browser_open",
            "browser_search",
            "note_add",
            "note_show",
            "send_email_with_confirmation",
        ]

    def handle(self, command: str) -> str:
        clean_command = command.strip()
        if not clean_command:
            return "Say something and I’ll help."

        confirmation_response = self._handle_confirmation_response(clean_command)
        if confirmation_response is not None:
            return confirmation_response

        if " and " in clean_command.lower():
            return self._handle_multi_step(clean_command)

        lower_command = clean_command.lower()

        if lower_command in {"bye", "exit", "quit"}:
            return "Bye. I’ll be here when you need me."

        if "tool" in lower_command and ("list" in lower_command or "available" in lower_command):
            return "Available tools: " + ", ".join(self.available_tools())

        if lower_command == "show notes":
            return self.notes_manager.get_notes()

        if lower_command.startswith("note this down") or lower_command.startswith("make a note"):
            note_text = re.sub(r"^(note this down|make a note)\s*", "", clean_command, flags=re.IGNORECASE).strip()
            if not note_text:
                return "Tell me what note to save."
            self.notes_manager.add_note(note_text)
            return "Saved your note."

        email_command = self._parse_email_command(clean_command)
        if email_command is not None:
            recipient, subject, body = email_command
            if not recipient or not subject or not body:
                return "Use: send email to recipient@example.com | Subject | Message"
            preview = f"Send email to {recipient} with subject '{subject}'?"
            self.pending_action = PendingAction(
                prompt=preview,
                callback=lambda: self._send_email(recipient, subject, body),
            )
            return f"{preview} Reply 'yes' to confirm or 'no' to cancel."

        preference_response = self._handle_preference_command(clean_command)
        if preference_response:
            return preference_response

        parsed_file_action = self._dispatch_file_commands(clean_command)
        if parsed_file_action:
            return parsed_file_action

        parsed_app_action = self._dispatch_application_commands(clean_command)
        if parsed_app_action:
            return parsed_app_action

        parsed_browser_action = self._dispatch_browser_commands(clean_command)
        if parsed_browser_action:
            return parsed_browser_action

        if any(hint in lower_command for hint in CONSEQUENTIAL_HINTS):
            return "That consequential action is not connected in this local build."

        local_answer = self.ollama_client.generate(clean_command)
        if local_answer:
            return local_answer

        try:
            from modules.web_search import search_and_answer
        except Exception:
            return "Local Ollama is unavailable and web search integration is not installed."

        web_answer = search_and_answer(clean_command)
        return (
            f"Local Ollama response unavailable. Web result:\n{web_answer}"
            if web_answer
            else "I couldn't answer that right now."
        )

    def _handle_multi_step(self, command: str) -> str:
        parts = [part.strip() for part in re.split(r"\band\b", command, flags=re.IGNORECASE) if part.strip()]
        results: List[str] = []
        for part in parts:
            outcome = self.handle(part)
            results.append(f"- {outcome}")
            if self.pending_action is not None:
                break
        return "\n".join(results)

    def _handle_confirmation_response(self, command: str) -> Optional[str]:
        if not self.pending_action:
            return None

        normalized = command.strip().lower()
        if normalized in YES_WORDS:
            callback = self.pending_action.callback
            self.pending_action = None
            return callback()

        if normalized in NO_WORDS:
            self.pending_action = None
            return "Cancelled."

        return f"{self.pending_action.prompt} Reply 'yes' or 'no'."

    def _parse_email_command(self, command: str) -> Optional[Tuple[str, str, str]]:
        lower_command = command.lower()
        if not lower_command.startswith("send email to "):
            return None
        payload = command[len("send email to ") :].strip()
        parts = [part.strip() for part in payload.split("|")]
        if len(parts) != 3 or not all(parts):
            return ("", "", "")
        return parts[0], parts[1], parts[2]

    def _send_email(self, recipient: str, subject: str, body: str) -> str:
        if not recipient or not subject or not body:
            return "Use: send email to recipient@example.com | Subject | Message"
        sent, result = self.gmail_handler.send_email(
            to_email=recipient,
            subject=subject,
            message_text=body,
        )
        return result if sent else f"Failed: {result}"

    def _resolve_path(self, raw_path: str) -> Path:
        cleaned = raw_path.strip().strip('"').strip("'")
        expanded = Path(cleaned).expanduser()
        if expanded.is_absolute():
            return expanded
        return (self.workspace_root / expanded).resolve()

    def _handle_preference_command(self, command: str) -> Optional[str]:
        match = re.match(r"save notes in (.+)", command, flags=re.IGNORECASE)
        if match:
            path = self._resolve_path(match.group(1))
            self.preferences.set_value("notes_dir", str(path))
            return f"Saved note location preference: {path}"
        return None

    def _dispatch_file_commands(self, command: str) -> Optional[str]:
        list_match = re.match(r"(list|ls|show files in|check folder)\s+(.+)", command, flags=re.IGNORECASE)
        if list_match:
            return self._list_directory(list_match.group(2))

        search_match = re.match(r"(find|search files?)\s+(.+)", command, flags=re.IGNORECASE)
        if search_match:
            return self._search_files(search_match.group(2))

        create_folder_match = re.match(r"(create|make)\s+(folder|directory)\s+(.+)", command, flags=re.IGNORECASE)
        if create_folder_match:
            return self._create_folder(create_folder_match.group(3))

        create_file_match = re.match(r"create file\s+(.+?)(?:\s*\|\s*(.*))?$", command, flags=re.IGNORECASE)
        if create_file_match:
            path = create_file_match.group(1)
            content = create_file_match.group(2) or ""
            return self._create_file(path, content)

        read_match = re.match(r"(read|open file and read)\s+(.+)", command, flags=re.IGNORECASE)
        if read_match:
            return self._read_file(read_match.group(2), summarize=False)

        summarize_match = re.match(r"summarize\s+(.+)", command, flags=re.IGNORECASE)
        if summarize_match:
            return self._read_file(summarize_match.group(1), summarize=True)

        copy_match = re.match(r"copy\s+(.+?)\s+to\s+(.+)", command, flags=re.IGNORECASE)
        if copy_match:
            return self._copy_path(copy_match.group(1), copy_match.group(2))

        move_match = re.match(r"move\s+(.+?)\s+to\s+(.+)", command, flags=re.IGNORECASE)
        if move_match:
            return self._move_path(move_match.group(1), move_match.group(2))

        rename_match = re.match(r"rename\s+(.+?)\s+to\s+(.+)", command, flags=re.IGNORECASE)
        if rename_match:
            return self._rename_path(rename_match.group(1), rename_match.group(2))

        open_file_match = re.match(r"open file\s+(.+)", command, flags=re.IGNORECASE)
        if open_file_match:
            return self._open_file(open_file_match.group(1))

        delete_match = re.match(r"(delete|remove)\s+(.+)", command, flags=re.IGNORECASE)
        if delete_match:
            target_path = self._resolve_path(delete_match.group(2))
            self.pending_action = PendingAction(
                prompt=f"Move '{target_path}' to trash?",
                callback=lambda: self._trash_path(target_path),
            )
            return f"Move '{target_path}' to trash? Reply 'yes' or 'no'."

        return None

    def _dispatch_application_commands(self, command: str) -> Optional[str]:
        open_match = re.match(r"(open|launch|start|khol|kholo)\s+(.+)", command, flags=re.IGNORECASE)
        if open_match:
            opened, message = open_application(open_match.group(2))
            return message if opened else f"Failed: {message}"

        close_match = re.match(r"(close|band|stop)\s+(.+)", command, flags=re.IGNORECASE)
        if close_match:
            closed, message = close_application(close_match.group(2))
            return message if closed else f"Failed: {message}"
        return None

    def _dispatch_browser_commands(self, command: str) -> Optional[str]:
        open_url_match = re.match(r"(open (website|site)|browser open)\s+(.+)", command, flags=re.IGNORECASE)
        if open_url_match:
            return self._browser_open(open_url_match.group(3))

        if command.lower().startswith("open http"):
            return self._browser_open(command[5:].strip())

        search_match = re.match(r"(browser search|search on browser|search web for)\s+(.+)", command, flags=re.IGNORECASE)
        if search_match:
            return self._browser_search(search_match.group(2))

        if "search this on browser" in command.lower():
            query = command.lower().split("search this on browser", 1)[1].strip()
            return self._browser_search(query) if query else "Tell me what to search."
        return None

    def _list_directory(self, raw_path: str) -> str:
        target = self._resolve_path(raw_path)
        if not target.exists():
            return f"Path not found: {target}"
        if not target.is_dir():
            return f"Not a directory: {target}"
        entries = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        if not entries:
            return f"{target} is empty."
        preview = [f"{'[DIR]' if entry.is_dir() else '[FILE]'} {entry.name}" for entry in entries[:30]]
        suffix = "" if len(entries) <= 30 else f"\n...and {len(entries) - 30} more"
        return f"Contents of {target}:\n" + "\n".join(preview) + suffix

    def _search_files(self, query: str) -> str:
        needle = query.strip().lower()
        if not needle:
            return "Tell me what file name to search."
        matches: List[Path] = []
        roots = [self.workspace_root, Path.home() / "Downloads", Path.home() / "Documents", Path.home() / "Desktop"]
        seen = set()
        for root in roots:
            if root in seen or not root.exists():
                continue
            seen.add(root)
            try:
                for item in root.rglob("*"):
                    if len(matches) >= 20:
                        break
                    if needle in item.name.lower():
                        matches.append(item)
            except OSError:
                continue
            if len(matches) >= 20:
                break

        if not matches:
            return f"No files matched '{query}'."
        return "Found:\n" + "\n".join(f"- {item}" for item in matches)

    def _create_folder(self, raw_path: str) -> str:
        target = self._resolve_path(raw_path)
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return f"Failed to create folder: {exc}"
        return f"Folder ready: {target}"

    def _create_file(self, raw_path: str, content: str) -> str:
        target = self._resolve_path(raw_path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        except OSError as exc:
            return f"Failed to create file: {exc}"
        return f"File created: {target}"

    def _redact_sensitive_lines(self, text: str) -> str:
        redacted: List[str] = []
        for line in text.splitlines():
            lower = line.lower()
            if any(key in lower for key in ["password", "token", "api_key", "apikey", "secret", "cookie"]):
                redacted.append("[REDACTED SENSITIVE LINE]")
            else:
                redacted.append(line)
        return "\n".join(redacted)

    def _read_file(self, raw_path: str, summarize: bool) -> str:
        target = self._resolve_path(raw_path)
        if not target.exists() or not target.is_file():
            return f"File not found: {target}"
        if target.suffix.lower() not in SUPPORTED_TEXT_EXTENSIONS:
            return f"Unsupported file type for direct reading: {target.suffix or 'unknown'}"

        try:
            content = target.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return f"Failed to read file: {exc}"

        safe_content = self._redact_sensitive_lines(content)
        if not summarize:
            preview = safe_content[:2000]
            suffix = "" if len(safe_content) <= 2000 else "\n...output truncated."
            return f"{target}:\n{preview}{suffix}"

        summary_prompt = f"Summarize this file in concise bullet points:\n\n{safe_content[:4000]}"
        summary = self.ollama_client.generate(summary_prompt)
        if summary:
            return f"Summary of {target}:\n{summary}"
        return f"Ollama unavailable. Read preview instead:\n{safe_content[:800]}"

    def _copy_path(self, source_raw: str, destination_raw: str) -> str:
        source = self._resolve_path(source_raw)
        destination = self._resolve_path(destination_raw)
        if not source.exists():
            return f"Source not found: {source}"
        try:
            if source.is_dir():
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        except OSError as exc:
            return f"Copy failed: {exc}"
        return f"Copied to {destination}"

    def _move_path(self, source_raw: str, destination_raw: str) -> str:
        source = self._resolve_path(source_raw)
        destination = self._resolve_path(destination_raw)
        if not source.exists():
            return f"Source not found: {source}"
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
        except OSError as exc:
            return f"Move failed: {exc}"
        return f"Moved to {destination}"

    def _rename_path(self, source_raw: str, new_name: str) -> str:
        source = self._resolve_path(source_raw)
        if not source.exists():
            return f"Path not found: {source}"
        target = source.with_name(new_name.strip())
        try:
            source.rename(target)
        except OSError as exc:
            return f"Rename failed: {exc}"
        return f"Renamed to {target.name}"

    def _trash_path(self, target: Path) -> str:
        if not target.exists():
            return f"Path not found: {target}"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        destination = TRASH_DIR / f"{timestamp}_{target.name}"
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), str(destination))
        except OSError as exc:
            return f"Trash move failed: {exc}"
        return f"Moved to trash: {destination}"

    def _open_file(self, raw_path: str) -> str:
        target = self._resolve_path(raw_path)
        if not target.exists():
            return f"File not found: {target}"
        try:
            opened = webbrowser.open(target.resolve().as_uri())
        except Exception as exc:
            return f"Could not open file: {exc}"
        return "Opened file." if opened else "I couldn't open that file with available local integrations."

    def _browser_open(self, url: str) -> str:
        normalized = url.strip()
        if not normalized:
            return "Provide a URL."
        if not normalized.startswith(("http://", "https://")):
            normalized = f"https://{normalized}"
        try:
            opened = webbrowser.open(normalized)
        except Exception as exc:
            return f"Browser open failed: {exc}"
        return f"Opened {normalized}" if opened else "Browser integration is unavailable on this environment."

    def _browser_search(self, query: str) -> str:
        clean_query = query.strip()
        if not clean_query:
            return "Tell me what to search."
        search_url = "https://duckduckgo.com/?q=" + clean_query.replace(" ", "+")
        return self._browser_open(search_url)
