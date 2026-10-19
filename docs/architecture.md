# Architecture

This document describes the module layout, class structure, runtime flow,
and extension points of the project as it exists in the code today. See
also the [General Software Architecture](../README.md#general-software-architecture)
summary in the README for the short version.

## Project layout

```
pac-man.py                      CLI entry point (argument validation only)
config.json                     Default game configuration (commented JSON allowed)
audio/                          Sound effects and menu music (loaded relative to cwd)
src/
  constants.py                  Menu option lists, FRIGHTENED_DURATION
  config/
    config.py                   Config / LevelConfig dataclasses + DEFAULT_CONFIG
    config_loader.py            Comment stripping, validation, load_config()
  game/
    game.py                     Game: pygame loop, input dispatch, music
    state.py                    GameState + ScreenTypes: rules, collisions, levels
    cheat.py                    CheatMode toggles
  entities/
    entity.py                   Direction enum + Entity base (grid movement)
    player.py                   Player(Entity)
    ghost.py                    Ghost(Entity), GhostState, BFS helpers
    palletfield.py              PelletField + build_pellet_field()
  maze/
    maze.py                     Maze dataclass
    maze_generator.py           MazeGenerator Protocol (the extension point)
    maze_adapter.py             MazeAdapter + ExternalGeneratorAdapter
  score/
    store.py                    ScoringSystem (point rules)
    highscore.py                HighscoreStore / HighscoreEntry (JSON persistence)
  ui/
    display.py                  Display: all pygame rendering
  images/                       Ghost / eyes / frightened sprites
tests/
  test_config.py                Config loader behaviour
  test_maze.py                  MazeAdapter / spawn-point behaviour
```

## Layering and dependencies

```mermaid
flowchart TD
    CLI["pac-man.py<br/>CLI entry point"]
    GAME["game/game.py<br/>Game (pygame loop, input)"]
    UI["ui/display.py<br/>Display (rendering)"]
    STATE["game/state.py<br/>GameState (rules, single source of truth)"]
    CHEAT["game/cheat.py<br/>CheatMode"]
    ENT["entities/<br/>Entity, Player, Ghost, PelletField"]
    SCORE["score/store.py<br/>ScoringSystem"]
    HS["score/highscore.py<br/>HighscoreStore"]
    MAZE["maze/<br/>MazeAdapter, Maze, MazeGenerator"]
    EXT[("mazegenerator<br/>external A-Maze-ing wheel")]
    CFG["config/<br/>load_config, Config, LevelConfig"]

    CLI --> GAME
    GAME --> CFG
    GAME --> STATE
    GAME --> UI
    GAME --> HS
    UI --> STATE
    UI --> HS
    STATE --> ENT
    STATE --> SCORE
    STATE --> CHEAT
    STATE --> MAZE
    STATE --> HS
    SCORE --> ENT
    ENT --> MAZE
    MAZE --> EXT
```

**Dependency rule:** `GameState` never imports from `src/ui/` or
`src/game/game.py`. `Display` reads `GameState` (phase, maze, pellets,
player, ghosts) and only draws; `Game` is the only place that translates
key presses into `GameState` calls and screen-phase changes. All game
rules (scoring, collisions, level progression, timers) live in
`GameState` and the entity classes it owns.

Two deliberate exceptions to be aware of:

- `GameState` imports `pygame` itself, because it loads and plays the
  sound effects. It is therefore not renderer-free, only UI-free.
- Some screen transitions are performed directly by `Game` (for example
  `self.state.phase = ScreenTypes.MENU`) rather than through a
  `GameState` method.

## Class diagram

```mermaid
classDiagram
    class Game {
        -config: Config
        -highscores: HighscoreStore
        -state: GameState
        -display: Display
        -menu_index: int
        -pause_index: int
        -running: bool
        +run() None
        -_handle_events() None
        -_handle_menu_keys(event) None
        -_handle_play_keys(event) None
        -_handle_pause_keys(event) None
        -_handle_back_keys(event) None
        -_handle_name_entry(event) None
        -_handle_waiting_keys(event) None
    }

    class Display {
        -config: Config
        -highscores: HighscoreStore
        -state: GameState
        -surface: pygame.Surface
        +draw() None
        +update_window_for_level() None
    }

    class GameState {
        +HIT_RADIUS: float
        +config: Config
        +phase: ScreenTypes
        +current_level_index: int
        +maze: Maze
        +pellets: PelletField
        +player: Player
        +ghosts: list~Ghost~
        +scoring: ScoringSystem
        +cheat: CheatMode
        +maze_adapter: MazeAdapter
        +fruit_cell: tuple
        +level_time_remained: float
        +is_dying: bool
        +start_new_game() None
        +update(dt) None
        +handle_player_direction(direction) None
        +handle_pause() None
        +advance_level() None
        +restart_current_level() None
        +cheat_skip_level() None
        +cheat_extra_life() None
        -_load_level(index) None
        -_create_ghosts() None
        -_hitting(ghost) bool
    }

    class ScreenTypes {
        <<enumeration>>
        MENU
        INSTRUCTIONS
        HIGH_SCORES
        WAITING_TO_START
        PLAYING
        PAUSED
        GAME_OVER
        VICTORY
        END_OF_GAME
        QUIT
    }

    class Direction {
        <<enumeration>>
        UP
        DOWN
        LEFT
        RIGHT
        NONE
        +dx: int
        +dy: int
        +opposite() Direction
    }

    class Entity {
        +col: int
        +row: int
        +speed_cells_per_sec: float
        +direction: Direction
        +next_direction: Direction
        -_progress: float
        +snap(col, row) None
        +pixel_position(cell_size) tuple
        +can_move(maze, direction) bool
        +available_directions(maze) list~Direction~
        +update(maze, dt, speed_multiplier) None
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
        -_update_chase(maze, dt, player_cell) None
        -_update_frightened(maze, dt, player_cell) None
        -_update_eaten(maze, dt) None
    }

    class GhostState {
        <<enumeration>>
        CHASE
        FRIGHTENED
        EATEN
    }

    class PelletField {
        +pacgums: set
        +super_pacgums: set
        +remaining() int
        +eat_pacgum(cell) bool
        +eat_super_pacgum(cell) bool
    }

    class Maze {
        +grid: list~list~int~~
        +cols: int
        +rows: int
        +ghosts_sp: list~tuple~
        +player_sp: tuple
        +is_walkable(row, col) bool
    }

    class MazeGenerator {
        <<interface>>
        +generate(width, height, seed, perfect) list
    }

    class ExternalGeneratorAdapter {
        +generate(width, height, seed, perfect) list
    }

    class MazeAdapter {
        -_generator: MazeGenerator
        +build(width, height, seed, perfect) Maze
    }

    class ScoringSystem {
        -_ghost_chain: int
        +award_pacgum(player) int
        +award_super_pacgum(player) int
        +award_ghost(player) int
        +award_fruit(player, level) int
        +reset_ghost_chain() None
    }

    class CheatMode {
        +enabled: bool
        +invincible: bool
        +ghosts_frozen: bool
        +speed_boost: bool
        +player_speed_multiplier: float
        +toggle_master() None
        +toggle_invincible() None
        +toggle_ghosts_frozen() None
        +toggle_speed_boost() None
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

    class Config {
        +highscore_filename: str
        +lives: int
        +pacgum: int
        +points_per_pacgum: int
        +points_per_super_pacgum: int
        +points_per_ghost: int
        +seed: int
        +level_max_time: int
        +cell_size: int
        +levels: list~LevelConfig~
    }

    class LevelConfig {
        +level_number: int
        +width: int
        +height: int
        +seed: int
        +level_max_time: int
        +bonus_fruit_type: str
        +points_per_bonus_fruit: int
        +walls_color: str
    }

    Game "1" --> "1" GameState : drives
    Game "1" --> "1" Display : calls draw()
    Game "1" --> "1" HighscoreStore : saves scores
    Display ..> GameState : reads
    Display ..> HighscoreStore : reads top 10

    GameState "1" --> "1" Player
    GameState "1" --> "4" Ghost
    GameState "1" --> "1" PelletField
    GameState "1" --> "1" Maze
    GameState "1" --> "1" MazeAdapter
    GameState "1" --> "1" ScoringSystem
    GameState "1" --> "1" CheatMode
    GameState "1" --> "1" HighscoreStore
    GameState --> ScreenTypes : phase
    GameState --> Config

    Player --|> Entity
    Ghost --|> Entity
    Entity --> Direction
    Ghost --> GhostState
    Entity ..> Maze : reads walls

    MazeAdapter --> MazeGenerator : depends on
    ExternalGeneratorAdapter ..|> MazeGenerator : implements
    MazeAdapter --> Maze : produces

    ScoringSystem ..> Player : adds score
    ScoringSystem --> Config

    HighscoreStore "1" --> "*" HighscoreEntry
    Config "1" --> "*" LevelConfig
```

## Screen flow (`ScreenTypes`)

`GameState.phase` is the single value that decides which input handler
`Game` runs and which screen `Display` draws.

```mermaid
stateDiagram-v2
    direction LR
    [*] --> MENU
    MENU --> WAITING_TO_START : Start
    MENU --> HIGH_SCORES : Scores
    MENU --> INSTRUCTIONS : Help
    HIGH_SCORES --> MENU : Back
    INSTRUCTIONS --> MENU : Back

    WAITING_TO_START --> PLAYING : Go
    WAITING_TO_START --> MENU : Esc

    PLAYING --> PAUSED : P / Esc
    PAUSED --> PLAYING : Resume
    PAUSED --> MENU : Quit to menu

    PLAYING --> WAITING_TO_START : restart or next level
    PLAYING --> GAME_OVER : no lives left
    PLAYING --> VICTORY : final level cleared

    GAME_OVER --> END_OF_GAME : Continue
    VICTORY --> END_OF_GAME : Continue
    END_OF_GAME --> MENU : Save or skip
```

Notes:

- Start leads to `WAITING_TO_START` (Enter, Space or a move key then begins play).
  `WAITING_TO_START` is also entered after a lost life, an expired level
  timer, or a cleared level.
- `END_OF_GAME` is the name-entry screen: Enter saves the score, Esc skips it.
- `ScreenTypes.QUIT` exists and the main loop checks for it, but nothing
  currently assigns it. The game exits via `Game.running = False`
  instead (Exit menu item, Esc on the menu, or closing the window).
- Losing a life is not instant: `GameState` sets `is_dying` and runs a
  1.2 s death timer during which the world is frozen. Only when the
  timer expires is the life removed and the phase changed.
- When the level timer runs out, `restart_current_level()` is called
  without costing a life.

## Runtime flow

### Startup

```mermaid
sequenceDiagram
    participant CLI as pac-man.py
    participant G as game.main()
    participant L as load_config()
    participant App as Game
    participant GS as GameState
    participant D as Display

    CLI->>CLI: validate argv (one *.json argument)
    CLI->>G: main(config_path)
    G->>L: load_config(config_path)
    L-->>G: Config (defaults on any problem, warnings on stderr)
    G->>App: Game(config)
    App->>App: pygame.init(), HighscoreStore(config.highscore_filename)
    App->>GS: GameState(config) (loads audio)
    App->>D: Display(config, highscores, state, ...)
    G->>App: run()
```

### One frame

```mermaid
sequenceDiagram
    participant App as Game.run()
    participant GS as GameState
    participant P as Player
    participant PF as PelletField
    participant G as Ghost
    participant D as Display

    App->>App: dt = clock.tick(FPS) / 1000
    App->>App: _handle_events() (dispatch on phase)
    opt phase == PLAYING
        App->>GS: update(dt)
        alt is_dying
            GS->>GS: tick death_timer, then lose life / game over / restart level
        else normal frame
            GS->>GS: level_time_remained -= dt (expired: restart level)
            GS->>P: update(maze, dt, speed_multiplier)
            GS->>PF: eat_pacgum(cell) / eat_super_pacgum(cell)
            opt super pacgum eaten
                GS->>G: frighten(FRIGHTENED_DURATION) for every ghost
            end
            opt pellets.remaining() == 0
                GS->>GS: advance_level() (next level or VICTORY)
            end
            GS->>GS: spawn / expire / collect bonus fruit
            loop each ghost
                GS->>G: update_ai(maze, dt, player_cell)
                alt pixel distance below HIT_RADIUS
                    alt ghost FRIGHTENED
                        GS->>G: get_eaten(respawn_delay)
                    else ghost CHASE (not invincible)
                        GS->>GS: is_dying = True
                    end
                end
            end
        end
    end
    App->>D: draw() (renders the screen for the current phase)
```

## Entities and movement

### Grid movement with sub-cell progress

`Entity` is the base class for `Player` and `Ghost`. Position is stored as
an integer cell (`col`, `row`) plus a `_progress` value from 0.0 to 1.0
describing how far the entity is toward the next cell in `direction`.

- `update()` adds `speed_cells_per_sec * speed_multiplier * dt` to
  `_progress`. Each time it reaches 1.0 the entity enters the next cell,
  and then tries `next_direction` (a queued turn) at that cell.
- `can_move()` checks the wall bitmask of the current cell:
  `UP=1, RIGHT=2, DOWN=4, LEFT=8`. A cell value of 15 is a fully walled
  (solid) cell.
- `pixel_position(cell_size)` interpolates between cells for smooth
  rendering.

Because `col`/`row` only change on a full cell crossing, anything that
must look correct on screen compares interpolated positions, not cells.
That is why ghost hits use `GameState._hitting()` (pixel distance below
`HIT_RADIUS` = 0.6 cells), while pellet and fruit pickup stay cell-based.

Speeds: `Player` runs at 6.0 cells/s; ghosts use the `Entity` default of
4.0 cells/s scaled per state (chase 0.7x, frightened 0.9x, eaten 1.8x).

### Ghost AI

```mermaid
stateDiagram-v2
    [*] --> CHASE
    CHASE --> FRIGHTENED : super pacgum eaten
    FRIGHTENED --> CHASE : frightened_timer expires
    FRIGHTENED --> EATEN : caught by player
    EATEN --> CHASE : reached home and respawn_timer elapsed
```

| State | Target / behaviour | Decision method |
|---|---|---|
| `CHASE` | All ghosts head for the player's current cell. | On arrival at a new cell, build a BFS distance field to the target and step to a closest neighbour; falls back to `choose_direction` if no path step exists. |
| `FRIGHTENED` | Semi-random flight: 50% random option, 50% option that maximizes squared distance from the player. Never reverses unless it is the only option. `frighten()` also flips the ghost's direction. | `choose_direction`, once per newly entered cell. |
| `EATEN` | Eyes return to the home cell, stop there, and revive into `CHASE` after `respawn_timer`. Cannot be re-frightened meanwhile. | Cached BFS distance field from home, stepping to a strictly closer neighbour. |

Key implementation detail: a ghost only picks a new direction when it
arrives at a cell it has not decided at yet (`_last_decided_cell`), and
assigns `direction` directly. Deciding every frame and only queueing
`next_direction` made turns get validated against the wrong cell when a
crossing happened mid-frame, so ghosts overshot junctions or froze.
`_last_decided_cell` is reset on every state change for the same reason.

`_chase_target()` currently returns the player cell for every ghost, so
the four ghosts differ only in sprite and starting corner.

## Maze generation

`MazeGenerator` (in `maze/maze_generator.py`) is a `typing.Protocol`
describing the one thing the game needs from a generator:

```python
class MazeGenerator(Protocol):
    def generate(self, width: int, height: int, seed: int, perfect: bool) -> list[list[int]]: ...
```

`MazeAdapter` depends on that protocol. By default it uses
`ExternalGeneratorAdapter`, a thin wrapper around the assigned
`mazegenerator` package (installed from the bundled wheel). To use a
different generator, pass any object with a matching `generate()` into
`MazeAdapter(generator=...)`. Everything downstream consumes only the
`Maze` dataclass.

`MazeAdapter.build()`:

1. Calls `generate()` and rejects an empty grid or a grid with no open cell.
2. On any failure it prints an error to stderr and exits with status 1.
   There is no fallback generator.
3. Derives spawn points from the grid with a BFS "nearest open cell"
   search: the four ghosts start near the four corners (inset by one
   cell), the player near the centre.

Levels call `build(..., perfect=False)` so mazes contain loops, which
suits Pac-Man play.

## Configuration

`load_config()` reads the file, strips `#`, `//` and `/* */` comments
outside of strings, parses JSON, and validates each field. Invalid or
missing values produce a warning on stderr and fall back to defaults
from `DEFAULT_CONFIG`; unknown keys are ignored with a warning. Level sizes are
clamped (width 5-40, height 5-30). Per-level `seed` and
`level_max_time` override the global values when present.

## Where each requirement lives

| Subject requirement | Implementation |
|---|---|
| Config file with comments and robust defaults | `src/config/config_loader.py::load_config` |
| Maze generation via the external package | `src/maze/maze_adapter.py::MazeAdapter` + `MazeGenerator` protocol |
| Persistent top-10 highscores | `src/score/highscore.py::HighscoreStore` |
| Cheat mode | `src/game/cheat.py::CheatMode`, keys wired in `Game._handle_play_keys`, effects applied in `GameState.update` |
| Main menu, game view, game-over / victory UI | `src/ui/display.py::Display` |
| Game loop and state machine | `src/game/game.py::Game` + `src/game/state.py::GameState` / `ScreenTypes` |
| Tests | `tests/test_config.py`, `tests/test_maze.py` (`make test`) |

## Known quirks

Behaviour in the current code that is easy to trip over:

- **Two `HighscoreStore` instances.** `Game` creates one from
  `config.highscore_filename` (used for saving and for the highscore
  screen). `GameState` creates its own with a hardcoded
  `"highscores.json"` and only calls `load()` on it. Saving and displaying
  use the configured one, so they agree unless the config names a
  different file.
- **Fruit points ignore config.** `ScoringSystem.award_fruit()` uses a
  hardcoded value per level number; the per-level
  `points_per_bonus_fruit` and `bonus_fruit_type` fields are read by the
  loader but not used for scoring.
- **Duplicate timer attribute.** `GameState` sets both
  `level_time_remaining` (written in `_load_level`, otherwise unused) and
  `level_time_remained` (the one actually used).
- **`ScreenTypes.QUIT` is never assigned**, as noted above.
- **Relative asset paths.** Audio paths (`audio/...`) are relative to the
  working directory, so the game must be started from the project root
  (or the packaged folder).
