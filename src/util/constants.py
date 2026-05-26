# Board dimensions
BOARD_SIZE = 9
CELL_SIZE = 62
WALL_THICKNESS = 10
WALL_LENGTH = 2

# Window dimensions
SIDEBAR_WIDTH = 260
WINDOW_WIDTH = BOARD_SIZE * CELL_SIZE + WALL_THICKNESS * (BOARD_SIZE + 1) + SIDEBAR_WIDTH
WINDOW_HEIGHT = BOARD_SIZE * CELL_SIZE + WALL_THICKNESS * (BOARD_SIZE + 1)

# Game rules
WALLS_PER_PLAYER = 10
MIN_PLAYERS = 2
MAX_PLAYERS = 2

# --- DARK SLATE THEME ---
COLOR_BACKGROUND    = (15, 17, 23)       # near-black
COLOR_BOARD         = (22, 27, 38)       # dark navy board
COLOR_GRID          = (35, 43, 58)       # subtle grid lines
COLOR_WALL          = (255, 160, 30)     # amber wall
COLOR_WALL_PREVIEW  = (255, 160, 30, 90) # amber preview
COLOR_PLAYER1       = (80, 200, 255)     # electric blue
COLOR_PLAYER2       = (255, 90, 120)     # neon rose
COLOR_VALID_MOVE    = (80, 200, 255, 55) # faint blue highlight

# Player starting positions (x, y)
PLAYER_STARTS = [
    (4, 0),  # Player 1 starts at top center
    (4, 8)   # Player 2 starts at bottom center
]

# Player goal rows
PLAYER_GOALS = [
    8,  # Player 1 aims for bottom row
    0   # Player 2 aims for top row
]

# Save directory (kept for compatibility, not used in UI)
SAVE_DIR = "saves"

# UI
BUTTON_WIDTH = 210
BUTTON_HEIGHT = 42
BUTTON_MARGIN = 10
