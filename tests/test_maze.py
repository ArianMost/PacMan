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
