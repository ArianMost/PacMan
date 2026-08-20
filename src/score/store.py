from typing import List, Any
from entities.player import Player

class LevelConfig:
    """Represents the configuration for a single level."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

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

    def __init__(self, config: GameConfig) -> None:
        """
        Create a scoring system from a fixed set of point values.
        """
        self.config = config
        self._ghost_chain: int = 0


    def award_pacgum(self, player: Player) -> int:
        """
        Award points for eating a regular pacgum.

        Args:
            player (Player): The player entity to award points to.

        Returns:
            int: The number of points added.
        """
        points = self.config.points_per_pacgum
        player.add_score(points)
        return points

    def award_super_pacgum(self, player: Player) -> int:
        """
        Award points for eating a super-pacgum and reset the chain.
        
        Args:
            player (Player): The player entity to award points to.

        Returns:
            int: The number of points added.
        """
        points = self.config.points_per_super_pacgum
        player.add_score(points)
        self._ghost_chain = 0
        return points

    def award_ghost(self, player: Player) -> int:
        """
        Award points for eating a currently-frightened ghost.

        Each consecutive ghost eaten during the same frightened window
        is worth double the previous one.
        
        Args:
            player (Player): The player entity to award points to.

        Returns:
            int: The number of points added for this specific ghost.
        """
        points: int = self.config.points_per_ghost * (2 ** self._ghost_chain)
        player.add_score(points)
        self._ghost_chain += 1
        return points

    def reset_ghost_chain(self) -> None:
        """Reset the combo, e.g. when the frightened period expires."""
        self._ghost_chain = 0
