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

    col: int
    row: int
    speed_cells_per_sec: float = 4.0
    direction: Direction = Direction.NONE
    next_direction: Direction = Direction.NONE
