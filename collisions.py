"""Collision handling logic for player movement and world interaction."""

import pygame
from settings import PLAYER_VEL


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if obj.name == "trampoline":
                if dy > 0:
                    player.rect.bottom = obj.rect.top
                    obj.bounce(player)
                    collided_objects.append(obj)
            else:
                if dy > 0:
                    player.rect.bottom = obj.rect.top
                    player.landed()
                elif dy < 0:
                    player.rect.top = obj.rect.bottom
                    player.hit_head()

                collided_objects.append(obj)

    return collided_objects


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    solid_objects = [obj for obj in objects if obj.name in (None, "block", "moving_platform") or (obj.name == "falling_platform" and getattr(obj, 'is_solid', False))]
    trampolines = [obj for obj in objects if obj.name == "trampoline"]

    player.x_vel = 0
    collide_left = collide(player, solid_objects, -PLAYER_VEL * 2)
    collide_right = collide(player, solid_objects, PLAYER_VEL * 2)

    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not collide_left:
        player.move_left(PLAYER_VEL)
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, solid_objects + trampolines, player.y_vel)

    for obj in vertical_collide:
        if obj.name == "moving_platform":
            player.move(obj.dx, obj.dy)
        elif obj.name == "falling_platform":
            obj.trigger()

    for obj in objects:
        if obj.name in ("fire", "spike", "saw", "arrow", "rock_head", "spike_head", "spiked_ball"):
            if pygame.sprite.collide_mask(player, obj):
                player.make_hit()

    for obj in objects:
        if obj.name == "fan":
            if hasattr(obj, 'wind_rect') and obj.wind_rect.colliderect(player.rect):
                player.y_vel -= 0.8
                if player.y_vel < -6:
                    player.y_vel = -6