import pygame
from game.state import GameState, ScreenTypes
from score.highscore import HighscoreStore
from src.constants import MAIN_MENU_OPTIONS, PAUSE_MENU_OPTIONS

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
        highscores: HighscoreStore,
        state: GameState,
        menu_index: int,
        pause_index: int
    ) -> None:
        self.highscores = highscores
        self.state = state
        self.surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.big_font = pygame.font.Font(None, 64)
        self.small_font = pygame.font.Font(None, 36)
        self.menu_selected = menu_index
        self.pause_selected = pause_index

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

    def draw(self) -> None:
        """Draw the screen that matches the current menu phase."""
        if self.state.phase is ScreenTypes.MENU:
            self._draw_menu()
        elif self.state.phase is ScreenTypes.INSTRUCTIONS:
            self._draw_instructions()
        elif self.state.phase is ScreenTypes.HIGH_SCORES:
            self._draw_highscores()
        elif self.state.phase is ScreenTypes.PLAYING:
            self._draw_game()
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
        time_text = f"Time: {int(self.state.level_time_remaining)}"
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
            top_right=(
                self.surface.get_width() - 20,
                20,
            )
        )
        self.surface.blit(time_surface, time_rect)

    def _draw_game(self) -> None:
        """Draw the game and the HUD."""
        self.surface.fill(BLACK)
        # Draw your maze, pellets, player, ghosts, etc. here.
        self._draw_hud()
