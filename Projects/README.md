# Virtual Piano (Flask + OpenCV + MediaPipe)

Play a 2-octave piano by moving your fingertip over keys drawn on your webcam image.

## Install
    python -m venv venv
    # Windows: venv\Scripts\activate      macOS/Linux: source venv/bin/activate
    pip install -r requirements.txt
    python app.py
Open http://127.0.0.1:5000, click **Start Sound**, and play.
Use Python 3.9-3.12. Sounds are generated automatically on first run (or run `python sound_generator.py`).

## Troubleshooting
- Black image / "Camera not available": change CAMERA_INDEX in config.py (0, 1, 2...).
- No sound: click "Start Sound" first; check browser/system volume.
- Too many accidental notes: choose "Index only" and raise the cooldown.
- Low FPS: lower FRAME_WIDTH/FRAME_HEIGHT in config.py, improve lighting.
