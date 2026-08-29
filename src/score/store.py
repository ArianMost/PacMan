from entities.player import Player
from config.config import Config


class ScoringSystem:
    """
    Applies scoring rules to a Player as game events occur.

    Includes an optional "ghost chain" bonus matching the original
    arcade game: eating several frightened ghosts back-to-back during
    the same super-pacgum window is worth increasing points.
    """

    def __init__(self, config: Config) -> None:
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
        points: int = self.config.points_per_pacgum
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
        points: int = self.config.points_per_super_pacgum
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

    def award_fruit(self, player: Player, level: int) -> int:
        """
        Award points for eating the bonus fruit.
        The point value depends on the current level number.
        Args:
            player (Player): The player entity to award points to.
            level (int): The current level (1 through 10).
        Returns:
            int: The number of points awarded.
        """
        if level == 1:
            points = 100       # Cherry
        elif level == 2:
            points = 300       # Strawberry
        elif 3 <= level <= 4:
            points = 500       # Orange
        elif 5 <= level <= 6:
            points = 700       # Apple
        elif 7 <= level <= 8:
            points = 1000      # Melon
        elif 9 <= level <= 10:
            points = 2000      # Galaxian Flagship
        else:
            points = 0         # Fallback if level is somehow out of bounds
        player.add_score(points)
        return points
