import pygame
from src.config.config import Config
from src.game.state import GameState, ScreenTypes
from src.score.highscore import HighscoreStore
from src.ui.display import MAIN_MENU_OPTIONS


class Game:
    def __init__(self, config: Config) -> None:
        self.config = config
        pygame.init()
        self.highscores = HighscoreStore(self.config.highscore_filename)
        self.state = GameState(self.config)
        self.menu_index = 0


    def run(self) -> None:
        ...

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type != pygame.KEYDOWN:
                continue

            match self.state.phase:
                case ScreenTypes.MENU:
                    self._handle_menu_keys(event)
                case ScreenTypes.PLAYING:
                    self._handle_play_keys(event)
                case ScreenTypes.PAUSED:
                    self._handle_pause_keys(event)
                case ScreenTypes.INSTRUCTIONS | ScreenTypes.HIGH_SCORES | ScreenTypes.VICTORY | ScreenTypes.GAME_OVER:
                    self._handle_back_only(event)
                case ScreenTypes.END_OF_GAME:
                    self._handle_name_entry(event)

    def _handle_menu_keys(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_DOWN:
            self.menu_index += 1
            if self.menu_index >= len(MAIN_MENU_OPTIONS):
                self.menu_index = 0

        elif event.key == pygame.K_UP:
            self.menu_index -= 1
            if self.menu_index < 0:
                self.menu_index = len(MAIN_MENU_OPTIONS) - 1

        elif event.key == pygame.K_ESCAPE:
            self.running = False

        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            item = MAIN_MENU_OPTIONS[self.menu_index]
            if item == "Start Game":
                self.state.start_new_game()
            elif item == "View Highscores":
                self.state.previous_screen = ScreenTypes.MENU
                self.state.phase = ScreenTypes.HIGH_SCORES
            elif item == "Instructions":
                self.state.previous_screen = ScreenTypes.MENU
                self.state.phase = ScreenTypes.INSTRUCTIONS
            elif item == "Exit":
                self.running = False

    def render(self) -> None:
        ...
