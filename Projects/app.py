"""Flask web server for the Virtual Piano."""
import time
from flask import Flask, Response, jsonify, render_template, request

import config
from engine import PianoEngine
from sound_generator import generate_all

app = Flask(__name__)
engine = PianoEngine()


def mjpeg_stream():
    while True:
        frame = engine.latest_jpeg
        if frame:
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        time.sleep(0.03)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(mjpeg_stream(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/keys")
def api_keys():
    return jsonify([{"name": k.name, "file": k.file, "black": k.is_black}
                    for k in engine.piano.keys])


@app.route("/api/notes")
def api_notes():
    since = request.args.get("since", default=-1, type=int)
    events, last_id = engine.get_events(since)
    if since < 0:          # first call: just learn the latest id, don't replay old notes
        events = []
    return jsonify({"events": events, "last_id": last_id})


@app.route("/api/status")
def api_status():
    return jsonify({"fps": round(engine.fps, 1), "camera_ok": engine.camera_ok})


@app.route("/api/config", methods=["POST"])
def api_config():
    data = request.get_json(force=True, silent=True) or {}
    engine.set_config(data.get("tips"), data.get("cooldown"), data.get("landmarks"))
    return jsonify({"ok": True})


if __name__ == "__main__":
    generate_all([k.name for k in engine.piano.keys], config.SOUNDS_DIR)  # only missing files
    engine.start()
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(host="127.0.0.1", port=5000, threaded=True, debug=False, use_reloader=False)
