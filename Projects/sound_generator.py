"""Creates piano-like WAV files with simple additive synthesis (no downloads)."""
import os
import wave
import numpy as np

SAMPLE_RATE = 44100
NOTE_INDEX = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
              "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def note_to_freq(name: str) -> float:
    """'A4' -> 440.0 Hz, 'C#5' -> 554.37 Hz ..."""
    letter, octave = name[:-1], int(name[-1])
    midi = 12 * (octave + 1) + NOTE_INDEX[letter]
    return 440.0 * 2 ** ((midi - 69) / 12)


def synth_piano(freq: float, duration: float = 2.5) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    amps = [1.0, 0.55, 0.32, 0.20, 0.12, 0.08, 0.05]   # harmonic strengths
    wave_sum = np.zeros_like(t)
    for n, amp in enumerate(amps, start=1):
        f = freq * n * np.sqrt(1 + 0.0004 * n * n)       # slight string stiffness
        if f > SAMPLE_RATE / 2.2:
            break
        decay = np.exp(-t * (1.6 + 1.2 * n))             # higher harmonics die faster
        # two slightly detuned "strings" give the warm piano shimmer
        wave_sum += amp * decay * (np.sin(2 * np.pi * f * t) +
                                   np.sin(2 * np.pi * f * 1.0015 * t)) / 2
    # hammer "thump": short burst of noise
    rng = np.random.default_rng(int(freq))
    wave_sum += 0.04 * rng.standard_normal(len(t)) * np.exp(-t * 90)
    # envelope: 5 ms attack, 80 ms release at the end
    attack = np.minimum(t / 0.005, 1.0)
    release = np.minimum((duration - t) / 0.08, 1.0)
    wave_sum *= attack * release
    return wave_sum / np.max(np.abs(wave_sum)) * 0.8


def save_wav(path: str, samples: np.ndarray) -> None:
    data = (samples * 32767).astype(np.int16)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(data.tobytes())


def generate_all(note_names, out_dir: str, force: bool = False) -> None:
    os.makedirs(out_dir, exist_ok=True)
    for name in note_names:
        path = os.path.join(out_dir, name.replace("#", "s") + ".wav")
        if force or not os.path.exists(path):
            save_wav(path, synth_piano(note_to_freq(name)))
            print("created", path)


if __name__ == "__main__":
    import config
    from piano import Piano
    p = Piano(960, 540, config.START_OCTAVE, config.NUM_OCTAVES, config.PIANO_HEIGHT_RATIO)
    generate_all([k.name for k in p.keys], config.SOUNDS_DIR, force=True)
