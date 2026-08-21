import sys
from src.constants import OPEN
from src.maze.maze import Maze
from src.maze.maze_generator import MazeGenerator


class MazeAdapter:
    """Adapts whatever generator is configured to the game's needs."""

    def __init__(self, generator: MazeGenerator) -> None:
        self._generator = generator

    def build(self, width: int, height: int, seed: int, perfect: bool = False) -> Maze:
        try:
            grid = self._generator.generate(width, height, seed, perfect)
            if not grid or not grid[0]:
                raise ValueError("empty maze grid")
            if not any(OPEN in row for row in grid):
                raise ValueError("maze grid has no valid path")
        except Exception as e:
            print(f"[maze] external generator failed: {e}; ", file=sys.stderr)
            sys.exit(1)

        return Maze(
            grid=grid, 
            cols=len(grid[0]), 
            rows=len(grid), 
            corners=self._get_corners(grid, len(grid[0]), len(grid)), 
            center=self._get_center(grid, len(grid[0]), len(grid))
        )
