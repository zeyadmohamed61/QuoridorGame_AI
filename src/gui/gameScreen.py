import pygame

from game.gameState import GameState
from game.pathFinding import Position
from gui.boardRenderer import BoardRenderer
from gui.constants import (
    COLOR_BACKGROUND, COLOR_PANEL, COLOR_PANEL_BORDER,
    COLOR_BUTTON, COLOR_BUTTON_HOVER,
    COLOR_BUTTON_ACCENT, COLOR_BUTTON_ACCENT_HOVER,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_SEPARATOR,
    COLOR_PLAYER1, COLOR_PLAYER2,
    FONT_TITLE, FONT_MEDIUM, FONT_SMALL, FONT_BUTTON, FONT_TINY,
    AI_DELAY_MS
)
from util.constants import (
    BOARD_SIZE, CELL_SIZE, WALL_THICKNESS,
    SIDEBAR_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT,
    BUTTON_WIDTH, BUTTON_HEIGHT
)
from ai.easy_ai   import EasyAI
from ai.medium_ai import MediumAI
from ai.hard_ai   import HardAI


# -------------------------------------------------------------------- Button

class _Btn:
    def __init__(self, rect, text, callback, accent=False, danger=False):
        self.rect     = rect
        self.text     = text
        self.callback = callback
        self.hovered  = False
        self.accent   = accent
        self.danger   = danger

    def draw(self, surface):
        if self.accent:
            base  = COLOR_BUTTON_ACCENT_HOVER if self.hovered else COLOR_BUTTON_ACCENT
            tcol  = (20, 25, 35)
        elif self.danger:
            base  = (180, 55, 75) if self.hovered else (140, 40, 58)
            tcol  = (255, 220, 225)
        else:
            base  = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON
            tcol  = COLOR_TEXT

        pygame.draw.rect(surface, base, self.rect, border_radius=7)
        hl = pygame.Surface((self.rect.w - 4, 2), pygame.SRCALPHA)
        hl.fill((255, 255, 255, 20))
        surface.blit(hl, (self.rect.x + 2, self.rect.y + 1))

        lbl = FONT_BUTTON.render(self.text, True, tcol)
        lr  = lbl.get_rect(center=self.rect.center)
        surface.blit(lbl, lr)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                self.callback()
                return True
        return False


# ----------------------------------------------------------------- GameScreen

class GameScreen:

    def __init__(self, screen, mode, difficulty):
        self.screen     = screen
        self.game_state = GameState(mode, difficulty)

        board_px = BOARD_SIZE * CELL_SIZE + (BOARD_SIZE + 1) * WALL_THICKNESS
        self.board_surface = pygame.Surface((board_px, board_px))
        self.renderer      = BoardRenderer(self.board_surface)

        self.ai_player = None
        if mode == "human_vs_ai":
            if difficulty == "easy":
                self.ai_player = EasyAI(1)
            elif difficulty == "medium":
                self.ai_player = MediumAI(1)
            elif difficulty == "hard":
                self.ai_player = HardAI(1)

        self.return_to_menu = False
        self.ai_thinking    = False
        self.ai_move_time   = 0

        self._sb_x = board_px   # sidebar left edge
        self._sb_w = SIDEBAR_WIDTH
        self.buttons = self._make_buttons()

    # ---------------------------------------------------------- button layout

    def _make_buttons(self):
        bx = self._sb_x + 25
        bw = self._sb_w - 50

        def btn(y, text, cb, **kw):
            return _Btn(pygame.Rect(bx, y, bw, BUTTON_HEIGHT), text, cb, **kw)

        win_h = WINDOW_HEIGHT
        # Place Reset near bottom, then Main Menu below it
        reset_y = win_h - BUTTON_HEIGHT * 2 - 40
        menu_y  = reset_y + BUTTON_HEIGHT + 12

        return [
            btn(reset_y, "Reset  (R)",  self.handle_reset,  accent=True),
            btn(menu_y,  "Main Menu",   self.handle_menu,   danger=True),
        ]

    # ---------------------------------------------------------- mouse helpers

    def _cell_from_mouse(self, pos):
        mx, my = pos
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                cx = x * (CELL_SIZE + WALL_THICKNESS) + WALL_THICKNESS
                cy = y * (CELL_SIZE + WALL_THICKNESS) + WALL_THICKNESS
                if cx <= mx < cx + CELL_SIZE and cy <= my < cy + CELL_SIZE:
                    return (x, y)
        return None

    def _wall_from_mouse(self, pos):
        mx, my  = pos
        thresh  = WALL_THICKNESS + 5
        for y in range(BOARD_SIZE - 1):
            for x in range(BOARD_SIZE - 1):
                hx = x * (CELL_SIZE + WALL_THICKNESS) + WALL_THICKNESS
                hy = (y + 1) * (CELL_SIZE + WALL_THICKNESS)
                hw = 2 * CELL_SIZE + WALL_THICKNESS
                if hx <= mx < hx + hw and hy - thresh <= my < hy + WALL_THICKNESS + thresh:
                    return (x, y, True)

                vx = (x + 1) * (CELL_SIZE + WALL_THICKNESS)
                vy = y * (CELL_SIZE + WALL_THICKNESS) + WALL_THICKNESS
                vh = 2 * CELL_SIZE + WALL_THICKNESS
                if vx - thresh <= mx < vx + WALL_THICKNESS + thresh and vy <= my < vy + vh:
                    return (x, y, False)
        return None

    # ---------------------------------------------------------- handlers

    def handle_mouse_click(self, pos):
        if self.game_state.winner is not None:
            return
        if self.game_state.get_current_player().is_ai:
            return
        cell = self._cell_from_mouse(pos)
        if cell:
            self.game_state.move_pawn(*cell)
            return
        wall = self._wall_from_mouse(pos)
        if wall:
            self.game_state.place_wall(*wall)

    def handle_mouse_move(self, pos):
        self.renderer.set_wall_preview(self._wall_from_mouse(pos))

    def handle_reset(self):
        self.game_state.reset_game()

    def handle_menu(self):
        self.return_to_menu = True

    def handle_key_press(self, key):
        if key == pygame.K_r:
            self.handle_reset()
        elif key == pygame.K_h:
            self.renderer.toggle_valid_moves()

    # ---------------------------------------------------------- AI

    def process_ai_turn(self):
        if self.game_state.winner is not None:
            return
        current = self.game_state.get_current_player()
        if not current.is_ai:
            return
        if not self.ai_thinking:
            self.ai_thinking    = True
            self.ai_move_time   = pygame.time.get_ticks()
            return
        if pygame.time.get_ticks() - self.ai_move_time < AI_DELAY_MS:
            return
        ai_move = self.ai_player.get_move(self.game_state)
        if ai_move:
            if ai_move.type.value == "pawn":
                self.game_state.move_pawn(ai_move.x, ai_move.y)
            else:
                self.game_state.place_wall(ai_move.x, ai_move.y, ai_move.is_horizontal)
        self.ai_thinking = False

    # ---------------------------------------------------------- event loop

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                return
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_move(event.pos)
        elif event.type == pygame.KEYDOWN:
            self.handle_key_press(event.key)

    # ---------------------------------------------------------- drawing

    def draw(self):
        self.screen.fill(COLOR_BACKGROUND)

        # Board
        self.renderer.render(self.game_state)
        self.screen.blit(self.board_surface, (0, 0))

        # Sidebar panel background
        pygame.draw.rect(
            self.screen, COLOR_PANEL,
            (self._sb_x, 0, self._sb_w, WINDOW_HEIGHT)
        )
        pygame.draw.line(
            self.screen, COLOR_PANEL_BORDER,
            (self._sb_x, 0), (self._sb_x, WINDOW_HEIGHT), 2
        )

        self._draw_sidebar()

        # Buttons
        for btn in self.buttons:
            btn.draw(self.screen)

        pygame.display.flip()

    def _draw_sidebar(self):
        sx = self._sb_x
        sw = self._sb_w
        cx = sx + sw // 2

        # ---- Title
        title = FONT_TITLE.render("QUORIDOR", True, COLOR_TEXT)
        self.screen.blit(title, title.get_rect(center=(cx, 32)))
        pygame.draw.line(self.screen, COLOR_SEPARATOR,
                         (sx + 20, 52), (sx + sw - 20, 52), 1)

        # ---- Difficulty / mode badge
        mode  = self.game_state.mode
        diff  = self.game_state.ai_difficulty
        badge = diff.upper() if diff else "2P"
        bs    = FONT_TINY.render(badge, True, (255, 160, 30))
        br    = bs.get_rect(center=(cx, 65))
        self.screen.blit(bs, br)

        # ---- Player panels
        self._draw_player_panel(sx + 20, 85,  sw - 40, 0)
        self._draw_player_panel(sx + 20, 175, sw - 40, 1)

        # ---- Turn indicator
        cur = self.game_state.get_current_player()
        col = COLOR_PLAYER1 if cur.player_id == 0 else COLOR_PLAYER2
        pname = "Player 1" if cur.player_id == 0 else (
            "AI" if cur.is_ai else "Player 2")

        pygame.draw.line(self.screen, COLOR_SEPARATOR,
                         (sx + 20, 273), (sx + sw - 20, 273), 1)

        if self.game_state.winner is None:
            if self.ai_thinking:
                lbl = FONT_SMALL.render("AI is thinking…", True, COLOR_PLAYER2)
            else:
                lbl = FONT_SMALL.render(f"{pname}'s turn", True, col)
        else:
            wid    = self.game_state.winner
            wcol   = COLOR_PLAYER1 if wid == 0 else COLOR_PLAYER2
            wname  = "Player 1" if wid == 0 else (
                "AI" if self.game_state.players[wid].is_ai else "Player 2")
            lbl = FONT_TITLE.render(f"{wname} wins!", True, wcol)

        self.screen.blit(lbl, lbl.get_rect(center=(cx, 293)))

        # ---- Message (small status text)
        msg = FONT_TINY.render(self.game_state.message, True, COLOR_TEXT_DIM)
        self.screen.blit(msg, msg.get_rect(center=(cx, 318)))

        # ---- Hint
        pygame.draw.line(self.screen, COLOR_SEPARATOR,
                         (sx + 20, 335), (sx + sw - 20, 335), 1)
        hint = FONT_TINY.render("H  —  toggle valid moves", True, COLOR_TEXT_DIM)
        self.screen.blit(hint, hint.get_rect(center=(cx, 352)))

    def _draw_player_panel(self, x, y, w, pid):
        h     = 80
        color = COLOR_PLAYER1 if pid == 0 else COLOR_PLAYER2
        player = self.game_state.players[pid]
        is_current = self.game_state.current_player_idx == pid

        # Panel bg
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        alpha = 40 if is_current else 15
        panel.fill((*color[:3], alpha))
        self.screen.blit(panel, (x, y))

        # Active left stripe
        if is_current and self.game_state.winner is None:
            pygame.draw.rect(self.screen, color, (x, y, 3, h), border_radius=2)

        # Pawn icon
        cx_icon = x + 26
        cy_icon = y + h // 2
        pygame.draw.circle(self.screen, color, (cx_icon, cy_icon), 14)
        pygame.draw.circle(self.screen, (0, 0, 0), (cx_icon, cy_icon), 14, 2)

        # Labels
        is_ai  = player.is_ai
        name   = f"Player {pid + 1}" + (" (AI)" if is_ai else "")
        nlbl   = FONT_SMALL.render(name, True, color)
        self.screen.blit(nlbl, (x + 50, y + 12))

        walls  = player.walls_remaining
        wlbl   = FONT_TINY.render("Walls remaining", True, COLOR_TEXT_DIM)
        self.screen.blit(wlbl, (x + 50, y + 34))

        # Wall pip indicators
        for i in range(10):
            pip_x = x + 50 + i * 14
            pip_y = y + 55
            pip_c = color if i < walls else (40, 50, 68)
            pygame.draw.rect(self.screen, pip_c,
                             (pip_x, pip_y, 10, 8), border_radius=2)

    # ---------------------------------------------------------- run

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                self.handle_event(event)
            if self.return_to_menu:
                return True
            self.process_ai_turn()
            self.draw()
            clock.tick(60)
