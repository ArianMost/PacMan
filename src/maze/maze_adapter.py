import sys
from typing import Deque
from collections import deque
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
            ghosts_sp=self._get_ghosts_sp(grid, len(grid[0]), len(grid)), 
            player_sp=self._get_player_sp(grid, len(grid[0]), len(grid))
        )

    @staticmethod
    def _get_ghosts_sp(
        grid: list[list[int]], cols: int, rows: int
    ) -> list[tuple[int, int]]:
        # maze_corners = [(1, 1), (cols - 2, 1), (1, rows - 2), (cols - 2, rows - 2)]
        # return [
        #     MazeAdapter._find_nearest_open(grid, cols, rows, col, row)
        #     for col, row in maze_corners
        # ]
        return [
            (0, 0),                           # Top-Left
            (cols - 1, 0),                    # Top-Right
            (0, rows - 1),                    # Bottom-Left
            (cols - 1, rows - 1)              # Bottom-Right
        ]

    @staticmethod
    def _get_player_sp(grid: list[list[int]], cols: int, rows: int) -> tuple[int, int]:
        player_col, player_row = cols // 2, rows // 2
        return MazeAdapter._find_nearest_open(grid, cols, rows, player_col, player_row)


    @staticmethod
    def _find_nearest_open(
        grid: list[list[int]],
        cols: int,
        rows: int,
        start_col: int,
        start_row: int,
    ) -> tuple[int, int]:
        """Find the nearest open cell to a starting position using BFS.
        
        The search checks cells in order of their grid distance from the
        starting position, considering four directions (up, down, left, and right).
        """
        queue: Deque[tuple[int, int]] = deque()
        visited: set[tuple[int, int]] = set()

        if start_col > cols - 1:
            start_col = cols - 1
        if start_col < 0:
            start_col = 0

        if start_row > rows - 1:
            start_row = rows - 1
        if start_row < 0:
            start_row = 0
                
        start = (start_col, start_row)
        queue.append(start)
        visited.add(start)

        while queue:
            col, row = queue.popleft()

            if grid[row][col] == OPEN:
                return col, row

            for distance_col, distance_row in (
                (0, -1),
                (0, 1),
                (-1, 0),
                (1, 0),
            ):
                next_col = col + distance_col
                next_row = row + distance_row
                next_cell = (next_col, next_row)

                if (
                    0 <= next_col < cols
                    and 0 <= next_row < rows
                    and next_cell not in visited
                ):
                    queue.append(next_cell)
                    visited.add(next_cell)

        return start