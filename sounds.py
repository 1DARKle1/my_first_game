import math
import os
import struct
import wave

from paths import resource_dir, writable_dir

SOUNDS_DIR = os.path.join(resource_dir(), "assets", "sounds")
WRITABLE_SOUNDS_DIR = os.path.join(writable_dir(), "sounds")

SAMPLE_RATE = 22050


def _active_sounds_dir():
    if os.path.isdir(SOUNDS_DIR) and any(f.endswith(".wav") for f in os.listdir(SOUNDS_DIR)):
        return SOUNDS_DIR
    os.makedirs(WRITABLE_SOUNDS_DIR, exist_ok=True)
    return WRITABLE_SOUNDS_DIR


def _write_tone(path, frequency, duration, volume=0.4, fade=True):
    n_samples = int(SAMPLE_RATE * duration)
    frames = []

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        sample = math.sin(2 * math.pi * frequency * t) * volume
        if fade:
            env = min(1.0, i / (SAMPLE_RATE * 0.02), (n_samples - i) / (SAMPLE_RATE * 0.05))
            sample *= max(0.0, env)
        frames.append(int(sample * 32767))

    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(struct.pack(f"<{len(frames)}h", *frames))


def _write_chord(path, frequencies, duration, volume=0.35):
    n_samples = int(SAMPLE_RATE * duration)
    frames = []

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        sample = sum(math.sin(2 * math.pi * f * t) for f in frequencies) / len(frequencies)
        env = min(1.0, i / (SAMPLE_RATE * 0.01), (n_samples - i) / (SAMPLE_RATE * 0.08))
        sample *= volume * max(0.0, env)
        frames.append(int(sample * 32767))

    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(struct.pack(f"<{len(frames)}h", *frames))


def _write_noise_hit(path, duration=0.25, volume=0.5):
    import random

    n_samples = int(SAMPLE_RATE * duration)
    frames = []

    for i in range(n_samples):
        decay = 1.0 - (i / n_samples)
        sample = (random.random() * 2 - 1) * volume * decay * decay
        frames.append(int(sample * 32767))

    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(struct.pack(f"<{len(frames)}h", *frames))


def ensure_sounds():
    target_dir = _active_sounds_dir()

    sounds = {
        "click.wav": lambda p: _write_tone(p, 880, 0.06, 0.25),
        "attack.wav": lambda p: _write_noise_hit(p, 0.2, 0.45),
        "heal.wav": lambda p: _write_chord(p, [523, 659, 784], 0.35, 0.3),
        "mana.wav": lambda p: _write_chord(p, [880, 1108, 1318], 0.25, 0.28),
        "buy.wav": lambda p: _write_chord(p, [988, 1319], 0.18, 0.32),
        "damage.wav": lambda p: _write_noise_hit(p, 0.35, 0.55),
        "victory.wav": lambda p: _write_chord(p, [523, 659, 784, 1047], 0.6, 0.35),
        "defeat.wav": lambda p: _write_chord(p, [392, 349, 294], 0.7, 0.3),
        "card_play.wav": lambda p: _write_tone(p, 660, 0.12, 0.22),
    }

    for filename, generator in sounds.items():
        path = os.path.join(target_dir, filename)
        if not os.path.exists(path):
            generator(path)


def sound_path(name):
    return os.path.abspath(os.path.join(_active_sounds_dir(), name))
