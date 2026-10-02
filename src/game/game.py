import pygame
from src.config.config import Config
from src.config.config_loader import load_config
from src.constants import MAIN_MENU_OPTIONS
from src.entities.entity import Direction
from src.game.state import GameState, ScreenTypes
from src.score.highscore import HighscoreStore
from src.ui.display import Display


DIRECTION_KEY = {
    pygame.K_UP: Direction.UP,
    pygame.K_w: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_s: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_a: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_d: Direction.RIGHT,
}

FPS = 40


class Game:
    def __init__(self, config: Config) -> None:
        self.config = config
        pygame.init()
        self.highscores = HighscoreStore(self.config.highscore_filename)
        self.state = GameState(self.config)
        self.menu_index = 0
        self.pause_index = 0
        self.display = Display(self.highscores, self.state, self.menu_index, self.pause_index)
        self.running = True


    def run(self) -> None:
        """Run the application until the user chooses Exit."""
        clock = pygame.time.Clock()

        # The loop runs as long as the state is not phase.QUIT
        while self.running and self.state.phase is not ScreenTypes.QUIT:
            dt = clock.tick(FPS) / 1000.0
            self._handle_events()
            if self.state.phase is ScreenTypes.PLAYING:
                self.state.update(dt)
            self.display.menu_selected = self.menu_index
            self.display.pause_selected = self.pause_index
            self.display.draw()
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()


    def _handle_events(self) -> None:
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
                case ScreenTypes.WAITING_TO_START:
                    self._handle_waiting_keys(event)
                case ScreenTypes.PAUSED:
                    self._handle_pause_keys(event)
                case ScreenTypes.INSTRUCTIONS | ScreenTypes.HIGH_SCORES | ScreenTypes.VICTORY | ScreenTypes.GAME_OVER:
                    self._handle_back_keys(event)
                case ScreenTypes.END_OF_GAME:
                    self._handle_name_entry(event)

    def _handle_menu_keys(self, event: pygame.event.Event) -> None:
        """Handle keyboard input while the main menu is displayed."""
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
                self.state.phase = ScreenTypes.WAITING_TO_START
            elif item == "View Highscores":
                self.state.previous_screen = ScreenTypes.MENU
                self.state.phase = ScreenTypes.HIGH_SCORES
            elif item == "Instructions":
                self.state.previous_screen = ScreenTypes.MENU
                self.state.phase = ScreenTypes.INSTRUCTIONS
            elif item == "Exit":
                self.running = False

    def _handle_play_keys(self, event: pygame.event.Event) -> None:
        """Handle keyboard input during gameplay."""
        if event.key in DIRECTION_KEY:
            direction = DIRECTION_KEY[event.key]
            self.state.handle_player_direction(direction)

        elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
            self.pause_index = 0
            self.state.handle_pause()

        elif event.key == pygame.K_F1:
            self.state.cheat.toggle_master()
            status = "ENABLED" if self.state.cheat.enabled else "DISABLED"
            print(f"Cheat Mode: {status}")
        elif event.key == pygame.K_F2:
            self.state.cheat.toggle_invincible()
            print(f"Invincibility: {self.state.cheat.invincible}")
        elif event.key == pygame.K_F3:
            self.state.cheat.toggle_ghosts_frozen()
            print(f"Ghosts Frozen: {self.state.cheat.ghosts_frozen}")
        elif event.key == pygame.K_F4:
            self.state.cheat.toggle_speed_boost()
            print(f"Speed Boost: {self.state.cheat.speed_boost}")
        elif event.key == pygame.K_F5:
            self.state.cheat_extra_life()
            print(f"Extra Life Granted! Lives: {self.state.player.lives}")
        elif event.key == pygame.K_F6:
            self.state.cheat_skip_level()
            print("Level Skipped!")

    def _handle_pause_keys(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_DOWN:
            self.pause_index += 1

            if self.pause_index > 1:
                self.pause_index = 0

        elif event.key == pygame.K_UP:
            self.pause_index -= 1

            if self.pause_index < 0:
                self.pause_index = 1

        elif event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
            if self.pause_index == 0:
                self.state.handle_pause()

        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            if self.pause_index == 0:
                self.state.handle_pause()
            else:
                self.state.phase = ScreenTypes.MENU

    def _handle_back_keys(self, event: pygame.event.Event) -> None:
        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            if self.state.phase in (ScreenTypes.GAME_OVER, ScreenTypes.VICTORY):
                self.state.phase = ScreenTypes.END_OF_GAME
            else:
                self.state.phase = ScreenTypes.MENU

    def _handle_name_entry(self, event: pygame.event.Event) -> None:
        """Handle typing a name to save on the highscore list."""
        if event.key == pygame.K_RETURN:
            if self.state.name_player.strip():
                self.highscores.add(self.state.name_player, self.state.player.score)
                self.highscores.save()
                self.state.phase = ScreenTypes.MENU

        elif event.key == pygame.K_BACKSPACE:
            self.state.name_player = self.state.name_player[:-1]

        elif event.key == pygame.K_ESCAPE:
            self.state.phase = ScreenTypes.MENU

        else:
            char = event.unicode
            if char and char.isprintable() and len(self.state.name_player) < 15:
                self.state.name_player += char

    def _handle_waiting_keys(self, event: pygame.event.Event) -> None:
        """Handle input when waiting at the start of a level before ghosts release."""
        if event.key in (pygame.K_RETURN, pygame.K_SPACE) or event.key in DIRECTION_KEY:
            # Transition from waiting to active gameplay
            self.state.phase = ScreenTypes.PLAYING
            if event.key in DIRECTION_KEY:
                self.state.handle_player_direction(DIRECTION_KEY[event.key])
        elif event.key == pygame.K_ESCAPE:
            self.state.phase = ScreenTypes.MENU

def main(config_path: str) -> int:
    config = load_config(config_path)
    HIGHSCORE_FILENAME = "highscore.json"
    pygame.init()
    highscores = HighscoreStore(HIGHSCORE_FILENAME)
    state = GameState(config)

    app = Game(config)
    app.run()
