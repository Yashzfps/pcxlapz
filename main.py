"""Rias Windows desktop assistant CLI entrypoint."""

from config import CREDENTIALS_FILE, GMAIL_SCOPES, NOTES_FILE, TOKEN_FILE, WEB_SEARCH_RESULTS
from modules.app_control import open_application
from modules.gmail_handler import GmailHandler
from modules.notes import NotesManager
from modules.personality import RiasPersonality
from modules.web_search import search_and_answer


def _parse_email_command(command: str):
    payload = command[len("send email to ") :].strip()
    parts = [part.strip() for part in payload.split("|", 2)]
    if len(parts) != 3 or not all(parts):
        return None
    return parts[0], parts[1], parts[2]


def main() -> None:
    personality = RiasPersonality()
    notes_manager = NotesManager(NOTES_FILE)
    gmail = GmailHandler(CREDENTIALS_FILE, TOKEN_FILE, GMAIL_SCOPES)

    print(personality.greeting())
    print(
        personality.info(
            "Type things like: 'open notepad', 'note this down ...', "
            "'show notes', 'send email to a@b.com | subject | message', or ask a question!"
        )
    )

    while True:
        user_input = input("You: ").strip()
        lower = user_input.lower()

        if lower in {"exit", "quit", "bye"}:
            print(personality.info("Okayy~ See you soon, Onii-chan!"))
            break

        if lower.startswith("open "):
            app_name = user_input[5:].strip()
            result = open_application(app_name)
            if result.startswith("Opened"):
                print(personality.success(result))
            else:
                print(personality.error(result))
            continue

        if lower.startswith("note this down"):
            content = user_input[len("note this down") :].strip(" :,-")
            if not content:
                print(personality.error("Please tell me what to note, pretty please~"))
                continue
            notes_manager.add_note(content)
            print(personality.success("I saved your note safely!"))
            continue

        if lower.startswith("note "):
            content = user_input[5:].strip()
            if not content:
                print(personality.error("Please share the note text first."))
                continue
            notes_manager.add_note(content)
            print(personality.success("Noted down perfectly!"))
            continue

        if lower in {"show notes", "read notes", "my notes"}:
            notes = notes_manager.get_notes()
            if not notes:
                print(personality.info("Your notebook is empty right now~"))
                continue
            for idx, note in enumerate(notes, start=1):
                print(personality.info(f"{idx}. [{note['timestamp']}] {note['content']}"))
            continue

        if lower.startswith("send email to "):
            parsed = _parse_email_command(user_input)
            if not parsed:
                print(
                    personality.error(
                        "Use this format: send email to recipient@example.com | Subject | Message"
                    )
                )
                continue
            to_email, subject, message = parsed
            ok, response = gmail.send_email(to_email, subject, message)
            print(personality.success(response) if ok else personality.error(response))
            continue

        answer = search_and_answer(user_input, max_results=WEB_SEARCH_RESULTS)
        print(personality.info(answer))


if __name__ == "__main__":
    main()

