from dataclasses import dataclass, field
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "highscore_filename": "highscores.json",
    "lives": 3,
    "pacgum": 4200,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
    "cell_size": 24,
    "levels": [
        {
            "level_number": 1,
            "width": 19,
            "height": 13,
            "seed": 505,
            "level_max_time": 130,
            "bonus_fruit_type": "Banana",
            "points_per_bonus_fruit": 700,
            "walls_color": "#f4a261"
        },
        {
            "level_number": 2,
            "width": 19,
            "height": 15,
            "seed": 606,
            "level_max_time": 145,
            "bonus_fruit_type": "Melon",
            "points_per_bonus_fruit": 1000,
            "walls_color": "#2a9d8f"
        },
    ]
}


@dataclass
class LevelConfig:
    """Dimensions and rules for a single level."""

    level_number: int = 1
    width: int = 14
    height: int = 10
    seed: int = 0
    level_max_time: int = 90
    bonus_fruit_type: str = "cherry"
    points_per_bonus_fruit: int = 100
    walls_color: str = "#1e2ac9"


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
