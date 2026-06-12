"""Windows app control module."""

import os
import shutil
import subprocess
from typing import Optional


APP_COMMANDS = {
    "notepad": ["notepad"],
    "chrome": ["chrome"],
    "google chrome": ["chrome"],
    "whatsapp": ["whatsapp"],
    "calculator": ["calc"],
    "paint": ["mspaint"],
    "cmd": ["cmd"],
    "powershell": ["powershell"],
}


def _resolve_command(app_name: str) -> Optional[list]:
    app_name = app_name.strip().lower()
    if app_name in APP_COMMANDS:
        return APP_COMMANDS[app_name]
    if shutil.which(app_name):
        return [app_name]
    return None


def open_application(app_name: str) -> str:
    """Open a Windows application by name."""
    if os.name != "nt":
        return "App launching is supported on Windows only."

    command = _resolve_command(app_name)
    if not command:
        return f"I couldn't find '{app_name}'. Try a full executable name."

    try:
        subprocess.Popen(command, shell=False)
        return f"Opened {app_name}!"
    except OSError as exc:
        return f"Couldn't open {app_name}: {exc}"

