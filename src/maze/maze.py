from dataclasses import dataclass
from constants import OPEN


@dataclass
class Maze:
    """A generated maze."""

    grid: list[list[int]]
    cols: int
    rows: int
    ghosts_sp: list[tuple[int, int]]
    player_sp: tuple[int, int]

    def is_walkable(self, row: int, col: int) -> bool:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col] == OPEN
        return False
