# Rias - Windows Desktop Assistant

Rias is a Python-based desktop assistant with a cute, anime-style personality.

## Features

- Web search and concise Q&A answers
- Windows app launching (`open notepad`, `open chrome`)
- Gmail sending with OAuth (`send email to ... | Subject | Message`)
- Persistent note-taking (`note this down ...`, `show notes`)
- Consistent Rias personality in every response

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Commands

- `open <app>`
- `send email to recipient@example.com | Subject | Message`
- `note this down <text>`
- `show notes`
- Any other text is treated as a web search question
- `bye` / `exit` / `quit`

## Gmail Setup

Follow `setup_gmail.md` and place OAuth credentials at repository root as `credentials.json`.

## Testing

```bash
python -m unittest discover -s tests -q
```
