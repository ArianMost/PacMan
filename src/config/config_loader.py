import json
from pathlib import Path
import sys
from typing import Any
from .config import DEFAULT_CONFIG, Config, LevelConfig


def _remove_comments(text: str) -> str:
    """Remove #, // line comments and /* */ block comments.
    Comments are only stripped when they are not inside a JSON string,
    so that URLs or text values containing ``//`` are left untouched.
    """
    chars = iter(text)
    res: list[str] = []
    in_json_str = False
    is_escape = False

    for char in chars:
        if in_json_str:
            res.append(char)

            if is_escape:
                is_escape = False
            elif char == "\\":
                is_escape = True
            elif char == '"':
                in_json_str = False
            continue

        if char == '"':
            in_json_str = True
            res.append(char)

        elif char == "#":
            for char in chars:
                if char == "\n":
                    res.append(char)
                    break

        elif char == "/":
            try:
                next_char = next(chars)
            except StopIteration:
                res.append(char)
                break

            if next_char == "/":
                for char in chars:
                    if char == "\n":
                        res.append(char)
                        break
            elif next_char == "*":
                previous = ""
                for char in chars:
                    if previous == "*" and char == "/":
                        break
                    previous = char
            else:
                res.extend((char, next_char))

        else:
            res.append(char)

    cleaned_text = "".join(res)
    return cleaned_text


def _validate_positive_int(val: Any, default_val: int, label: str) -> int:
    """Validate that a value is a positive
    integer, returning the default if not."""
    try:
        num = int(val)
        if num <= 0:
            raise ValueError
        return num
    except (TypeError, ValueError):
        print(
            f"[config] warning: invalid '{label} : "
            f"{val}', using the default value "
            f"'{default_val}'",
            file=sys.stderr,
        )
        return default_val


def _validate_optional_positive_int(val: Any, name: str) -> int | None:
    """Like ``_validate_positive_int`` but
    for an optional per-level override."""
    if val is None:
        return None
    try:
        result = int(val)
        if result <= 0:
            raise ValueError
        return result
    except (TypeError, ValueError):
        print(
            f"[config] warning: invalid '{name}' {val}', "
            "ignoring this override",
            file=sys.stderr,
        )
        return None


def _validate_nonnegative_int(val: Any, default_val: int, label: str) -> int:
    """Validate that a value is a non-negative integer,
    returning the default if not."""
    try:
        num = int(val)
        if num < 0:
            raise ValueError
        return num
    except (TypeError, ValueError):
        print(
            f"[config] warning: invalid '{label} : {val}', "
            f"using the default value '{default_val}'",
            file=sys.stderr,
        )
        return default_val


def _validate_optional_nonnegative_int(val: Any, name: str) -> int | None:
    """Like ``_validate_nonnegative_int`` but
    for an optional per-level override."""
    if val is None:
        return None
    try:
        result = int(val)
        if result < 0:
            raise ValueError
        return result
    except (TypeError, ValueError):
        print(
            f"[config] warning: invalid '{name}' {val}', "
            "ignoring this override",
            file=sys.stderr,
        )
        return None


def _validate_optional_str(val: Any, name: str) -> str | None:
    """Validate that a value is a non-empty string,
    returning None if not."""
    if val is None:
        return None
    if not isinstance(val, str) or not val.strip():
        print(
            f"[config] warning: invalid '{name}' {val}', "
            "ignoring this override",
            file=sys.stderr,
        )
        return None
    return val


def _parse_hex_color(val: Any, name: str) -> str | None:
    """Parse a hex color string like '#1e2ac9' into an RGB tuple."""
    if val is None:
        return None
    if not isinstance(val, str):
        print(
            f"[config] warning: invalid '{name}' {val}', expected a"
            "hex color string like '#1e2ac9'",
            file=sys.stderr,
        )
        return None

    digits = val.strip().lstrip("#")
    if len(digits) != 6 or not all(
        c in "0123456789abcdefABCDEF" for c in digits
    ):
        print(
            f"[config] warning: invalid '{name}' {val}', expected a "
            "6-digit hex color like '#1e2ac9'",
            file=sys.stderr,
        )
        return None

    red = int(digits[0:2], 16)
    green = int(digits[2:4], 16)
    blue = int(digits[4:6], 16)

    return f"#{red:02x}{green:02x}{blue:02x}"


def _validate_levels(raw_levels: Any) -> list[LevelConfig]:
    """Validate the levels configuration,
    returning a list of LevelConfig objects."""
    levels: list[LevelConfig] = []
    if not isinstance(raw_levels, list) or not raw_levels:
        print(
            "[config] warning: invalid or missing level, " "using defaults",
            file=sys.stderr,
        )
        raw_levels = DEFAULT_CONFIG["levels"]

    for i, data in enumerate(raw_levels):
        if not isinstance(data, dict):
            print(
                f"[config] warning: level[{i}] is not " "valid!",
                file=sys.stderr,
            )
            continue
        height = _validate_positive_int(
            data.get("height"), 15, f"level[{i}].height"
        )
        width = _validate_positive_int(
            data.get("width"), 15, f"level[{i}].width"
        )
        height = max(5, min(height, 30))
        width = max(5, min(width, 40))
        prefix = f"levels[{i}]"
        levels.append(
            LevelConfig(
                width=width,
                height=height,
                level_number=_validate_optional_positive_int(
                    data.get("level_number"), f"{prefix}.level_number"
                )
                or i + 1,
                seed=_validate_optional_nonnegative_int(
                    data.get("seed"), f"{prefix}.seed"
                )
                or DEFAULT_CONFIG["seed"],
                level_max_time=_validate_optional_positive_int(
                    data.get("level_max_time"), f"{prefix}.level_max_time"
                )
                or DEFAULT_CONFIG["level_max_time"],
                map_filename=_validate_optional_str(
                    data.get("map_filename"), f"{prefix}.map_filename"
                )
                or "",
                bonus_fruit_type=str(data.get("bonus_fruit_type", "")).strip(),
                points_per_bonus_fruit=_validate_nonnegative_int(
                    data.get("points_per_bonus_fruit"),
                    0,
                    f"{prefix}.points_per_bonus_fruit",
                ),
                walls_color=_parse_hex_color(
                    data.get("walls_color"), f"{prefix}.walls_color"
                )
                or "#1e2ac9",
            )
        )

    if not levels:
        levels = []
        for level in DEFAULT_CONFIG["level"]:
            levels.append(LevelConfig(**level))

    return levels


def load_config(config_file: str) -> Config:
    """Load the configuration from a JSON file, returning a Config object.
    If the file is missing or malformed, defaults are used.
    """
    config_text = ""

    try:
        file_path = Path(config_file)
        config_text = file_path.read_text(encoding="utf-8")
    except OSError as e:
        print(
            f"[config] warning: could not read config file "
            f"'{config_file}' ({e}) using defaults",
            file=sys.stderr,
        )
        config_text = ""

    config_data: dict[str, Any] = {}
    if config_text.strip():
        try:
            cleaned_config = _remove_comments(config_text)
            parsed = json.loads(cleaned_config)

            if isinstance(parsed, dict):
                config_data = parsed
            else:
                print(
                    "[config] warning: config root is not a "
                    "JSON object; using defaults",
                    file=sys.stderr,
                )
        except json.JSONDecodeError as e:
            print(
                f"[config] warning: malformed JSON in config file ({e}); "
                "using defaults",
                file=sys.stderr,
            )

    default_keys = set(DEFAULT_CONFIG.keys())
    for key in config_data:
        if key not in default_keys:
            print(
                f"[config] warning: unknown key- '{key}' " "is ignored",
                file=sys.stderr,
            )

    highscore = str(
        config_data.get(
            "highscore_filename", DEFAULT_CONFIG["highscore_filename"]
        )
    )
    levels = _validate_levels(config_data.get("levels"))
    lives = _validate_positive_int(
        config_data.get("lives"), DEFAULT_CONFIG["lives"], "lives"
    )
    pacgum = _validate_positive_int(
        config_data.get("pacgum"), DEFAULT_CONFIG["pacgum"], "pacgum"
    )
    points_per_pacgum = _validate_nonnegative_int(
        config_data.get("points_per_pacgum"),
        DEFAULT_CONFIG["points_per_pacgum"],
        "points_per_pacgum",
    )
    points_per_super_pacgum = _validate_nonnegative_int(
        config_data.get("points_per_super_pacgum"),
        DEFAULT_CONFIG["points_per_super_pacgum"],
        "points_per_super_pacgum",
    )
    points_per_ghost = _validate_nonnegative_int(
        config_data.get("points_per_ghost"),
        DEFAULT_CONFIG["points_per_ghost"],
        "points_per_ghost",
    )
    seed = _validate_nonnegative_int(
        config_data.get("seed"), DEFAULT_CONFIG["seed"], "seed"
    )
    level_max_time = _validate_positive_int(
        config_data.get("level_max_time"),
        DEFAULT_CONFIG["level_max_time"],
        "level_max_time",
    )
    cell_size = _validate_positive_int(
        config_data.get("cell_size"), DEFAULT_CONFIG["cell_size"], "cell_size"
    )

    return Config(
        highscore,
        lives,
        pacgum,
        points_per_pacgum,
        points_per_super_pacgum,
        points_per_ghost,
        seed,
        level_max_time,
        cell_size,
        levels,
    )
