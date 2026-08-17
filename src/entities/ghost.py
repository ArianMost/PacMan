from enum import Enum
from typing import Tuple, Any
from entity import Entity
from entities.entity import Direction
import random


class GhostState(Enum):
    """Enumeration representing the behavioral states of a ghost."""
    CHASE = 1
    FRIGHTENED = 2
    EATEN = 3

Cell = tuple[int, int]


_CHASE_SPEED_MULT: ClassVar[float] = 1.0
_FRIGHТENED_SPEED_MULT: ClassVar[float] = 0.5
_EATEN_SPEED_MULT: ClassVar[float] = 1.8

class Ghost(Entity):
    def __init__(self, name: str, color: Tuple[int, int, int]) -> None:
        self.name: str = name
        self.color: Tuple[int, int, int] = color
        self.home_col: int = 0
        self.home_row: int = 0
        self.state: GhostState = GhostState.CHASE
        self.frightened_timer: float = 0.0
        self.respawn_timer: float = 0.0

    def set_home(self, col: int, row: int) -> None:
        """Assign (or reassign) this ghost's home/respawn corner."""
        self.home_col = col
        self.home_row = row

    def frighten(self, duration: float) -> None:
        """Enter FRIGHTENED state for `duration` seconds.
 
        A ghost that is already EATEN (just a pair of eyes heading home)
        ignores this — it isn't "on the board" to be caught again until
        it respawns.
        """
        if self.state is GhostState.EATEN:
            return
        self.state = GhostState.FRIGHTENED
        self.frightened_timer = duration
        self.direction = self.direction.opposite()
        self.next_direction = Direction.NONE

    def get_eaten(self, respawn_delay: float) -> None:
        """Called when the player catches this ghost while it's frightened."""
        self.state = GhostState.EATEN
        self.respawn_timer = respawn_delay
        self.frightened_timer = 0.0

    def choose_direction(self, maze: "Maze", target: Cell) -> None:
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
                self.next_direction = random.choice(options)
            else:
                self.next_direction = max(
                    options, key=lambda d: self._squared_distance(d, target)
                )
        else:
            self.next_direction = min(
                options, key=lambda d: self._squared_distance(d, target)
            )

    def _squared_distance(self, direction: Direction, target: Cell) -> float | Any:
        """Squared distance from target if the ghost stepped in `direction`."""
        col = self.col + direction.dx
        row = self.row + direction.dy
        tcol, trow = target
        return (col - tcol) ** 2 + (row - trow) ** 2

    def _chase_target(self, player_cell: Cell) -> Cell:
        """Compute the CHASE-mode target cell, varied by ghost personality.
 
        - blinky: targets the player directly (classic aggressive chaser).
        - pinky: targets 4 cells ahead of the player (ambush).
        - inky: targets near the player with randomized jitter
          (unpredictable).
        - clyde: chases directly when far away, but flees home once close
          (the classic "shy" behaviour) so it doesn't pile onto the player.
        - anything else: falls back to direct chase.
        """
        pcol, prow = player_cell
        if self.name == "pinky":
            return pcol + 4, prow - 4
        if self.name == "inky":
            return pcol + random.choice((-4, 4)), prow + random.choice((-4, 4))
        if self.name == "clyde":
            distance = (self.col - pcol) ** 2 + (self.row - prow) ** 2
            if distance <= 64:  # within 8 cells: get shy, retreat home
                return self.home_col, self.home_row
            return pcol, prow
        return pcol, prow  # blinky and default

    def _update_eaten(self, maze: "Maze", dt: float) -> None:
        self.respawn_timer = max(0.0, self.respawn_timer - dt)
        home = (self.home_col, self.home_row)
        self.choose_direction(maze, home)
        self.update(maze, dt, speed_multiplier=self._EATEN_SPEED_MULT)
        if (self.col, self.row) == home and self.respawn_timer <= 0.0:
            self.snap(self.home_col, self.home_row)
            self.state = GhostState.CHASE

    def _update_frightened(self, maze: "Maze", dt: float, player_cell: Cell) -> None:
        self.frightened_timer = max(0.0, self.frightened_timer - dt)
        self.choose_direction(maze, player_cell)
        self.update(maze, dt, speed_multiplier=self._FRIGHTENED_SPEED_MULT)
        if self.frightened_timer <= 0.0:
            self.state = GhostState.CHASE
 
    def _update_chase(self, maze: "Maze", dt: float, player_cell: Cell) -> None:
        target = self._chase_target(player_cell)
        self.choose_direction(maze, target)
        self.update(maze, dt, speed_multiplier=self._CHASE_SPEED_MULT)

    def update_ai(self, maze: "Maze", dt: float, player_cell: Cell) -> None:
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
