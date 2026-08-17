import json
from pathlib import Path
import sys
from typing import Any
from config import DEFAULT_CONFIG, Config, LevelConfig

def _validate_levels(raw_levels: Any) -> list[LevelConfig]:
    levels: list[LevelConfig] = []
    if not isinstance(raw_levels, list) or not raw_levels:
        print(f"[config] warning: invalid or missing level, using defaults", file=sys.stderr)
        raw_levels = DEFAULT_CONFIG["level"]

    for i, data in enumerate(raw_levels):
        if not isinstance(data, dict):
            print(f"[config] warning: level[{i}] is not valid!", file=sys.stderr)
            continue
        height = _validate_positive_int(data.get("height"), 8, f"level[{i}].height")
        width = _validate_positive_int(data.get("width"), 10, f"level[{i}].width")
        height = max(5, min(height, 30))
        width = max(5, min(width, 40))
        levels.append(LevelConfig(width=width, height=height))

    if not levels:
        levels = []
        for level in DEFAULT_CONFIG["level"]:
            levels.append(LevelConfig(**level))

    return levels

def load_config(config_file: str) -> Config:
    config_text = ""

    try:
        file_path = Path(config_file)
        config_text = file_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[config] warning: could not read config file '{config_file}' ({e}) using defaults", file=sys.stderr)
        config_text = ""


    config_data: dict[str, Any] = {}
    if config_text.strip():
        try:
            cleaned_config = _remove_comments(config_text)
            parsed = json.loads(cleaned_config)
            
            if isinstance(parsed, dict):
                config_data = parsed
            else:
                print(f"[config] warning: config root is not a JSON object; using defaults", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"[config] warning: malformed JSON in config file ({e}); using defaults", file=sys.stderr)

    default_keys = set(DEFAULT_CONFIG.keys())
    for key in config_data:
        if key not in default_keys:
            print(f"[config] warning: unknown key- '{key}' is ignored", file=sys.stderr)

    highscore = str(config_data.get("highscore_filename", DEFAULT_CONFIG["highscore_filename"]))
    levels = _validate_levels(config_data.get("level"))
    lives = _validate_positive_int(config_data.get("lives"), DEFAULT_CONFIG["lives"], "lives")
    pacgum = _validate_positive_int(config_data.get("pacgum"), DEFAULT_CONFIG["pacgum"], "pacgum")
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
    seed = _validate_nonnegative_int(config_data.get("seed"), DEFAULT_CONFIG["seed"], "seed"),
    level_max_time = _validate_positive_int(
        config_data.get("level_max_time"),
        DEFAULT_CONFIG["level_max_time"],
        "level_max_time",
    )
    cell_size = _validate_positive_int(
        config_data.get("cell_size"), DEFAULT_CONFIG["cell_size"], "cell_size"
    )