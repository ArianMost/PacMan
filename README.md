*This project has been created as part of the 42 curriculum by `amostash` and `spostica`.*

---

# Pac-Man 42

## Description

This project is a Python implementation of the classic arcade game Pac-Man, developed with an object-oriented and modular architecture.
The project focuses on gameplay completeness, robustness, and maintainability:

- Playable multi-level Pac-Man loop
- Configurable game behavior via a commented JSON config file
- Persistent top-10 highscores
- Integration of an external A-Maze-ing maze generator package
- Menu / game-over / victory UI flow
- Cheat mode for testing and peer-evaluation convenience
- Packaging-ready project with Makefile automation (install, run, lint, test, build)

Main game loop:

`Main Menu → Start Game → Win/Lose → Enter Name (save highscore) → Back to Main Menu`

---

## Instructions

### Requirements

- Python 3.10 or later (below 3.14 — pygame doesn't ship wheels for 3.14 yet)
- [`uv`](https://docs.astral.sh/uv/) for dependency management

### Installation

```bash
make install
```

This installs `uv` if it's missing, syncs dependencies (`pygame`), installs the bundled `mazegenerator` wheel, and writes a `.env` file.

### Usage

```bash
# Run with the default configuration (config.json)
make run

# Run with your own configuration
make run CONFIG=my_config.json

# Run directly, once dependencies are installed
uv run pac-man.py my_config.json
```

### Debug

```bash
make debug
make debug CONFIG=my_config.json
```

### Lint

```bash
make lint
```

Optional stricter check:

```bash
make lint-strict
```

### Test

```bash
make test
```

### Build

```bash
make build
```

Packages the game into a standalone executable via PyInstaller and produces `dist/pacman-linux.zip`.
The build is implemented in build.sh and pacman.spec. A ready-made build is published on itch.io and can be downloaded here: https://arianmost.itch.io/pac-man-42

---

## Play

### Controls

- **W** or **⇧** — Move Up
- **A** or **⇦** — Move Left
- **S** or **⇩** — Move Down
- **D** or **⇨** — Move Right
- **P** or **Esc** — Pause / Resume
- **Enter** or **Space** — Confirm menu selection / start level
- **Esc** — Back out of a menu

#### Cheat mode

Cheat mode is toggled live during gameplay, no config flag needed. Press **F1** first to enable the master switch — the other keys only take effect while it's on:

- **F1** — Cheat mode master switch (enable/disable)
- **F2** — Invincibility (no life lost when caught by a ghost)
- **F3** — Freeze all ghosts in place
- **F4** — Speed boost (player moves faster)
- **F5** — Extra life
- **F6** — Skip to the next level

### Configuration

The configuration file controls level layout, timing, and scoring rules. Lines may use `#` or `//` comments, or `/* ... */` block comments — these are stripped before parsing.

```json
{
    "highscore_filename": "highscores.json",
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "cell_size": 24,
    "level_max_time": 120,
    "levels": [
        {
            "level_number": 1,
            "width": 15,
            "height": 11,
            "seed": 101,
            "level_max_time": 75,
            "bonus_fruit_type": "Cherry",
            "points_per_bonus_fruit": 200,
            "walls_color": "#1e2ac9"
        }
    ]
}
```

#### Key notes

- Unknown keys are ignored.
- Missing/invalid values are replaced with safe defaults, with a warning printed to stderr.
- Typical tunables:
  - player lives
  - scoring values (per pacgum, super pacgum, ghost, bonus fruit)
  - level dimensions and per-level time limit
  - random seed (global default, overridable per level)
  - highscore output file path/name

---

## Highscore

The project uses a persistent highscore system stored in JSON (`highscore_filename` from config, default `highscores.json`).
```json
  {
    "name": "example",
    "score": 2000
  },
```

### Behavior

- Highscores are loaded at game start.
- At game end (win or lose), the player can enter a name to save their score, or skip and return to the main menu.
- Name rules:
  - max 10 characters
  - alphanumeric + spaces only
- Score rules:
  - non-negative integer
- Top 10 entries are kept and saved to disk; a corrupt or unreadable highscore file is never fatal — it's logged and the game starts with an empty list instead.

---

## Maze Generation

This project integrates an **assigned external A-Maze-ing package** through a dedicated adapter.

### Integration principles

- The external package is used **as-is**; the adapter (`MazeAdapter`) conforms to its API rather than the other way around.
- `perfect=False` is used for Pac-Man-friendly corridor topology (loops instead of a pure spanning-tree maze).
- Ghost and player spawn points are derived from the generated grid via a BFS search for the nearest open cell to each maze corner / the center.
- If the external generator fails, returns an empty grid, or returns a grid with no open path, the game prints a clear error to stderr and exits rather than running with a broken maze.

---

## Implementation

### Implementation technical summary

- Entry point: `pac-man.py`
- Runtime flow:
  1. Config file parsing/validation (commented JSON → `Config`)
  2. `Game` / `pygame` initialization
  3. Menu → level load → play loop → game-over/victory → highscore entry
- Core design goals:
  - modular code organization under `src/`
  - separation of concerns (config / entities / game state / maze / scoring / UI)
  - invalid config values degrade to safe defaults with a warning instead of crashing

### Key design decisions

- Both Pac-Man and the ghosts use the same grid-based movement model: a current cell, a direction, and a sub-cell progress fraction — no free-form or accelerating movement.
- Ghost AI has three states:
  - **Chase** — each ghost targets Pac-Man using its own personality:
    - Blinky (red) — targets Pac-Man's current cell directly.
    - Pinky (green) — targets 4 cells ahead of Pac-Man.
    - Inky (yellow) — targets near Pac-Man with randomized jitter.
    - Clyde (blue) — chases directly while far away, but flees toward its home corner once within 8 cells (the classic "shy" behaviour).
  - **Frightened** — triggered by a super pacgum; ghosts move with a mix of random and away-from-player choices and can be eaten, with each consecutive ghost eaten in the same window worth double the last.
  - **Eaten** — a caught ghost becomes a pair of eyes that paths straight back to its home corner (via a cached BFS distance field) and revives into Chase after a respawn delay.
- Rendering: the maze is pre-rendered onto a surface for fast blitting, while pellets, Pac-Man, and the ghosts are redrawn every frame.

---

## General Software Architecture

- **Entrypoint Layer**
  - `pac-man.py` — CLI config argument, app launch
- **Configuration Layer**
  - `src/config/config_loader.py` — commented-JSON parsing and validation
  - `src/config/config.py` — `Config` / `LevelConfig` dataclasses with defaults
- **Application Layer**
  - `src/game/game.py` — main loop, input handling, cheat keys
- **Domain/Game Layer**
  - `src/game/state.py` — menu/level state machine, collisions, timers
  - `src/entities/` — player, ghosts, pellet field
  - `src/score/store.py` — scoring rules
- **UI Layer**
  - `src/ui/display.py` — menus, HUD, maze and sprite rendering
- **Persistence Layer**
  - `src/score/highscore.py` — highscore JSON read/write with robust error handling
- **Integration Layer**
  - `src/maze/maze_adapter.py` — adapter over the external `mazegenerator` package

This modular decomposition supports reuse, easier testing, and clearer maintenance boundaries. See [`docs/architecture.md`](docs/architecture.md) for a more detailed breakdown and diagrams.

---

## Resources

[Pac-Man on Wikipedia](https://en.wikipedia.org/wiki/Pac-Man)
[Pac-Man Ghosts Wiki](https://en.wikipedia.org/wiki/Ghosts_(Pac-Man))
[PyGame Docs](https://www.pygame.org/docs/)

### AI Usage

Tools Used:
- ChatGPT (GPT-4)

AI was used to generate images and structuring this README and the documentation.

## License

Part of the 42 curriculum project.
