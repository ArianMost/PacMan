import pytest
from src.maze.maze_adapter import MazeAdapter
from src.maze.maze_generator import MazeGenerator


def test_external_generator_adapter() -> None:
    class FakeGenerator:
        def generate(
                self,
                width: int,
                height: int,
                seed: int,
                perfect: bool
        ) -> list[list[int]]:
            return [
                [15, 15, 15, 15, 15],
                [15, 0, 15, 0, 15],
                [15, 15, 0, 15, 15],
                [15, 0, 15, 0, 15],
                [15, 15, 15, 15, 15],
            ]

    adapter = MazeAdapter(FakeGenerator())
    maze = adapter.build(5, 5, 123)
    assert maze.cols == 5
    assert maze.rows == 5
    assert maze.player_sp == (2, 2)


def test_player_finds_nearest_open_cell() -> None:
    grid = [
        [15, 15, 15],
        [15, 15, 0],
        [15, 15, 15],
    ]
    result = MazeAdapter._get_player_sp(grid, 3, 3)
    assert result == (2, 1)


def test_ghost_find_open_cells() -> None:
    grid = [
        [15, 15, 15, 15, 15],
        [15, 15, 0, 15, 15],
        [15, 0, 0, 0, 15],
        [15, 15, 0, 15, 15],
        [15, 15, 15, 15, 15],
    ]
    spawns = MazeAdapter._get_ghosts_sp(grid, 5, 5)
    assert len(spawns) == 4
    for col, row in spawns:
        assert grid[row][col] != 15


def test_maze_build_exits(capsys: pytest.CaptureFixture[str]) -> None:
    class FakeGenerator(MazeGenerator):
        def generate(
                self,
                width: int,
                height: int,
                seed: int,
                perfect: bool
        ) -> list[list[int]]:
            return [[]]

    adapter = MazeAdapter(FakeGenerator())
    with pytest.raises(SystemExit) as exc_info:
        adapter.build(5, 5, 123)
    assert exc_info.value.code == 1
    assert "empty maze grid" in capsys.readouterr().err


def test_maze_build_using_seed() -> None:
    class FakeGenerator:
        def __init__(self) -> None:
            self.received_seed = 0

        def generate(
                self,
                width: int,
                height: int,
                seed: int,
                perfect: bool
        ) -> list[list[int]]:
            self.received_seed = seed
            return [
                [15, 15, 15],
                [15, 0, 15],
                [15, 15, 15],
            ]
    generator = FakeGenerator()
    adapter = MazeAdapter(generator)
    adapter.build(3, 3, 9876)
    assert generator.received_seed == 9876


def test_maze_find_nearest_open() -> None:
    grid = [
        [15, 15, 15],
        [15, 0, 15],
        [15, 15, 15],
    ]
    result = MazeAdapter._find_nearest_open(grid, 3, 3, 0, 0)
    assert result == (1, 1)
