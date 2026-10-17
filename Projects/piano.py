"""Piano geometry: builds the keys, hit-tests fingertips and draws the keyboard."""
from dataclasses import dataclass
import cv2

WHITE_NAMES = ["C", "D", "E", "F", "G", "A", "B"]
BLACK_AFTER = {0: "C#", 1: "D#", 3: "F#", 4: "G#", 5: "A#"}  # white index -> sharp

WHITE_COLOR, WHITE_ACTIVE = (245, 245, 245), (120, 230, 120)
BLACK_COLOR, BLACK_ACTIVE = (30, 30, 30), (0, 170, 0)


@dataclass
class Key:
    name: str
    is_black: bool
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def file(self) -> str:
        return self.name.replace("#", "s") + ".wav"

    def contains(self, x: int, y: int) -> bool:
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2


class Piano:
    def __init__(self, width, height, start_octave=4, num_octaves=2, height_ratio=0.38):
        self.width, self.height = width, height
        self.white, self.black = [], []
        top = int(height * (1 - height_ratio))
        n_white = 7 * num_octaves
        w = width / n_white
        for i in range(n_white):
            octave = start_octave + i // 7
            idx = i % 7
            self.white.append(Key(f"{WHITE_NAMES[idx]}{octave}", False,
                                  int(i * w), top, int((i + 1) * w), height - 1))
            if idx in BLACK_AFTER and i < n_white - 1:
                cx = (i + 1) * w
                bw = w * 0.6
                self.black.append(Key(f"{BLACK_AFTER[idx]}{octave}", True,
                                      int(cx - bw / 2), top, int(cx + bw / 2),
                                      top + int((height - top) * 0.6)))
        self.keys = sorted(self.white + self.black, key=lambda k: k.x1)

    def hit(self, x, y):
        """Return the key under (x, y). Black keys are on top, so check them first."""
        for k in self.black:
            if k.contains(x, y):
                return k
        for k in self.white:
            if k.contains(x, y):
                return k
        return None

    def draw(self, frame, active_names):
        overlay = frame.copy()
        for k in self.white:
            col = WHITE_ACTIVE if k.name in active_names else WHITE_COLOR
            cv2.rectangle(overlay, (k.x1, k.y1), (k.x2, k.y2), col, -1)
        for k in self.black:
            col = BLACK_ACTIVE if k.name in active_names else BLACK_COLOR
            cv2.rectangle(overlay, (k.x1, k.y1), (k.x2, k.y2), col, -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)  # translucent keys
        for k in self.white:
            cv2.rectangle(frame, (k.x1, k.y1), (k.x2, k.y2), (60, 60, 60), 2)
            cv2.putText(frame, k.name, (k.x1 + 6, k.y2 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (40, 40, 40), 1, cv2.LINE_AA)
        for k in self.black:
            cv2.rectangle(frame, (k.x1, k.y1), (k.x2, k.y2), (0, 0, 0), 2)
        return frame
