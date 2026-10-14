import csv
import os
from datetime import datetime


class EventLogger:
    def __init__(self, path, enabled=True):
        self.path = path
        self.enabled = enabled and bool(path)
        if self.enabled:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            if not os.path.exists(path):
                with open(path, "w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(["time", "event", "detail", "value"])

    def log(self, event, detail="", value=""):
        if not self.enabled:
            return
        with open(self.path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().isoformat(timespec="seconds"), event, detail, value])
