from enum import Enum
from src.maze.maze import Maze


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

Cell = tuple[int, int]


class Entity:
    """A game entity that moves through the maze one cell at a time."""
    def __init__(
        self,
        col: int,
        row: int,
        speed_cells_per_sec: float = 4.0,

        direction: Direction = Direction.NONE,
        next_direction: Direction = Direction.NONE,
    ) -> None:
        """Create an entity at the given maze cell and set its movement."""
        self.col = col
        self.row = row
        self.speed_cells_per_sec = speed_cells_per_sec
        self.direction = direction
        self.next_direction = next_direction
        self._progress = 0.0
    # how far the entity has moved from its current cell toward the next cell.

    def snap(self, col: int, row: int) -> None:
        """Move the entity immediately to a cell and stop its movement."""
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

    def can_move(self, maze: Maze, direction: Direction) -> bool:
        """Return True if moving one cell in `direction` is legal."""

        if direction is Direction.NONE:
            return False

        x = self.col
        y = self.row

        # Never allow an entity to leave the maze.
        if not (0 <= x + self.direction.dx < maze.cols and 0 <= y + self.direction.dy < maze.rows):
            return False

        if direction is Direction.UP:
            wall = 1
        elif direction is Direction.RIGHT:
            wall = 2
        elif direction is Direction.DOWN:
            wall = 4
        else:  # LEFT
            wall = 8

        return (maze.grid[y][x] & wall) == 0

    def available_directions(self, maze: Maze) -> list[Direction]:
        """Return all directions that are currently open in the maze."""
        return [d for d in _CARDINALS if self.can_move(maze, d)]

    def update(
        self,
        maze: Maze,
        dt: float,
        speed_multiplier: float = 1.0
    ) -> None:
        """Move the entity based on its speed, direction, and maze walls."""

        if (
            self.direction is Direction.NONE
            and self.next_direction is not Direction.NONE
        ):
            if self.can_move(maze, self.next_direction):
                self.direction = self.next_direction

        if self.direction is Direction.NONE:
            return

        self._progress += (
            self.speed_cells_per_sec
            * speed_multiplier
            * dt
        )

        while self._progress >= 1.0:

            # Never enter a blocked/out-of-bounds cell.
            if not self.can_move(maze, self.direction):
                self.direction = Direction.NONE
                self._progress = 0.0
                break

            self._progress -= 1.0

            self.col += self.direction.dx
            self.row += self.direction.dy

            # Try requested direction at the new cell.
            if (
                self.next_direction is not Direction.NONE
                and self.next_direction is not self.direction
                and self.can_move(maze, self.next_direction)
            ):
                self.direction = self.next_direction

            # If we cannot continue in the current direction, stop.
            if not self.can_move(maze, self.direction):
                self.direction = Direction.NONE
                self._progress = 0.0
                break
