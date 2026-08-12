import pygame
import sys
import enum


class GameState(enum.Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()
    current_state = GameState.MENU
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.KEYDOWN:
                if current_state == GameState.MENU and event.key == pygame.K_SPACE:
                    current_state = GameState.PLAYING
                # Example: Pressing ESC quits the game
                elif event.key == pygame.K_ESCAPE:
                    is_running = False
        screen.fill((0, 0, 0))
        if current_state == GameState.MENU:
            # TODO: Draw "Start Game", "View Highscores", "Instructions",
            # "Exit"
            pass

        elif current_state == GameState.PLAYING:
            # TODO: Draw Maze, Player, Ghosts
            # TODO: Draw In-Game HUD (Score, Lives, Level, Time)
            pass
        elif current_state == GameState.PAUSED:
            # TODO: Draw Pause Menu (Resume, Return to main menu)
            pass

        elif current_state == GameState.GAME_OVER:
            # TODO: Draw Final Score and Name Entry prompt
            pass
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
