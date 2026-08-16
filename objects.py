"""Static/animated world objects: base Object, Block, Fire, and all traps.

Hierarchy
─────────
Object
├── Block            – static terrain tile
├── SpikedBall       – static hazard (no animation)
└── AnimatedObject   – base with ``_animate()`` helper
    ├── Fire
    ├── Goal
    ├── Fruit         – now plays a "Collected" animation
    ├── Fan
    ├── Trampoline
    ├── FallingPlatform
    ├── MovingPlatform
    ├── Arrow
    └── MovingHazard  – oscillating obstacle base
        ├── Saw
        ├── RockHead
        └── SpikeHead
"""

import random
import pygame
from os.path import join

from utils import get_block, load_sprite_sheets


# ── base classes ──────────────────────────────────────────────────

class Object(pygame.sprite.Sprite):
    """Root sprite for every world object."""

    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class AnimatedObject(Object):
    """Object that cycles through a sprite list every frame."""

    ANIMATION_DELAY = 3

    def _animate(self, sprites):
        """Advance one animation tick and update image + mask."""
        idx = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[idx]
        self.animation_count += 1
        self.mask = pygame.mask.from_surface(self.image)
        return idx


# ── terrain ───────────────────────────────────────────────────────

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


# ── fire ──────────────────────────────────────────────────────────

class Fire(AnimatedObject):
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
        self._animate(sprites)
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))


# ── goal ──────────────────────────────────────────────────────────

class Goal(AnimatedObject):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width=64, height=64):
        super().__init__(x, y, width, height, "goal")
        raw = load_sprite_sheets("Items/Checkpoints", "End", 64, 64)
        self.sprites = {
            "idle": [pygame.transform.scale(img, (width, height))
                     for img in raw["End (Idle)"]],
            "pressed": [pygame.transform.scale(img, (width, height))
                        for img in raw["End (Pressed) (64x64)"]],
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
        self._animate(self.sprites[self.animation_name])
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))


# ── spike (static) ───────────────────────────────────────────────

class Spike(Object):
    def __init__(self, x, y, width=64, height=32):
        super().__init__(x, y, width, height, "spike")
        raw = load_sprite_sheets("Traps", "Spikes", 16, 16)
        spike_img = raw["Idle"][0]
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        single = pygame.transform.scale(spike_img, (32, height))
        for off in range(0, width, 32):
            self.image.blit(single, (off, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)


# ── moving hazard base ───────────────────────────────────────────

class MovingHazard(AnimatedObject):
    """Animated obstacle that oscillates along one axis."""

    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, name, sprites,
                 move_range=0, axis="x", speed=2):
        super().__init__(x, y, width, height, name)
        self.sprites = sprites
        self.animation_count = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.start_pos = x if axis == "x" else y
        self.move_range = move_range
        self.axis = axis
        self.speed = speed

    def loop(self):
        self._animate(self.sprites)
        if self.move_range > 0:
            if self.axis == "x":
                self.rect.x += self.speed
                if (self.rect.x > self.start_pos + self.move_range
                        or self.rect.x < self.start_pos):
                    self.speed *= -1
            else:
                self.rect.y += self.speed
                if (self.rect.y > self.start_pos + self.move_range
                        or self.rect.y < self.start_pos):
                    self.speed *= -1


class Saw(MovingHazard):
    ANIMATION_DELAY = 2

    def __init__(self, x, y, width=64, height=64,
                 move_range=0, axis="x", speed=2):
        raw = load_sprite_sheets("Traps", "Saw", 38, 38)
        sprites = [pygame.transform.scale(img, (width, height))
                   for img in raw["on"]]
        super().__init__(x, y, width, height, "saw", sprites,
                         move_range, axis, speed)


class RockHead(MovingHazard):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width=84, height=84,
                 move_range=150, axis="y", speed=3):
        raw = load_sprite_sheets("Traps", "Rock Head", 42, 42)
        sprites = [pygame.transform.scale(img, (width, height))
                   for img in raw["Blink (42x42)"]]
        super().__init__(x, y, width, height, "rock_head", sprites,
                         move_range, axis, speed)


class SpikeHead(MovingHazard):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width=84, height=84,
                 move_range=150, axis="y", speed=3):
        raw = load_sprite_sheets("Traps", "Spike Head", 54, 52)
        sprites = [pygame.transform.scale(img, (width, height))
                   for img in raw["Blink (54x52)"]]
        super().__init__(x, y, width, height, "spike_head", sprites,
                         move_range, axis, speed)


# ── trampoline ────────────────────────────────────────────────────

class Trampoline(AnimatedObject):
    ANIMATION_DELAY = 2

    def __init__(self, x, y, width=56, height=56):
        super().__init__(x, y, width, height, "trampoline")
        raw = load_sprite_sheets("Traps", "Trampoline", 28, 28)
        self.sprites = {
            "idle": [pygame.transform.scale(img, (width, height))
                     for img in raw["Idle"]],
            "jump": [pygame.transform.scale(img, (width, height))
                     for img in raw["Jump (28x28)"]],
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
        idx = self._animate(sprites)
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        if self.animation_name == "jump" and idx == len(sprites) - 1:
            self.animation_name = "idle"
            self.animation_count = 0


# ── moving platform ──────────────────────────────────────────────

class MovingPlatform(AnimatedObject):
    ANIMATION_DELAY = 4

    def __init__(self, x, y, width=128, height=32,
                 move_range=150, axis="x", speed=2):
        super().__init__(x, y, width, height, "moving_platform")
        raw = load_sprite_sheets("Traps", "Platforms", 32, 8)
        key = ("Brown On (32x8)" if "Brown On (32x8)" in raw
               else list(raw.keys())[0])
        self.sprites = [pygame.transform.scale(img, (width, height))
                        for img in raw[key]]
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
        self._animate(self.sprites)
        self.dx = self.dy = 0
        if self.move_range > 0:
            if self.axis == "x":
                self.dx = self.speed
                self.rect.x += self.dx
                if (self.rect.x > self.start_pos + self.move_range
                        or self.rect.x < self.start_pos):
                    self.speed *= -1
            else:
                self.dy = self.speed
                self.rect.y += self.dy
                if (self.rect.y > self.start_pos + self.move_range
                        or self.rect.y < self.start_pos):
                    self.speed *= -1


# ── fruit ─────────────────────────────────────────────────────────

class Fruit(AnimatedObject):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, fruit_type="Apple", width=40, height=40):
        super().__init__(x, y, width, height, "fruit")
        raw = load_sprite_sheets("Items", "Fruits", 32, 32)
        key = fruit_type if fruit_type in raw else "Apple"
        self.sprites = [pygame.transform.scale(img, (width, height))
                        for img in raw[key]]
        # "Collected" sparkle animation (asset-pack sheet)
        self.collected_sprites = [
            pygame.transform.scale(img, (width, height))
            for img in raw.get("Collected", raw[key][:1])
        ]
        self.animation_count = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.collected = False
        self.collect_anim_done = False
        self._collect_count = 0

    def collect(self):
        """Start the collection animation."""
        self.collected = True
        self._collect_count = 0

    def loop(self):
        if self.collected:
            if not self.collect_anim_done:
                idx = (self._collect_count // self.ANIMATION_DELAY
                       ) % len(self.collected_sprites)
                self.image = self.collected_sprites[idx]
                self._collect_count += 1
                self.mask = pygame.mask.from_surface(self.image)
                if (self._collect_count // self.ANIMATION_DELAY
                        >= len(self.collected_sprites)):
                    self.collect_anim_done = True
            return
        self._animate(self.sprites)


# ── arrow ─────────────────────────────────────────────────────────

class Arrow(AnimatedObject):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width=48, height=48, speed=4,
                 move_range=400):
        super().__init__(x, y, width, height, "arrow")
        raw = load_sprite_sheets("Traps", "Arrow", 18, 18)
        self.sprites = {
            "idle": [pygame.transform.scale(img, (width, height))
                     for img in raw["Idle (18x18)"]],
            "hit": [pygame.transform.scale(img, (width, height))
                    for img in raw.get("Hit (18x18)",
                                       raw["Idle (18x18)"])],
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
        self._animate(self.sprites[self.animation_name])
        self.rect.x += self.speed
        if self.rect.x > self.start_x + self.move_range:
            self.rect.x = self.start_x


# ── falling platform ─────────────────────────────────────────────

class FallingPlatform(AnimatedObject):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width=96, height=32):
        super().__init__(x, y, width, height, "falling_platform")
        raw = load_sprite_sheets("Traps", "Falling Platforms", 32, 10)
        self.sprites = {
            "off": [pygame.transform.scale(img, (width, height))
                    for img in raw["Off"]],
            "on":  [pygame.transform.scale(img, (width, height))
                    for img in raw["On (32x10)"]],
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

        self._animate(self.sprites[self.animation_name])


# ── fan ───────────────────────────────────────────────────────────

class Fan(AnimatedObject):
    ANIMATION_DELAY = 1

    def __init__(self, x, y, width=48, height=24):
        super().__init__(x, y, width, height, "fan")
        raw = load_sprite_sheets("Traps", "Fan", 24, 8)
        self.sprites = [pygame.transform.scale(img, (width, height))
                        for img in raw["On (24x8)"]]
        self.animation_count = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.wind_rect = pygame.Rect(x, y - 500, width, 500)

    def loop(self):
        self._animate(self.sprites)


# ── spiked ball (static) ─────────────────────────────────────────

class SpikedBall(Object):
    def __init__(self, x, y, width=48, height=48):
        super().__init__(x, y, width, height, "spiked_ball")
        image = pygame.image.load(
            join("assets", "Traps", "Spiked Ball", "Spiked Ball.png")
        ).convert_alpha()
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)