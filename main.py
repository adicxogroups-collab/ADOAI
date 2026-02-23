from __future__ import annotations

from pathlib import Path

from adoai import AdoaiAssistant, AssistantConfig


HELP_TEXT = """
Adoai commands:
  /help               Show commands
  /reset              Clear session memory
  /save <file>        Save conversation history
  /load <file>        Load conversation history
  /exit               Quit
""".strip()


def run_repl() -> None:
    assistant = AdoaiAssistant(
        config=AssistantConfig(
            name="Adoai",
            mission=(
                "Operate at highest capability: strategic problem-solving, precise writing, deep analysis, "
                "and practical execution guidance"
            ),
        )
    )
    print("Adoai is online. Type /help for commands.")
    while True:
        try:
            user_input = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return

        if not user_input:
            continue
        if user_input == "/help":
            print(HELP_TEXT)
            continue
        if user_input == "/reset":
            assistant.memory.clear()
            print("Memory cleared.")
            continue
        if user_input.startswith("/save "):
            path = Path(user_input.replace("/save ", "", 1)).expanduser()
            assistant.memory.save(path)
            print(f"Saved to {path}")
            continue
        if user_input.startswith("/load "):
            path = Path(user_input.replace("/load ", "", 1)).expanduser()
            assistant.memory.load(path)
            print(f"Loaded from {path}")
            continue
        if user_input == "/exit":
            print("Goodbye.")
            return

        answer = assistant.ask(user_input)
        print(f"\nAdoai> {answer}")


if __name__ == "__main__":
    run_repl()
