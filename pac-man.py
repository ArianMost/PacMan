import sys
import pygame
from src.config.config import Config
from src.score.highscore import HighscoreStore
from src.game.state import GameState
from src.ui.display import Display


def main() -> None:
    """CLI entry point for Pac-Man."""
    # 1. Initialize Pygame
    pygame.init()
    # 2. Load the configuration and highscores
    config = Config()
    highscores = HighscoreStore(filename="highscores.json")
    highscores.load()
    # 3. Create the single source of truth (GameState)
    state = GameState(config)
    # 4. Create and run the Application (UI)
    app = Display(highscores, state, 0, 0)
    app.run()


if __name__ == "__main__":
    main()
