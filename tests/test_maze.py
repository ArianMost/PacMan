import pytest
from src.maze.maze_adapter import MazeAdapter

def test_external_generator_adapter():
    class FakeGenerator:
        def generate(self, width, height, seed, perfect):
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

def test_player_finds_nearest_open_cell():
    grid = [
        [15, 15, 15],
        [15, 15, 0],
        [15, 15, 15],
    ]
    result = MazeAdapter._get_player_sp(grid, 3, 3)
    assert result == (2, 1)

def test_ghost_find_open_cells():
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

def test_maze_build_exits(capsys):
    class FakeGenerator:
        def generate(self, width, height, seed, perfect):
            return None

    adapter = MazeAdapter(FakeGenerator())
    with pytest.raises(SystemExit) as exc_info:
        adapter.build(5, 5, 123)
    assert exc_info.value.code == 1
    assert "empty maze grid" in capsys.readouterr().err

def test_maze_build_using_seed():
    class FakeGenerator:
        def __init__(self):
            self.received_seed = None

        def generate(self, width, height, seed, perfect):
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
