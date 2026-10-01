# AURA - Local Personal Assistant

AURA is a local-first Python desktop assistant. It uses local tools first and can use Ollama as its local model backend.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Ollama Configuration (Optional but Recommended)

1. Install and start Ollama locally.
2. Pull a model, for example:
   ```bash
   ollama pull llama3.1:8b
   ```
3. Default AURA config:
   - Base URL: `http://127.0.0.1:11434`
   - Model: `llama3.1:8b`

If Ollama is unavailable, AURA reports that and falls back to web-answer flow when possible.

## Implemented Tool/Action Architecture

AURA only exposes tools that are implemented:

- `open_application`, `close_application` (Windows process integrations)
- `list_directory`, `search_files`
- `create_folder`, `create_file`
- `read_file`, `summarize_file`
- `copy_path`, `move_path`, `rename_path`
- `trash_path` (safe delete via local trash folder)
- `open_file`
- `browser_open`, `browser_search` (via local default browser integration)
- `note_add`, `note_show`
- `send_email_with_confirmation`

## Safety and Confirmation

- Permanent deletion is not performed directly.
- `delete/remove` requests require confirmation and move items to local `data/trash`.
- Consequential actions like email sending require explicit `yes` confirmation immediately before execution.
- If a capability is not connected (for example, form submission automation), AURA returns an unavailable-capability response.

## Privacy

- Local-first behavior: no private local files are uploaded by default.
- Sensitive-looking lines (password/token/secret style lines) are redacted in direct file-read output.
- OAuth secrets are still local files (`credentials.json`, `token.json`) and are git-ignored.

## Cross-Platform Notes

- File operations and browser open/search are cross-platform (subject to OS/browser availability).
- App launch/close helpers currently use Windows-specific behavior and report unsupported on non-Windows platforms.

## Example Commands

- `open notepad`
- `close chrome`
- `find maths pdf`
- `list ./`
- `create folder notes/college`
- `create file notes/todo.txt | revise calculus`
- `read notes/todo.txt`
- `summarize notes/todo.txt`
- `copy notes/todo.txt to backup/todo.txt`
- `move backup/todo.txt to notes/todo-final.txt`
- `rename notes/todo-final.txt to todo-latest.txt`
- `delete notes/todo-latest.txt`
- `send email to someone@example.com | Subject | Message`
- `show notes`

## Gmail Setup

Follow `setup_gmail.md` and place OAuth credentials at repository root as `credentials.json`.

## Tests

```bash
python -m unittest discover -s tests -q
```
