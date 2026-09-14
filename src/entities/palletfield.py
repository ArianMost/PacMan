from dataclasses import dataclass, field
import random
from typing import Set, Tuple
from src.maze.maze import Maze

@dataclass
class PelletField:
    """
    Manages all the consumable pellets (dots) in the maze.
    Uses sets of (col, row) tuples for ultra-fast collision detection.
    """
    pacgums: Set[Tuple[int, int]] = field(default_factory=set)
    super_pacgums: Set[Tuple[int, int]] = field(default_factory=set)

    def remaining(self) -> int:
        """
        Calculates how many total pellets are left in the maze.
        Useful for determining if the level is complete.

        Returns:
            int: The total count of regular and super pacgums remaining.
        """
        return len(self.pacgums) + len(self.super_pacgums)

    def eat_pacgum(self, cell: Tuple[int, int]) -> bool:
        """
        Attempts to eat a regular pacgum at the given cell coordinate.

        Args:
            cell: The (col, row) tuple representing Pac-Man's current location.

        Returns:
            bool: True if a pacgum was actually eaten, False if the cell was empty.
        """
        if cell in self.pacgums:
            self.pacgums.remove(cell)
            return True
        return False

    def eat_super_pacgum(self, cell: Tuple[int, int]) -> bool:
        """
        Attempts to eat a super-pacgum (power pellet) at the given cell coordinate.

        Args:
            cell: The (col, row) tuple representing Pac-Man's current location.

        Returns:
            bool: True if a super-pacgum was eaten, False if the cell was empty.
        """
        if cell in self.super_pacgums:
            self.super_pacgums.remove(cell)
            return True
        return False


def build_pellet_field(
    maze: Maze,
    seed: int,
    corners: list[tuple[int, int]],
    exclude: set[tuple[int, int]],
    max_pacgums: int,
) -> PelletField:
    """Place super-pacgums on the four maze corners and pacgums on the
    remaining open corridors, capped at ``max_pacgums``."""

    pf = PelletField()
    open_cells = [
        (col, row)
        for row in range(maze.rows)
        for col in range(maze.cols)
        if (
            maze.is_walkable(row, col)
            and (col, row) not in pf.super_pacgums
            and (col, row) not in exclude
        )
    ]

    random_seed = random.Random(seed)
    pf.super_pacgums = set(corners)
    random_seed.shuffle(open_cells)

    if max_pacgums:
        pf.pacgums = set(open_cells[: max(0, max_pacgums)])
    else:
        pf.pacgums = set(open_cells)

    return pf
