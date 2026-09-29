"""Mobile touch controls — virtual D-pad and action buttons.

The overlay is drawn on top of the game frame and handles
``FINGERDOWN / FINGERUP / FINGERMOTION`` events so that
multi-touch works correctly.

Public API used by the rest of the codebase
───────────────────────────────────────────
``touch.handle_event(event)``
    Call for every pygame event.  Returns a string or None:
    ``"jump"``  – the jump button was just pressed
    ``"pause"`` – the pause button was just pressed
    ``"enter"`` – the enter/confirm button (also jump btn in DEAD state)
    ``None``    – no one-shot action this event

``touch.virtual_keys``
    A dict that is *True* for keys currently held by the virtual pad.
    Keys used: ``pygame.K_LEFT``, ``pygame.K_RIGHT``, ``pygame.K_DOWN``.

``touch.draw(surface)``
    Renders the semi-transparent overlay.

``touch.is_active``
    True after the first touch event — overlay hidden until then.
"""

import pygame
import math
from settings import WIDTH, HEIGHT


# ── layout constants ──────────────────────────────────────────────

# Buttons are placed relative to the bottom of the screen.
# All sizes are in *game-space* pixels (1280×720 logical).
_PAD       = 24          # padding from screen edge
_BTN_R     = 42          # radius of circular buttons
_DPAD_R    = 48          # radius of D-pad arrows
_DPAD_GAP  = 18          # gap between the two D-pad arrows
_ALPHA     = 100         # base opacity (0-255) when not pressed
_ALPHA_HIT = 170         # opacity when pressed

# Bottom-left: D-pad
_DPAD_Y  = HEIGHT - _PAD - _DPAD_R
_LEFT_X  = _PAD + _DPAD_R
_RIGHT_X = _LEFT_X + _DPAD_R * 2 + _DPAD_GAP

# Bottom-right: action buttons
_JUMP_X  = WIDTH - _PAD - _BTN_R
_JUMP_Y  = HEIGHT - _PAD - _BTN_R * 2 - 20   # jump sits a bit higher
_DOWN_X  = WIDTH - _PAD - _BTN_R * 3 - 10
_DOWN_Y  = HEIGHT - _PAD - _BTN_R
_PAUSE_X = WIDTH - _PAD - _BTN_R
_PAUSE_Y = _PAD + _BTN_R + 60  # top-right area, below HUD


class _VButton:
    """A single circular virtual button."""

    def __init__(self, cx, cy, radius, label, color):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.label = label
        self.color = color
        self.pressed = False
        self._finger_id = None          # which finger is on this button

    def contains(self, x, y):
        """Check if (x, y) in *game-space* coords hits this button.
        Uses a slightly larger hitbox (1.3×) for fat-finger friendliness."""
        dx = x - self.cx
        dy = y - self.cy
        return math.hypot(dx, dy) <= self.radius * 1.35

    def draw(self, surface):
        alpha = _ALPHA_HIT if self.pressed else _ALPHA
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha),
                           (self.radius, self.radius), self.radius)
        pygame.draw.circle(s, (*self.color, min(255, alpha + 60)),
                           (self.radius, self.radius), self.radius, 3)
        surface.blit(s, (self.cx - self.radius, self.cy - self.radius))

        # label
        font = pygame.font.SysFont("arial", int(self.radius * 0.7), bold=True)
        txt = font.render(self.label, True, (255, 255, 255, min(255, alpha + 80)))
        surface.blit(txt, txt.get_rect(center=(self.cx, self.cy)))


class TouchControls:
    """Virtual on-screen controls for mobile play."""

    def __init__(self):
        self.is_active = False  # becomes True on first touch

        # D-pad
        self.btn_left  = _VButton(_LEFT_X,  _DPAD_Y, _DPAD_R, "◀", (80, 80, 80))
        self.btn_right = _VButton(_RIGHT_X, _DPAD_Y, _DPAD_R, "▶", (80, 80, 80))

        # Action buttons
        self.btn_jump  = _VButton(_JUMP_X,  _JUMP_Y,  _BTN_R, "▲", (50, 160, 80))
        self.btn_down  = _VButton(_DOWN_X,  _DOWN_Y,  _BTN_R, "▼", (60, 60, 160))
        self.btn_pause = _VButton(_PAUSE_X, _PAUSE_Y, 30,     "⏸", (180, 60, 60))

        self._all_buttons = [
            self.btn_left, self.btn_right,
            self.btn_jump, self.btn_down,
            self.btn_pause,
        ]

        # Virtual key state — checked by collisions.py / player.py
        self.virtual_keys = {
            pygame.K_LEFT:  False,
            pygame.K_RIGHT: False,
            pygame.K_DOWN:  False,
        }

    # ── event handling ────────────────────────────────────────────

    def handle_event(self, event):
        """Process a pygame event.  Returns ``"jump"``/``"pause"``/
        ``"enter"`` on button press, else ``None``."""

        if event.type not in (pygame.FINGERDOWN, pygame.FINGERUP,
                              pygame.FINGERMOTION):
            return None

        self.is_active = True

        # Convert normalised finger coords (0-1) → game-space pixels
        gx = event.x * WIDTH
        gy = event.y * HEIGHT
        fid = event.finger_id

        if event.type == pygame.FINGERDOWN:
            return self._finger_down(gx, gy, fid)
        elif event.type == pygame.FINGERUP:
            return self._finger_up(fid)
        elif event.type == pygame.FINGERMOTION:
            return self._finger_move(gx, gy, fid)

        return None

    def _finger_down(self, gx, gy, fid):
        action = None
        for btn in self._all_buttons:
            if btn.contains(gx, gy):
                btn.pressed = True
                btn._finger_id = fid
                if btn is self.btn_jump:
                    action = "jump"
                elif btn is self.btn_pause:
                    action = "pause"
                break
        self._sync_keys()
        return action

    def _finger_up(self, fid):
        for btn in self._all_buttons:
            if btn._finger_id == fid:
                btn.pressed = False
                btn._finger_id = None
        self._sync_keys()
        return None

    def _finger_move(self, gx, gy, fid):
        # If a finger slides off a button, release it;
        # if it slides onto one, press it.
        for btn in self._all_buttons:
            if btn._finger_id == fid:
                if not btn.contains(gx, gy):
                    btn.pressed = False
                    btn._finger_id = None
            elif btn._finger_id is None and btn.contains(gx, gy):
                # Only auto-grab directional buttons on slide
                if btn in (self.btn_left, self.btn_right, self.btn_down):
                    btn.pressed = True
                    btn._finger_id = fid
        self._sync_keys()
        return None

    def _sync_keys(self):
        self.virtual_keys[pygame.K_LEFT]  = self.btn_left.pressed
        self.virtual_keys[pygame.K_RIGHT] = self.btn_right.pressed
        self.virtual_keys[pygame.K_DOWN]  = self.btn_down.pressed

    # ── drawing ───────────────────────────────────────────────────

    def draw(self, surface):
        """Draw semi-transparent overlay buttons.  No-op if touch
        has never been used."""
        if not self.is_active:
            return
        for btn in self._all_buttons:
            btn.draw(surface)

    def release_all(self):
        """Force-release every button (e.g. on state change)."""
        for btn in self._all_buttons:
            btn.pressed = False
            btn._finger_id = None
        self._sync_keys()
