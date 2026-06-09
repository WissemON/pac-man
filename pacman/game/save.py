from pathlib import Path

SAVE_FILE = Path(__file__).resolve().parent / "saves" / "save.txt"


def save_levels(_game: object, level: int) -> None:
    """Persist the unlocked level number.

    Args:
        _game: Unused game object kept for call-site compatibility.
        level: Unlocked level number to persist.
    """
    SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with SAVE_FILE.open('w+') as f:
            current_level = int(f.readline().strip())
            if level <= current_level:
                return
    except (FileNotFoundError, ValueError):
        pass

    with SAVE_FILE.open('w+') as f:
        f.write(f"{level}\n")


def load_levels() -> int:
    """Load the unlocked level number from disk.

    Returns:
        Unlocked level number.
    """
    try:
        with SAVE_FILE.open('r') as f:
            level = int(f.readline().strip())
            return level
    except (FileNotFoundError, ValueError):
        return 1
