"""Static/animated world objects: base Object, Block, and Fire."""

import random
import pygame
from os.path import join

from utils import get_block, load_sprite_sheets


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Goal(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width=64, height=64):
        super().__init__(x, y, width, height, "goal")
        raw = load_sprite_sheets("Items/Checkpoints", "End", 64, 64)
        self.sprites = {
            "idle": [pygame.transform.scale(img, (width, height)) for img in raw["End (Idle)"]],
            "pressed": [pygame.transform.scale(img, (width, height)) for img in raw["End (Pressed) (64x64)"]],
        }
        self.animation_name = "idle"
        self.animation_count = 0
        self.image = self.sprites[self.animation_name][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def reach(self):
        if self.animation_name != "pressed":
            self.animation_name = "pressed"
            self.animation_count = 0

    def loop(self):
        sprites = self.sprites[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)


class Spike(Object):
    def __init__(self, x, y, width=64, height=32):
        super().__init__(x, y, width, height, "spike")
        raw = load_sprite_sheets("Traps", "Spikes", 16, 16)
        spike_img = raw["Idle"][0]
        # Tile or scale spike across surface
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        single_spike = pygame.transform.scale(spike_img, (32, height))
        for offset in range(0, width, 32):
            self.image.blit(single_spike, (offset, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)


class Saw(Object):
    ANIMATION_DELAY = 2

    def __init__(self, x, y, width=64, height=64, move_range=0, axis="x", speed=2):
        super().__init__(x, y, width, height, "saw")
        raw = load_sprite_sheets("Traps", "Saw", 38, 38)
        self.sprites = [pygame.transform.scale(img, (width, height)) for img in raw["on"]]
        self.animation_count = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
        self.start_pos = x if axis == "x" else y
        self.move_range = move_range
        self.axis = axis
        self.speed = speed

    def loop(self):
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.sprites)
        self.image = self.sprites[sprite_index]
        self.animation_count += 1

        if self.move_range > 0:
            if self.axis == "x":
                self.rect.x += self.speed
                if self.rect.x > self.start_pos + self.move_range or self.rect.x < self.start_pos:
                    self.speed *= -1
            else:
                self.rect.y += self.speed
                if self.rect.y > self.start_pos + self.move_range or self.rect.y < self.start_pos:
                    self.speed *= -1

        self.mask = pygame.mask.from_surface(self.image)


class Trampoline(Object):
    ANIMATION_DELAY = 2

    def __init__(self, x, y, width=56, height=56):
        super().__init__(x, y, width, height, "trampoline")
        raw = load_sprite_sheets("Traps", "Trampoline", 28, 28)
        self.sprites = {
            "idle": [pygame.transform.scale(img, (width, height)) for img in raw["Idle"]],
            "jump": [pygame.transform.scale(img, (width, height)) for img in raw["Jump (28x28)"]],
        }
        self.animation_name = "idle"
        self.animation_count = 0
        self.image = self.sprites[self.animation_name][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def bounce(self, player):
        player.y_vel = -16
        player.jump_count = 1
        player.fall_count = 0
        self.animation_name = "jump"
        self.animation_count = 0

    def loop(self):
        sprites = self.sprites[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        if self.animation_name == "jump" and sprite_index == len(sprites) - 1:
            self.animation_name = "idle"
            self.animation_count = 0

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)


class MovingPlatform(Object):
    ANIMATION_DELAY = 4

    def __init__(self, x, y, width=128, height=32, move_range=150, axis="x", speed=2):
        super().__init__(x, y, width, height, "moving_platform")
        raw = load_sprite_sheets("Traps", "Platforms", 32, 8)
        platform_key = "Brown On (32x8)" if "Brown On (32x8)" in raw else list(raw.keys())[0]
        self.sprites = [pygame.transform.scale(img, (width, height)) for img in raw[platform_key]]
        self.animation_count = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        self.start_pos = x if axis == "x" else y
        self.move_range = move_range
        self.axis = axis
        self.speed = speed
        self.dx = 0
        self.dy = 0

    def loop(self):
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.sprites)
        self.image = self.sprites[sprite_index]
        self.animation_count += 1

        self.dx = 0
        self.dy = 0
        if self.move_range > 0:
            if self.axis == "x":
                self.dx = self.speed
                self.rect.x += self.dx
                if self.rect.x > self.start_pos + self.move_range or self.rect.x < self.start_pos:
                    self.speed *= -1
            else:
                self.dy = self.speed
                self.rect.y += self.dy
                if self.rect.y > self.start_pos + self.move_range or self.rect.y < self.start_pos:
                    self.speed *= -1

        self.mask = pygame.mask.from_surface(self.image)


class Fruit(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, fruit_type="Apple", width=40, height=40):
        super().__init__(x, y, width, height, "fruit")
        raw = load_sprite_sheets("Items", "Fruits", 32, 32)
        key = fruit_type if fruit_type in raw else "Apple"
        self.sprites = [pygame.transform.scale(img, (width, height)) for img in raw[key]]
        self.animation_count = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.collected = False

    def loop(self):
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.sprites)
        self.image = self.sprites[sprite_index]
        self.animation_count += 1
        self.mask = pygame.mask.from_surface(self.image)


class Arrow(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width=48, height=48, speed=4, move_range=400):
        super().__init__(x, y, width, height, "arrow")
        raw = load_sprite_sheets("Traps", "Arrow", 18, 18)
        self.sprites = {
            "idle": [pygame.transform.scale(img, (width, height)) for img in raw["Idle (18x18)"]],
            "hit": [pygame.transform.scale(img, (width, height)) for img in raw.get("Hit (18x18)", raw["Idle (18x18)"])],
        }
        self.animation_name = "idle"
        self.animation_count = 0
        self.image = self.sprites[self.animation_name][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
        self.start_x = x
        self.move_range = move_range
        self.speed = speed

    def loop(self):
        sprites = self.sprites[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect.x += self.speed
        if self.rect.x > self.start_x + self.move_range:
            self.rect.x = self.start_x

        self.mask = pygame.mask.from_surface(self.image)


class FallingPlatform(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width=96, height=32):
        super().__init__(x, y, width, height, "falling_platform")
        raw = load_sprite_sheets("Traps", "Falling Platforms", 32, 10)
        self.sprites = {
            "off": [pygame.transform.scale(img, (width, height)) for img in raw["Off"]],
            "on": [pygame.transform.scale(img, (width, height)) for img in raw["On (32x10)"]],
        }
        self.animation_name = "off"
        self.animation_count = 0
        self.image = self.sprites[self.animation_name][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
        self.start_y = y
        self.start_x = x
        self.state = "active"
        self.shake_count = 0
        self.fall_speed = 0
        self.inactive_count = 0

    @property
    def is_solid(self):
        return self.state in ("active", "triggered")

    def trigger(self):
        if self.state == "active":
            self.state = "triggered"
            self.animation_name = "on"
            self.animation_count = 0
            self.shake_count = 0

    def loop(self):
        if self.state == "active":
            self.animation_name = "off"
        elif self.state == "triggered":
            self.shake_count += 1
            self.rect.x = self.start_x + random.randint(-2, 2)
            if self.shake_count >= 30:
                self.state = "falling"
                self.rect.x = self.start_x
                self.fall_speed = 0
        elif self.state == "falling":
            self.fall_speed += 0.5
            self.rect.y += self.fall_speed
            if self.rect.y > self.start_y + 500:
                self.state = "inactive"
                self.inactive_count = 0
        elif self.state == "inactive":
            self.inactive_count += 1
            if self.inactive_count >= 180:
                self.state = "active"
                self.rect.x = self.start_x
                self.rect.y = self.start_y
                self.animation_name = "off"

        sprites = self.sprites[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.mask = pygame.mask.from_surface(self.image)


class Fan(Object):
    ANIMATION_DELAY = 1

    def __init__(self, x, y, width=48, height=24):
        super().__init__(x, y, width, height, "fan")
        raw = load_sprite_sheets("Traps", "Fan", 24, 8)
        self.sprites = [pygame.transform.scale(img, (width, height)) for img in raw["On (24x8)"]]
        self.animation_count = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
        self.wind_rect = pygame.Rect(x, y - 500, width, 500)

    def loop(self):
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.sprites)
        self.image = self.sprites[sprite_index]
        self.animation_count += 1
        
        self.mask = pygame.mask.from_surface(self.image)


class RockHead(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width=84, height=84, move_range=150, axis="y", speed=3):
        super().__init__(x, y, width, height, "rock_head")
        raw = load_sprite_sheets("Traps", "Rock Head", 42, 42)
        self.sprites = [pygame.transform.scale(img, (width, height)) for img in raw["Blink (42x42)"]]
        self.animation_count = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
        self.start_pos = x if axis == "x" else y
        self.move_range = move_range
        self.axis = axis
        self.speed = speed

    def loop(self):
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.sprites)
        self.image = self.sprites[sprite_index]
        self.animation_count += 1

        if self.move_range > 0:
            if self.axis == "x":
                self.rect.x += self.speed
                if self.rect.x > self.start_pos + self.move_range or self.rect.x < self.start_pos:
                    self.speed *= -1
            else:
                self.rect.y += self.speed
                if self.rect.y > self.start_pos + self.move_range or self.rect.y < self.start_pos:
                    self.speed *= -1

        self.mask = pygame.mask.from_surface(self.image)


class SpikeHead(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width=84, height=84, move_range=150, axis="y", speed=3):
        super().__init__(x, y, width, height, "spike_head")
        raw = load_sprite_sheets("Traps", "Spike Head", 54, 52)
        self.sprites = [pygame.transform.scale(img, (width, height)) for img in raw["Blink (54x52)"]]
        self.animation_count = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
        self.start_pos = x if axis == "x" else y
        self.move_range = move_range
        self.axis = axis
        self.speed = speed

    def loop(self):
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.sprites)
        self.image = self.sprites[sprite_index]
        self.animation_count += 1

        if self.move_range > 0:
            if self.axis == "x":
                self.rect.x += self.speed
                if self.rect.x > self.start_pos + self.move_range or self.rect.x < self.start_pos:
                    self.speed *= -1
            else:
                self.rect.y += self.speed
                if self.rect.y > self.start_pos + self.move_range or self.rect.y < self.start_pos:
                    self.speed *= -1

        self.mask = pygame.mask.from_surface(self.image)


class SpikedBall(Object):
    def __init__(self, x, y, width=48, height=48):
        super().__init__(x, y, width, height, "spiked_ball")
        image = pygame.image.load(join("assets", "Traps", "Spiked Ball", "Spiked Ball.png")).convert_alpha()
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)