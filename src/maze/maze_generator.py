from typing import Protocol, cast, runtime_checkable
import mazegenerator.mazegenerator


@runtime_checkable
class MazeGenerator(Protocol):
    """Interface expected from the assigned A-Maze-ing package."""

    def generate(
        self, width: int, height: int, seed: int, perfect: bool
    ) -> list[list[int]]:
        pass


class ExternalMazeGenerator:
    """Maze generator wrapping the external mazegenerator package."""

    def generate(
        self, width: int, height: int, seed: int = 0, perfect: bool = False
    ) -> list[list[int]]:
        generator = mazegenerator.mazegenerator.MazeGenerator(
            size=(width, height), perfect=perfect, seed=seed
        )
        return cast(list[list[int]], generator.maze)


# class FallbackGenerator:
#     """A backup generator producing a grid with boundary walls."""

#     def generate(
#         self, width: int, height: int, seed: int = 0, perfect: bool = False
#     ) -> list[list[int]]:
#         grid: list[list[int]] = []
#         for r in range(height):
#             row: list[int] = []
#             for c in range(width):
#                 val = 0
#                 if r == 0:
#                     val |= 1  # UP
#                 if c == width - 1:
#                     val |= 2  # RIGHT
#                 if r == height - 1:
#                     val |= 4  # DOWN
#                 if c == 0:
#                     val |= 8  # LEFT
#                 row.append(val)
#             grid.append(row)
#         return grid
