# Team Contributions

Who did what in the Pac-Man project, based on the Jira board (21 tickets,
project key `PAC`) and the git history (207 commits, 10 Aug – 16 Oct 2026).

| | Arian Mostashari | Svetlana Postica |
|---|---|---|
| Jira tickets assigned | 8 | 8 |
| Commits (excluding merges) | 127 (about 119 distinct, see notes) | 39 |
| Merge commits | 32 | 9 |
| Active between | 10 Aug – 16 Oct | 10 Aug – 15 Oct |

Three tickets (PAC-17, PAC-20, PAC-21) are unassigned in Jira; the work
that matches them is credited below from the git history.

## Arian Mostashari

Focus: project foundation, configuration, maze, game core, packaging,
tests and documentation.

### Jira tickets

| Ticket | Title | Resolved |
|---|---|---|
| PAC-1 | Project setup (folder structure, Makefile, flake8, mypy, venv) | 11 Aug |
| PAC-2 | Design game architecture | 13 Aug |
| PAC-3 | Configuration loader | 19 Aug |
| PAC-4 | Maze generator integration | 24 Aug |
| PAC-5 | Level manager | 29 Aug |
| PAC-6 | Player movement and collision detection | 2 Sep |
| PAC-8 | Fixing issues | 4 Sep |
| PAC-7 | Pacgums & Super Pacgums system | 4 Oct |
| PAC-18 | Packaging | 15 Oct |
| PAC-19 | README | 15 Oct |

### What was done, by area

- **Project setup (PAC-1).** Repository structure, `Makefile` (install,
  run, uv/env installer), `pyproject.toml`, `.gitignore`, removal of the
  redundant `requirements.txt`, and the `pac-man.py` entry point.
- **Architecture (PAC-2).** First `docs/architecture.md`, later updated
  for the final structure (15 Oct).
- **Configuration (PAC-3, PAC-21).** `config.json`, the `Config` and
  `LevelConfig` classes, the loader with path finder and dictionary
  casting, level validation, integer validators and comment stripping.
  Later: detailed per-level data, `cell_size`, the `walls_color` option,
  default level configs, and removal of `map_filename`.
- **Maze (PAC-4).** `Maze` type with `is_walkable`, the `MazeGenerator`
  protocol, `MazeAdapter` with its `build` function, integration of the
  bundled `mazegenerator` wheel, and `find_nearest_open` for player and
  ghost spawn points. On 3 Sep the external generator became the default.
- **Level manager (PAC-5).** `load_level`, ghost creation with colour
  mapping, `build_pellet_field`, the `ScreenTypes` enum, `advance_level`
  and `restart_current_level`.
- **Game core and player (PAC-6).** The `Game` class, pygame
  initialisation and event handling, main menu navigation, player
  movement keys, pause handling, name entry and back-key logic, menu
  constants, a player `speed` attribute, and the `FRIGHTENED_DURATION`
  constant. Also the command-line config argument for `main`.
- **Pellets and fruit (PAC-7).** `PelletField` converted to a dataclass,
  the waiting phase and fruit spawning in the game state, fruit no longer
  drawn on non-walkable tiles, and the bonus fruit type change.
- **Gameplay fixes (PAC-8).** Movement and boundary fixes in the entity
  code, `is_walkable` argument order, ghost frightened movement,
  BFS distance field for ghosts returning home, random ghost direction
  choice, ghost speed multipliers and decision logic, a ghost hit radius,
  restart logic, and level time remaining per level. Ghost personality
  behaviours were disabled on 12 Oct.
- **Display fixes.** Wall colour taken from config and blocked cells drawn
  in the maze display (8 Oct).
- **Packaging (PAC-18).** PyInstaller dependency, `build.sh` (Linux zip),
  `pacman.spec` and the `make build` target.
- **Tests and quality (PAC-17, shared).** Config tests (loading, error handling,
  level overrides, wall colour, per-level seed), maze adapter tests
  (injected generator, nearest open cell for the player, ghost spawn
  cells, empty grid exit, seed passthrough, nearest-open BFS), flake8
  venv exclusion, and lint fixes.
- **Documentation (PAC-19).** `README.md`, `docs/architecture.md` and
  `docs/test-results.md`.
- **Repository management.** Opened and merged most pull requests
  (#2–#26) and resolved merge conflicts.

## Svetlana Postica

Focus: ghost AI, scoring and highscores, and all UI (menus, HUD, screens,
display, assets, cheat mode).

### Jira tickets

| Ticket | Title | Resolved |
|---|---|---|
| PAC-9 | Ghost AI | 18 Aug |
| PAC-10 | Scoring system | 20 Aug |
| PAC-11 | Persistent highscore system | 24 Aug |
| PAC-12 | Main menu UI | 26 Aug |
| PAC-13 | HUD (score, lives, timer, level) | 27 Aug |
| PAC-15 | Cheat mode | 1 Sep |
| PAC-14 | Pause menu, Game Over, Victory screens | 2 Sep |
| PAC-16 | Integrate gameplay with UI | 15 Oct |

### What was done, by area

- **Ghost AI (PAC-9).** `ghost.py` and the base `entity` class
  (10–14 Aug), chase targeting (`chase_target`, 16 Aug), the ghost AI
  itself (17 Aug). Later, the movement helpers `step_toward` and the BFS
  algorithm (14–15 Oct) and the ghost updates with the Makefile.
- **Scoring (PAC-10).** Scores, `store` and pellet changes (18–20 Aug),
  fruit scoring (`fruit_score`, 20 Aug), and the player class (19 Aug).
- **Highscores (PAC-11).** Highscore system in three parts (21–22 Aug)
  and later highscore changes (4 Oct).
- **Main menu, HUD and screens (PAC-12, PAC-13, PAC-14).** UI base
  (26 Aug), HUD (26 Aug), pause menu, Game Over and Victory screens
  (28 Aug), `display.py` work (31 Aug, 3 Sep), pause menu follow-up
  (2 Oct).
- **Cheat mode (PAC-15).** The `cheatmode` class (31 Aug).
- **UI integration and assets (PAC-16).** Images (3 Sep), UI and pac-man
  UI refinements (4 Sep), fruit sprites (5 Sep) and the Pac-Man start
  (7 Sep).
- **Music and sound.** The whole audio side of the game: music and sound
  effects (`audios` commit, 7 Oct).
- **Quality (shared).** Config, mypy and pellet fixes (9 Oct), mypy and
  instructions (13 Oct), mypy and docstrings (13 Oct).
- **Repository management.** Merged `main` into the working branch
  several times and merged pull requests #1 and #9.

## Shared and unassigned work

**Testing and debugging.** All testing and debugging across the whole
project was done by both programmers together. The per-person lists above
only show who wrote which tests and fixes in git; they do not split this
work between you.

| Ticket | Title | Jira assignee | Where the work shows up |
|---|---|---|---|
| PAC-17 | Testing, bug fixing, gameplay balancing | Unassigned | Both programmers (unit tests and lint fixes in git from Arian; mypy and docstring passes from Svetlana) |
| PAC-20 | Project management documentation | Unassigned | No matching commits in the git log |
| PAC-21 | Fixing Config issues | Unassigned | Branch `PAC_21-Fixing_config_issues` (PRs #21–#23), Arian |

## Notes on reading the numbers

- Commit counts come from `git log`. Author names appear under several
  machine emails, and Svetlana's two pull-request merges are recorded as
  "Postica Svetlana"; all are counted under the same person.
- Eight of Arian's commits (25–27 Aug: level data, maze integration,
  ghost creation, `build_pellet_field`, `ScreenTypes`) appear twice in the
  log because of a rebase or merge, so the distinct count is about 119.
- Many of Svetlana's commit messages are short ("changes", "ui", "main"),
  so the assignment of those to a specific feature above relies on the
  message and the matching Jira ticket and dates, not on a diff review.
- Ticket-to-commit matching uses ticket titles, branch names that follow
  Jira keys (for example `PAC-03-Configuration`, `PAC5-Level_manager`,
  `PAC6-Game_Core`, `PAC8-Packaging`) and dates. Work after a ticket's
  resolved date is credited to the same area (for example, ghost fixes
  after PAC-9 closed).
- The `bfs_distance_field` function (28 Sep, Arian) and the BFS/`step_toward`
  work (14–15 Oct, Svetlana) both touch ghost movement, so ghost AI
  ended up shared between the two.
