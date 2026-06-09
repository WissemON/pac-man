import json
import os

from pacman.game.type_defs import HighscoreEntry


def _entry_from_json(entry: object) -> HighscoreEntry | None:
    """Parse a highscore entry from raw JSON data.

    Args:
        entry: Raw highscore entry to validate.

    Returns:
        Validated highscore entry, or None when invalid.
    """
    if not isinstance(entry, dict):
        return None

    player_name = entry.get("player_name")
    score = entry.get("score")
    skin_color = entry.get("skin_color")
    cheat = entry.get("cheat")

    if (
        isinstance(player_name, str)
        and validate_name(player_name)
        and isinstance(score, int)
        and not isinstance(score, bool)
        and score >= 0
        and isinstance(skin_color, str)
        and isinstance(cheat, bool)
    ):
        return {
            "player_name": player_name,
            "score": score,
            "skin_color": skin_color,
            "cheat": cheat,
        }

    return None


def load_highscores() -> list[HighscoreEntry]:
    """Load highscores from disk.

    Returns:
        Validated highscore entries.
    """
    try:
        absolute_path = os.path.dirname(__file__) + "/highscores.json"
        with open(absolute_path, "r") as file:
            data: object = json.load(file)
            if not isinstance(data, dict):
                return []

            highscores: list[HighscoreEntry] = []
            for key in sorted(data.keys(), key=int):
                entry = _entry_from_json(data[key])
                if entry is not None:
                    highscores.append(entry)
            return highscores
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Error loading highscores: {e}")
        return []


def validate_name(name: str) -> bool:
    """Validate a player name for score saving.

    Args:
        name: Name value to validate.

    Returns:
        True when the name is valid.
    """
    if not (0 < len(name) <= 10):
        return False
    for char in name:
        if not (char.isalnum() or char.isspace()):
            return False
    return True


def insert_highscore(
    highscores: list[HighscoreEntry],
    player_name: str,
    score: int,
    skin_color: str,
    cheat: bool,
) -> list[HighscoreEntry]:
    """Insert a score into the sorted highscore list.

    Args:
        highscores: Highscore entries to read or update.
        player_name: Player name associated with the score.
        score: Score value to insert or save.
        skin_color: Player skin color associated with the score.
        cheat: Whether cheat mode was enabled for the run.

    Returns:
        Highscores sorted with the new entry inserted.
    """
    new_entry: HighscoreEntry = {
        "player_name": player_name,
        "score": score,
        "skin_color": skin_color,
        "cheat": cheat,
    }
    highscores.append(new_entry)
    highscores.sort(key=lambda entry: entry["score"], reverse=True)
    return highscores[:10]


def save_highscores(highscores: list[HighscoreEntry]) -> None:
    """Save highscores to disk.

    Args:
        highscores: Highscore entries to read or update.
    """
    absolute_path = os.path.dirname(__file__) + "/highscores.json"
    try:
        data: dict[str, HighscoreEntry] = {}
        for index, entry in enumerate(highscores, start=1):
            data[str(index)] = entry
        with open(absolute_path, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Highscores saved to: {absolute_path}")
    except Exception as e:
        print(f"Error saving highscores: {e}")
