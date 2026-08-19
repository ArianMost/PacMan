from typing import TYPE_CHECKING, List, Any
from entities.player import Player

class LevelConfig:
    """Represents the configuration for a single level."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

class ScoringRules:
    """The three point values scoring is built from, read from config."""

    def __init__(
        self,
        points_per_pacgum: int,
        points_per_super_pacgum: int,
        points_per_ghost: int,
    ) -> None:
        self.points_per_pacgum = points_per_pacgum
        self.points_per_super_pacgum = points_per_super_pacgum
        self.points_per_ghost = points_per_ghost

class GameConfig:
    """
    Data structure representing the parsed configuration file.
    Aligns with the GameConfig UML provided.
    """

    def __init__(
        self,
        highscore_filename: str,
        levels: List[LevelConfig],
        lives: int,
        pacgum: int,
        points_per_pacgum: int,
        points_per_super_pacgum: int,
        points_per_ghost: int,
        seed: int,
        level_max_time: int,
        cell_size: int,
    ) -> None:
        self.highscore_filename = highscore_filename
        self.levels = levels
        self.lives = lives
        self.pacgum = pacgum
        self.points_per_pacgum = points_per_pacgum
        self.points_per_super_pacgum = points_per_super_pacgum
        self.points_per_ghost = points_per_ghost
        self.seed = seed
        self.level_max_time = level_max_time
        self.cell_size = cell_size

class ScoringSystem:
    """
    Applies scoring rules to a Player as game events occur.

    Includes an optional "ghost chain" bonus matching the original
    arcade game: eating several frightened ghosts back-to-back during
    the same super-pacgum window is worth increasing points.
    """

    def __init__(self, rules: ScoringRules) -> None:
        """
        Create a scoring system from a fixed set of point values.
        
        Args:
            rules (ScoringRules): The point values for different actions.
        """
        self.rules: ScoringRules = rules
        self._ghost_chain: int = 0
