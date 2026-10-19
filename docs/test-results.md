# Test Results

Results of the automated tests for the parts of the project that have
test functions: the configuration package (`src/config/`) and the maze
package (`src/maze/`). Run on 2026-10-15.

## Summary

| Check | Result |
|---|---|
| Unit tests | **16 passed, 0 failed** (0.13 s) |
| Coverage of the tested modules | **81%** (212 of 263 statements) |
| `mypy --strict` on the tested source files | **No issues** in 5 files |
| flake8 on the tested source files | 17 warnings, all in `src/config/config.py` |

## Environment

| Item | Version |
|---|---|
| Python | 3.13.16 (project allows `>=3.10,<3.14`) |
| pytest | 9.1.1 |
| pytest-cov | used for the coverage figures |
| flake8 | 7.4.1 |
| mypy | 2.4.0 |
| mazegenerator | 2.0.1 (installed from the bundled wheel) |
| OS | Linux, headless |

Run in an isolated virtual environment with the project's dependencies,
using `pytest tests/` (the same command as `make test`).

## Unit tests

16 tests in 2 files, all passing.

### `tests/test_config.py` (config loader)

| Test | What it checks | Result |
|---|---|---|
| `test_missing_file` | A nonexistent config file falls back to defaults (3 lives, at least one level). | Pass |
| `test_comments_stripped` | `#` comments are removed, including a commented-out key. | Pass |
| `test_invalid_values` | A negative `lives` and a non-numeric `pacgum` fall back to positive defaults. | Pass |
| `test_unknown_keys` | An unknown key is ignored and known keys still load. | Pass |
| `test_malformed_json` | Invalid JSON falls back to defaults instead of crashing. | Pass |
| `test_levels_keys` | A level's `width` and `height` are read. | Pass |
| `test_level_overrides` | Per-level `level_number`, `seed`, `level_max_time`, `bonus_fruit_type` and `points_per_bonus_fruit` are read. | Pass |
| `test_walls_color` | A valid `walls_color` hex value is kept. | Pass |
| `test_invalid_walls_color` | An invalid `walls_color` falls back to `#1e2ac9`. | Pass |
| `test_invalid_per_level_seed` | An invalid per-level `seed` falls back to the global seed (42). | Pass |

### `tests/test_maze.py` (maze adapter)

| Test | What it checks | Result |
|---|---|---|
| `test_external_generator_adapter` | `MazeAdapter` accepts an injected generator and builds a `Maze` with the right size and player spawn. | Pass |
| `test_player_finds_nearest_open_cell` | The player spawn is the open cell nearest the centre. | Pass |
| `test_ghost_find_open_cells` | Four ghost spawn points are returned and none is on a solid cell. | Pass |
| `test_maze_build_exits` | A generator returning `None` makes `build()` exit with status 1 and an "empty maze grid" message on stderr. | Pass |
| `test_maze_build_using_seed` | The seed passed to `build()` reaches the generator unchanged. | Pass |
| `test_maze_find_nearest_open` | The BFS search finds the nearest open cell from a solid start cell. | Pass |

## Coverage

| File | Statements | Missed | Coverage |
|---|---|---|---|
| `src/config/config.py` | 25 | 0 | 100% |
| `src/config/config_loader.py` | 163 | 39 | 76% |
| `src/maze/maze.py` | 12 | 3 | 75% |
| `src/maze/maze_adapter.py` | 59 | 8 | 86% |
| `src/maze/maze_generator.py` | 4 | 1 | 75% |
| **Total** | **263** | **51** | **81%** |
