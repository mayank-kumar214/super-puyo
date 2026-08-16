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
import pygame

SAMPLE_RATE = 44100


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
                              buffer=2048)
        self._sfx: dict[str, pygame.mixer.Sound] = {}
        self._generate_all_sfx()
        self._music_channel: pygame.mixer.Channel | None = None
        self._music_sound: pygame.mixer.Sound | None = None
        self._music_playing = False
        self._sfx_volume = 0.5
        self._music_volume = 0.25
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
        if self._music_sound is None:
            self._music_sound = self._generate_melody()
        self._music_sound.set_volume(self._music_volume)
        self._music_channel = pygame.mixer.Channel(7)
        self._music_channel.play(self._music_sound, loops=-1)
        self._music_playing = True

    def stop_music(self):
        if self._music_playing and self._music_channel is not None:
            self._music_channel.stop()
        self._music_playing = False

    def set_sfx_volume(self, vol: float):
        self._sfx_volume = max(0.0, min(1.0, vol))

    def set_music_volume(self, vol: float):
        self._music_volume = max(0.0, min(1.0, vol))
        if self._music_sound is not None:
            self._music_sound.set_volume(self._music_volume)

    # ── waveform helpers ──────────────────────────────────────────

    @staticmethod
    def _wave(wtype: str, freq: float, t: float) -> float:
        if wtype == "square":
            return 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        if wtype == "triangle":
            phase = (t * freq) % 1.0
            return 4.0 * abs(phase - 0.5) - 1.0
        # default → sine
        return math.sin(2 * math.pi * freq * t)

    def _buf_to_sound(self, buf: array.array) -> pygame.mixer.Sound:
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
        return self._buf_to_sound(buf)

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
        return self._buf_to_sound(buf)

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
        return self._buf_to_sound(buf)

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
        return self._buf_to_sound(buf)

    def _arpeggio(self, freqs, note_ms, vol=0.3):
        buf = array.array("h")
        for freq in freqs:
            n = int(SAMPLE_RATE * note_ms / 1000)
            for i in range(n):
                t = i / SAMPLE_RATE
                p = i / n
                env = 1.0 if p < 0.8 else (1.0 - (p - 0.8) / 0.2)
                val = int(vol * env * 32767
                          * self._wave("square", freq, t))
                val = max(-32768, min(32767, val))
                buf.append(val); buf.append(val)
        return self._buf_to_sound(buf)

    def _noise_burst(self, dur_ms, vol=0.2):
        n = int(SAMPLE_RATE * dur_ms / 1000)
        buf = array.array("h")
        for i in range(n):
            p = i / n
            env = (1.0 - p) ** 2
            val = int(vol * env * 32767 * random.uniform(-1, 1))
            val = max(-32768, min(32767, val))
            buf.append(val); buf.append(val)
        return self._buf_to_sound(buf)

    # ── bank builder ──────────────────────────────────────────────

    def _generate_all_sfx(self):
        s = self._sfx
        s["jump"]          = self._chirp(300,  500,  100, "square",   0.25)
        s["double_jump"]   = self._chirp(500,  900,   80, "square",   0.25)
        s["land"]          = self._thump(80,          40,              0.15)
        s["death"]         = self._chirp(600,  150,  400, "triangle", 0.30)
        s["fruit_collect"] = self._ding(880, 1200,   150,              0.30)
        s["trampoline"]    = self._boing(200,  800,  200,              0.25)
        s["level_clear"]   = self._arpeggio([523, 659, 784, 1047],
                                            120,                       0.30)
        s["victory"]       = self._arpeggio([523, 659, 784, 1047,
                                             1319, 1568], 150,         0.30)
        s["hit"]           = self._noise_burst(60,                     0.20)
        s["wall_jump"]     = self._chirp(400,  700,   80, "square",   0.20)
        s["pause"]         = self._chirp(600,  400,   80, "sine",     0.20)
        s["unpause"]       = self._chirp(400,  600,   80, "sine",     0.20)

    # ── background melody ─────────────────────────────────────────

    def _generate_melody(self) -> pygame.mixer.Sound:
        """Short C-major pentatonic loop, triangle wave."""
        notes = [
            (523, 200), (587, 200), (659, 200), (784, 400),
            (659, 200), (587, 200), (523, 400),
            (392, 200), (440, 200), (523, 200), (587, 400),
            (523, 200), (440, 200), (392, 400),
        ]
        buf = array.array("h")
        for freq, dur in notes:
            n = int(SAMPLE_RATE * dur / 1000)
            for i in range(n):
                t = i / SAMPLE_RATE
                p = i / n
                attack = min(1.0, p * 20)
                release = 1.0 if p < 0.85 else (1.0 - (p - 0.85) / 0.15)
                env = attack * release
                val = int(0.15 * env * 32767
                          * self._wave("triangle", freq, t))
                val = max(-32768, min(32767, val))
                buf.append(val); buf.append(val)
        return self._buf_to_sound(buf)


# Global singleton — import and use anywhere
sound_manager = SoundManager()
