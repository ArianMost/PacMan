<<<<<<< HEAD
=======
from enum import Enum
>>>>>>> 2973399 (ui)
from typing import List
from src.entities.player import Player
from src.score.store import ScoringSystem
from src.entities.ghost import GHOST_NAMES_COLORS, GhostState
from src.entities.ghost import Ghost
from src.entities.palletfield import PelletField, build_pellet_field
from src.entities.entity import Direction
from src.config.config import Config
from src.constants import FRIGHTENED_DURATION
from src.maze.maze import Maze
from src.maze.maze_adapter import MazeAdapter
<<<<<<< HEAD
from src.score.highscore import HighscoreStore
from src.game.cheat import CheatMode
from enum import Enum

# Assuming you saved cheat.py in the src/game/ folder next to state.py
=======
from src.maze.maze_generator import ExternalMazeGenerator
>>>>>>> 2973399 (ui)
from src.game.cheat import CheatMode

class ScreenTypes(Enum):
    MENU = "menu"
    INSTRUCTIONS = "instructions"
    HIGH_SCORES = "high_scores"
    PLAYING = "playing"
    PAUSED = "paused"
    END_OF_GAME = "end_of_game"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    QUIT = "quit"
    WAITING_TO_START = "waiting_to_start"


class GameState:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.highscores = HighscoreStore(filename="highscores.json")
        self.player = Player(config.lives)
        self.scoring = ScoringSystem(config)
        self.pellets = PelletField(set(), set())
        self.ghosts: List[Ghost] = []
        self.phase = ScreenTypes.MENU
        self.previous_screen = ScreenTypes.MENU
        self.maze: Maze = Maze(grid=[], cols=0, rows=0, ghosts_sp=[], player_sp=(0, 0))
        self.maze_adapter = MazeAdapter(ExternalMazeGenerator())
        self.current_level_index: int = 0
        self.fruit_cell: tuple | None = None
        self.fruit_timer: float = 0.0
        self.level_time_remained = float(config.level_max_time)
        self.cheat = CheatMode()
        self.name_player = ""

    def start_new_game(self) -> None:
        """Start a new game, resetting the player and loading level 1."""
        self.player = Player(self.config.lives)
        self.current_level_index = 0
        self.phase = ScreenTypes.WAITING_TO_START
        self._load_level(self.current_level_index)
        self.highscores.load()

    def cheat_skip_level(self) -> None:
        """Instantly beat the current level."""
        if self.cheat.enabled:
            self.advance_level()

    def cheat_extra_life(self) -> None:
        """Grant the player an extra life."""
        if self.cheat.enabled:
            self.player.lives += 1

    def update(self, dt: float) -> None:
        """Update the game for one frame."""
        if self.phase != ScreenTypes.PLAYING:
            return

        self.level_time_remained -= dt
        if self.level_time_remained <= 0:
            self.restart_current_level()

        player_cell = (self.player.col, self.player.row)
        if self.cheat.enabled and self.cheat.speed_boost:
            speed_mult = self.cheat.player_speed_multiplier
        else:
            speed_mult = 1.0
        self.player.update(self.maze, dt, speed_multiplier=speed_mult)
        player_cell = (self.player.col, self.player.row)
        if self.pellets.eat_pacgum(player_cell):
            self.scoring.award_pacgum(self.player)
        elif self.pellets.eat_super_pacgum(player_cell):
            self.scoring.award_super_pacgum(self.player)
            for ghost in self.ghosts:
                ghost.frighten(duration=FRIGHTENED_DURATION)
        if self.fruit_cell is not None:
            if player_cell == self.fruit_cell:
                display_level = self.current_level_index + 1
                self.scoring.award_fruit(self.player, display_level)
                self.fruit_cell = None
        for ghost in self.ghosts:
            if not (self.cheat.enabled and self.cheat.ghosts_frozen):
                ghost.update_ai(self.maze, dt, player_cell)
            if player_cell == (ghost.col, ghost.row):
                if ghost.state is GhostState.FRIGHTENED:
                    self.scoring.award_ghost(self.player)
                    ghost.get_eaten(respawn_delay=3.0)
                elif ghost.state is GhostState.CHASE:
                    if not (self.cheat.enabled and self.cheat.invincible):
                        self.player.lose_life()
                        self.restart_current_level()


    def handle_player_direction(self, direction: Direction) -> None:
        self.player.next_direction = direction

    def handle_pause(self) -> None:
        if self.phase == ScreenTypes.PLAYING:
            self.phase = ScreenTypes.PAUSED
        elif self.phase == ScreenTypes.PAUSED:
            self.phase = ScreenTypes.PLAYING


    def _create_ghosts(self):
        self.ghosts = []

        for i in range(len(GHOST_NAMES_COLORS)):
            # Get the ghost's name and color
            name = GHOST_NAMES_COLORS[i][0]
            color = GHOST_NAMES_COLORS[i][1]

            # Get the ghost's starting position
            col = self.maze.ghosts_sp[i][0]
            row = self.maze.ghosts_sp[i][1]

            # Create the ghost
            ghost = Ghost(col=col, row=row, name=name, color=color)

            # Remember the ghost's starting position
            ghost.set_home(col, row)

            self.ghosts.append(ghost)

    def _load_level(self, level_index: int) -> None:
        levels = self.config.levels
        level_config = levels[level_index % len(levels)]
        perfect = False

        if level_config.seed is not None:
            seed = level_config.seed
        else:
            seed = self.config.seed + level_index

        self.level_time_remaining = level_config.level_max_time
        self.maze = self.maze_adapter.build(
            level_config.width, level_config.height, seed, perfect
        )

        self._create_ghosts()
        self.player.respawn(*self.maze.player_sp)

        occupied_cells = {(self.player.col, self.player.row)}

        for ghost in self.ghosts:
            occupied_cells.add((ghost.col, ghost.row))

        self.pellets = build_pellet_field(
            maze=self.maze,
            seed=seed,
            corners=self.maze.ghosts_sp,
            exclude=occupied_cells,
            max_pacgums=self.config.pacgum,
        )
        self.level_time_remained = float(self.config.level_max_time)


    def advance_level(self) -> None:
        self.current_level_index += 1
        if self.current_level_index >= len(self.config.levels):
            self.phase = ScreenTypes.VICTORY
            return
        self._load_level(self.current_level_index)
        self.phase = ScreenTypes.WAITING_TO_START

    def restart_current_level(self) -> None:
        self._load_level(self.current_level_index)
        self.phase = ScreenTypes.WAITING_TO_START
