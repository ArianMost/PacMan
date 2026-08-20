from config.loader import GameConfig
from entities.player import Player
from score.store import ScoringSystem
from entities.ghost import GhostState
from entities.ghost import Ghost
from typing import List
from entities.palletfield import PelletField
from .maze import Maze

class GameState:
    def __init__(self, config: GameConfig) -> None:
        self.config = config
        self.player = Player(config.lives)
        self.scoring = ScoringSystem(config)
        self.pellets = PelletField(set(), set())
        self.ghosts: List[Ghost] = []
        self.maze: Maze = Maze()

    def update(self, dt: float) -> None:
        """Update the game for one frame."""

        player_cell = (self.player.col, self.player.row)

        if self.pellets.eat_pacgum(player_cell):
            self.scoring.award_pacgum(self.player)

        elif self.pellets.eat_super_pacgum(player_cell):
            self.scoring.award_super_pacgum(self.player)

            for ghost in self.ghosts:
                ghost.frighten(duration=5.0)

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
