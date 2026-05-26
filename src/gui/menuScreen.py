import pygame
import math
from gui.constants import (
    MENU_WIDTH, MENU_HEIGHT,
    COLOR_BACKGROUND, COLOR_PANEL, COLOR_PANEL_BORDER,
    COLOR_BUTTON, COLOR_BUTTON_HOVER,
    COLOR_BUTTON_ACCENT, COLOR_BUTTON_ACCENT_HOVER,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_SEPARATOR,
    COLOR_PLAYER1, COLOR_PLAYER2,
    FONT_TITLE_LARGE, FONT_TITLE, FONT_MEDIUM, FONT_SMALL, FONT_BUTTON,
    BUTTON_WIDTH, BUTTON_HEIGHT
)


class Button:
    def __init__(self, x, y, width, height, text, callback, accent=False):
        self.rect    = pygame.Rect(x, y, width, height)
        self.text    = text
        self.callback = callback
        self.hovered  = False
        self.accent   = accent

    def draw(self, surface):
        if self.accent:
            color = COLOR_BUTTON_ACCENT_HOVER if self.hovered else COLOR_BUTTON_ACCENT
            text_color = (20, 25, 35)
        else:
            color = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON
            text_color = COLOR_TEXT

        # Shadow
        shadow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 60))
        surface.blit(shadow, (self.rect.x + 2, self.rect.y + 3))

        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        # Top-edge highlight
        hl = pygame.Surface((self.rect.width - 4, 2), pygame.SRCALPHA)
        hl.fill((255, 255, 255, 25))
        surface.blit(hl, (self.rect.x + 2, self.rect.y + 1))

        label = FONT_BUTTON.render(self.text, True, text_color)
        lr    = label.get_rect(center=self.rect.center)
        surface.blit(label, lr)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                self.callback()
                return True
        return False


class MenuScreen:

    def __init__(self, screen):
        self.screen = screen
        self.buttons = []
        self.selected_mode       = None
        self.selected_difficulty = None
        self._tick = 0  # for simple animation

        modes = [
            ("2 Players",             "human_vs_human", None,     True),
            ("vs AI  —  Easy",        "human_vs_ai",    "easy",   False),
            ("vs AI  —  Medium",      "human_vs_ai",    "medium", False),
            ("vs AI  —  Hard",        "human_vs_ai",    "hard",   False),
        ]

        bw       = BUTTON_WIDTH
        start_y  = 230
        spacing  = BUTTON_HEIGHT + 14

        for i, (text, mode, diff, accent) in enumerate(modes):
            bx = (MENU_WIDTH - bw) // 2
            by = start_y + i * spacing
            self.buttons.append(Button(
                bx, by, bw, BUTTON_HEIGHT, text,
                lambda m=mode, d=diff: self._start(m, d),
                accent=accent
            ))

    def _start(self, mode, difficulty):
        self.selected_mode       = mode
        self.selected_difficulty = difficulty

    # ------------------------------------------------------ helpers

    def _draw_background(self):
        self.screen.fill(COLOR_BACKGROUND)

        # Subtle grid pattern
        for x in range(0, MENU_WIDTH, 40):
            pygame.draw.line(self.screen, (28, 35, 50), (x, 0), (x, MENU_HEIGHT))
        for y in range(0, MENU_HEIGHT, 40):
            pygame.draw.line(self.screen, (28, 35, 50), (0, y), (MENU_WIDTH, y))

        # Vignette corners
        for corner in [(0, 0), (MENU_WIDTH, 0), (0, MENU_HEIGHT), (MENU_WIDTH, MENU_HEIGHT)]:
            s = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 0, 0, 80), corner, 200)
            self.screen.blit(s, (corner[0] - 200, corner[1] - 200))

    def _draw_header(self):
        # Glowing title
        t  = FONT_TITLE_LARGE.render("QUORIDOR", True, COLOR_TEXT)
        tr = t.get_rect(center=(MENU_WIDTH // 2, 85))

        # Glow layer
        glow = FONT_TITLE_LARGE.render("QUORIDOR", True, (80, 200, 255))
        gs   = pygame.Surface(glow.get_size(), pygame.SRCALPHA)
        gs.blit(glow, (0, 0))
        gs.set_alpha(30)
        for off in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            self.screen.blit(gs, (tr.x + off[0], tr.y + off[1]))

        self.screen.blit(t, tr)

        # Decorative line under title
        lw = 120
        lx = MENU_WIDTH // 2 - lw // 2
        ly = tr.bottom + 10
        pygame.draw.line(self.screen, (80, 200, 255), (lx, ly), (lx + lw, ly), 2)

        sub = FONT_SMALL.render("SELECT GAME MODE", True, COLOR_TEXT_DIM)
        sr  = sub.get_rect(center=(MENU_WIDTH // 2, ly + 20))
        self.screen.blit(sub, sr)

        # Player pawn icons
        self._draw_pawn_icon(MENU_WIDTH // 2 - 55, 150, COLOR_PLAYER1)
        self._draw_pawn_icon(MENU_WIDTH // 2 + 55, 150, COLOR_PLAYER2)

    def _draw_pawn_icon(self, cx, cy, color):
        pygame.draw.circle(self.screen, color, (cx, cy), 14)
        s = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, 50), (8, 6), 6)
        self.screen.blit(s, (cx - 14, cy - 14))
        pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), 14, 2)

    def _draw_footer(self):
        hint = FONT_SMALL.render("Press H in-game to toggle valid moves", True, COLOR_TEXT_DIM)
        hr   = hint.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT - 24))
        self.screen.blit(hint, hr)

    # ------------------------------------------------------ event / run

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        return False

    def draw(self):
        self._draw_background()
        self._draw_header()
        for btn in self.buttons:
            btn.draw(self.screen)
        self._draw_footer()
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None, None
                self.handle_event(event)
                if self.selected_mode:
                    return self.selected_mode, self.selected_difficulty
            self.draw()
            clock.tick(60)
