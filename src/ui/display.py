import pygame
from game.state import GameState, Phase
from config.config import Config
from score.highscore import HighscoreStore

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREY = (150, 150, 150)
RED = (200, 30, 30)
GREEN = (60, 220, 90)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
HIGHSCORE_FILENAME = "highscore.json"

MAIN_MENU_OPTIONS = ["Start Game", "View Highscores", "Instructions", "Exit"]
PAUSE_MENU_OPTIONS = ["Resume", "Return to Main Menu"]


class Application:
    def __init__(
        self,
        config: Config,
        highscores: HighscoreStore,
        state: GameState,
    ) -> None:
        self.config = config
        self.highscores = highscores
        self.state = state
        self.surface = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Pac-Man")
        self.big_font = pygame.font.Font(None, 64)
        self.small_font = pygame.font.Font(None, 36)
        self.menu_selected = 0
        self.pause_selected = 0
        self.name_buffer = ""

    def _select_menu_option(self) -> None:
        """Perform the action selected in the main menu."""
        option = MAIN_MENU_OPTIONS[self.menu_selected]
        if option == "Start Game":
            self.state.start_new_game() 
        elif option == "View Highscores":
            self.state.phase = Phase.HIGHSCORES
        elif option == "Instructions":
            self.state.phase = Phase.INSTRUCTIONS
        elif option == "Exit":
            self.state.phase = Phase.QUIT

    def _select_pause_option(self) -> None:
        """Perform the action selected in the pause menu."""
        option = PAUSE_MENU_OPTIONS[self.pause_selected]
        if option == "Resume":
            self.state.phase = Phase.PLAYING
        elif option == "Return to Main Menu":
            self.pause_selected = 0
            self.menu_selected = 0
            self.state.phase = Phase.MENU

    def run(self) -> None:
        """Run the application until the user chooses Exit."""
        clock = pygame.time.Clock()

        # The loop runs as long as the state is not Phase.QUIT
        while self.state.phase is not Phase.QUIT:
            dt = clock.tick(FPS) / 1000.0
            self._handle_events()
            if self.state.phase is Phase.PLAYING:
                self.state.update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()

    def _handle_events(self) -> None:
        """Handle keyboard and window events for the menu phase."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state.phase = Phase.QUIT
                continue
            if event.type != pygame.KEYDOWN:
                continue
            # 1. Main Menu Controls
            if self.state.phase is Phase.MENU:
                self._handle_menu_input(event)
            # 2. Return to Menu from Instructions/Highscores
            elif self.state.phase in (Phase.INSTRUCTIONS, Phase.HIGHSCORES):
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    self.state.phase = Phase.MENU
            elif self.state.phase is Phase.PLAYING:
                self._handle_playing_input(event)
            elif self.state.phase is Phase.PAUSED:
                self._handle_pause_input(event)
            elif self.state.phase in (Phase.GAME_OVER, Phase.VICTORY):
                self._handle_end_screen_input(event)
            elif self.state.phase is Phase.ENTER_NAME:
                self._handle_enter_name_input(event)

    def _handle_menu_input(self, event: pygame.event.Event) -> None:
        """Handle keyboard input while the main menu is displayed."""
        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu_selected = (self.menu_selected -
                                  1) % len(MAIN_MENU_OPTIONS)

        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu_selected = (self.menu_selected +
                                  1) % len(MAIN_MENU_OPTIONS)

        elif event.key == pygame.K_RETURN:
            self._select_menu_option()

    def _handle_playing_input(self, event: pygame.event.Event) -> None:
        """Handle keyboard input during gameplay."""
        if event.key == pygame.K_ESCAPE:
            self.pause_selected = 0
            self.state.phase = Phase.PAUSED
        # TODO: forward arrow/WASD keys to
        # self.state.set_player_direction(...) once Player movement
        # input is wired up.
        # if event.key == pygame.K_UP:
        #     self.state.set_player_direction("UP")
        # elif event.key == pygame.K_DOWN:
        #     self.state.set_player_direction("DOWN")
        # elif event.key == pygame.K_LEFT:
        #     self.state.set_player_direction("LEFT")
        # elif event.key == pygame.K_RIGHT:
        #     self.state.set_player_direction("RIGHT")

    def _handle_pause_input(self, event: pygame.event.Event) -> None:
        """Handle keyboard input while the pause menu is displayed."""
        if event.key in (pygame.K_UP, pygame.K_w):
            self.pause_selected = (self.pause_selected -
                                   1) % len(PAUSE_MENU_OPTIONS)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.pause_selected = (self.pause_selected +
                                   1) % len(PAUSE_MENU_OPTIONS)
        elif event.key == pygame.K_RETURN:
            self._select_pause_option()
        elif event.key == pygame.K_ESCAPE:
            # ESC while paused resumes, mirroring how ESC opened the
            # pause menu in the first place.
            self.state.phase = Phase.PLAYING

    def _handle_end_screen_input(self, event: pygame.event.Event) -> None:
        """Handle input on the Game Over / Victory screens.
        Both screens just wait for the player to acknowledge the
        result before moving on to name entry.
        """
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.name_buffer = ""
            self.state.phase = Phase.ENTER_NAME

    def _handle_enter_name_input(self, event: pygame.event.Event) -> None:
        """Handle typing a name to save on the highscore list."""
        if event.key == pygame.K_RETURN:
            if self.name_buffer.strip():
                self.highscores.add(self.name_buffer, self.state.player.score)
                self.highscores.save()
                self.menu_selected = 0
                self.state.phase = Phase.MENU
        elif event.key == pygame.K_BACKSPACE:
            self.name_buffer = self.name_buffer[:-1]
        elif event.key == pygame.K_ESCAPE:
            # Let the player skip saving instead of forcing a name.
            self.menu_selected = 0
            self.state.phase = Phase.MENU
        else:
            char = event.unicode
            is_allowed = char.isalnum() or char == " "
            if char and is_allowed:
                self.name_buffer += char

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
                center=(self.surface.get_width() // 2,
                        start_y + index * line_height)
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
                center=(self.surface.get_width() // 2,
                        start_y + index * line_height)
            )
            self.surface.blit(option_surface, option_rect)
        self._draw_hint("Arrows/WASD to move, Enter to select")

    def _draw_title(self,
                    text: str,
                    y: int,
                    color: tuple[int, int, int] = YELLOW) -> None:
        """Draw a title centered horizontally, yellow by default."""
        title_surface = self.big_font.render(text, True, color)
        title_rect = title_surface.get_rect(center=(self.surface.get_width()
                                                    // 2, y))
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
            f"{self.name_buffer}{cursor}", True, YELLOW
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
                center=(self.surface.get_width() // 2,
                        start_y + index * line_height)
            )
            self.surface.blit(line_surface, line_rect)

    def _draw_hint(self, text: str) -> None:
        """Draw a small grey instruction at the bottom of the screen."""
        hint_surface = self.small_font.render(text, True, GREY)
        hint_rect = hint_surface.get_rect(
            center=(self.surface.get_width() // 2,
                    self.surface.get_height() - 40)
        )
        self.surface.blit(hint_surface, hint_rect)

    def _draw(self) -> None:
        """Draw the screen that matches the current menu phase."""
        if self.state.phase is Phase.MENU:
            self._draw_menu()
        elif self.state.phase is Phase.INSTRUCTIONS:
            self._draw_instructions()
        elif self.state.phase is Phase.HIGHSCORES:
            self._draw_highscores()
        elif self.state.phase is Phase.PLAYING:
            self._draw_game()
        elif self.state.phase is Phase.PAUSED:
            self._draw_pause_menu()
        elif self.state.phase is Phase.GAME_OVER:
            self._draw_game_over()
        elif self.state.phase is Phase.VICTORY:
            self._draw_victory()
        elif self.state.phase is Phase.ENTER_NAME:
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


if __name__ == "__main__":
    pygame.init()
    config = Config()
    highscores = HighscoreStore(HIGHSCORE_FILENAME)
    state = GameState(config)

    app = Application(
        config,
        highscores,
        state,
    )
    app.run()
