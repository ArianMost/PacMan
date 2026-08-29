import pygame
from src.config.config import Config
from src.game.state import GameState, ScreenTypes
from src.score.highscore import HighscoreStore


class Game:
    def __init__(self, config: Config) -> None:
        self.config = config
        pygame.init()
        self.highscores = HighscoreStore(self.config.highscore_filename)
        self.state = GameState(self.config)

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


    def render(self) -> None:
        ...
