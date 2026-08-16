"""Player character class with health, coyote-time, jump-buffer,
wall-jump, and invincibility frames."""

import pygame

from utils import load_sprite_sheets
from sound import sound_manager


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = None  # lazy-loaded after pygame.init()
    ANIMATION_DELAY = 3

    # Gameplay tuning
    MAX_HEALTH = 3
    COYOTE_FRAMES = 8          # grace period after leaving ground
    BUFFER_FRAMES = 8          # jump-input buffer window
    INVINCIBLE_DURATION = 90   # frames (~1.5 s at 60 FPS)

    def __init__(self, x, y, width, height):
        super().__init__()
        # Load sprites on first instantiation (pygame must be initialised)
        if Player.SPRITES is None:
            Player.SPRITES = load_sprite_sheets(
                "MainCharacters", "VirtualGuy", 32, 32, True)
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

        # ── new fields ──
        self.health = self.MAX_HEALTH
        self.dead = False                 # True once health reaches 0

        self.invincible = False
        self.invincible_timer = 0

        self.coyote_timer = 0
        self.jump_buffer = 0
        self.just_landed = False          # set for one frame on landing

        self.touching_wall_left = False
        self.touching_wall_right = False
        self.wall_sliding = False
        self.last_safe_pos = (x, y)

        self.update_sprite()

    # ── jumping ───────────────────────────────────────────────────

    def request_jump(self):
        """Called when the player presses the jump key."""
        # Wall-jump takes priority if sliding on a wall
        if self.wall_sliding:
            self.wall_jump()
            return
        if self.jump_count < 2 and (self.jump_count > 0 or self.coyote_timer > 0
                                     or self.fall_count < self.COYOTE_FRAMES):
            self.jump()
        else:
            # Buffer the press so it fires on next landing
            self.jump_buffer = self.BUFFER_FRAMES

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
            sound_manager.play_sfx("jump")
        elif self.jump_count == 2:
            sound_manager.play_sfx("double_jump")
        self.coyote_timer = 0
        self.jump_buffer = 0

    def wall_jump(self):
        self.y_vel = -self.GRAVITY * 7
        if self.touching_wall_left:
            self.x_vel = 6
            self.direction = "right"
        else:
            self.x_vel = -6
            self.direction = "left"
        self.jump_count = 1
        self.fall_count = 0
        self.wall_sliding = False
        self.coyote_timer = 0
        self.jump_buffer = 0
        sound_manager.play_sfx("wall_jump")

    # ── movement ──────────────────────────────────────────────────

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    # ── damage ────────────────────────────────────────────────────

    def make_hit(self):
        """Take one hit.  Ignored during invincibility."""
        if self.invincible or self.dead:
            return
        self.health -= 1
        self.hit = True
        self.hit_count = 0
        self.invincible = True
        self.invincible_timer = self.INVINCIBLE_DURATION
        sound_manager.play_sfx("hit")
        if self.health <= 0:
            self.dead = True

    # ── per-frame update ──────────────────────────────────────────

    def loop(self, fps):
        # Gravity
        grav = min(1, (self.fall_count / fps) * self.GRAVITY)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            grav *= 2.5
        self.y_vel += grav
        self.move(self.x_vel, self.y_vel)

        # Clear one-frame flags
        self.just_landed = False

        # Hit animation counter
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps:
            self.hit = False
            self.hit_count = 0

        # Invincibility countdown
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        # Coyote / buffer timers
        if self.coyote_timer > 0:
            self.coyote_timer -= 1
        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        # Wall-slide detection (set externally by collisions.py)
        self.wall_sliding = ((self.touching_wall_left
                              or self.touching_wall_right)
                             and self.y_vel > 0
                             and self.fall_count > 5)
        if self.wall_sliding:
            self.y_vel = min(self.y_vel, 2)   # slow fall

        # Coyote grace: after coyote runs out, consume ground jump
        if (self.fall_count > self.COYOTE_FRAMES
                and self.coyote_timer <= 0
                and self.jump_count == 0
                and self.y_vel > 0):
            self.jump_count = 1  # can now only double-jump

        # Record safe position if standing on solid ground
        if self.fall_count == 0 and self.y_vel == 0 and not self.wall_sliding and not self.invincible:
            ground = getattr(self, "ground_obj", None)
            if ground is not None and ground.name in (None, "block"):
                self.last_safe_pos = (self.rect.x, self.rect.y)

        self.fall_count += 1
        self.update_sprite()

    # ── landing callback ──────────────────────────────────────────

    def landed(self, obj=None):
        was_falling = self.y_vel > 2
        self.fall_count = 0
        self.ground_obj = obj
        self.y_vel = 0
        self.jump_count = 0
        self.coyote_timer = self.COYOTE_FRAMES
        self.just_landed = True
        if was_falling:
            sound_manager.play_sfx("land")
        # Execute any buffered jump
        if self.jump_buffer > 0:
            self.jump()

    def hit_head(self):
        self.fall_count = 0
        self.y_vel *= -1

    # ── sprite selection ──────────────────────────────────────────

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.wall_sliding:
            sprite_sheet = "wall_jump"
            # face away from wall
            if self.touching_wall_left:
                self.direction = "right"
            else:
                self.direction = "left"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        key = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[key]
        idx = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[idx]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    # ── drawing ───────────────────────────────────────────────────

    def draw(self, window, offset_x):
        # Flash during invincibility (skip every other 4-frame block)
        if self.invincible and (self.invincible_timer // 4) % 2 == 0:
            return
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))