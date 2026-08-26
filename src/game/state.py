from numpy._core import einsumfunc
from numpy._core import einsumfunc
from entities.player import Player
from score.store import ScoringSystem
from entities.ghost import GhostState
from entities.ghost import Ghost
from typing import List
from entities.palletfield import PelletField
from .maze import Maze
from config.config import Config

class GameState:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.highscores = HighscoreStore(filename='highscores.json')
        self.player = Player(config.lives)
        self.scoring = ScoringSystem(config)
        self.pellets = PelletField(set(), set())
        self.ghosts: List[Ghost] = []
        self.maze: Maze = Maze()
        self.current_level_index: int = 0
        self.fruit_cell: tuple | None = None
        self.fruit_timer: float = 0.0

    def start_new_game(self) -> None:
        """Start a new game, resetting the player and loading level 1."""
        self.player = Player(self.config.lives)
        self.current_level_index = 0
        self.phase = Phase.PLAYING
        #self._load_current_level()
        self.highscores.load()   

    def update(self, dt: float) -> None:
        """Update the game for one frame."""

        player_cell = (self.player.col, self.player.row)
        if self.pellets.eat_pacgum(player_cell):
            self.scoring.award_pacgum(self.player)
        elif self.pellets.eat_super_pacgum(player_cell):
            self.scoring.award_super_pacgum(self.player)
            for ghost in self.ghosts:
                ghost.frighten(duration=5.0)
        if self.fruit_cell is not None:
            if player_cell == self.fruit_cell:
                display_level = self.current_level_index + 1
                self.scoring.award_fruit(self.player, display_level)
                self.fruit_cell = None
        for ghost in self.ghosts:
            ghost.update_ai(
                self.maze,
                dt,
                player_cell
            )
            if player_cell == (ghost.col, ghost.row):
                if ghost.state is GhostState.FRIGHTENED:
                    self.scoring.award_ghost(self.player)
                    ghost.get_eaten(respawn_delay=3.0)
                elif ghost.state is GhostState.CHASE:
                    self.player.lose_life()
                    # self.restart_current_level()

    def _load_level(self, level_index: int) -> None:
        levels = self.config.levels
        level_config = levels[level_index % len(levels)]
        perfect = False

        if level_config.seed is not None:
            seed = level_config.seed
        else:
            seed = self.config.seed + level_index

        self.maze = self.maze_adapter.build(
            level_config.width,
            level_config.height,
            seed,
            perfect
        )

