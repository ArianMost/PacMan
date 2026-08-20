from dataclasses import dataclass


@dataclass
class Maze:
    """A generated maze."""

    grid: list[list[int]]
    cols: int
    rows: int
    corners: list[tuple[int, int]]
    center: tuple[int, int]