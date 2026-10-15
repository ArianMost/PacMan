from src.entities.entity import Direction, Entity


class Player(Entity):
    def __init__(self, lives: int, score: int = 0) -> None:
        """Initialize a player entity with
        the given number of lives and score."""
        super().__init__(col=0, row=0, speed_cells_per_sec = 6.0)
        self.lives = lives
        self.score = score

    def add_score(self, points: int) -> None:
        """Add points to the player's score."""
        self.score += points

    def lose_life(self) -> bool:
        """Decrement the player's lives by one."""
        if self.lives > 0:
            self.lives -= 1
            return True
        return False

    def respawn(self, col: int, row: int) -> None:
        """Respawn the player at the given cell coordinates."""
        self.snap(col, row)
        self.next_direction = Direction.NONE
