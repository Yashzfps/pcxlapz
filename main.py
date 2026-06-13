from modules.app_control import open_application
from modules.gmail_handler import GmailHandler
from modules.notes import NotesManager
from modules.personality import error, greeting, info, style, success
from modules.web_search import search_and_answer


def _handle_email_command(command: str, gmail_handler: GmailHandler) -> str:
    payload = command[len("send email to ") :].strip()
    parts = [part.strip() for part in payload.split("|")]

    if len(parts) != 3 or not all(parts):
        return error(
            "Pwease use: send email to recipient@example.com | Subject | Message"
        )

    recipient, subject, message = parts
    sent, result = gmail_handler.send_email(
        to_email=recipient,
        subject=subject,
        message_text=message,
    )

    return success(result) if sent else error(result)


def process_command(command: str, notes_manager: NotesManager, gmail_handler: GmailHandler) -> str:
    clean_command = command.strip()
    lower_command = clean_command.lower()

    if lower_command in {"bye", "exit", "quit"}:
        return info("B-bye~ Rias will be waiting right here for you, okay? 💖")

    if lower_command == "show notes":
        return info(notes_manager.get_notes())

    if lower_command.startswith("note this down"):
        note_text = clean_command[len("note this down") :].strip()
        if not note_text:
            return error("Pwease tell me what to note down, pretty please~")
        notes_manager.add_note(note_text)
        return success("I saved your note safely, yay~")

    if lower_command.startswith("send email to "):
        return _handle_email_command(clean_command, gmail_handler)

    if lower_command.startswith("open "):
        app_name = clean_command[len("open ") :].strip()
        opened, message = open_application(app_name)
        return success(message) if opened else error(message)

    answer = search_and_answer(clean_command)
    return info(answer)


def run_assistant() -> None:
    notes_manager = NotesManager()
    gmail_handler = GmailHandler()

    print(style(greeting()))
    print(style("Type your command, or 'bye' if you want to rest, okay?"))

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print(style(info("A-ah! I will go now~ See you soon!")))
            break

        if not user_input:
            print(style(error("Say something, pwease~ I'm listening!")))
            continue

        reply = process_command(user_input, notes_manager, gmail_handler)
        print(style(reply))

        if user_input.lower() in {"bye", "exit", "quit"}:
            break


if __name__ == "__main__":
    run_assistant()
