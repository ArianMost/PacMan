from enum import Enum
from typing import Tuple, Any
from entity import Entity


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
