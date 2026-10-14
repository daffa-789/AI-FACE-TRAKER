import os
import urllib.request
from collections import Counter, deque

from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from .utils import clamp


GESTURE_LABELS = {
    "Closed_Fist": "Kepal",
    "Open_Palm": "Telapak",
    "Pointing_Up": "Tunjuk",
    "Thumb_Down": "Jempol turun",
    "Thumb_Up": "Jempol",
    "Victory": "Victory",
    "ILoveYou": "I Love You",
    "None": "None",
}


SINGLE_GESTURE_NAMES = {
    "Closed_Fist": "Tangan mengepal",
    "Open_Palm": "Telapak terbuka",
    "Pointing_Up": "Tangan menunjuk",
    "Thumb_Down": "Tangan jempol turun",
    "Thumb_Up": "Tangan menjempol",
    "Victory": "Tangan victory",
    "ILoveYou": "Tangan I Love You",
}


DOUBLE_GESTURE_NAMES = {
    "Closed_Fist": "2 Tangan mengepal",
    "Open_Palm": "2 Telapak terbuka",
    "Thumb_Up": "2 Tangan menjempol",
    "Victory": "2 Tangan victory",
}


def ensure_gesture_model(model_path):
    model_path = os.path.abspath(model_path)
    if os.path.exists(model_path):
        return model_path

    url = (
        "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/"
        "gesture_recognizer/float16/1/gesture_recognizer.task"
    )
    model_dir = os.path.dirname(model_path)
    if model_dir and not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)

    print("Mengunduh model gesture MediaPipe...")
    urllib.request.urlretrieve(url, model_path)
    return model_path


def load_gesture_model_buffer(model_path):
    with open(model_path, "rb") as model_file:
        return model_file.read()


def create_gesture_recognizer(args):
    gesture_model_path = ensure_gesture_model(args.gesture_model)
    gesture_model_buffer = load_gesture_model_buffer(gesture_model_path)
    gesture_options = vision.GestureRecognizerOptions(
        base_options=mp_python.BaseOptions(model_asset_buffer=gesture_model_buffer),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=args.max_hands,
        min_hand_detection_confidence=args.min_det,
        min_hand_presence_confidence=args.min_det,
        min_tracking_confidence=args.min_track,
    )
    return vision.GestureRecognizer.create_from_options(gesture_options)


class GestureStabilizer:
    def __init__(self, required_hits=4, dominance=0.67):
        self.required_hits = max(1, required_hits)
        self.history = deque(maxlen=max(5, self.required_hits + 3))
        self.dominance = clamp(dominance, 0.5, 1.0)

    def update(self, gesture, score):
        self.history.append((gesture, float(score or 0.0)))
        valid = [(name, confidence) for name, confidence in self.history if name]
        if not valid:
            return None, 0.0, 0.0

        hit_counts = Counter(name for name, _ in valid)
        score_totals = Counter()
        for name, confidence in valid:
            score_totals[name] += confidence

        best_name, best_hits = hit_counts.most_common(1)[0]
        best_score_total = score_totals[best_name]
        total_score = max(0.001, sum(score_totals.values()))
        dominance = best_score_total / total_score
        confidence = best_score_total / max(1, best_hits)
        progress = clamp(best_hits / self.required_hits, 0.0, 1.0)

        if best_hits >= self.required_hits and dominance >= self.dominance:
            return best_name, confidence, progress
        return None, confidence, progress


def extract_hand_infos(gesture_result, smoother):
    hand_landmarks_list = gesture_result.hand_landmarks if gesture_result else []
    gestures_list = gesture_result.gestures if gesture_result else []
    handedness_list = gesture_result.handedness if gesture_result else []

    hand_infos = []
    active_indexes = []
    for hand_idx, hand_landmarks in enumerate(hand_landmarks_list or []):
        active_indexes.append(hand_idx)
        hand_points = smoother.smooth(("hand", hand_idx), hand_landmarks)
        gesture_candidates = gestures_list[hand_idx] if hand_idx < len(gestures_list) else []
        handedness_candidates = handedness_list[hand_idx] if hand_idx < len(handedness_list) else []

        top_category = "None"
        top_score = 0.0
        if gesture_candidates:
            top = gesture_candidates[0]
            top_category = top.category_name
            top_score = float(top.score)

        hand_label = "Hand"
        if handedness_candidates:
            hand_label = handedness_candidates[0].category_name

        hand_infos.append(
            {
                "index": hand_idx,
                "category": top_category,
                "score": top_score,
                "label": hand_label,
                "points": hand_points,
            }
        )

    return hand_infos, active_indexes


def recognize_raw_gesture(hand_infos, min_score):
    valid = [info for info in hand_infos if info["category"] != "None" and info["score"] >= min_score]
    if not valid:
        return None, 0.0

    category_counts = Counter(info["category"] for info in valid)
    category_scores = Counter()
    for info in valid:
        category_scores[info["category"]] += info["score"]

    for category, display_name in DOUBLE_GESTURE_NAMES.items():
        if category_counts[category] >= 2:
            matching_scores = [info["score"] for info in valid if info["category"] == category]
            return display_name, min(matching_scores[:2])

    best_category, best_hits = category_counts.most_common(1)[0]
    best_score = category_scores[best_category] / max(1, best_hits)
    return SINGLE_GESTURE_NAMES.get(best_category, GESTURE_LABELS.get(best_category, best_category)), best_score
