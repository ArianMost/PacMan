from entities.player import Player
from score.store import ScoringSystem
from entities.ghost import GHOST_NAMES_COLORS, GhostState
from entities.ghost import Ghost
from typing import List
from entities.palletfield import PelletField, build_pellet_field
from config.config import Config
from src.constants import FRIGHTENED_DURATION
from src.maze.maze import Maze
from src.maze.maze_adapter import MazeAdapter

class GameState:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.player = Player(config.lives)
        self.scoring = ScoringSystem(config)
        self.pellets = PelletField(set(), set())
        self.ghosts: List[Ghost] = []
        self.maze: Maze = Maze()
        self.maze_adapter = MazeAdapter()
        self.current_level_index: int = 0
        self.fruit_cell: tuple | None = None
        self.fruit_timer: float = 0.0

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
            ghost = Ghost(
                col=col,
                row=row,
                name=name,
                color=color
            )

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

        self.maze = self.maze_adapter.build(
            level_config.width,
            level_config.height,
            seed,
            perfect
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
