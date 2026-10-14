import time
from collections import Counter


class SessionStats:
    def __init__(self):
        self.started_at = time.perf_counter()
        self.frames = 0
        self.max_faces = 0
        self.max_hands = 0
        self.gesture_counts = Counter()

    def update_frame(self, face_count, hand_count):
        self.frames += 1
        self.max_faces = max(self.max_faces, face_count)
        self.max_hands = max(self.max_hands, hand_count)

    def record_gesture(self, gesture):
        if gesture:
            self.gesture_counts[gesture] += 1

    def runtime_seconds(self):
        return max(0.0, time.perf_counter() - self.started_at)

    def runtime_label(self):
        seconds = int(self.runtime_seconds())
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def top_gesture_label(self):
        if not self.gesture_counts:
            return "-"
        gesture, count = self.gesture_counts.most_common(1)[0]
        return f"{gesture} ({count})"
