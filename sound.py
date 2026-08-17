"""Sound effects and music manager using procedurally generated chiptune audio.

All sounds are synthesised at runtime from basic waveforms — no external
audio files needed.  Call ``sound_manager.init()`` once after
``pygame.init()`` to generate the sound bank, then use ``play_sfx(name)``
anywhere.
"""

import math
import struct
import random
import array
import sys
import pygame

# Use a lower sample rate for browser compatibility (less CPU in WASM)
SAMPLE_RATE = 22050

# Detect if running inside a browser / WASM environment
_IS_WASM = sys.platform in ("emscripten", "wasi")

# Short fade to prevent click/pop artifacts (in samples)
_FADE_SAMPLES = 64


class SoundManager:
    """Singleton that holds every sound effect and the background melody."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ── public API ────────────────────────────────────────────────

    def init(self):
        """Generate all SFX.  Safe to call more than once."""
        if self._initialized:
            return
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2,
                              buffer=4096)
        self._sfx: dict[str, pygame.mixer.Sound] = {}
        self._generate_all_sfx()
        self._music_channel: pygame.mixer.Channel | None = None
        self._music_sound: pygame.mixer.Sound | None = None
        self._music_playing = False
        self._sfx_volume = 0.4 if _IS_WASM else 0.5
        self._music_volume = 0.18 if _IS_WASM else 0.25
        self._initialized = True

    def play_sfx(self, name: str):
        if not self._initialized or name not in self._sfx:
            return
        snd = self._sfx[name]
        snd.set_volume(self._sfx_volume)
        snd.play()

    def play_music(self):
        if not self._initialized or self._music_playing:
            return
            
        # Load the external audio file you just saved.
        # NOTE: use .ogg, not .mp3 — pygbag's WASM build of SDL_mixer has
        # unreliable/missing MP3 decoding support, so mp3 files can fail to
        # produce audible output even when .load()/.play() raise no error.
        pygame.mixer.music.load("bg_music.ogg")
        
        # Apply your manager's existing music volume variable
        pygame.mixer.music.set_volume(self._music_volume)
        
        # Play the music (-1 tells Pygame to loop it indefinitely)
        pygame.mixer.music.play(-1)
        
        self._music_playing = True

    def stop_music(self):
        if self._music_playing:
            pygame.mixer.music.stop()
        self._music_playing = False

    def set_sfx_volume(self, vol: float):
        self._sfx_volume = max(0.0, min(1.0, vol))

    def set_music_volume(self, vol: float):
        self._music_volume = max(0.0, min(1.0, vol))
        # Update the streaming music volume dynamically
        if self._initialized:
            pygame.mixer.music.set_volume(self._music_volume)

    # ── waveform helpers ──────────────────────────────────────────

    @staticmethod
    def _wave(wtype: str, freq: float, t: float) -> float:
        if wtype == "square":
            # Band-limited square: use tanh to soften the hard edges
            # This avoids the sharp discontinuity that causes crackling
            return math.tanh(4.0 * math.sin(2 * math.pi * freq * t))
        if wtype == "triangle":
            phase = (t * freq) % 1.0
            return 4.0 * abs(phase - 0.5) - 1.0
        # default → sine
        return math.sin(2 * math.pi * freq * t)

    @staticmethod
    def _apply_fade(buf: array.array, n_samples: int):
        """Apply a short fade-in and fade-out to eliminate click artifacts.
        buf is interleaved stereo (L, R, L, R, ...) so total length = n_samples * 2."""
        fade = min(_FADE_SAMPLES, n_samples // 4)
        for i in range(fade):
            scale = i / fade
            # Fade in
            buf[i * 2]     = int(buf[i * 2] * scale)
            buf[i * 2 + 1] = int(buf[i * 2 + 1] * scale)
            # Fade out (from end)
            j = n_samples - 1 - i
            buf[j * 2]     = int(buf[j * 2] * scale)
            buf[j * 2 + 1] = int(buf[j * 2 + 1] * scale)

    def _buf_to_sound(self, buf: array.array, n_samples: int) -> pygame.mixer.Sound:
        self._apply_fade(buf, n_samples)
        return pygame.mixer.Sound(buffer=buf)

    # ── sound generators ──────────────────────────────────────────

    def _chirp(self, f0, f1, dur_ms, wtype="square", vol=0.3):
        n = int(SAMPLE_RATE * dur_ms / 1000)
        buf = array.array("h")
        for i in range(n):
            t = i / SAMPLE_RATE
            p = i / n
            freq = f0 + (f1 - f0) * p
            env = 1.0 - p
            val = int(vol * env * 32767 * self._wave(wtype, freq, t))
            val = max(-32768, min(32767, val))
            buf.append(val); buf.append(val)
        return self._buf_to_sound(buf, n)

    def _thump(self, freq, dur_ms, vol=0.2):
        n = int(SAMPLE_RATE * dur_ms / 1000)
        buf = array.array("h")
        for i in range(n):
            t = i / SAMPLE_RATE
            p = i / n
            env = (1.0 - p) ** 3
            val = int(vol * env * 32767
                      * self._wave("sine", freq * (1 - p * 0.5), t))
            val = max(-32768, min(32767, val))
            buf.append(val); buf.append(val)
        return self._buf_to_sound(buf, n)

    def _ding(self, f0, f1, dur_ms, vol=0.3):
        n = int(SAMPLE_RATE * dur_ms / 1000)
        buf = array.array("h")
        for i in range(n):
            t = i / SAMPLE_RATE
            p = i / n
            freq = f0 + (f1 - f0) * p
            env = (1.0 - p) ** 0.5
            val = int(vol * env * 32767 * self._wave("sine", freq, t))
            val = max(-32768, min(32767, val))
            buf.append(val); buf.append(val)
        return self._buf_to_sound(buf, n)

    def _boing(self, f_lo, f_hi, dur_ms, vol=0.3):
        n = int(SAMPLE_RATE * dur_ms / 1000)
        buf = array.array("h")
        for i in range(n):
            t = i / SAMPLE_RATE
            p = i / n
            freq = (f_lo + (f_hi - f_lo) * (p / 0.3) if p < 0.3
                    else f_hi + (f_lo - f_hi) * ((p - 0.3) / 0.7))
            env = 1.0 - p * 0.8
            val = int(vol * env * 32767 * self._wave("triangle", freq, t))
            val = max(-32768, min(32767, val))
            buf.append(val); buf.append(val)
        return self._buf_to_sound(buf, n)

    def _arpeggio(self, freqs, note_ms, vol=0.3):
        buf = array.array("h")
        total_n = 0
        for freq in freqs:
            n = int(SAMPLE_RATE * note_ms / 1000)
            total_n += n
            for i in range(n):
                t = i / SAMPLE_RATE
                p = i / n
                # Smooth note transitions to prevent inter-note clicks
                attack = min(1.0, p * 15)
                release = 1.0 if p < 0.75 else (1.0 - (p - 0.75) / 0.25)
                env = attack * release
                val = int(vol * env * 32767
                          * self._wave("square", freq, t))
                val = max(-32768, min(32767, val))
                buf.append(val); buf.append(val)
        return self._buf_to_sound(buf, total_n)

    def _noise_burst(self, dur_ms, vol=0.2):
        n = int(SAMPLE_RATE * dur_ms / 1000)
        buf = array.array("h")
        for i in range(n):
            p = i / n
            env = (1.0 - p) ** 2
            val = int(vol * env * 32767 * random.uniform(-1, 1))
            val = max(-32768, min(32767, val))
            buf.append(val); buf.append(val)
        return self._buf_to_sound(buf, n)

    # ── bank builder ──────────────────────────────────────────────

    def _generate_all_sfx(self):
        s = self._sfx
        s["jump"]          = self._chirp(300,  500,  100, "square",   0.20)
        s["double_jump"]   = self._chirp(500,  900,   80, "square",   0.20)
        s["land"]          = self._thump(80,          40,              0.12)
        s["death"]         = self._chirp(600,  150,  400, "triangle", 0.25)
        s["fruit_collect"] = self._ding(880, 1200,   150,              0.25)
        s["trampoline"]    = self._boing(200,  800,  200,              0.20)
        s["level_clear"]   = self._arpeggio([523, 659, 784, 1047],
                                            120,                       0.25)
        s["victory"]       = self._arpeggio([523, 659, 784, 1047,
                                             1319, 1568], 150,         0.25)
        s["hit"]           = self._noise_burst(60,                     0.15)
        s["wall_jump"]     = self._chirp(400,  700,   80, "square",   0.15)
        s["pause"]         = self._chirp(600,  400,   80, "sine",     0.15)
        s["unpause"]       = self._chirp(400,  600,   80, "sine",     0.15)


    # ── background melody ─────────────────────────────────────────

    def _generate_melody(self) -> pygame.mixer.Sound:
        """Cute, soothing pixel-art style melody."""
        # A sweet, uplifting major scale melody that feels bouncy but gentle
        notes = [
            (523, 300), (659, 300), (784, 600),  # C5, E5, G5
            (880, 300), (784, 300), (659, 600),  # A5, G5, E5
            (523, 300), (659, 300), (784, 400), (659, 200), 
            (587, 600), (523, 800)               # D5, C5 (held longer to resolve)
        ]
        buf = array.array("h")
        total_n = 0
        for freq, dur in notes:
            n = int(SAMPLE_RATE * dur / 1000)
            total_n += n
            for i in range(n):
                t = i / SAMPLE_RATE
                p = i / n
                
                # Softer attack and a long, gentle fade-out for a cozy feel
                attack = min(1.0, p * 10)
                release = 1.0 if p < 0.5 else (1.0 - (p - 0.5) / 0.5)
                env = attack * release
                
                # The 'triangle' wave gives that classic, soft 8-bit flute sound
                val = int(0.10 * env * 32767
                          * self._wave("triangle", freq, t))
                
                val = max(-32768, min(32767, val))
                buf.append(val); buf.append(val)
        return self._buf_to_sound(buf, total_n)


# Global singleton — import and use anywhere
sound_manager = SoundManager()