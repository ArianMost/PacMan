from dataclasses import dataclass, field
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "highscore_filename": "highscores.json",
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
    "cell_size": 24,
    "level": [
        {"width": 10, "height": 8},
        {"width": 11, "height": 9},
        {"width": 12, "height": 9},
        {"width": 12, "height": 10},
        {"width": 13, "height": 10},
        {"width": 13, "height": 11},
        {"width": 14, "height": 11},
        {"width": 14, "height": 12},
        {"width": 15, "height": 12},
        {"width": 16, "height": 13},
    ],
}

@dataclass
class LevelConfig:
    """Dimensions and rules for a single level."""

    level_number: int
    width: int
    height: int
    seed: int
    level_max_time: int
    map_filename: str
    bonus_fruit_type: str
    points_per_bonus_fruit: int

@dataclass
class Config:
    highscore_filename: str = DEFAULT_CONFIG["highscore_filename"]
    lives: int = DEFAULT_CONFIG["lives"]
    pacgum: int = DEFAULT_CONFIG["pacgum"]
    points_per_pacgum: int = DEFAULT_CONFIG["points_per_pacgum"]
    points_per_super_pacgum: int = DEFAULT_CONFIG["points_per_super_pacgum"]
    points_per_ghost: int = DEFAULT_CONFIG["points_per_ghost"]
    seed: int = DEFAULT_CONFIG["seed"]
    level_max_time: int = DEFAULT_CONFIG["level_max_time"]
    cell_size: int = DEFAULT_CONFIG["cell_size"]
    levels: list[LevelConfig] = field(default_factory=list)