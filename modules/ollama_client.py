import json
from typing import Optional
from urllib import error, request

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS
from modules.prompts import AURA_SYSTEM_PROMPT


class OllamaClient:
    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
        timeout: int = OLLAMA_TIMEOUT_SECONDS,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, user_prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        payload = {
            "model": self.model,
            "prompt": user_prompt,
            "system": system_prompt or AURA_SYSTEM_PROMPT,
            "stream": False,
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                parsed = json.loads(resp.read().decode("utf-8"))
        except (error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return None

        response_text = parsed.get("response")
        if isinstance(response_text, str):
            return response_text.strip() or None
        return None
