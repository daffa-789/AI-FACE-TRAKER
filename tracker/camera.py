import sys

import cv2
import numpy as np

from .utils import clamp


def open_capture(source, width, height, fps):
    try:
        source_index = int(source)
        if sys.platform.startswith("win"):
            cap = cv2.VideoCapture(source_index, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(source_index)
    except ValueError:
        cap = cv2.VideoCapture(source)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def enhance_frame(frame, clahe, strength):
    strength = clamp(strength, 0.0, 1.0)
    if strength <= 0:
        return frame

    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    y = clahe.apply(y)
    balanced = cv2.cvtColor(cv2.merge((y, cr, cb)), cv2.COLOR_YCrCb2BGR)
    balanced = cv2.addWeighted(balanced, strength, frame, 1.0 - strength, 0)
    blur = cv2.GaussianBlur(balanced, (0, 0), 1.0)
    return cv2.addWeighted(balanced, 1.18, blur, -0.18, 0)


def frame_quality_metrics(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    light_score = 1.0 - abs(brightness - 128.0) / 128.0
    sharpness_score = clamp(sharpness / 260.0, 0.0, 1.0)
    health = clamp(light_score * 0.45 + sharpness_score * 0.55, 0.0, 1.0)
    return {
        "brightness": brightness,
        "sharpness": sharpness,
        "health": health,
    }
