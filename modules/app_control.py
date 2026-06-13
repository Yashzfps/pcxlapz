import os
import subprocess
import sys
from typing import Dict, List, Tuple


APP_MAPPINGS: Dict[str, List[str]] = {
    "notepad": ["notepad.exe"],
    "chrome": ["chrome.exe"],
    "explorer": ["explorer.exe"],
    "calculator": ["calc.exe"],
    "paint": ["mspaint.exe"],
    "cmd": ["cmd.exe"],
    "powershell": ["powershell.exe"],
    "whatsapp": ["whatsapp"],
}


def open_application(app_name: str) -> Tuple[bool, str]:
    app_key = app_name.strip().lower()
    if not app_key:
        return False, "Tell me which app you want me to open."

    if sys.platform != "win32":
        return False, "App launching is available on Windows only."

    command = APP_MAPPINGS.get(app_key, [app_name])

    try:
        if app_key == "explorer":
            os.startfile(".")  # type: ignore[attr-defined]
        else:
            subprocess.Popen(command, shell=False)
    except FileNotFoundError:
        return False, f"I couldn't find '{app_name}' on this PC."
    except OSError as exc:
        return False, f"I couldn't open '{app_name}': {exc}"

    return True, f"Opening {app_name} now~"
