import time


def clamp(value, low, high):
    return max(low, min(high, value))


class FpsMeter:
    def __init__(self):
        self.last_time = time.perf_counter()
        self.fps = 0.0

    def update(self):
        now = time.perf_counter()
        dt = now - self.last_time
        self.last_time = now
        if dt > 0:
            instant = 1.0 / dt
            self.fps = instant if self.fps <= 0 else (self.fps * 0.85 + instant * 0.15)
        return self.fps


class TimestampClock:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.last_timestamp_ms = -1

    def next_ms(self):
        timestamp_ms = int((time.perf_counter() - self.start_time) * 1000)
        if timestamp_ms <= self.last_timestamp_ms:
            timestamp_ms = self.last_timestamp_ms + 1
        self.last_timestamp_ms = timestamp_ms
        return timestamp_ms


class Toast:
    def __init__(self):
        self.message = ""
        self.until = 0.0

    def show(self, message, duration=1.6):
        self.message = message
        self.until = time.perf_counter() + duration

    def active(self):
        return bool(self.message) and time.perf_counter() < self.until
