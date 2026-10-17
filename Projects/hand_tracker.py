"""Thin wrapper around MediaPipe Hands. Returns fingertip pixel positions."""
import cv2
import mediapipe as mp
import config


class HandTracker:
    def __init__(self):
        self._mp_hands = mp.solutions.hands
        self._drawer = mp.solutions.drawing_utils
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.MAX_HANDS,
            model_complexity=0,  # fastest model
            min_detection_confidence=config.DETECTION_CONFIDENCE,
            min_tracking_confidence=config.TRACKING_CONFIDENCE,
        )

    def process(self, frame_bgr):
        """Return a list of hands: {'label', 'tips': {tip_id: (x, y)}, 'raw'}."""
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = self._hands.process(rgb)
        hands = []
        if result.multi_hand_landmarks:
            for i, lm in enumerate(result.multi_hand_landmarks):
                label = result.multi_handedness[i].classification[0].label
                tips = {tid: (int(lm.landmark[tid].x * w), int(lm.landmark[tid].y * h))
                        for tid in config.TIP_IDS.values()}
                hands.append({"label": label, "tips": tips, "raw": lm})
        return hands

    def draw_landmarks(self, frame, raw):
        self._drawer.draw_landmarks(frame, raw, self._mp_hands.HAND_CONNECTIONS)

    def close(self):
        self._hands.close()
