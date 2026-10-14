import argparse
import os


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WINDOW_NAME = "AI Face + Hand Tracker MAX"


def project_path(*parts):
    return os.path.join(PROJECT_DIR, *parts)


def parse_args():
    default_model = project_path("gesture_recognizer.task")
    default_output = project_path("captures")
    default_event_log = os.path.join(default_output, "events.csv")

    parser = argparse.ArgumentParser(description="AI Face & Hand Tracker (MediaPipe + OpenCV).")
    parser.add_argument(
        "--source",
        default="0",
        help="Video source. Use camera index (e.g., 0) or a video file path.",
    )
    parser.add_argument("--width", type=int, default=1280, help="Capture width.")
    parser.add_argument("--height", type=int, default=720, help="Capture height.")
    parser.add_argument("--fps", type=int, default=30, help="Requested camera FPS.")
    parser.add_argument("--max-faces", type=int, default=2, help="Maximum faces to track.")
    parser.add_argument("--max-hands", type=int, default=2, help="Maximum hands to track.")
    parser.add_argument("--min-det", type=float, default=0.55, help="Min detection confidence.")
    parser.add_argument("--min-track", type=float, default=0.55, help="Min tracking confidence.")
    parser.add_argument("--gesture-score", type=float, default=0.62, help="Min gesture score.")
    parser.add_argument(
        "--gesture-delay",
        type=float,
        default=2.0,
        help="Delay in seconds before replaying the same gesture audio.",
    )
    parser.add_argument(
        "--stable-frames",
        type=int,
        default=4,
        help="Gesture hits needed inside the smoothing window before audio is confirmed.",
    )
    parser.add_argument(
        "--gesture-dominance",
        type=float,
        default=0.67,
        help="Winning vote ratio needed to confirm a gesture.",
    )
    parser.add_argument(
        "--smoothing",
        type=float,
        default=0.42,
        help="Landmark smoothing response. Higher is faster, lower is steadier.",
    )
    parser.add_argument(
        "--gesture-model",
        default=default_model,
        help="Path to MediaPipe gesture model (.task). Auto-download if missing.",
    )
    parser.add_argument(
        "--output-dir",
        default=default_output,
        help="Folder for screenshots and recordings.",
    )
    parser.add_argument(
        "--event-log",
        default=default_event_log,
        help="CSV file for gesture, toggle, screenshot, and recording events.",
    )
    parser.add_argument("--no-event-log", action="store_true", help="Disable CSV event logging.")
    parser.add_argument("--no-mirror", action="store_true", help="Disable selfie mirror mode.")
    parser.add_argument("--no-enhance", action="store_true", help="Disable adaptive image enhancement.")
    parser.add_argument(
        "--enhance-strength",
        type=float,
        default=0.45,
        help="Adaptive light/sharpness strength from 0.0 to 1.0.",
    )
    parser.add_argument("--no-face", action="store_true", help="Disable face mesh tracking.")
    parser.add_argument("--no-hands", action="store_true", help="Disable hand gesture tracking.")
    parser.add_argument("--dense-face", action="store_true", help="Draw full face mesh tessellation.")
    parser.add_argument("--privacy-blur", action="store_true", help="Start with face privacy blur enabled.")
    parser.add_argument("--no-trails", action="store_true", help="Hide hand motion trails.")
    parser.add_argument(
        "--gesture-snapshots",
        action="store_true",
        help="Automatically save a screenshot when a stable gesture is confirmed.",
    )
    parser.add_argument("--record", action="store_true", help="Start recording immediately.")
    parser.add_argument("--mute", action="store_true", help="Start with gesture audio muted.")
    parser.add_argument("--hide-help", action="store_true", help="Hide keyboard shortcut help.")
    return parser.parse_args()


def audio_map():
    return {
        "Tangan menjempol": project_path("Selamat.mp3"),
        "Tangan mengepal": project_path("Berjuang.mp3"),
        "2 Tangan menjempol": project_path("Sukses.mp3"),
    }
