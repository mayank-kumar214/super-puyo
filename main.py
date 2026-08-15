"""Entry point: sets up the window and runs the game loop."""

import pygame
from settings import WIDTH, HEIGHT, FPS
pygame.init()
pygame.display.set_caption("Platformer")
window = pygame.display.set_mode((WIDTH, HEIGHT))

from utils import get_background
from player import Player
from collisions import handle_move
from render import draw, draw_death_screen, draw_level_complete_screen, draw_victory_screen
from levels import load_level, level_count


def init_level(level_idx):
    bg_name, player_start, objects, fires, goal = load_level(level_idx)
    background, bg_image = get_background(bg_name)
    player = Player(player_start[0], player_start[1], 50, 50)
    total_fruits_in_level = sum(1 for obj in objects if getattr(obj, "name", None) == "fruit")
    return bg_name, background, bg_image, player, objects, fires, goal, player_start, total_fruits_in_level


def main(window):
    clock = pygame.time.Clock()

    current_level_idx = 0
    total_levels = level_count()

    bg_name, background, bg_image, player, objects, fires, goal, player_start, total_fruits_in_level = init_level(current_level_idx)

    offset_x = 0
    scroll_area_width = 200
    dead = False
    death_time = 0
    falling = False
    level_cleared = False
    level_clear_time = 0
    game_won = False
    restart_button = None

    score = 0
    total_fruits_collected = 0
    cumulative_total_fruits = total_fruits_in_level
    level_score_start = 0
    level_fruits_start = 0

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if dead or game_won:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_button and restart_button.collidepoint(event.pos):
                        if game_won:
                            current_level_idx = 0
                            game_won = False
                            score = 0
                            total_fruits_collected = 0
                        else:
                            # Revert score/fruits back to level start values
                            score = level_score_start
                            total_fruits_collected = level_fruits_start

                        # Reset level
                        bg_name, background, bg_image, player, objects, fires, goal, player_start, total_fruits_in_level = init_level(current_level_idx)
                        offset_x = 0
                        dead = False
                        falling = False
                        death_time = 0
                        level_cleared = False
            elif not falling and not level_cleared:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and player.jump_count < 2:
                        player.jump()
                    if event.key == pygame.K_ESCAPE:
                        run = False
        if dead:
            restart_button = draw_death_screen(
                window, background, bg_image, objects, offset_x,
                current_level_idx + 1, total_levels,
                total_fruits_collected, cumulative_total_fruits, score
            )
            continue

        if game_won:
            restart_button = draw_victory_screen(
                window, background, bg_image, objects, offset_x,
                total_levels, total_fruits_collected, cumulative_total_fruits, score
            )
            continue

        if level_cleared:
            for obj in objects:
                if hasattr(obj, "loop") and callable(obj.loop):
                    obj.loop()

            draw_level_complete_screen(
                window, background, bg_image, objects, offset_x,
                current_level_idx + 1, total_levels,
                total_fruits_collected, cumulative_total_fruits, score
            )

            if pygame.time.get_ticks() - level_clear_time >= 1500:
                current_level_idx += 1
                if current_level_idx < total_levels:
                    bg_name, background, bg_image, player, objects, fires, goal, player_start, total_fruits_in_level = init_level(current_level_idx)
                    cumulative_total_fruits += total_fruits_in_level
                    level_score_start = score
                    level_fruits_start = total_fruits_collected
                    offset_x = 0
                    level_cleared = False
                else:
                    game_won = True
                    level_cleared = False
            continue

        player.loop(FPS)
        for obj in objects:
            if hasattr(obj, "loop") and callable(obj.loop):
                obj.loop()

        handle_move(player, objects)

        # Check Fruit Collection
        for obj in objects:
            if getattr(obj, "name", None) == "fruit" and not getattr(obj, "collected", False):
                if pygame.sprite.collide_rect(player, obj):
                    obj.collected = True
                    total_fruits_collected += 1
                    score += 100

        # Check goal collision
        if goal and (pygame.sprite.collide_mask(player, goal) or pygame.sprite.collide_rect(player, goal)) and not level_cleared:
            goal.reach()
            level_cleared = True
            level_clear_time = pygame.time.get_ticks()

        # Check if player hit fire/hazard or fell off bottom of screen
        if player.hit and not falling:
            falling = True
            death_time = pygame.time.get_ticks()

        if player.rect.top > HEIGHT and not falling:
            falling = True
            death_time = pygame.time.get_ticks()

        # Show death screen after delay
        if falling and not dead:
            if pygame.time.get_ticks() - death_time >= 1200:
                dead = True

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        draw(
            window, background, bg_image, player, objects, offset_x,
            current_level_idx + 1, total_levels,
            total_fruits_collected, cumulative_total_fruits, score
        )

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)