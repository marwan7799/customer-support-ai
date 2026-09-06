from pathlib import Path

PROMPT_PATH = Path(__file__).parent / "prompts" / "system_prompt.txt"


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")
