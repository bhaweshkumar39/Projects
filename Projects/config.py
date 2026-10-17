"""Central settings. Change values here to tune the piano."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "static", "sounds")

# --- Camera -----------------------------------------------------------
CAMERA_INDEX = 0          # try 1 if you have several cameras
FRAME_WIDTH = 960
FRAME_HEIGHT = 540
JPEG_QUALITY = 80

# --- Piano ------------------------------------------------------------
START_OCTAVE = 4          # first key is C4
NUM_OCTAVES = 2           # C4 ... B5  (14 white + 10 black keys)
PIANO_HEIGHT_RATIO = 0.38 # piano height as a fraction of frame height

# --- Hand tracking ----------------------------------------------------
MAX_HANDS = 2
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.6
TIP_IDS = {"thumb": 4, "index": 8, "middle": 12, "ring": 16, "pinky": 20}
DEFAULT_TIPS = ["index"]  # "index" only, or switch to "all" in the web UI

# --- Playing ----------------------------------------------------------
KEY_COOLDOWN = 0.20       # seconds before the same key can sound again
