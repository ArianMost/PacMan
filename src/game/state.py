import time
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
from src.score.highscore import HighscoreStore
from src.game.cheat import CheatMode
from enum import Enum
import pygame
import os
import random


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
    HIT_RADIUS = 0.6

    def __init__(self, config: Config) -> None:
        self.config = config
        self.highscores = HighscoreStore(filename="highscores.json")
        self.player = Player(config.lives)
        self.scoring = ScoringSystem(config)
        self.pellets = PelletField(set(), set())
        self.ghosts: List[Ghost] = []
        self.phase = ScreenTypes.MENU
        self.previous_screen = ScreenTypes.MENU
        self.maze: Maze = Maze(grid=[[1]], cols=1, rows=1,
                               ghosts_sp=[(0, 0)], player_sp=(0, 0))
        self.maze_adapter = MazeAdapter()
        self.current_level_index: int = 0
        self.fruit_cell: tuple[int, int] | None = None
        self.fruit_timer: float = 0.0
        self.level_time_remained = float(config.level_max_time)
        self.is_dying = False
        self.death_timer = 0.0
        self.fruit_spawned_this_level = False
        self.cheat = CheatMode()
        self.name_player = ""
        self.death_sound: pygame.mixer.Sound | None = None
        self.level_win_sound: pygame.mixer.Sound | None = None
        self.start_music_path: str | None = None
        self.pacgum_sound: pygame.mixer.Sound | None = None
        self.super_pacgum_sound: pygame.mixer.Sound | None = None
        self.fruit_sound: pygame.mixer.Sound | None = None
        self.ghost_eaten_sound: pygame.mixer.Sound | None = None
        try:
            pygame.mixer.init()
            self.death_sound = pygame.mixer.Sound("audio/pac_man_death.wav")
        except Exception as e:
            print(f"Warning: Could not load death sound: {e}")
            self.death_sound = None
        try:
            # Load your level win sound effect (change path as needed)
            win_paths = [
                "audio/level_win.wav"
            ]
            self.level_win_sound = None
            for path in win_paths:
                if os.path.exists(path):
                    self.level_win_sound = pygame.mixer.Sound(path)
                    print(f"Successfully loaded level win sound from: {path}")
                    break
        except Exception as e:
            print(f"Warning: Could not load level win sound: {e}")
            self.level_win_sound = None
        # Load start screen background music
        try:
            music_paths = [
                "audio/pac_man_start_music.mp3"
            ]
            self.start_music_path = None
            for path in music_paths:
                if os.path.exists(path):
                    self.start_music_path = path
                    print(f"Successfully found start music at: {path}")
                    break
        except Exception as e:
            print(f"Warning: Could not setup start music: {e}")
        try:
            # Load your pacgum/pellet eating sound effect
            pellet_paths = [
                "audio/pacgum.wav"
            ]
            self.pacgum_sound = None
            for path in pellet_paths:
                if os.path.exists(path):
                    self.pacgum_sound = pygame.mixer.Sound(path)
                    print(f"Successfully loaded pacgum sound from: {path}")
                    break
        except Exception as e:
            print(f"Warning: Could not load pacgum sound: {e}")
            self.pacgum_sound = None
        try:
            # Load your single audio track for special items
            track_paths = ["audio/super_pacgum_fruit.wav"]
            single_sound = None
            for path in track_paths:
                if os.path.exists(path):
                    single_sound = pygame.mixer.Sound(path)
                    print(f"Successfully loaded shared sound from: {path}")
                    break
            # Use this same sound for both super pac-gum and fruit
            self.super_pacgum_sound = single_sound
            self.fruit_sound = single_sound
            self.ghost_eaten_sound = single_sound
        except Exception as e:
            print(f"Warning: Could not load sound: {e}")
            self.super_pacgum_sound = None
            self.fruit_sound = None

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
        if self.is_dying:
            self.death_timer -= dt
            if self.death_timer <= 0:
                self.is_dying = False
                self.player.lose_life()
                if self.player.lives <= 0:
                    self.phase = ScreenTypes.GAME_OVER
                else:
                    self.restart_current_level()
            return
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
            # === PLAY PELLET EAT SOUND HERE ===
            if hasattr(self, "pacgum_sound") and self.pacgum_sound:
                self.pacgum_sound.play()
        elif self.pellets.eat_super_pacgum(player_cell):
            self.scoring.award_super_pacgum(self.player)
            for ghost in self.ghosts:
                ghost.frighten(duration=FRIGHTENED_DURATION)
            # === PLAY SUPER PAC-GUM SOUND ===
            if self.super_pacgum_sound is not None:
                self.super_pacgum_sound.play()
        if self.pellets.remaining() == 0:
            self.advance_level()
            return

        # Spawn fruit only once when a specific
        # threshold of pacgums is reached
        if (
            self.fruit_cell is None
            and not self.fruit_spawned_this_level
            and 0 < len(self.pellets.pacgums) <= 20
        ):
            open_cells = [
                (c, r)
                for r in range(self.maze.rows)
                for c in range(self.maze.cols)
                if self.maze.is_walkable(c, r)
            ]
            if open_cells:
                self.fruit_cell = random.choice(open_cells)
                self.fruit_timer = 10.0  # Fruit stays for 10 seconds
                self.fruit_spawned_this_level = True

        # Countdown fruit timer or handle eating collision
        # (WITHOUT premature return)
        if self.fruit_cell is not None:
            self.fruit_timer -= dt
            if self.fruit_timer <= 0:
                self.fruit_cell = None
            elif player_cell == self.fruit_cell:
                display_level = self.current_level_index + 1
                self.scoring.award_fruit(self.player, display_level)
                self.fruit_cell = None

                # === PLAY FRUIT SOUND HERE ===
                if self.fruit_sound is not None:
                    self.fruit_sound.play()

        for ghost in self.ghosts:
            if not (self.cheat.enabled and self.cheat.ghosts_frozen):
                ghost.update_ai(self.maze, dt, player_cell)
            if self._hitting(ghost):
                if ghost.state is GhostState.FRIGHTENED:
                    self.scoring.award_ghost(self.player)
                    ghost.get_eaten(respawn_delay=3.0)

                    # Play a sound when eating a frightened ghost.
                    if self.ghost_eaten_sound is not None:
                        self.ghost_eaten_sound.play()

                elif ghost.state is GhostState.CHASE:
                    if not (self.cheat.enabled and self.cheat.invincible):
                        if not self.is_dying:
                            self.is_dying = True
                            self.death_timer = 1.2
                            # === PLAY DEATH SOUND HERE ===
                            if self.death_sound is not None:
                                self.death_sound.set_volume(1.0)
                                self.death_sound.play()

    def handle_player_direction(self, direction: Direction) -> None:
        self.player.next_direction = direction

    def handle_pause(self) -> None:
        if self.phase == ScreenTypes.PLAYING:
            self.phase = ScreenTypes.PAUSED
        elif self.phase == ScreenTypes.PAUSED:
            self.phase = ScreenTypes.PLAYING

    def _create_ghosts(self) -> None:
        self.ghosts = []

        for i in range(len(GHOST_NAMES_COLORS)):
            # Get the ghost's name and color
            name = GHOST_NAMES_COLORS[i][0]
            configured_color = pygame.Color(GHOST_NAMES_COLORS[i][1])
            color = (
                configured_color.r,
                configured_color.g,
                configured_color.b,
            )

            # Get the ghost's starting position
            col = self.maze.ghosts_sp[i][0]
            row = self.maze.ghosts_sp[i][1]

            # Create the ghost
            ghost = Ghost(col=col,
                          row=row,
                          name=name,
                          color=color)

            # Remember the ghost's starting position
            ghost.set_home(col, row)
            self.ghosts.append(ghost)

    def _hitting(self, ghost: Ghost) -> bool:
        px, py = self.player.pixel_position(1)
        gx, gy = ghost.pixel_position(1)
        return (px - gx) ** 2 + (py - gy) ** 2 < self.HIT_RADIUS ** 2

    def _load_level(self, level_index: int) -> None:
        print("LOADING LEVEL:", level_index + 1)
        levels = self.config.levels
        level_config = levels[level_index % len(levels)]
        perfect = False

        if level_config.seed is not None:
            seed = level_config.seed
        else:
            seed = self.config.seed + level_index

        self.level_time_remaining = level_config.level_max_time
        t0 = time.time()
        self.maze = self.maze_adapter.build(
            level_config.width, level_config.height, seed, perfect
        )
        print(f"  -> Maze built in {time.time() - t0:.4f} seconds")
        self._create_ghosts()
        self.player.respawn(*self.maze.player_sp)

        occupied_cells = {(self.player.col, self.player.row)}

        for ghost in self.ghosts:
            occupied_cells.add((ghost.col, ghost.row))

        self.pellets = build_pellet_field(
            maze=self.maze,
            seed=seed,
            corners=[
                (0, 0),
                (self.maze.cols - 1, 0),
                (0, self.maze.rows - 1),
                (self.maze.cols - 1, self.maze.rows - 1),
            ],
            exclude=occupied_cells,
            max_pacgums=self.config.pacgum,
        )
        self.level_time_remained = (
            float(level_config.level_max_time)
            or float(self.config.level_max_time)
        )
        # Reset fruit state for the new level
        self.fruit_cell = None
        self.fruit_spawned_this_level = False
        # self.level_protection_timer = 0.5

    def advance_level(self) -> None:
        print("ADVANCING LEVEL")
        # Play the level win sound effect
        if hasattr(self, "level_win_sound") and self.level_win_sound:
            self.level_win_sound.play()
        self.current_level_index += 1
        max_levels = len(self.config.levels)
        if self.current_level_index >= len(self.config.levels):
            self.phase = ScreenTypes.VICTORY
            self.current_level_index = max_levels - 1
            return
        self._load_level(self.current_level_index)
        self.phase = ScreenTypes.WAITING_TO_START

    def restart_current_level(self) -> None:
        # Reset Pac-Man and ghosts, but keep the pellets already eaten
        self.player.respawn(*self.maze.player_sp)
        for ghost in self.ghosts:
            ghost.snap(ghost.home_col, ghost.home_row)
            ghost.frightened_timer = 0.0
            ghost.respawn_timer = 0.0
            ghost.state = GhostState.CHASE
        self.level_time_remained = float(
            self.config.levels[self.current_level_index].level_max_time
        ) or float(self.config.level_max_time)
        self.phase = ScreenTypes.WAITING_TO_START
