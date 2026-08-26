import pygame
from game.state import GameState, Phase
from config.config import Config
from score.highscore import HighscoreStore

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREY = (150, 150, 150)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
HIGHSCORE_FILENAME = "highscore.json"

MAIN_MENU_OPTIONS = ["Start Game", "View Highscores", "Instructions", "Exit"]


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
        print("Application created")
        pygame.display.set_caption("Pac-Man")
        self.big_font = pygame.font.Font(None, 64)
        self.small_font = pygame.font.Font(None, 36)
        self.menu_selected = 0

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

    def run(self) -> None:
        """Run the application until the user chooses Exit."""
        clock = pygame.time.Clock()

        # The loop runs as long as the state is not Phase.QUIT
        while self.state.phase is not Phase.QUIT:
            clock.tick(FPS)
            self._handle_events()
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

    def _draw_title(self, text: str, y: int) -> None:
        """Draw a yellow title centered horizontally."""
        title_surface = self.big_font.render(text, True, YELLOW)
        title_rect = title_surface.get_rect(center=(self.surface.get_width()
                                                    // 2, y))
        self.surface.blit(title_surface, title_rect)

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


if __name__ == "__main__":
    pygame.init()
    print("Program started")
    config = Config()
    highscores = HighscoreStore(HIGHSCORE_FILENAME)
    state = GameState(config)

    app = Application(
        config,
        highscores,
        state,
    )

    app.run()
