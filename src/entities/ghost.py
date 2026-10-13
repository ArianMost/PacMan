from collections import deque
from enum import Enum
from typing import Tuple, Any
from typing import ClassVar
from src.entities.entity import _CARDINALS, Entity
from src.entities.entity import Direction
import random
from src.maze.maze_adapter import Maze

GHOST_NAMES_COLORS = [
    ("blinky", "#9B59B6"),
    ("pinky",  "#2ECC71"),
    ("inky",   "#F1C40F"),
    ("clyde",  "#3498DB")
]
_WALL_BIT = {Direction.UP: 1,
             Direction.RIGHT: 2,
             Direction.DOWN: 4,
             Direction.LEFT: 8}
Cell = tuple[int, int]


def _bfs_distance_field(maze: Maze, target: Cell) -> dict[Cell, int]:
    """BFS distance from every reachable cell to target."""
    distance = {target: 0}
    queue: deque[Cell] = deque([target])

    while queue:
        current = queue.popleft()
        col, row = current
        for direction in _CARDINALS:
            neighbor_col, neighbor_row = col + direction.dx, row + direction.dy
            if 0 <= neighbor_col < maze.cols and 0 <= neighbor_row < maze.rows:
                if (maze.grid[row][col] & _WALL_BIT[direction]) == 0:
                    neighbor = (neighbor_col, neighbor_row)
                    if neighbor not in distance:
                        distance[neighbor] = distance[current] + 1
                        queue.append(neighbor)
    return distance


def _step_toward(maze: Maze, start: Cell, dist: dict[Cell, int]) -> Direction:
    """Choose a direction toward home with some random variation."""
    col, row = start
    options = []

    for d in _CARDINALS:
        neighbor_col, neighbor_row = col + d.dx, row + d.dy

        if 0 <= neighbor_col < maze.cols and 0 <= neighbor_row < maze.rows:
            if (maze.grid[row][col] & _WALL_BIT[d]) == 0:
                neighbor_distance = dist.get((neighbor_col, neighbor_row))

                if neighbor_distance is not None:
                    options.append((d, neighbor_distance))

    if not options:
        return Direction.NONE

    # Prefer directions that get closer, but not necessarily the shortest one.
    best_distance = min(distance for _, distance in options)

    best = [
        d for d, distance in options
        if distance == best_distance
    ]

    # 70% chance to choose a best direction,
    if random.random() < 0.7:
        return random.choice(best)

    return random.choice([d for d, _ in options])


class GhostState(Enum):
    """Enumeration representing the behavioral states of a ghost."""
    CHASE = 1
    FRIGHTENED = 2
    EATEN = 3


class Ghost(Entity):
    def __init__(self, col: int, row: int, name: str,
                 color: Tuple[int, int, int]) -> None:
        """Initialize a ghost entity with its position, name, and color."""
        super().__init__(col=col, row=row)
        self.name: str = name
        self.color: Tuple[int, int, int] = color
        self.home_col: int = col
        self.home_row: int = row
        self.state: GhostState = GhostState.CHASE
        self.frightened_timer: float = 0.0
        self.respawn_timer: float = 0.0
        self.reverse_requested = False
        self._home_distance_field: dict[Cell, int] | None = None
        self._last_decided_cell: Cell | None = None

    _CHASE_SPEED_MULT: ClassVar[float] = 0.7
    _FRIGHTENED_SPEED_MULT: ClassVar[float] = 0.9
    _EATEN_SPEED_MULT: ClassVar[float] = 1.8

    def set_home(self, col: int, row: int) -> None:
        """Assign (or reassign) this ghost's home/respawn corner."""
        self.home_col = col
        self.home_row = row

    def frighten(self, duration: float) -> None:
        """Enter FRIGHTENED state for `duration` seconds.

        A ghost that is already EATEN (just a pair of eyes heading home)
        ignores this, it isn't "on the board" to be caught again until
        it respawns.
        """
        if self.state is GhostState.EATEN:
            return
        self.state = GhostState.FRIGHTENED
        self.frightened_timer = duration
        self._last_decided_cell = None

        if self.direction is not Direction.NONE:
            old_direction = self.direction
            self.col += old_direction.dx
            self.row += old_direction.dy
            self.direction = self.direction.opposite()
            self._progress = 1.0 - self._progress
        else:
            self.next_direction = Direction.NONE

    def get_eaten(self, respawn_delay: float) -> None:
        """Called when the player catches this ghost while it's frightened."""
        self.state = GhostState.EATEN
        self.respawn_timer = respawn_delay
        self.frightened_timer = 0.0
        self._last_decided_cell = None

    def choose_direction(self, maze: Maze, target: Cell) -> None:
        """Pick `next_direction` given the current target cell and state.

        Ghosts never reverse into the cell they just came from unless
        it's the only option (a dead end) — this is what stops them
        jittering back and forth and matches classic Pac-Man ghost
        behaviour. FRIGHTENED ghosts move somewhat randomly instead of
        optimally, so they're not trivial to predict and dodge.
        """
        options = self.available_directions(maze)
        if not options:
            return

        if len(options) > 1 and self.direction is not Direction.NONE:
            reverse = self.direction.opposite()
            if reverse in options:
                options.remove(reverse)

        if self.state is GhostState.FRIGHTENED:
            if random.random() < 0.5:
                chosen_dir = random.choice(options)
            else:
                chosen_dir = max(options,
                                 key=lambda d:
                                 self._squared_distance(d, target))
        else:
            chosen_dir = min(options, key=lambda d:
                             self._squared_distance(d, target))

        self.direction = chosen_dir
        self.next_direction = chosen_dir

    def _decide_if_new_cell(self, maze: Maze, target: Cell) -> None:
        """Only re-decide a direction when we've actually arrived at a new
        cell — not every single frame — mirroring how _update_eaten decides."""
        current_cell = (self.col, self.row)
        if current_cell != self._last_decided_cell:
            self.choose_direction(maze, target)
            self._last_decided_cell = current_cell

    def _squared_distance(self,
                          direction: Direction,
                          target: Cell) -> float | Any:
        """Squared distance from target if the ghost stepped in `direction`."""
        col = self.col + direction.dx
        row = self.row + direction.dy
        tcol, trow = target
        return (col - tcol) ** 2 + (row - trow) ** 2

    def _chase_target(self, player_cell: Cell) -> Cell:
        """Compute the CHASE-mode target cell, varied by ghost personality.
        """
        pcol, prow = player_cell
        # if self.name == "pinky":
        #     return pcol + 4, prow - 4
        # if self.name == "inky":
        #     return (
        #         pcol + random.choice((-4, 4)),
        #         prow + random.choice((-4, 4)),
        #     )
        # if self.name == "clyde":
        #     distance = (self.col - pcol) ** 2 + (self.row - prow) ** 2
        #     if distance <= 64:  # within 8 cells: get shy, retreat home
        #         return self.home_col, self.home_row
        #     return pcol, prow
        return pcol, prow  # blinky and default

    def _update_eaten(self, maze: Maze, dt: float) -> None:
        """Move the ghost back to its home corner, then revive into CHASE."""
        self.respawn_timer = max(0.0, self.respawn_timer - dt)
        home = (self.home_col, self.home_row)
        current_cell = (self.col, self.row)

        if current_cell == home:
            self.direction = Direction.NONE
            self.next_direction = Direction.NONE
            self._home_distance_field = None
            self._last_decided_cell = None
            if self.respawn_timer <= 0.0:
                self.state = GhostState.CHASE
            return

        distance_field = self._home_distance_field
        if distance_field is None:
            distance_field = _bfs_distance_field(maze, home)
            self._home_distance_field = distance_field
        if current_cell != self._last_decided_cell:
            direction = _step_toward(maze, current_cell, distance_field)
            self.direction = direction
            self.next_direction = direction
            self._last_decided_cell = current_cell
        self.update(maze, dt, speed_multiplier=self._EATEN_SPEED_MULT)

    def _update_frightened(self,
                           maze: Maze,
                           dt: float,
                           player_cell: Cell) -> None:
        self.frightened_timer = max(0.0, self.frightened_timer - dt)
        """Frightened ghosts move semi-randomly, but still
        try to flee from the player."""

        self._decide_if_new_cell(maze, player_cell)
        self.update(maze, dt, speed_multiplier=self._FRIGHTENED_SPEED_MULT)
        if self.frightened_timer <= 0.0:
            self.state = GhostState.CHASE
            self._last_decided_cell = None

    def _update_chase(self, maze: Maze, dt: float, player_cell: Cell) -> None:
        """Chase ghosts move toward their target cell,
        which is determined by their personality."""
        target = self._chase_target(player_cell)
        self._decide_if_new_cell(maze, target)
        self.update(maze, dt, speed_multiplier=self._CHASE_SPEED_MULT)

    def update_ai(self, maze: Maze, dt: float, player_cell: Cell) -> None:
        """Advance AI + movement by `dt` seconds. Call once per frame.
        Dispatches on `state`:
          EATEN      -> race back to home corner, then revive into CHASE.
          FRIGHTENED -> flee-ish movement, timer ticks down to CHASE.
          CHASE      -> hunt the player using this ghost's personality.
        """
        if self.state is GhostState.EATEN:
            self._update_eaten(maze, dt)
            return

        if self.state is GhostState.FRIGHTENED:
            self._update_frightened(maze, dt, player_cell)
            return

        self._update_chase(maze, dt, player_cell)
