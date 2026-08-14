from enum import Enum
from typing import Tuple
from entity import Entity
from entities.entity import Direction
import random


class GhostState(Enum):
    """Enumeration representing the behavioral states of a ghost."""
    CHASING = 1
    FRIGHTENED = 2
    EATEN = 3


class Ghost(Entity):
    def __init__(self, name: str, color: Tuple[int, int, int]) -> None:
        self.name: str = name
        self.color: Tuple[int, int, int] = color
        self.home_col: int = 0
        self.home_row: int = 0
        self.state: GhostState = GhostState.CHASING
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
 