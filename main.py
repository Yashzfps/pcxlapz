from modules.aura_assistant import AuraAssistant
from modules.gmail_handler import GmailHandler
from modules.notes import NotesManager
from modules.personality import error, greeting, info, style, success


def process_command(command: str, assistant: AuraAssistant) -> str:
    response = assistant.handle(command)
    lower_response = response.lower()
    if lower_response.startswith("failed") or "couldn't" in lower_response:
        return error(response)
    if lower_response.startswith("cancelled"):
        return info(response)
    return success(response)


def run_assistant() -> None:
    notes_manager = NotesManager()
    gmail_handler = GmailHandler()
    assistant = AuraAssistant(notes_manager=notes_manager, gmail_handler=gmail_handler)

    print(style(greeting()))
    print(style("Type your command, or 'bye' to quit."))

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print(style(info("A-ah! I will go now~ See you soon!")))
            break

        if not user_input:
            print(style(error("Say something, pwease~ I'm listening!")))
            continue

        reply = process_command(user_input, assistant)
        print(style(reply))

        if user_input.lower() in {"bye", "exit", "quit"}:
            break


if __name__ == "__main__":
    run_assistant()
