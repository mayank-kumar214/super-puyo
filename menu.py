"""Main-menu, pause-menu and screen-transition overlays."""

import math
import os
import pygame
from settings import WIDTH, HEIGHT
from utils import get_background


# ── reusable button ───────────────────────────────────────────────

class Button:
    """A rounded-rectangle button with hover-scale animation."""

    def __init__(self, x, y, width, height, text, font_size=28,
                 color=(60, 60, 80), hover_color=(80, 80, 120),
                 text_color=(255, 255, 255),
                 border_color=(120, 120, 180)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont("arial", font_size, bold=True)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.hovered = False
        self.scale = 1.0

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        target = 1.08 if self.hovered else 1.0
        self.scale += (target - self.scale) * 0.2

    def draw(self, surface):
        w = int(self.rect.width * self.scale)
        h = int(self.rect.height * self.scale)
        x = self.rect.centerx - w // 2
        y = self.rect.centery - h // 2
        scaled = pygame.Rect(x, y, w, h)

        btn_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        col = self.hover_color if self.hovered else self.color
        btn_surf.fill((*col, 200))
        surface.blit(btn_surf, scaled)
        pygame.draw.rect(surface, self.border_color, scaled, 2,
                         border_radius=10)

        txt = self.font.render(self.text, True, self.text_color)
        surface.blit(txt, txt.get_rect(center=scaled.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ── main menu ─────────────────────────────────────────────────────

class MainMenu:
    def __init__(self):
        self.background, self.bg_image = get_background("Blue.png")
        self.title_font = pygame.font.SysFont("arial", 72, bold=True)
        self.sub_font = pygame.font.SysFont("arial", 24)
        
        self.refresh_save_status()
        self._bob = 0.0

    def refresh_save_status(self):
        self.has_save = os.path.exists("save.json")
        bw, bh = 260, 60
        cx = WIDTH // 2
        if self.has_save:
            self.continue_btn = Button(
                cx - bw // 2, HEIGHT // 2, bw, bh, "CONTINUE", 32,
                color=(140, 100, 20), hover_color=(180, 130, 30),
                border_color=(255, 200, 50))
            self.play_btn = Button(
                cx - bw // 2, HEIGHT // 2 + 80, bw, bh, "NEW GAME", 32,
                color=(30, 120, 60), hover_color=(40, 160, 80),
                border_color=(100, 255, 150))
            self.quit_btn = Button(
                cx - bw // 2, HEIGHT // 2 + 160, bw, bh, "QUIT", 32,
                color=(120, 30, 30), hover_color=(160, 40, 40),
                border_color=(255, 100, 100))
        else:
            self.continue_btn = None
            self.play_btn = Button(
                cx - bw // 2, HEIGHT // 2 + 20, bw, bh, "PLAY", 32,
                color=(30, 120, 60), hover_color=(40, 160, 80),
                border_color=(100, 255, 150))
            self.quit_btn = Button(
                cx - bw // 2, HEIGHT // 2 + 100, bw, bh, "QUIT", 32,
                color=(120, 30, 30), hover_color=(160, 40, 40),
                border_color=(255, 100, 100))

    def update(self):
        mp = pygame.mouse.get_pos()
        if self.has_save:
            self.continue_btn.update(mp)
        self.play_btn.update(mp)
        self.quit_btn.update(mp)
        self._bob += 0.05

    def draw(self, window):
        for tile in self.background:
            window.blit(self.bg_image, tile)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        window.blit(overlay, (0, 0))

        bob = math.sin(self._bob) * 8

        # shadow
        shadow = self.title_font.render("SUPER PUYO", True, (0, 0, 0))
        window.blit(shadow, shadow.get_rect(
            center=(WIDTH // 2 + 3, HEIGHT // 3 + 3 + bob)))
        # title
        title = self.title_font.render("SUPER PUYO", True, (255, 215, 0))
        window.blit(title, title.get_rect(
            center=(WIDTH // 2, HEIGHT // 3 + bob)))
        # subtitle
        sub = self.sub_font.render("A Pixel Platformer Adventure", True,
                                   (200, 200, 220))
        window.blit(sub, sub.get_rect(
            center=(WIDTH // 2, HEIGHT // 3 + 50 + bob)))

        if self.has_save:
            self.continue_btn.draw(window)
        self.play_btn.draw(window)
        self.quit_btn.draw(window)

    def handle_click(self, pos):
        if self.has_save and self.continue_btn.is_clicked(pos):
            return "continue"
        if self.play_btn.is_clicked(pos):
            return "play"
        if self.quit_btn.is_clicked(pos):
            return "quit"
        return None


# ── pause menu ────────────────────────────────────────────────────

class PauseMenu:
    def __init__(self):
        bw, bh = 260, 55
        cx = WIDTH // 2
        by = HEIGHT // 2 - 40

        self.resume_btn = Button(
            cx - bw // 2, by, bw, bh, "RESUME", 28,
            color=(30, 120, 60), hover_color=(40, 160, 80),
            border_color=(100, 255, 150))
        self.restart_btn = Button(
            cx - bw // 2, by + 70, bw, bh, "RESTART LEVEL", 28,
            color=(140, 100, 20), hover_color=(180, 130, 30),
            border_color=(255, 200, 50))
        self.menu_btn = Button(
            cx - bw // 2, by + 140, bw, bh, "SAVE & QUIT", 28,
            color=(120, 30, 30), hover_color=(160, 40, 40),
            border_color=(255, 100, 100))

        self.title_font = pygame.font.SysFont("arial", 48, bold=True)

    def update(self):
        mp = pygame.mouse.get_pos()
        self.resume_btn.update(mp)
        self.restart_btn.update(mp)
        self.menu_btn.update(mp)

    def draw(self, window):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        window.blit(overlay, (0, 0))

        title = self.title_font.render("PAUSED", True, (255, 255, 255))
        window.blit(title, title.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 120)))

        self.resume_btn.draw(window)
        self.restart_btn.draw(window)
        self.menu_btn.draw(window)

    def handle_click(self, pos):
        if self.resume_btn.is_clicked(pos):
            return "resume"
        if self.restart_btn.is_clicked(pos):
            return "restart"
        if self.menu_btn.is_clicked(pos):
            return "save_quit"
        return None


# ── fade transition ───────────────────────────────────────────────

class Transition:
    """Fade-to-black → callback → fade-from-black."""

    def __init__(self, speed=10):
        self.alpha = 0
        self.speed = speed
        self.active = False
        self._callback = None
        self._phase = "idle"   # idle | fade_out | fade_in

    def start(self, callback=None):
        self._phase = "fade_out"
        self.alpha = 0
        self.active = True
        self._callback = callback

    def update(self):
        if self._phase == "fade_out":
            self.alpha = min(255, self.alpha + self.speed)
            if self.alpha >= 255:
                if self._callback:
                    try:
                        self._callback()
                    except Exception:
                        import traceback
                        print("=" * 60, flush=True)
                        print("[Transition] callback raised an exception:", flush=True)
                        traceback.print_exc()
                        print("=" * 60, flush=True)
                    self._callback = None
                self._phase = "fade_in"
        elif self._phase == "fade_in":
            self.alpha = max(0, self.alpha - self.speed)
            if self.alpha <= 0:
                self._phase = "idle"
                self.active = False

    def draw(self, surface):
        if self.alpha > 0:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, int(self.alpha)))
            surface.blit(ov, (0, 0))