"""Screen rendering: normal frame draw and the death screen overlay."""

import pygame
from settings import WIDTH, HEIGHT

def draw_hud(window, current_level, total_levels, fruits_collected=0, total_fruits=0, score=0):
    """Draw level indicator HUD and fruit score card."""
    # Level card
    level_rect = pygame.Rect(20, 20, 180, 48)
    level_surface = pygame.Surface((level_rect.width, level_rect.height), pygame.SRCALPHA)
    level_surface.fill((0, 0, 0, 160))
    window.blit(level_surface, level_rect)
    pygame.draw.rect(window, (70, 130, 240), level_rect, 2, border_radius=8)

    font = pygame.font.SysFont("arial", 22, bold=True)
    text = font.render(f"Level {current_level} / {total_levels}", True, (255, 255, 255))
    text_rect = text.get_rect(center=level_rect.center)
    window.blit(text, text_rect)

    # Score & Fruit card
    score_rect = pygame.Rect(WIDTH - 240, 20, 220, 48)
    score_surface = pygame.Surface((score_rect.width, score_rect.height), pygame.SRCALPHA)
    score_surface.fill((0, 0, 0, 160))
    window.blit(score_surface, score_rect)
    pygame.draw.rect(window, (255, 200, 50), score_rect, 2, border_radius=8)

    score_font = pygame.font.SysFont("arial", 20, bold=True)
    score_text = score_font.render(f"Fruits: {fruits_collected}/{total_fruits}  Score: {score}", True, (255, 230, 100))
    score_text_rect = score_text.get_rect(center=score_rect.center)
    window.blit(score_text, score_text_rect)

def draw(window, background, bg_image, player, objects, offset_x, current_level=1, total_levels=5, fruits_collected=0, total_fruits=0, score=0):
    for tile in background:
        window.blit(bg_image, tile) 

    for obj in objects:
        if getattr(obj, "collected", False):
            continue
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
    draw_hud(window, current_level, total_levels, fruits_collected, total_fruits, score)

    pygame.display.update()

def draw_death_screen(window, background, bg_image, objects, offset_x, current_level=1, total_levels=5, fruits_collected=0, total_fruits=0, score=0):
    """Draw the game world with a 'YOU DIED' overlay. Returns the restart button rect."""
    for tile in background:
        window.blit(bg_image, tile)
    for obj in objects:
        if getattr(obj, "collected", False):
            continue
        obj.draw(window, offset_x)

    draw_hud(window, current_level, total_levels, fruits_collected, total_fruits, score)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    window.blit(overlay, (0, 0))

    # "YOU DIED" text
    death_font = pygame.font.SysFont("arial", 80, bold=True)
    death_text = death_font.render("YOU DIED", True, (230, 40, 40))
    death_text_rect = death_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    window.blit(death_text, death_text_rect)

    # Restart button
    button_font = pygame.font.SysFont("arial", 34, bold=True)
    button_text = button_font.render("Restart Level", True, (255, 255, 255))
    button_width, button_height = 240, 60
    button_rect = pygame.Rect(
        WIDTH // 2 - button_width // 2,
        HEIGHT // 2 + 40,
        button_width,
        button_height
    )

    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(window, (190, 40, 40), button_rect, border_radius=10)
    else:
        pygame.draw.rect(window, (140, 20, 20), button_rect, border_radius=10)

    pygame.draw.rect(window, (255, 255, 255), button_rect, 2, border_radius=10)
    button_text_rect = button_text.get_rect(center=button_rect.center)
    window.blit(button_text, button_text_rect)

    pygame.display.update()
    return button_rect

def draw_level_complete_screen(window, background, bg_image, objects, offset_x, cleared_level, total_levels, fruits_collected=0, total_fruits=0, score=0):
    """Draw level complete overlay when player reaches the end goal flag."""
    for tile in background:
        window.blit(bg_image, tile)
    for obj in objects:
        if getattr(obj, "collected", False):
            continue
        obj.draw(window, offset_x)

    draw_hud(window, cleared_level, total_levels, fruits_collected, total_fruits, score)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 130))
    window.blit(overlay, (0, 0))

    font_title = pygame.font.SysFont("arial", 56, bold=True)
    title_text = font_title.render(f"LEVEL {cleared_level} CLEARED!", True, (255, 215, 0))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    window.blit(title_text, title_rect)

    font_sub = pygame.font.SysFont("arial", 28)
    sub_text = font_sub.render("Loading Next Level...", True, (255, 255, 255))
    sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
    window.blit(sub_text, sub_rect)

    pygame.display.update()

def draw_victory_screen(window, background, bg_image, objects, offset_x, total_levels, fruits_collected=0, total_fruits=0, score=0):
    """Draw game victory overlay when all levels are completed."""
    for tile in background:
        window.blit(bg_image, tile)
    for obj in objects:
        if getattr(obj, "collected", False):
            continue
        obj.draw(window, offset_x)

    draw_hud(window, total_levels, total_levels, fruits_collected, total_fruits, score)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    window.blit(overlay, (0, 0))

    font_title = pygame.font.SysFont("arial", 64, bold=True)
    title_text = font_title.render("VICTORY!", True, (255, 215, 0))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    window.blit(title_text, title_rect)

    font_msg = pygame.font.SysFont("arial", 30, bold=True)
    msg_text = font_msg.render("Congratulations! All Levels Completed!", True, (255, 255, 255))
    msg_rect = msg_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 35))
    window.blit(msg_text, msg_rect)

    font_stats = pygame.font.SysFont("arial", 24)
    stats_text = font_stats.render(f"Fruits Collected: {fruits_collected}/{total_fruits}  |  Final Score: {score}", True, (255, 230, 100))
    stats_rect = stats_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
    window.blit(stats_text, stats_rect)

    # Play Again button
    button_font = pygame.font.SysFont("arial", 32, bold=True)
    button_text = button_font.render("Play Again", True, (255, 255, 255))
    button_width, button_height = 220, 60
    button_rect = pygame.Rect(
        WIDTH // 2 - button_width // 2,
        HEIGHT // 2 + 75,
        button_width,
        button_height
    )

    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(window, (40, 180, 70), button_rect, border_radius=12)
    else:
        pygame.draw.rect(window, (25, 140, 50), button_rect, border_radius=12)

    pygame.draw.rect(window, (255, 255, 255), button_rect, 2, border_radius=12)
    button_text_rect = button_text.get_rect(center=button_rect.center)
    window.blit(button_text, button_text_rect)

    pygame.display.update()
    return button_rect