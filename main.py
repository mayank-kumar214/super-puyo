"""Entry point: sets up the window and runs the game loop.

Game states
───────────
MENU → PLAYING ⇄ PAUSED
     → DEAD    → PLAYING (restart level)
     → LEVEL_CLEAR → PLAYING (next) or VICTORY
     → VICTORY → MENU
"""

import random
import pygame
import os
import json
import asyncio
from settings import WIDTH, HEIGHT, FPS

SAVE_FILE = "save.json"

def save_game_state(current_level_idx, score, total_fruits_collected, cumulative_total_fruits, health, player_x=None, player_y=None):
    data = {
        "current_level_idx": current_level_idx,
        "score": score,
        "total_fruits_collected": total_fruits_collected,
        "cumulative_total_fruits": cumulative_total_fruits,
        "health": health
    }
    if player_x is not None and player_y is not None:
        data["player_x"] = player_x
        data["player_y"] = player_y
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_game_state():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return None

def delete_save_game():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

# ── game states ───────────────────────────────────────────────────
MENU        = "menu"
PLAYING     = "playing"
PAUSED      = "paused"
DEAD        = "dead"
LEVEL_CLEAR = "level_clear"
VICTORY     = "victory"


def init_level(level_idx):
    from levels import load_level
    from utils import get_background
    from player import Player

    bg_name, player_start, objects, fires, goal = load_level(level_idx)
    background, bg_image = get_background(bg_name)
    player = Player(player_start[0], player_start[1], 50, 50)
    total_fruits = sum(1 for o in objects
                       if getattr(o, "name", None) == "fruit")
    return (bg_name, background, bg_image, player,
            objects, fires, goal, player_start, total_fruits)


# ──────────────────────────────────────────────────────────────────

async def main(window):                              # noqa: C901 — game loop
    from sound import sound_manager
    from utils import get_background
    from player import Player
    from collisions import handle_move
    from render import (draw, draw_death_screen,
                        draw_level_complete_screen,
                        draw_victory_screen)
    from levels import load_level, level_count
    from menu import MainMenu, PauseMenu, Transition
    from particles import ParticleSystem

    sound_manager.init()

    clock = pygame.time.Clock()

    # UI helpers
    main_menu      = MainMenu()
    pause_menu     = PauseMenu()
    transition     = Transition(speed=10)
    particle_system = ParticleSystem()

    # Level bookkeeping
    current_level_idx    = 0
    total_levels         = level_count()
    bg_name = background = bg_image = None
    player = objects = fires = goal = player_start = None
    total_fruits_in_level = 0

    # Camera
    offset_x = 0.0

    # Score / progress
    score                  = 0
    total_fruits_collected = 0
    cumulative_total_fruits = 0
    level_score_start      = 0
    level_fruits_start     = 0

    # Timing / flags
    death_time      = 0
    falling         = False
    level_clear_time = 0
    level_cleared   = False
    confetti_done   = False
    restart_button  = None

    state = MENU

    # ── helper closures (modify enclosing scope via nonlocal) ────

    def _start_game(load_save=False):
        nonlocal state, current_level_idx, score
        nonlocal total_fruits_collected, cumulative_total_fruits
        nonlocal bg_name, background, bg_image, player
        nonlocal objects, fires, goal, player_start
        nonlocal total_fruits_in_level, offset_x
        nonlocal falling, level_cleared, confetti_done
        nonlocal level_score_start, level_fruits_start

        data = None
        if load_save:
            data = load_game_state()
            if data:
                current_level_idx       = data.get("current_level_idx", 0)
                score                   = data.get("score", 0)
                total_fruits_collected  = data.get("total_fruits_collected", 0)
                cumulative_total_fruits = data.get("cumulative_total_fruits", 0)
            else:
                load_save = False
        
        if not load_save:
            current_level_idx       = 0
            score                   = 0
            total_fruits_collected  = 0

        (bg_name, background, bg_image, player,
         objects, fires, goal, player_start,
         total_fruits_in_level) = init_level(current_level_idx)

        if load_save and data:
            player.health = data.get("health", 3)
            level_score_start = score
            level_fruits_start = total_fruits_collected
            if "player_x" in data and "player_y" in data:
                player.rect.x = data["player_x"]
                player.rect.y = data["player_y"]
        else:
            cumulative_total_fruits = total_fruits_in_level
            level_score_start       = 0
            level_fruits_start      = 0
        offset_x                = 0.0
        falling                 = False
        level_cleared           = False
        confetti_done           = False
        particle_system.clear()
        state = PLAYING
        sound_manager.play_music()

    def _restart_level():
        nonlocal state, bg_name, background, bg_image, player
        nonlocal objects, fires, goal, player_start
        nonlocal total_fruits_in_level, offset_x
        nonlocal falling, level_cleared, confetti_done
        nonlocal score, total_fruits_collected, death_time

        score                  = level_score_start
        total_fruits_collected = level_fruits_start

        (bg_name, background, bg_image, player,
         objects, fires, goal, player_start,
         total_fruits_in_level) = init_level(current_level_idx)

        offset_x      = 0.0
        falling       = False
        level_cleared = False
        death_time    = 0
        confetti_done = False
        particle_system.clear()
        state = PLAYING

    def _next_level():
        nonlocal state, current_level_idx
        nonlocal bg_name, background, bg_image, player
        nonlocal objects, fires, goal, player_start
        nonlocal total_fruits_in_level, cumulative_total_fruits
        nonlocal offset_x, level_score_start, level_fruits_start
        nonlocal level_cleared, confetti_done

        current_level_idx += 1
        if current_level_idx < total_levels:
            (bg_name, background, bg_image, player,
             objects, fires, goal, player_start,
             total_fruits_in_level) = init_level(current_level_idx)
            cumulative_total_fruits += total_fruits_in_level
            level_score_start  = score
            level_fruits_start = total_fruits_collected
            offset_x           = 0.0
            level_cleared      = False
            confetti_done      = False
            particle_system.clear()
            state = PLAYING
        else:
            confetti_done = False
            state = VICTORY
            sound_manager.play_sfx("victory")
            delete_save_game()

    def _go_to_menu():
        nonlocal state
        sound_manager.stop_music()
        main_menu.refresh_save_status()
        state = MENU

    def _save_and_quit():
        save_game_state(current_level_idx, score, total_fruits_collected, cumulative_total_fruits, player.health, player.rect.x, player.rect.y)
        transition.start(_go_to_menu)

    # ── main loop ─────────────────────────────────────────────────

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            # ── MENU ──
            if state == MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    result = main_menu.handle_click(event.pos)
                    if result == "play":
                        transition.start(_start_game)
                    elif result == "continue":
                        transition.start(lambda: _start_game(load_save=True))
                    elif result == "quit":
                        run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False

            # ── PLAYING ──
            elif state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        player.request_jump()
                    elif event.key == pygame.K_ESCAPE:
                        state = PAUSED
                        sound_manager.play_sfx("pause")

            # ── PAUSED ──
            elif state == PAUSED:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = PLAYING
                        sound_manager.play_sfx("unpause")
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    result = pause_menu.handle_click(event.pos)
                    if result == "resume":
                        state = PLAYING
                        sound_manager.play_sfx("unpause")
                    elif result == "restart":
                        transition.start(_restart_level)
                    elif result == "save_quit":
                        _save_and_quit()

            # ── DEAD ──
            elif state == DEAD:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_button and restart_button.collidepoint(event.pos):
                        transition.start(_restart_level)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        transition.start(_go_to_menu)

            # ── VICTORY ──
            elif state == VICTORY:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_button and restart_button.collidepoint(event.pos):
                        transition.start(_go_to_menu)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        transition.start(_go_to_menu)

        if not run:
            break

        # ── per-frame updates & rendering ─────────────────────────
        transition.update()
        particle_system.update()

        # ·· MENU ··
        if state == MENU:
            main_menu.update()
            main_menu.draw(window)

        # ·· PLAYING ··
        elif state == PLAYING:
            player.loop(FPS)
            for obj in objects:
                if hasattr(obj, "loop") and callable(obj.loop):
                    obj.loop()

            handle_move(player, objects)

            # Dust particles
            if player.just_landed:
                particle_system.emit_dust(player.rect.centerx,
                                          player.rect.bottom)
            if (player.x_vel != 0 and player.jump_count == 0
                    and not player.wall_sliding
                    and random.random() < 0.25):
                particle_system.emit_run_dust(player.rect.centerx,
                                              player.rect.bottom)

            # Fruit collection
            for obj in objects:
                if (getattr(obj, "name", None) == "fruit"
                        and not getattr(obj, "collected", False)):
                    if pygame.sprite.collide_rect(player, obj):
                        obj.collect()
                        total_fruits_collected += 1
                        score += 100
                        sound_manager.play_sfx("fruit_collect")
                        particle_system.emit_sparkle(obj.rect.centerx,
                                                     obj.rect.centery)

            # Goal collision
            if goal and not level_cleared:
                if (pygame.sprite.collide_mask(player, goal)
                        or pygame.sprite.collide_rect(player, goal)):
                    goal.reach()
                    level_cleared   = True
                    level_clear_time = pygame.time.get_ticks()
                    confetti_done   = False
                    sound_manager.play_sfx("level_clear")
                    state = LEVEL_CLEAR

            # Death checks
            if player.dead and not falling:
                falling    = True
                death_time = pygame.time.get_ticks()
                sound_manager.play_sfx("death")
                delete_save_game()
                particle_system.emit_death(player.rect.centerx,
                                           player.rect.centery)
                particle_system.start_screen_shake(6, 20)

            if player.rect.top > HEIGHT and not falling:
                if player.health > 1 or player.invincible:
                    player.make_hit()
                    player.rect.x, player.rect.y = player.last_safe_pos
                    player.y_vel = 0
                    player.x_vel = 0
                    player.fall_count = 0
                    particle_system.emit_dust(player.rect.centerx, player.rect.bottom)
                else:
                    player.health = 0
                    player.dead = True
                    falling     = True
                    death_time  = pygame.time.get_ticks()
                    sound_manager.play_sfx("death")

            if falling and state == PLAYING:
                if pygame.time.get_ticks() - death_time >= 1200:
                    state = DEAD

            # Smooth camera (lerp)
            target_x = max(0.0, player.rect.centerx - WIDTH / 2)
            offset_x += (target_x - offset_x) * 0.08

            shake_x, shake_y = particle_system.get_shake_offset()

            draw(window, background, bg_image, player, objects,
                 offset_x + shake_x,
                 current_level_idx + 1, total_levels,
                 total_fruits_collected, cumulative_total_fruits, score,
                 player.health, player.MAX_HEALTH, particle_system)

        # ·· PAUSED ··
        elif state == PAUSED:
            # Render frozen game underneath
            draw(window, background, bg_image, player, objects,
                 offset_x,
                 current_level_idx + 1, total_levels,
                 total_fruits_collected, cumulative_total_fruits, score,
                 player.health, player.MAX_HEALTH, particle_system)
            pause_menu.update()
            pause_menu.draw(window)

        # ·· LEVEL_CLEAR ··
        elif state == LEVEL_CLEAR:
            for obj in objects:
                if hasattr(obj, "loop") and callable(obj.loop):
                    obj.loop()

            if not confetti_done:
                for _ in range(3):
                    particle_system.emit_confetti(
                        random.randint(WIDTH // 4, 3 * WIDTH // 4),
                        random.randint(HEIGHT // 4, HEIGHT // 2))
                confetti_done = True

            draw_level_complete_screen(
                window, background, bg_image, objects, offset_x,
                current_level_idx + 1, total_levels,
                total_fruits_collected, cumulative_total_fruits, score,
                particle_system)

            if (pygame.time.get_ticks() - level_clear_time >= 1500
                    and not transition.active):
                transition.start(_next_level)

        # ·· DEAD ··
        elif state == DEAD:
            restart_button = draw_death_screen(
                window, background, bg_image, objects, offset_x,
                current_level_idx + 1, total_levels,
                total_fruits_collected, cumulative_total_fruits, score)

        # ·· VICTORY ··
        elif state == VICTORY:
            if not confetti_done:
                for _ in range(5):
                    particle_system.emit_confetti(
                        random.randint(WIDTH // 4, 3 * WIDTH // 4),
                        random.randint(HEIGHT // 4, HEIGHT // 2))
                confetti_done = True

            restart_button = draw_victory_screen(
                window, background, bg_image, objects, offset_x,
                total_levels,
                total_fruits_collected, cumulative_total_fruits, score,
                particle_system)

        # Draw transition overlay last, then flip
        transition.draw(window)
        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()


# ── pygame init (top-level so pygbag can set up display) ──────
pygame.mixer.pre_init(22050, -16, 2, 4096)
pygame.init()
pygame.display.set_caption("Super Puyo")
window = pygame.display.set_mode((WIDTH, HEIGHT))

asyncio.run(main(window))
