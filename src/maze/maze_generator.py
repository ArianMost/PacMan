from typing import Protocol


class MazeGenerator(Protocol):
    """Interface expected from the assigned A-Maze-ing package."""

    def generate(
        self, width: int, height: int, seed: int, perfect: bool
    ) -> list[list[int]]:
        pass
