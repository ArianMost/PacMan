# Architecture

This document describes the class structure, module boundaries, and the
one interface designed for external replacement (the maze generator).
See also the [General Software Architecture](../README.md#general-software-architecture)
summary in the README for the one-paragraph version.

## Layering

```
┌─────────────────────────────────────────────────────────────┐
│  pac-man.py            CLI entry point (arg validation only) │
└───────────────────────────────┬───────────────────────────────┘
                                 │
┌────────────────────────────────▼───────────────────────────────┐
│  src/game/loop.py :: Application                                │
│  pygame init, event loop, input → GameState calls, rendering    │
└───────┬──────────────────────────────────────────────┬──────────┘
        │ reads/renders                                 │ calls
┌───────▼──────────────┐                       ┌─────────▼─────────┐
│  src/ui/              │                       │  src/game/state.py │
│  menu, screens,        │◄──────renders state───│  GameState          │
│  render                │                       │  (single source     │
│                        │                       │   of truth)          │
└────────────────────────┘                       └───┬───────┬───────┬─┘
                                                       │       │       │
                                     ┌──────────────────┘       │       └───────────────┐
                                     │                          │                       │
                          ┌──────────▼─────────┐   ┌────────────▼──────────┐  ┌──────────▼─────────┐
                          │ src/entities/       │   │ src/maze/adapter.py    │  │ src/highscore/      │
                          │ Player, Ghost,       │   │ MazeAdapter            │  │ store.py             │
                          │ PelletField          │   │ (+ pluggable           │  │ HighscoreStore       │
                          │                      │   │  generator)            │  │                      │
                          └──────────────────────┘   └────────────────────────┘  └──────────────────────┘
                                     │
                          ┌──────────▼─────────┐
                          │ src/game/cheat.py   │
                          │ CheatMode           │
                          └─────────────────────┘

                          ┌─────────────────────┐
                          │ src/config/loader.py │  (read once at startup by Application)
                          │ load_config → GameConfig │
                          └─────────────────────┘
```

**Rule of dependency:** `GameState` never imports from `src/ui/` or
`src/game/loop.py`. UI code reads `GameState` and calls its methods; it
never reaches into `Maze`, `Ghost`, or `PelletField` internals directly
except to read plain data for rendering (position, state enum, remaining
pellets). All game rules — scoring, collisions, win/lose, level
progression — live in `GameState` and the entity classes it owns, not in
`Application` or the UI modules.

## Class diagram

```mermaid
classDiagram
    class Application {
        -config: GameConfig
        -highscores: HighscoreStore
        -state: GameState
        -surface: pygame.Surface
        +run() None
        -_handle_events() None
        -_draw() None
    }

    class GameState {
        +config: GameConfig
        +highscores: HighscoreStore
        +cheat: CheatMode
        +maze_adapter: MazeAdapter
        +phase: Phase
        +current_level_index: int
        +maze: Maze
        +pellets: PelletField
        +player: Player
        +ghosts: list~Ghost~
        +level_time_remaining: float
        +start_new_game() None
        +restart_current_level() None
        +advance_level() None
        +set_player_direction(direction) None
        +toggle_pause() None
        +update(dt) None
        +cheat_skip_level() None
        +cheat_extra_life() None
        +submit_highscore() bool
    }

    class Phase {
        <<enumeration>>
        MENU
        INSTRUCTIONS
        HIGHSCORES
        PLAYING
        PAUSED
        ENTER_NAME
        GAME_OVER
        VICTORY
        QUIT
    }

    class Entity {
        +col: int
        +row: int
        +speed_cells_per_sec: float
        +direction: Direction
        +next_direction: Direction
        +snap(col, row) None
        +pixel_position(cell_size) tuple
        +can_move(maze, direction) bool
        +update(maze, dt, speed_multiplier) None
        +available_directions(maze) list~Direction~
    }

    class Player {
        +lives: int
        +score: int
        +add_score(points) None
        +lose_life() bool
        +respawn(col, row) None
    }

    class Ghost {
        +name: str
        +color: tuple
        +home_col: int
        +home_row: int
        +state: GhostState
        +frightened_timer: float
        +respawn_timer: float
        +set_home(col, row) None
        +frighten(duration) None
        +get_eaten(respawn_delay) None
        +choose_direction(maze, target) None
        +update_ai(maze, dt, player_cell) None
    }

    class GhostState {
        <<enumeration>>
        CHASE
        FRIGHTENED
        EATEN
    }

    class PelletField {
        +pacgums: set~tuple~
        +super_pacgums: set~tuple~
        +remaining() int
        +eat_pacgum(cell) bool
        +eat_super_pacgum(cell) bool
    }

    class Maze {
        +grid: list~list~int~~~
        +cols: int
        +rows: int
        +corners: list~tuple~
        +center: tuple
        +is_open(col, row) bool
    }

    class MazeGeneratorProtocol {
        <<interface>>
        +generate(width, height, seed, perfect) list
    }

    class FallbackGenerator {
        +generate(width, height, seed, perfect) list
    }

    class MazeAdapter {
        -_generator: MazeGeneratorProtocol
        +build(width, height, seed, perfect) Maze
    }

    class GameConfig {
        +highscore_filename: str
        +levels: list~LevelConfig~
        +lives: int
        +pacgum: int
        +points_per_pacgum: int
        +points_per_super_pacgum: int
        +points_per_ghost: int
        +seed: int
        +level_max_time: int
        +cell_size: int
    }

    class LevelConfig {
        +width: int
        +height: int
    }

    class HighscoreStore {
        +filename: str
        +entries: list~HighscoreEntry~
        +load() None
        +save() None
        +add(name, score) bool
        +top(count) list~HighscoreEntry~
    }

    class HighscoreEntry {
        +name: str
        +score: int
    }

    class CheatMode {
        +enabled: bool
        +invincible: bool
        +ghosts_frozen: bool
        +speed_boost: bool
        +toggle_master() None
        +toggle_invincible() None
        +toggle_ghosts_frozen() None
        +toggle_speed_boost() None
        +player_speed_multiplier float
    }

    Application --> GameState : drives
    Application --> HighscoreStore : reads for menu display
    Application ..> GameConfig : loads once at startup

    GameState --> Phase : current phase
    GameState "1" --> "1" Player
    GameState "1" --> "*" Ghost
    GameState "1" --> "1" PelletField
    GameState "1" --> "1" Maze
    GameState "1" --> "1" CheatMode
    GameState "1" --> "1" MazeAdapter
    GameState "1" --> "1" HighscoreStore
    GameState "1" --> "1" GameConfig

    Player --|> Entity
    Ghost --|> Entity
    Ghost --> GhostState

    MazeAdapter --> MazeGeneratorProtocol : depends on (injected)
    FallbackGenerator ..|> MazeGeneratorProtocol : implements
    MazeAdapter --> Maze : produces

    GameConfig "1" --> "*" LevelConfig
    HighscoreStore "1" --> "*" HighscoreEntry
```

## Sequence: one frame while playing

```mermaid
sequenceDiagram
    participant User
    participant App as Application
    participant GS as GameState
    participant P as Player
    participant G as Ghost
    participant PF as PelletField

    User->>App: key press (direction)
    App->>GS: set_player_direction(dir)
    loop every frame
        App->>GS: update(dt)
        GS->>P: update(maze, dt, speed_mult)
        GS->>G: update_ai(maze, dt, player_cell)  (for each ghost)
        GS->>PF: eat_pacgum(cell) / eat_super_pacgum(cell)
        alt pellet eaten
            GS->>P: add_score(points)
        end
        alt collision with ghost
            alt ghost frightened
                GS->>G: get_eaten(respawn_delay)
                GS->>P: add_score(points_per_ghost)
            else ghost chasing
                GS->>P: lose_life()
                GS->>GS: phase = GAME_OVER (if out of lives)
            end
        end
        alt pellets.remaining() == 0
            GS->>GS: advance_level() / phase = VICTORY
        end
    end
    App->>GS: read phase, maze, player, ghosts
    App->>User: draw frame
```

## Interfaces

### `MazeGeneratorProtocol` — the only designed extension point

```python
class MazeGeneratorProtocol(Protocol):
    def generate(self, width: int, height: int, seed: int, perfect: bool) -> list[list[int]]:
        ...
```
main
This is the interface the assigned "A-Maze-ing" package is expected to
satisfy. `MazeAdapter` depends on this interface, not on any concrete
generator:

```python
class MazeAdapter:
    def __init__(self, generator: MazeGeneratorProtocol | None = None) -> None:
        self._generator = generator or FallbackGenerator()

    def build(self, width, height, seed, perfect=False) -> Maze:
        # calls self._generator.generate(...), validates the grid,
        # falls back to FallbackGenerator on any failure
```

`FallbackGenerator` is the only class currently implementing the
protocol (structurally — Python's `Protocol` needs no explicit
inheritance). To wire in a real package: wrap it in a class exposing
`generate(width, height, seed, perfect) -> list[list[int]]` and pass an
instance to `MazeAdapter(generator=...)` in `GameState.__init__`. No
other file needs to change, because everything downstream consumes only
the `Maze` dataclass the adapter returns.

### Implicit interfaces (structural, not `Protocol`-declared)

These aren't formal interfaces in the codebase, but they're the
contracts other classes rely on:

| Contract | Used by | Shape |
|---|---|---|
| `Entity` base | `Player`, `Ghost` | grid position (`col`, `row`), `update(maze, dt, speed_multiplier)`, `pixel_position(cell_size)` for rendering |
| Renderable state | `src/ui/render.py` | reads `GameState.maze`, `.pellets`, `.player`, `.ghosts` — never mutates them |
| `Phase`-driven dispatch | `Application._handle_events` / `._draw` | a dict keyed by `Phase` selects the input handler and the draw function each frame |

## Where each requirement lives

| Subject requirement | Implementation |
|---|---|
| Config file with comments, robust defaults | `src/config/loader.py::load_config` |
| Maze generation via external package | `src/maze/adapter.py::MazeAdapter` + `MazeGeneratorProtocol` |
| Persistent highscore, top 10 | `src/highscore/store.py::HighscoreStore` |
| Cheat mode | `src/game/cheat.py::CheatMode`, wired into `GameState` and `Application` |
| Main menu / game view / game-over UI | `src/ui/menu.py`, `src/ui/screens.py`, `src/ui/render.py` |
| Game loop or state machine | `src/game/state.py::Phase` + `GameState`, driven by `src/game/loop.py::Application` |
