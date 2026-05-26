import pygame
pygame.init()

from util.constants import (
    COLOR_BACKGROUND, COLOR_BOARD, COLOR_GRID, COLOR_WALL,
    COLOR_PLAYER1, COLOR_PLAYER2, COLOR_VALID_MOVE,
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_MARGIN
)

# --- UI PALETTE ---
COLOR_PANEL         = (20, 25, 35)       # sidebar panel
COLOR_PANEL_BORDER  = (40, 50, 68)       # subtle border
COLOR_BUTTON        = (32, 40, 56)       # default button
COLOR_BUTTON_HOVER  = (50, 62, 88)       # hover state
COLOR_BUTTON_ACCENT = (255, 160, 30)     # amber accent button
COLOR_BUTTON_ACCENT_HOVER = (255, 180, 60)
COLOR_TEXT          = (220, 230, 245)    # primary text
COLOR_TEXT_DIM      = (100, 120, 150)    # muted text
COLOR_TEXT_DARK     = (220, 230, 245)    # alias
COLOR_TEXT_GRAY     = (100, 120, 150)    # alias
COLOR_SEPARATOR     = (35, 45, 62)

# --- FONTS (use a clean sans-serif) ---
FONT_TITLE_LARGE = pygame.font.Font(None, 52)
FONT_LARGE       = pygame.font.Font(None, 44)
FONT_TITLE       = pygame.font.Font(None, 32)
FONT_MEDIUM      = pygame.font.Font(None, 26)
FONT_SMALL       = pygame.font.Font(None, 21)
FONT_BUTTON      = pygame.font.Font(None, 23)
FONT_TINY        = pygame.font.Font(None, 18)

# Screen dimensions
MENU_WIDTH  = 640
MENU_HEIGHT = 520

# Animation
AI_DELAY_MS = 600
