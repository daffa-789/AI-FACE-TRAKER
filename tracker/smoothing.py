import numpy as np

from .utils import clamp


class LandmarkSmoother:
    def __init__(self, response=0.42):
        self.response = clamp(response, 0.05, 1.0)
        self.tracks = {}

    def smooth(self, track_key, landmarks):
        current = np.array([(lm.x, lm.y, lm.z) for lm in landmarks], dtype=np.float32)
        previous = self.tracks.get(track_key)
        if previous is not None and previous.shape == current.shape:
            current = previous + (current - previous) * self.response
        self.tracks[track_key] = current
        return current

    def keep_only(self, prefix, active_indexes):
        active_keys = {(prefix, idx) for idx in active_indexes}
        for key in list(self.tracks):
            if isinstance(key, tuple) and key[0] == prefix and key not in active_keys:
                self.tracks.pop(key, None)
