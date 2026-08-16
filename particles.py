"""Lightweight particle effects: dust, sparkles, confetti, and screen-shake."""

import random
import math
import pygame


class Particle:
    """A single short-lived visual particle."""

    __slots__ = ("x", "y", "vx", "vy", "lifetime", "age",
                 "color", "size", "gravity", "alive")

    def __init__(self, x, y, vx, vy, lifetime, color,
                 size=3.0, gravity=0.1):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.age = 0
        self.color = color
        self.size = size
        self.gravity = gravity
        self.alive = True

    def update(self):
        self.age += 1
        if self.age >= self.lifetime:
            self.alive = False
            return
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.98

    def draw(self, surface, offset_x):
        if not self.alive:
            return
        alpha = max(0.0, 1.0 - self.age / self.lifetime)
        sz = max(1, int(self.size * alpha))
        sx = int(self.x - offset_x)
        sy = int(self.y)
        if 0 <= sx < surface.get_width() and 0 <= sy < surface.get_height():
            pygame.draw.circle(surface, self.color, (sx, sy), sz)


class ParticleSystem:
    """Manages a pool of particles and a screen-shake timer."""

    def __init__(self):
        self.particles: list[Particle] = []
        # screen shake
        self._shake_x = 0
        self._shake_y = 0
        self._shake_dur = 0
        self._shake_intensity = 0

    # ── core ──────────────────────────────────────────────────────

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]
        # shake
        if self._shake_dur > 0:
            self._shake_dur -= 1
            self._shake_x = random.randint(-self._shake_intensity,
                                           self._shake_intensity)
            self._shake_y = random.randint(-self._shake_intensity,
                                           self._shake_intensity)
        else:
            self._shake_x = self._shake_y = 0

    def draw(self, surface, offset_x):
        for p in self.particles:
            p.draw(surface, offset_x)

    def clear(self):
        self.particles.clear()
        self._shake_dur = 0
        self._shake_x = self._shake_y = 0

    # ── emitters ──────────────────────────────────────────────────

    def emit_dust(self, x, y, count=6):
        """Puff of dust on landing."""
        for _ in range(count):
            self.particles.append(Particle(
                x, y,
                vx=random.uniform(-1.5, 1.5),
                vy=random.uniform(-2.5, -0.5),
                lifetime=random.randint(10, 25),
                color=random.choice([(180, 160, 140),
                                     (200, 180, 160),
                                     (160, 140, 120)]),
                size=random.uniform(2, 4),
                gravity=0.08,
            ))

    def emit_run_dust(self, x, y):
        """Tiny puff each frame while running."""
        self.particles.append(Particle(
            x, y,
            vx=random.uniform(-0.5, 0.5),
            vy=random.uniform(-1.5, -0.3),
            lifetime=random.randint(6, 12),
            color=random.choice([(180, 160, 140), (160, 140, 120)]),
            size=2,
            gravity=0.05,
        ))

    def emit_sparkle(self, x, y, count=12):
        """Sparkle burst on fruit collection."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            self.particles.append(Particle(
                x, y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                lifetime=random.randint(15, 35),
                color=random.choice([(255, 255, 100),
                                     (255, 200, 50),
                                     (255, 255, 200),
                                     (255, 230, 100)]),
                size=random.uniform(2, 5),
                gravity=0.02,
            ))

    def emit_confetti(self, x, y, count=30):
        """Big colourful burst on level-clear / victory."""
        for _ in range(count):
            self.particles.append(Particle(
                x, y,
                vx=random.uniform(-5, 5),
                vy=random.uniform(-8, -2),
                lifetime=random.randint(40, 80),
                color=random.choice([(255, 50, 50), (50, 255, 50),
                                     (50, 50, 255), (255, 255, 50),
                                     (255, 50, 255), (50, 255, 255)]),
                size=random.uniform(3, 6),
                gravity=0.15,
            ))

    def emit_death(self, x, y, count=20):
        """Red burst on player death."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append(Particle(
                x, y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                lifetime=random.randint(20, 40),
                color=random.choice([(230, 40, 40),
                                     (200, 20, 20),
                                     (255, 80, 80)]),
                size=random.uniform(2, 5),
                gravity=0.1,
            ))

    # ── screen shake ──────────────────────────────────────────────

    def start_screen_shake(self, intensity=5, duration=15):
        self._shake_intensity = intensity
        self._shake_dur = duration

    def get_shake_offset(self):
        return self._shake_x, self._shake_y
