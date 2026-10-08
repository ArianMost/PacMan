import pygame
from src.config.config import Config
from src.game.state import GameState, ScreenTypes
from src.score.highscore import HighscoreStore
from src.constants import MAIN_MENU_OPTIONS, PAUSE_MENU_OPTIONS
from src.entities.ghost import GhostState
from src.entities.entity import Direction

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREY = (150, 150, 150)
RED = (200, 30, 30)
GREEN = (60, 220, 90)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


class Display:
    def __init__(
        self,
        config: Config,
        highscores: HighscoreStore,
        state: GameState,
        menu_index: int,
        pause_index: int
    ) -> None:
        self.config = config
        self.highscores = highscores
        self.state = state
        self.surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.big_font = pygame.font.Font(None, 64)
        self.small_font = pygame.font.Font(None, 36)
        self.menu_selected = menu_index
        self.pause_selected = pause_index
        self.ghost_images = {}

    def _draw_menu(self) -> None:
        """Draw the main menu and its four selectable options."""
        self.surface.fill(BLACK)
        self._draw_title("PAC-MAN", y=120)
        start_y = 260
        line_height = 50
        for index, option in enumerate(MAIN_MENU_OPTIONS):
            is_selected = index == self.menu_selected
            color = YELLOW if is_selected else WHITE
            text = f"> {option} <" if is_selected else option
            option_surface = self.small_font.render(text, True, color)
            option_rect = option_surface.get_rect(
                center=(
                    self.surface.get_width() // 2,
                    start_y + index * line_height,
                )
            )
            self.surface.blit(option_surface, option_rect)
        self._draw_hint("Arrows/WASD to move, Enter to select")

    def _draw_instructions(self) -> None:
        """Draw the game controls and rules."""
        self.surface.fill(BLACK)
        self._draw_title("Instructions", y=80)

        lines = [
            "Move with the arrow keys or WASD.",
            "Eat every pacgum to clear the level.",
            "Super-pacgums make ghosts frightened.",
            "Eat frightened ghosts to gain bonus points.",
            "Touching a normal ghost costs one life.",
            "Clear all levels to win the game.",
        ]

        self._draw_lines(lines, start_y=160)
        self._draw_hint("Press ESC or Enter to return")

    def _draw_highscores(self) -> None:
        """Draw the top 10 saved high scores."""
        self.surface.fill(BLACK)
        self._draw_title("Highscores", y=80)

        entries = self.highscores.top(10)

        if not entries:
            lines = ["No highscores yet."]
        else:
            lines = [
                f"{rank}. {entry.name} - {entry.score} pts"
                for rank, entry in enumerate(entries, start=1)
            ]
        self._draw_lines(lines, start_y=150)
        self._draw_hint("Press ESC or Enter to return")

    def _draw_pause_menu(self) -> None:
        """Draw the frozen game with a translucent pause menu on top."""
        self._draw_game()  # keep the last frame visible behind the menu
        overlay = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.surface.blit(overlay, (0, 0))
        self._draw_title("PAUSED", y=220)
        start_y = 320
        line_height = 50
        for index, option in enumerate(PAUSE_MENU_OPTIONS):
            is_selected = index == self.pause_selected
            color = YELLOW if is_selected else WHITE
            text = f"> {option} <" if is_selected else option
            option_surface = self.small_font.render(text, True, color)
            option_rect = option_surface.get_rect(
                center=(
                    self.surface.get_width() // 2,
                    start_y + index * line_height,
                )
            )
            self.surface.blit(option_surface, option_rect)
        self._draw_hint("Arrows/WASD to move, Enter to select")

    def _draw_title(
        self, text: str, y: int, color: tuple[int, int, int] = YELLOW
    ) -> None:
        """Draw a title centered horizontally, yellow by default."""
        title_surface = self.big_font.render(text, True, color)
        title_rect = title_surface.get_rect(
            center=(self.surface.get_width() // 2, y)
        )
        self.surface.blit(title_surface, title_rect)

    def _draw_game_over(self) -> None:
        """Draw the Game Over screen with the player's final score."""
        self.surface.fill(BLACK)
        self._draw_title("GAME OVER", y=180, color=RED)
        self._draw_lines(
            [f"Final score: {self.state.player.score}"], start_y=300
        )
        self._draw_hint("Press Enter to save your score")

    def _draw_victory(self) -> None:
        """Draw the Victory screen with a congratulatory message."""
        self.surface.fill(BLACK)
        self._draw_title("YOU WIN!", y=180, color=GREEN)
        self._draw_lines(
            [
                "Congratulations, you cleared every level!",
                f"Final score: {self.state.player.score}",
            ],
            start_y=300,
        )
        self._draw_hint("Press Enter to save your score")

    def _draw_enter_name(self) -> None:
        """Draw the name-entry prompt shown after Game Over/Victory."""
        self.surface.fill(BLACK)
        self._draw_title("New Highscore!", y=140)
        self._draw_lines(
            [f"Final score: {self.state.player.score}"], start_y=220
        )
        prompt_surface = self.small_font.render(
            "Enter your name:", True, WHITE
        )
        prompt_rect = prompt_surface.get_rect(
            center=(self.surface.get_width() // 2, 300)
        )
        self.surface.blit(prompt_surface, prompt_rect)
        # Blinking cursor so an empty/unchanged text box doesn't look frozen.
        cursor = "_" if pygame.time.get_ticks() % 1000 < 500 else " "
        name_surface = self.small_font.render(
            f"{self.state.name_player}{cursor}", True, YELLOW
        )
        name_rect = name_surface.get_rect(
            center=(self.surface.get_width() // 2, 345)
        )
        self.surface.blit(name_surface, name_rect)
        self._draw_hint("Enter to confirm, Esc to skip (max 10 characters)")

    def _draw_lines(
        self,
        lines: list[str],
        start_y: int,
        line_height: int = 36,
    ) -> None:
        """Draw a list of centered white text lines."""
        for index, line in enumerate(lines):
            line_surface = self.small_font.render(line, True, WHITE)
            line_rect = line_surface.get_rect(
                center=(
                    self.surface.get_width() // 2,
                    start_y + index * line_height,
                )
            )
            self.surface.blit(line_surface, line_rect)

    def _draw_hint(self, text: str) -> None:
        """Draw a small grey instruction at the bottom of the screen."""
        hint_surface = self.small_font.render(text, True, GREY)
        hint_rect = hint_surface.get_rect(
            center=(
                self.surface.get_width() // 2,
                self.surface.get_height() - 40,
            )
        )
        self.surface.blit(hint_surface, hint_rect)

    def _draw_waiting_to_start(self) -> None:
        """Draw the frozen game with a prompt to start."""
        self._draw_game()  # Draw the maze and entities in the background

        # Add a dark translucent overlay so text is easier to read
        overlay = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.surface.blit(overlay, (0, 0))

        self._draw_title("GET READY", y=250)
        self._draw_lines(["Press SPACE to start", "Press ESC for menu"], start_y=320)

    def draw(self) -> None:
        """Draw the screen that matches the current menu phase."""
        if self.state.phase is ScreenTypes.MENU:
            self._draw_menu()
        # elif self.state.phase is ScreenTypes.WAITING_TO_START:
        #     self._draw_waiting_to_start()
        elif self.state.phase is ScreenTypes.INSTRUCTIONS:
            self._draw_instructions()
        elif self.state.phase is ScreenTypes.HIGH_SCORES:
            self._draw_highscores()
        elif self.state.phase is ScreenTypes.PLAYING:
            self._draw_game()
        elif self.state.phase is ScreenTypes.WAITING_TO_START:
            self._draw_waiting_to_start()
        elif self.state.phase is ScreenTypes.PAUSED:
            self._draw_pause_menu()
        elif self.state.phase is ScreenTypes.GAME_OVER:
            self._draw_game_over()
        elif self.state.phase is ScreenTypes.VICTORY:
            self._draw_victory()
        elif self.state.phase is ScreenTypes.END_OF_GAME:
            self._draw_enter_name()

    def _draw_hud(self) -> None:
        """Draw the current score, lives, level, and remaining time."""
        score_text = f"Score: {self.state.player.score}"
        lives_text = f"Lives: {self.state.player.lives}"
        level_text = f"Level: {self.state.current_level_index + 1}"
        time_text = f"Time: {int(self.state.level_time_remained)}"
        score_surface = self.small_font.render(
            score_text,
            True,
            WHITE,
        )
        lives_surface = self.small_font.render(
            lives_text,
            True,
            WHITE,
        )
        level_surface = self.small_font.render(
            level_text,
            True,
            WHITE,
        )
        time_surface = self.small_font.render(
            time_text,
            True,
            WHITE,
        )
        self.surface.blit(score_surface, (20, 20))
        self.surface.blit(lives_surface, (20, 55))
        level_rect = level_surface.get_rect(
            midtop=(
                self.surface.get_width() // 2,
                20,
            )
        )
        self.surface.blit(level_surface, level_rect)
        time_rect = time_surface.get_rect(
            topright=(
                self.surface.get_width() - 20,
                20,
            )
        )
        self.surface.blit(time_surface, time_rect)


    def _draw_game(self) -> None:
        """Draw the maze using bitmask wall lines, pellets, entities, and HUD."""
        self.surface.fill(BLACK)

        if not hasattr(self.state, "maze") or not self.state.maze:
            self._draw_hud()
            return

        maze = self.state.maze
        grid = getattr(maze, "grid", getattr(maze, "maze", None))
        if not grid:
            self._draw_hud()
            return

        rows = maze.rows if hasattr(maze, "rows") else len(grid)
        cols = maze.cols if hasattr(maze, "cols") else len(grid[0])

        hud_space = 80
        available_width = WINDOW_WIDTH - 40
        available_height = WINDOW_HEIGHT - hud_space - 20

        cell_size_x = available_width // cols
        cell_size_y = available_height // rows
        cell_size = max(16, min(cell_size_x, cell_size_y))

        maze_pixel_width = cols * cell_size
        maze_pixel_height = rows * cell_size
        offset_x = (WINDOW_WIDTH - maze_pixel_width) // 2
        offset_y = hud_space + (available_height - maze_pixel_height) // 2

        # Draw components modularly
        self._draw_maze_walls(grid, rows, cols, offset_x, offset_y, cell_size, maze_pixel_width, maze_pixel_height)
        self._draw_pellets(offset_x, offset_y, cell_size)
        self._draw_super_gums(offset_x, offset_y, cell_size)
        self._draw_pacman(offset_x, offset_y, cell_size)
        self._draw_ghosts(offset_x, offset_y, cell_size)
        self._draw_fruit(offset_x, offset_y, cell_size)

        # Draw the HUD on top
        self._draw_hud()

    def _draw_maze_walls(self, grid, rows, cols, offset_x, offset_y, cell_size, maze_pixel_width, maze_pixel_height) -> None:
        """Draw maze walls via bitmask lines and outer boundary."""
        wall_color = self.config.levels[self.state.current_level_index].walls_color or (30, 30, 200)
        pygame.draw.rect(self.surface, wall_color, (offset_x, offset_y, maze_pixel_width, maze_pixel_height), 3)

        for row_idx, row in enumerate(grid):
            for col_idx, cell_value in enumerate(row):
                x = offset_x + col_idx * cell_size
                y = offset_y + row_idx * cell_size

                wall_thickness = max(2, cell_size // 8)
                if cell_value & 1:  # UP
                    pygame.draw.line(self.surface, wall_color, (x, y), (x + cell_size, y), wall_thickness)
                if cell_value & 2:  # RIGHT
                    pygame.draw.line(self.surface, wall_color, (x + cell_size, y), (x + cell_size, y + cell_size), wall_thickness)
                if cell_value & 4:  # DOWN
                    pygame.draw.line(self.surface, wall_color, (x, y + cell_size), (x + cell_size, y + cell_size), wall_thickness)
                if cell_value & 8:  # LEFT
                    pygame.draw.line(self.surface, wall_color, (x, y), (x, y + cell_size), wall_thickness)

    def _draw_pellets(self, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Draw standard pacgums."""
        if hasattr(self.state, "pellets") and self.state.pellets:
            if hasattr(self.state.pellets, "pacgums"):
                for pcol, prow in self.state.pellets.pacgums:
                    px = offset_x + pcol * cell_size + cell_size // 2
                    py = offset_y + prow * cell_size + cell_size // 2
                    pygame.draw.circle(self.surface, (255, 180, 180), (px, py), max(2, cell_size // 6))

    def _draw_super_gums(self, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Draw flashing power pellets."""
        if hasattr(self.state, "pellets") and self.state.pellets and hasattr(self.state.pellets, "super_pacgums"):
            super_gums = self.state.pellets.super_pacgums
            current_time = pygame.time.get_ticks()
            if (current_time // 250) % 2 == 0:
                for scol, srow in super_gums:
                    px = offset_x + scol * cell_size + cell_size // 2
                    py = offset_y + srow * cell_size + cell_size // 2
                    pygame.draw.circle(self.surface, (255, 184, 255), (px, py), max(4, cell_size // 3))

    def _draw_pacman(self, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Draw Pac-Man player with directional and animated sprites."""
        if not (hasattr(self.state, "player") and self.state.player):
            return

        px, py = self.state.player.pixel_position(cell_size)
        draw_x = int(offset_x + px)
        draw_y = int(offset_y + py)

        if not hasattr(self, "pacman_images"):
            self.pacman_images = {}

        current_time = pygame.time.get_ticks()

        dir_str = "right"
        player_dir = getattr(self.state.player, "direction", getattr(self.state.player, "current_direction", None))
        if player_dir:
            if hasattr(player_dir, "name"):
                d_name = player_dir.name.lower()
            elif isinstance(player_dir, str):
                d_name = player_dir.lower()
            else:
                d_name = "right"
            if d_name in ("up", "down", "left", "right"):
                dir_str = d_name

        is_dying = getattr(self.state, "is_dying", False)
        if is_dying:
            # Total death duration is 1.2 seconds. Calculate elapsed time from death_timer.
            total_duration = 1.2
            death_timer = getattr(self.state, "death_timer", total_duration)
            elapsed = total_duration - death_timer

            # Divide elapsed time evenly across 3 frames (0.4 seconds per frame)
            # Clamp between 1 and 3 so it never exceeds 3 or loops
            anim_frame = int(elapsed / (total_duration / 3)) + 1
            anim_frame = max(1, min(3, anim_frame))

            action_str = f"die{anim_frame}"
        elif self.state.player.direction is Direction.NONE:
            action_str = "start"
        else:
            # Keep global ticks for normal eating animation so it loops smoothly while moving
            anim_frame = (current_time // 250) % 3 + 1
            action_str = f"eat{anim_frame}"

        cache_key = ("pac_man", dir_str, action_str)

        if cache_key not in self.pacman_images:
            if action_str == "start":
                paths = [
                    "images/pac_man/pac_man_start.png",
                    "src/images/pac_man/pac_man_start.png",
                    "src/images/pac_man.png",
                ]
            elif action_str.startswith("die"):
                paths = [
                    f"images/pac_man/pac_man_{action_str}.png",
                    f"src/images/pac_man/pac_man_{action_str}.png",
                    f"images/pac_man/pac_man_{dir_str}_{action_str}.png",
                    "src/images/pac_man.png",
                ]
            else:
                paths = [
                    f"images/pac_man/pac_man_{dir_str}_{action_str}.png",
                    f"src/images/pac_man/pac_man_{dir_str}_{action_str}.png",
                    f"images/pac_man/pac_man_{action_str}.png",
                    "src/images/pac_man.png",
                ]

            loaded_img = None
            for path in paths:
                try:
                    loaded_img = pygame.image.load(path).convert_alpha()
                    break
                except Exception:
                    continue
            self.pacman_images[cache_key] = loaded_img

        img = self.pacman_images.get(cache_key)

        if img:
            p_width = int(cell_size * 1)
            p_height = int(cell_size * 1)
            scaled_img = pygame.transform.scale(img, (p_width, p_height))
            p_draw_x = draw_x + (cell_size - p_width) // 2
            p_draw_y = draw_y + (cell_size - p_height) // 2
            self.surface.blit(scaled_img, (p_draw_x, p_draw_y))
        else:
            center_x = draw_x + cell_size // 2
            center_y = draw_y + cell_size // 2
            pygame.draw.circle(self.surface, YELLOW, (center_x, center_y), cell_size // 2 - 2)

    def _draw_ghosts(self, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Draw ghosts with frightened, flashing, eyes, and directional states."""
        if not (hasattr(self.state, "ghosts") and self.state.ghosts):
            return

        current_time = pygame.time.get_ticks()
        for ghost in self.state.ghosts:
            gx, gy = ghost.pixel_position(cell_size)
            ghost_name = getattr(ghost, "name", "blinky").lower()

            state_suffix = ""
            if hasattr(ghost, "state"):
                if ghost.state == GhostState.FRIGHTENED:
                    state_suffix = "frightened"
                    frightened_timer = getattr(ghost, "frightened_timer", 2.0)
                    if frightened_timer < 2.0:
                        if (current_time // 300) % 2 == 0:
                            state_suffix = "frightened_flash"
                elif ghost.state == GhostState.EATEN:
                    state_suffix = "eyes"

            dir_str = "left"
            if hasattr(ghost, "direction") and ghost.direction:
                d_name = ghost.direction.name.lower()
                if d_name in ("up", "down", "left", "right"):
                    dir_str = d_name

            cache_key = (ghost_name, state_suffix, dir_str)

            if cache_key not in self.ghost_images:
                paths = []
                if state_suffix == "frightened":
                    paths = [
                        f"src/images/frightened_{dir_str}.png",
                        f"src/images/{ghost_name}_frightened.png",
                        "src/images/frightened.png"
                    ]
                elif state_suffix == "eyes":
                    paths = [
                        f"src/images/eyes_{dir_str}.png",
                        f"src/images/{ghost_name}_eyes_{dir_str}.png",
                        "src/images/eyes.png"
                    ]
                else:
                    paths = [
                        f"src/images/{ghost_name}_{dir_str}.png",
                        f"src/images/{ghost_name}.png",
                        "src/images/ghost.png"
                    ]

                loaded_img = None
                for path in paths:
                    try:
                        loaded_img = pygame.image.load(path).convert_alpha()
                        break
                    except Exception:
                        continue
                self.ghost_images[cache_key] = loaded_img

            img = self.ghost_images.get(cache_key)

            if img:
                ghost_width = int(cell_size * 0.75)
                ghost_height = int(cell_size * 1.25)
                scaled_img = pygame.transform.scale(img, (ghost_width, ghost_height))
                draw_x = int(offset_x + gx + (cell_size - ghost_width) // 2)
                draw_y = int(offset_y + gy)
                self.surface.blit(scaled_img, (draw_x, draw_y))
            else:
                draw_x = int(offset_x + gx)
                draw_y = int(offset_y + gy)
                g_center_x = draw_x + cell_size // 2
                g_center_y = draw_y + cell_size // 2

                if hasattr(ghost, "state") and ghost.state == GhostState.FRIGHTENED:
                    ghost_color = (0, 0, 255)
                elif hasattr(ghost, "state") and ghost.state == GhostState.EATEN:
                    ghost_color = (150, 150, 150)
                else:
                    ghost_color = getattr(ghost, "color", (255, 0, 0))
                    if isinstance(ghost_color, str) and ghost_color.startswith("#"):
                        ghost_color = tuple(int(ghost_color[i:i+2], 16) for i in (1, 3, 5))

                pygame.draw.circle(self.surface, ghost_color, (g_center_x, g_center_y), cell_size // 2 - 2)

    def _draw_fruit(self, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Draw bonus fruit if active."""
        if self.state.fruit_cell is not None:
            level_cfg = self.state.config.levels[self.state.current_level_index]
            fruit_name = str(getattr(level_cfg, "bonus_fruit_type", "Cherry")).lower()
            fruit_filename = fruit_name.replace(" ", "_")
            fcol, frow = self.state.fruit_cell
            fx = offset_x + fcol * cell_size + cell_size // 2
            fy = offset_y + frow * cell_size + cell_size // 2
            cache_key = ("fruit", fruit_filename)

            if cache_key not in self.ghost_images:
                paths = [
                    f"src/images/fruits/{fruit_filename}.png",
                    f"images/fruits/{fruit_filename}.png",
                    f"src/images/{fruit_filename}.png"
                ]
                loaded_fruit = None
                for path in paths:
                    try:
                        loaded_fruit = pygame.image.load(path).convert_alpha()
                        break
                    except Exception:
                        continue
                self.ghost_images[cache_key] = loaded_fruit

            f_img = self.ghost_images.get(cache_key)
            if f_img:
                f_width = int(cell_size * 1.0)
                f_height = int(cell_size * 1.0)
                scaled_fruit = pygame.transform.scale(f_img, (f_width, f_height))
                f_draw_x = fx - f_width // 2
                f_draw_y = fy - f_height // 2
                self.surface.blit(scaled_fruit, (f_draw_x, f_draw_y))
            else:
                pygame.draw.circle(self.surface, (255, 100, 0), (fx, fy), cell_size // 2 - 2)
        self._draw_hud()
