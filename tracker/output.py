import os
from datetime import datetime

import cv2


def save_frame(frame, output_dir, prefix):
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = os.path.join(output_dir, filename)
    cv2.imwrite(path, frame)
    print(f"Disimpan: {path}")
    return path


def start_recording(frame, output_dir, fps):
    os.makedirs(output_dir, exist_ok=True)
    height, width = frame.shape[:2]
    filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    path = os.path.join(output_dir, filename)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, max(10.0, min(60.0, fps or 30.0)), (width, height))
    if not writer.isOpened():
        writer.release()
        filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
        path = os.path.join(output_dir, filename)
        writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"XVID"), 30.0, (width, height))

    if not writer.isOpened():
        writer.release()
        print("Gagal mulai recording.")
        return None, None

    print(f"Recording: {path}")
    return writer, path
