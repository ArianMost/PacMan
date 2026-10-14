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
