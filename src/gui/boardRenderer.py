import pygame
from util.constants import (
    BOARD_SIZE, CELL_SIZE, WALL_THICKNESS,
    COLOR_BACKGROUND, COLOR_BOARD, COLOR_GRID, COLOR_WALL,
    COLOR_VALID_MOVE, COLOR_PLAYER1, COLOR_PLAYER2
)


class BoardRenderer:

    def __init__(self, surface):
        self.surface = surface
        self.wall_preview = None
        self.show_valid_moves = False

    def render(self, game_state):
        self.draw_board()
        self.draw_goal_rows()
        self.draw_walls(game_state.board)

        if self.show_valid_moves and not game_state.get_current_player().is_ai:
            self.highlight_valid_moves(game_state.get_valid_moves())

        if self.wall_preview:
            self.draw_wall_preview(*self.wall_preview)

        self.draw_pawns(game_state.players)

    # ------------------------------------------------------------------ board

    def draw_board(self):
        board_px = BOARD_SIZE * CELL_SIZE + (BOARD_SIZE + 1) * WALL_THICKNESS
        self.surface.fill(COLOR_BACKGROUND)

        # Main board rectangle with slight rounded feel via filled rect
        pygame.draw.rect(self.surface, COLOR_BOARD, (0, 0, board_px, board_px))

        # Grid lines
        for i in range(BOARD_SIZE + 1):
            pos = i * (CELL_SIZE + WALL_THICKNESS)
            pygame.draw.rect(self.surface, COLOR_GRID,
                             (pos, 0, WALL_THICKNESS, board_px))
            pygame.draw.rect(self.surface, COLOR_GRID,
                             (0, pos, board_px, WALL_THICKNESS))

    def draw_goal_rows(self):
        """Tint the goal rows for each player."""
        board_px = BOARD_SIZE * CELL_SIZE + (BOARD_SIZE + 1) * WALL_THICKNESS
        tint_h = CELL_SIZE + WALL_THICKNESS

        # Player 1 goal = row 8 (bottom)
        s = pygame.Surface((board_px, tint_h), pygame.SRCALPHA)
        s.fill((80, 200, 255, 18))
        y_bottom = 8 * (CELL_SIZE + WALL_THICKNESS) + WALL_THICKNESS
        self.surface.blit(s, (0, y_bottom - WALL_THICKNESS))

        # Player 2 goal = row 0 (top)
        s2 = pygame.Surface((board_px, tint_h), pygame.SRCALPHA)
        s2.fill((255, 90, 120, 18))
        self.surface.blit(s2, (0, 0))

    # ------------------------------------------------------------------ walls

    def draw_walls(self, board):
        # Horizontal walls
        for y in range(BOARD_SIZE - 1):
            for x in range(BOARD_SIZE - 1):
                if board.horizontal_walls[y][x]:
                    self._draw_h_wall(x, y, COLOR_WALL)

        # Vertical walls
        for y in range(BOARD_SIZE - 1):
            for x in range(BOARD_SIZE - 1):
                if board.vertical_walls[y][x]:
                    self._draw_v_wall(x, y, COLOR_WALL)

    def _draw_h_wall(self, x, y, color, alpha=255):
        px = x * (CELL_SIZE + WALL_THICKNESS) + WALL_THICKNESS
        py = (y + 1) * (CELL_SIZE + WALL_THICKNESS)
        w  = 2 * CELL_SIZE + WALL_THICKNESS
        h  = WALL_THICKNESS
        if alpha == 255:
            pygame.draw.rect(self.surface, color, (px, py, w, h), border_radius=3)
            # Highlight strip on top
            hl = (*color[:3],) if len(color) == 3 else color[:3]
            s = pygame.Surface((w, 3), pygame.SRCALPHA)
            s.fill((*hl, 120))
            self.surface.blit(s, (px, py))
        else:
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            s.fill((*color[:3], alpha))
            self.surface.blit(s, (px, py))

    def _draw_v_wall(self, x, y, color, alpha=255):
        px = (x + 1) * (CELL_SIZE + WALL_THICKNESS)
        py = y * (CELL_SIZE + WALL_THICKNESS) + WALL_THICKNESS
        w  = WALL_THICKNESS
        h  = 2 * CELL_SIZE + WALL_THICKNESS
        if alpha == 255:
            pygame.draw.rect(self.surface, color, (px, py, w, h), border_radius=3)
            s = pygame.Surface((3, h), pygame.SRCALPHA)
            s.fill((*color[:3], 120))
            self.surface.blit(s, (px, py))
        else:
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            s.fill((*color[:3], alpha))
            self.surface.blit(s, (px, py))

    def draw_wall_preview(self, x, y, is_horizontal):
        if is_horizontal:
            self._draw_h_wall(x, y, COLOR_WALL, alpha=100)
        else:
            self._draw_v_wall(x, y, COLOR_WALL, alpha=100)

    # ------------------------------------------------------------------ pawns

    def draw_pawns(self, players):
        for player in players:
            cx = player.x * (CELL_SIZE + WALL_THICKNESS) + WALL_THICKNESS + CELL_SIZE // 2
            cy = player.y * (CELL_SIZE + WALL_THICKNESS) + WALL_THICKNESS + CELL_SIZE // 2
            r  = CELL_SIZE // 3 + 1

            # Shadow
            shadow_s = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(shadow_s, (0, 0, 0, 80), (r + 3, r + 5), r)
            self.surface.blit(shadow_s, (cx - r - 3, cy - r - 3))

            # Body
            pygame.draw.circle(self.surface, player.color, (cx, cy), r)

            # Inner highlight
            hr = max(r // 3, 4)
            hi_s = pygame.Surface((hr * 2, hr * 2), pygame.SRCALPHA)
            pygame.draw.circle(hi_s, (255, 255, 255, 70), (hr, hr), hr)
            self.surface.blit(hi_s, (cx - hr + 3, cy - hr - 4))

            # Crisp outline
            pygame.draw.circle(self.surface, (0, 0, 0), (cx, cy), r, 2)

    # ------------------------------------------------------------------ moves

    def highlight_valid_moves(self, valid_moves):
        for pos in valid_moves:
            px = pos.x * (CELL_SIZE + WALL_THICKNESS) + WALL_THICKNESS
            py = pos.y * (CELL_SIZE + WALL_THICKNESS) + WALL_THICKNESS
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            s.fill(COLOR_VALID_MOVE[:4] if len(COLOR_VALID_MOVE) >= 4 else (*COLOR_VALID_MOVE, 55))
            self.surface.blit(s, (px, py))
            # Dot indicator
            dot_s = pygame.Surface((14, 14), pygame.SRCALPHA)
            pygame.draw.circle(dot_s, (*COLOR_VALID_MOVE[:3], 160), (7, 7), 7)
            self.surface.blit(dot_s, (px + CELL_SIZE // 2 - 7, py + CELL_SIZE // 2 - 7))

    # ------------------------------------------------------------------ utils

    def set_wall_preview(self, preview):
        self.wall_preview = preview

    def toggle_valid_moves(self):
        self.show_valid_moves = not self.show_valid_moves
