from typing import Set, Tuple


class PelletField:
    """
    Manages all the consumable pellets (dots) in the maze.
    Uses sets of (col, row) tuples for ultra-fast collision detection.
    """

    def __init__(self, pacgums: set[tuple[int, int]], super_pacgums: set[tuple[int, int]]) -> None:
        """
        Initializes the field with starting pellet coordinates.

        Args:
            pacgums: A set of (col, row) coordinates for regular dots.
            super_pacgums: A set of (col, row) coordinates for power pellets.
        """
        self.pacgums: Set[Tuple[int, int]] = pacgums
        self.super_pacgums: Set[Tuple[int, int]] = super_pacgums

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
