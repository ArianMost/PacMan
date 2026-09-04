import sys
import pygame
import json
from src.config.config import Config, LevelConfig
from src.score.highscore import HighscoreStore
from src.game.state import GameState
from src.ui.display import Display
from src.game.game import Game

from src.config.config_loader import load_config
from src.game.game import Game 

def main() -> None:
    """CLI entry point for Pac-Man."""

    # Get the filename from the terminal, or use an empty string
    config_file = sys.argv[1] if len(sys.argv) > 1 else ""

    # Let your amazing custom loader do all the hard work!
    config = load_config(config_file)

    app = Game(config)
    app.run()

if __name__ == "__main__":
    main()
