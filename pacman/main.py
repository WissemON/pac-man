from pathlib import Path
from sys import argv
import sys

from pacman.game.game import Game
from pacman.config import load_config, validate_config
from pacman.highscores import load_highscores


def _pyinstaller_data_dir() -> Path | None:
    """Return the PyInstaller data directory when the app is frozen.

    Returns:
        PyInstaller data directory, or None when running from source.
    """
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if isinstance(bundle_dir, str):
        return Path(bundle_dir)
    return None


def _resolve_config_path() -> str:
    """Resolve the configuration path for CLI and double-click launches.

    Returns:
        Path to the configuration file, or the default filename fallback.
    """
    if len(argv) >= 2:
        return argv[1]

    candidates: list[Path] = []
    data_dir = _pyinstaller_data_dir()
    if data_dir is not None:
        candidates.append(data_dir / "config.json")

    candidates.extend([
        Path(argv[0]).resolve().parent / "config.json",
        Path.cwd() / "config.json",
        Path(__file__).resolve().parents[1] / "config.json",
    ])

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    return "config.json"


def main() -> None:
    """Load configuration and start the game."""
    print("\nStarting Pacman...\n")
    raw_config = load_config(_resolve_config_path())
    config = validate_config(raw_config)
    highscores = load_highscores()
    le_goat = Game(config, highscores)
    le_goat.on_execute()


if __name__ == "__main__":
    main()
