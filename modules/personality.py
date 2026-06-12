"""Personality formatting for Rias."""


class RiasPersonality:
    """Formats all assistant responses in a playful anime-like tone."""

    def style(self, message: str) -> str:
        return f"Rias: {message} ✨"

    def greeting(self) -> str:
        return self.style("Hii~ Onii-chan! I'm Rias, ready to help you today!")

    def success(self, message: str) -> str:
        return self.style(f"Done done~ {message}")

    def info(self, message: str) -> str:
        return self.style(message)

    def error(self, message: str) -> str:
        return self.style(f"Eeep, I hit a tiny problem: {message}")

