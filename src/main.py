import pygame
import sys

from gui.menuScreen import MenuScreen
from gui.gameScreen import GameScreen
from gui.constants import MENU_WIDTH, MENU_HEIGHT
from util.constants import WINDOW_WIDTH, WINDOW_HEIGHT


def main():
    pygame.init()

    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.display.set_caption("Quoridor")

    running = True
    while running:
        menu = MenuScreen(screen)
        mode, difficulty = menu.run()

        if mode is None:
            break

        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        game   = GameScreen(screen, mode, difficulty)

        if not game.run():
            break

        screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
