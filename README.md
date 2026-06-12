# Rias - Local Desktop Assistant

Rias is a complete local desktop assistant that runs entirely on your machine.

## Features

- **File & Folder Management**: list, organize, search, analyze, and clean folders.
- **Task Automation**: create/list/complete/delete tasks with local persistence.
- **Email Integration**: SMTP sending + reusable templates.
- **Learning & Adaptation**: local preferences + usage tracking in SQLite.
- **CLI Interface**: full command groups for file, task, email, and preferences.

## Project Structure

```
pcxlapz/
├── main.py
├── requirements.txt
├── config.py
├── data/
│   ├── preferences.json
│   ├── tasks.json
│   └── templates/
│       └── emails.json
├── core/
│   ├── __init__.py
│   ├── file_manager.py
│   ├── task_manager.py
│   ├── email_handler.py
│   └── learning.py
├── ui/
│   ├── __init__.py
│   ├── cli.py
│   └── gui.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── helpers.py
└── tests/
    ├── test_file_manager.py
    └── test_task_learning.py
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optionally set SMTP env vars in a `.env` file:

```env
RIAS_SMTP_HOST=smtp.example.com
RIAS_SMTP_PORT=587
RIAS_SMTP_USER=you@example.com
RIAS_SMTP_PASSWORD=app_password
RIAS_SMTP_SENDER=you@example.com
```

## Run

```bash
python main.py --help
```

## CLI Examples

```bash
# Files
python main.py files list /path/to/folder
python main.py files organize /path/to/folder --mode type
python main.py files search /path/to/folder invoice --content
python main.py files analyze /path/to/folder
python main.py files clean /path/to/folder

# Tasks
python main.py task create "Backup docs" --recurring "daily"
python main.py task list
python main.py task complete <task_id>
python main.py task delete <task_id>

# Email templates and sending
python main.py email-cmd template-save followup "Follow-up" "Hi {name}, checking in."
python main.py email-cmd template-list
python main.py email-cmd send-template followup person@example.com --var name=Alex

# Preferences / learning
python main.py prefs set organize_mode date
python main.py prefs get organize_mode
python main.py prefs suggest
```

## Tests

```bash
python -m unittest discover -s tests -q
```
