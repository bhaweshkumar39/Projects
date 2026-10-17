"""Background worker: camera -> hand tracking -> key detection -> JPEG + note events."""
import threading
import time
from collections import deque

import cv2
import numpy as np

import config
from hand_tracker import HandTracker
from piano import Piano


class PianoEngine:
    def __init__(self):
        self.piano = Piano(config.FRAME_WIDTH, config.FRAME_HEIGHT,
                           config.START_OCTAVE, config.NUM_OCTAVES,
                           config.PIANO_HEIGHT_RATIO)
        self.tracker = None
        self.running = False
        self.thread = None

        self.latest_jpeg = None
        self.fps = 0.0
        self.camera_ok = False

        self.events = deque(maxlen=200)   # recent note events
        self.event_id = 0
        self._lock = threading.Lock()
        self._last_trigger = {}           # key name -> last time it sounded
        self._finger_state = {}           # (hand, tip) -> key name it is over

        # settings changeable from the web UI
        self.tips = list(config.DEFAULT_TIPS)
        self.cooldown = config.KEY_COOLDOWN
        self.show_landmarks = True

    # ---------- public API ----------
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def set_config(self, tips=None, cooldown=None, landmarks=None):
        if tips is not None:
            names = config.TIP_IDS.keys() if tips == "all" else [tips]
            self.tips = [n for n in names if n in config.TIP_IDS]
        if cooldown is not None:
            self.cooldown = max(0.05, min(1.0, float(cooldown)))
        if landmarks is not None:
            self.show_landmarks = bool(landmarks)

    def get_events(self, since):
        with self._lock:
            return [e for e in self.events if e["id"] > since], self.event_id

    # ---------- internals ----------
    def _trigger(self, key):
        now = time.time()
        if now - self._last_trigger.get(key.name, 0) < self.cooldown:
            return
        self._last_trigger[key.name] = now
        with self._lock:
            self.event_id += 1
            self.events.append({"id": self.event_id, "note": key.name})

    def _placeholder(self, text):
        img = np.zeros((config.FRAME_HEIGHT, config.FRAME_WIDTH, 3), np.uint8)
        cv2.putText(img, text, (40, config.FRAME_HEIGHT // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
        return img

    def _loop(self):
        self.tracker = HandTracker()
        cap = cv2.VideoCapture(config.CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        prev = time.time()

        while self.running:
            ok, frame = cap.read()
            self.camera_ok = bool(ok)
            if not ok:
                frame = self._placeholder("Camera not available - check CAMERA_INDEX")
                self._store(frame)
                time.sleep(0.2)
                continue

            frame = cv2.flip(frame, 1)  # mirror view feels natural
            frame = cv2.resize(frame, (config.FRAME_WIDTH, config.FRAME_HEIGHT))

            hands = self.tracker.process(frame)
            current = {}
            for hand in hands:
                if self.show_landmarks:
                    self.tracker.draw_landmarks(frame, hand["raw"])
                for tip_name in self.tips:
                    tid = config.TIP_IDS[tip_name]
                    x, y = hand["tips"][tid]
                    key = self.piano.hit(x, y)
                    current[(hand["label"], tid)] = key
                    cv2.circle(frame, (x, y), 10, (0, 0, 255), -1)

            # a note fires when a fingertip ENTERS a key it was not on before
            for fid, key in current.items():
                prev_key = self._finger_state.get(fid)
                if key is not None and (prev_key is None or prev_key != key.name):
                    self._trigger(key)
            self._finger_state = {fid: (k.name if k else None) for fid, k in current.items()}

            active = {k.name for k in current.values() if k}
            self.piano.draw(frame, active)

            now = time.time()
            self.fps = 0.9 * self.fps + 0.1 * (1 / max(now - prev, 1e-6))
            prev = now
            cv2.putText(frame, f"FPS {self.fps:.0f}", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
            self._store(frame)

        cap.release()
        self.tracker.close()

    def _store(self, frame):
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, config.JPEG_QUALITY])
        if ok:
            self.latest_jpeg = buf.tobytes()
