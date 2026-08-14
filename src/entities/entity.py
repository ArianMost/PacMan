from enum import Enum
from typing import Tuple, Any


class Direction(Enum):
    """One of the four cardinal directions, or no movement at all.

    Each member stores its (dx, dy) delta in grid cells so that entities
    can add it directly to their (col, row) position.
    """

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)

    @property
    def dx(self) -> int:
        """Column delta for one step in this direction."""
        return self.value[0]

    @property
    def dy(self) -> int:
        """Row delta for one step in this direction."""
        return self.value[1]

    def opposite(self) -> "Direction":
        """Return the 180-degree reverse of this direction."""
        return _OPPOSITES[self]


_OPPOSITES: dict[Direction, Direction] = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
    Direction.NONE: Direction.NONE,
}

_CARDINALS: tuple[Direction, ...] = (
    Direction.UP,
    Direction.DOWN,
    Direction.LEFT,
    Direction.RIGHT,
)


class Entity:
    """A grid-aligned actor that can move smoothly through a `Maze`.
    Position is tracked as an exact grid cell (`col`, `row`) plus an
    internal sub-cell progress value, so rendering can interpolate pixel
    position mid-move while all collision/AI logic reasons in whole cells.
    """
    def __init__(
        self,
        col: int,
        row: int,
        speed_cells_per_sec: float = 4.0,
        direction: Direction = Direction.NONE,
        next_direction: Direction = Direction.NONE,
    ):
        self.col = col
        self.row = row
        self.speed_cells_per_sec = speed_cells_per_sec
        self.direction = direction
        self.next_direction = next_direction
        self._progress = 0.0
    # how far the entity has moved from its current cell toward the next cell.

    def snap(self, col: int, row: int) -> None:
        """Teleport to an exact cell and clear all movement state.
        Used for spawning, respawning, and level (re)start.
        This is a method that moves the entity
        immediately to a specific grid cell.
        """
        self.col = col
        self.row = row
        self._progress = 0.0
        self.direction = Direction.NONE
        self.next_direction = Direction.NONE

    def pixel_position(self, cell_size: int) -> tuple[float, float]:
        """
        calculates where the entity should actually be drawn on the screen.
        """
        x = (self.col + self.direction.dx * self._progress) * cell_size
        y = (self.row + self.direction.dy * self._progress) * cell_size
        return x, y

    def can_move(self, maze: "Maze", direction: Direction) -> bool:
        if direction is Direction.NONE:
            return False

        x = self.col
        y = self.row
        if direction is Direction.UP:
            wall = 1
        elif direction is Direction.RIGHT:
            wall = 2
        elif direction is Direction.DOWN:
            wall = 4
        else:  # LEFT
            wall = 8
        return (maze.maze[y][x] & wall) == 0

    def available_directions(self, maze: Any) -> list[Direction]:
        """Return all cardinal directions that are not blocked by a wall."""
        return [d for d in _CARDINALS if self.can_move(maze, d)]
