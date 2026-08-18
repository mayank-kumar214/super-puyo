"""Screen rendering: normal frame, death/victory overlays, and HUD.

NOTE: No function in this module calls ``pygame.display.update()``
      — the main loop does that once after transitions are drawn.
"""

import pygame
import math
from settings import WIDTH, HEIGHT


# ── HUD ───────────────────────────────────────────────────────────

def draw_hud(window, current_level, total_levels,
             fruits_collected=0, total_fruits=0, score=0,
             health=3, max_health=3):
    """Draw level card, score card, and hearts."""

    # Level card
    level_rect = pygame.Rect(20, 20, 180, 48)
    _draw_card(window, level_rect, (70, 130, 240))
    _center_text(window, level_rect,
                 f"Level {current_level} / {total_levels}",
                 22, (255, 255, 255))

    # Score & fruit card
    score_rect = pygame.Rect(WIDTH - 260, 20, 240, 48)
    _draw_card(window, score_rect, (255, 200, 50))
    _center_text(window, score_rect,
                 f"Fruits: {fruits_collected}/{total_fruits}  Score: {score}",
                 18, (255, 230, 100))

    # Hearts
    heart_size = 28
    heart_gap = 6
    hx = 20
    hy = 78
    for i in range(max_health):
        rect = pygame.Rect(hx + i * (heart_size + heart_gap), hy,
                           heart_size, heart_size)
        if i < health:
            # Filled heart
            pygame.draw.polygon(window, (230, 40, 50), _heart_points(rect))
            pygame.draw.polygon(window, (255, 80, 90), _heart_points(rect), 2)
        else:
            # Empty heart
            pygame.draw.polygon(window, (80, 80, 80), _heart_points(rect))
            pygame.draw.polygon(window, (120, 120, 120), _heart_points(rect), 2)


def _draw_card(window, rect, border_color):
    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 160))
    window.blit(surf, rect)
    pygame.draw.rect(window, border_color, rect, 2, border_radius=8)


def _center_text(window, rect, text, size, color):
    font = pygame.font.SysFont("arial", size, bold=True)
    rendered = font.render(text, True, color)
    window.blit(rendered, rendered.get_rect(center=rect.center))


def _heart_points(rect):
    """Return polygon points for a heart shape inside *rect*."""
    cx, cy = rect.centerx, rect.centery
    w, h = rect.width * 0.5, rect.height * 0.5
    return [
        (cx, cy + h * 0.85),
        (cx - w, cy - h * 0.1),
        (cx - w * 0.7, cy - h * 0.75),
        (cx - w * 0.25, cy - h * 0.85),
        (cx, cy - h * 0.35),
        (cx + w * 0.25, cy - h * 0.85),
        (cx + w * 0.7, cy - h * 0.75),
        (cx + w, cy - h * 0.1),
    ]


# ── main game draw ───────────────────────────────────────────────

def draw(window, background, bg_image, player, objects, offset_x,
         current_level=1, total_levels=5,
         fruits_collected=0, total_fruits=0, score=0,
         health=3, max_health=3, particle_system=None):
    """Draw one normal gameplay frame (no display.update)."""

    ox = int(offset_x)

    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        if getattr(obj, "collect_anim_done", False):
            continue
        obj.draw(window, ox)

    player.draw(window, ox)

    if particle_system is not None:
        particle_system.draw(window, ox)

    draw_hud(window, current_level, total_levels,
             fruits_collected, total_fruits, score,
             health, max_health)


# ── death screen ──────────────────────────────────────────────────

def draw_death_screen(window, background, bg_image, objects, offset_x,
                      current_level=1, total_levels=5,
                      fruits_collected=0, total_fruits=0, score=0):
    """Draw world + 'YOU DIED' overlay.  Returns the restart-button rect."""

    ox = int(offset_x)

    for tile in background:
        window.blit(bg_image, tile)
    for obj in objects:
        if getattr(obj, "collect_anim_done", False):
            continue
        obj.draw(window, ox)

    draw_hud(window, current_level, total_levels,
             fruits_collected, total_fruits, score, 0, 3)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    window.blit(overlay, (0, 0))

    # "YOU DIED"
    font = pygame.font.SysFont("arial", 80, bold=True)
    text = font.render("YOU DIED", True, (230, 40, 40))
    window.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

    # "Press ENTER to restart" prompt (blinking)
    hint_font = pygame.font.SysFont("arial", 32, bold=True)
    alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() / 300))
    hint_surf = hint_font.render("Press ENTER to Restart", True, (255, 255, 255))
    hint_surf.set_alpha(alpha)
    window.blit(hint_surf,
                hint_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))


# ── level-clear screen ───────────────────────────────────────────

def draw_level_complete_screen(window, background, bg_image,
                               objects, offset_x,
                               cleared_level, total_levels,
                               fruits_collected=0, total_fruits=0,
                               score=0, particle_system=None):
    ox = int(offset_x)

    for tile in background:
        window.blit(bg_image, tile)
    for obj in objects:
        if getattr(obj, "collect_anim_done", False):
            continue
        obj.draw(window, ox)

    if particle_system is not None:
        particle_system.draw(window, ox)

    draw_hud(window, cleared_level, total_levels,
             fruits_collected, total_fruits, score)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 130))
    window.blit(overlay, (0, 0))

    font_t = pygame.font.SysFont("arial", 56, bold=True)
    title = font_t.render(f"LEVEL {cleared_level} CLEARED!", True,
                          (255, 215, 0))
    window.blit(title, title.get_rect(center=(WIDTH // 2,
                                              HEIGHT // 2 - 40)))

    font_s = pygame.font.SysFont("arial", 28)
    sub = font_s.render("Loading Next Level...", True, (255, 255, 255))
    window.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))


# ── victory screen ───────────────────────────────────────────────

def draw_victory_screen(window, background, bg_image,
                        objects, offset_x,
                        total_levels,
                        fruits_collected=0, total_fruits=0,
                        score=0, particle_system=None):
    ox = int(offset_x)

    for tile in background:
        window.blit(bg_image, tile)
    for obj in objects:
        if getattr(obj, "collect_anim_done", False):
            continue
        obj.draw(window, ox)

    if particle_system is not None:
        particle_system.draw(window, ox)

    draw_hud(window, total_levels, total_levels,
             fruits_collected, total_fruits, score)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    window.blit(overlay, (0, 0))

    font_t = pygame.font.SysFont("arial", 64, bold=True)
    title = font_t.render("VICTORY!", True, (255, 215, 0))
    window.blit(title, title.get_rect(center=(WIDTH // 2,
                                              HEIGHT // 2 - 100)))

    font_m = pygame.font.SysFont("arial", 30, bold=True)
    msg = font_m.render("Congratulations! All Levels Completed!",
                        True, (255, 255, 255))
    window.blit(msg, msg.get_rect(center=(WIDTH // 2,
                                          HEIGHT // 2 - 35)))

    font_s = pygame.font.SysFont("arial", 24)
    stats = font_s.render(
        f"Fruits Collected: {fruits_collected}/{total_fruits}"
        f"  |  Final Score: {score}", True, (255, 230, 100))
    window.blit(stats, stats.get_rect(center=(WIDTH // 2,
                                              HEIGHT // 2 + 10)))

    return _overlay_button(window, "Play Again",
                           WIDTH // 2, HEIGHT // 2 + 75,
                           220, 60, (25, 140, 50), (40, 180, 70))


# ── internal helpers ──────────────────────────────────────────────

def _overlay_button(window, label, cx, cy, w, h,
                    color_normal, color_hover):
    """Draw a centred button and return its rect."""
    font = pygame.font.SysFont("arial", 32, bold=True)
    text = font.render(label, True, (255, 255, 255))
    rect = pygame.Rect(cx - w // 2, cy, w, h)

    mp = pygame.mouse.get_pos()
    col = color_hover if rect.collidepoint(mp) else color_normal
    pygame.draw.rect(window, col, rect, border_radius=12)
    pygame.draw.rect(window, (255, 255, 255), rect, 2, border_radius=12)
    window.blit(text, text.get_rect(center=rect.center))
    return rect