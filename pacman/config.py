import json
import os
import re

from pacman.game.type_defs import AIConfig, GameConfig, JsonValue, LevelConfig


def strip_comments(text: str) -> str:
    """Remove supported comments from JSON-like text.

    Args:
        text: Text content to process or draw.

    Returns:
        Comment-free text suitable for JSON parsing.
    """
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"(//|#)[^\n]*", "", text)
    return text


def _json_value(value: object) -> JsonValue:
    """Normalize raw JSON data into the typed JSON value alias.

    Args:
        value: Raw value to normalize or apply.

    Returns:
        Normalized JSON value, or None for unsupported data.
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value

    if isinstance(value, list):
        return [_json_value(item) for item in value]

    if isinstance(value, dict):
        result: dict[str, JsonValue] = {}
        for key, item in value.items():
            if isinstance(key, str):
                result[key] = _json_value(item)
        return result

    return None


def _read_positive_int(
    config: dict[str, JsonValue],
    key: str,
    default: int,
    minimum: int,
) -> int:
    """Read and validate a positive integer from config data.

    Args:
        config: Configuration mapping to read from.
        key: Configuration key to validate.
        default: Fallback value used when validation fails.
        minimum: Minimum accepted integer value.

    Returns:
        Validated integer value.
    """
    value = config.get(key, default)
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < minimum
    ):
        print(f"Invalid {key} number. Defaulting to {default}.")
        return default
    return value


def validate_config(config: dict[str, JsonValue]) -> GameConfig:
    """Validate raw config data and fill missing defaults.

    Args:
        config: Configuration mapping to read from.

    Returns:
        Validated game configuration.
    """
    default_ai: AIConfig = {
        "scatter_duration": 6.0,
        "chase_duration": 7.0,
        "frightened_duration": 6.0,
        "eaten_duration": 7.0,
    }

    def _default_level_config() -> LevelConfig:
        """Build a default level configuration.

        Returns:
            Default level configuration.
        """
        return {
            "width": 14,
            "height": 14,
            "ai": default_ai.copy(),
        }

    def _sanitize_level_config(
        level_id: str,
        level_cfg: dict[str, JsonValue],
    ) -> LevelConfig:
        """Validate one level configuration entry.

        Args:
            level_id: String identifier of the level.
            level_cfg: Raw configuration for one level.

        Returns:
            Validated level configuration.
        """
        width = level_cfg.get("width", 14)
        if (
            not isinstance(width, int)
            or isinstance(width, bool)
            or width < 1
        ):
            print(f"Invalid width for level {level_id}. Defaulting to 14.")
            width = 14

        height = level_cfg.get("height", 14)
        if (
            not isinstance(height, int)
            or isinstance(height, bool)
            or height < 1
        ):
            print(f"Invalid height for level {level_id}. Defaulting to 14.")
            height = 14

        ai_cfg = level_cfg.get("ai", {})
        if not isinstance(ai_cfg, dict):
            print(f"Invalid ai config for level {level_id}. Using defaults.")
            ai_cfg = {}

        ai_sanitized: AIConfig = default_ai.copy()
        for key, default_value in default_ai.items():
            value = ai_cfg.get(key, default_value)
            if not isinstance(value, (int, float)) or value <= 0:
                print(
                    f"Invalid {key} for level {level_id}. "
                    f"Defaulting to {default_value}."
                )
                value = default_value
            ai_sanitized[key] = float(value)

        return {
            "width": width,
            "height": height,
            "ai": ai_sanitized,
        }

    sanitized_map: dict[str, LevelConfig] = {}
    raw_levels = config.get("level", [])
    if isinstance(raw_levels, list) and raw_levels:
        for level_entry in raw_levels:
            if not isinstance(level_entry, dict) or not level_entry:
                print("Invalid level entry. Using defaults.")
                continue

            for raw_level_id, level_cfg in level_entry.items():
                level_id = str(raw_level_id)
                if not isinstance(level_cfg, dict):
                    print(
                        f"Invalid level config for level {level_id}. "
                        "Using defaults."
                    )
                    sanitized_map[level_id] = _default_level_config()
                    continue

                sanitized_map[level_id] = _sanitize_level_config(
                    level_id,
                    level_cfg,
                )
    else:
        print("Invalid level. Default levels configuration used.")

    for i in range(1, 17):
        key = str(i)
        if key not in sanitized_map:
            sanitized_map[key] = _default_level_config()

    return {
        "lives": _read_positive_int(config, "lives", 3, 1),
        "pacgum": _read_positive_int(config, "pacgum", 42, 1),
        "points_per_pacgum": _read_positive_int(
            config, "points_per_pacgum", 1, 0
        ),
        "points_per_super_pacgum": _read_positive_int(
            config, "points_per_super_pacgum", 20, 0
        ),
        "points_per_special_item": _read_positive_int(
            config, "points_per_special_item", 30, 0
        ),
        "points_per_ghost": _read_positive_int(
            config, "points_per_ghost", 40, 0
        ),
        "level_max_time": _read_positive_int(
            config, "level_max_time", 300, 1
        ),
        "seed": _read_positive_int(config, "seed", 42, 1),
        "level": [sanitized_map],
    }


def load_config(filename: str) -> dict[str, JsonValue]:
    """Load raw configuration data from disk.

    Args:
        filename: Path to the file to load.

    Returns:
        Raw configuration mapping.
    """
    candidates = [
        filename,
        os.path.join(os.getcwd(), filename),
        os.path.join(os.path.dirname(__file__), filename),
        os.path.join(os.path.dirname(__file__), "..", filename),
    ]

    for path in candidates:
        print(f"Load config from: {path}")
        try:
            with open(path) as f:
                loaded: object = json.loads(strip_comments(f.read()))
        except FileNotFoundError:
            continue
        except json.JSONDecodeError:
            print(f"Error decoding {path}.\nPlease check the file format.")
            continue

        normalized = _json_value(loaded)
        if isinstance(normalized, dict):
            return normalized

    print(f"No valid config file found for '{filename}'. Tried paths:")
    for path in candidates:
        print(f" - {path}")
    print("Using empty configuration fallback.")
    return {}
