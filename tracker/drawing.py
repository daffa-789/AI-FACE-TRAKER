from collections import abc as collections_abc

import cv2
import numpy as np

from .face import describe_pose
from .geometry import landmark_center, normalized_bbox, points_to_landmark_list
from .gestures import GESTURE_LABELS
from .utils import clamp


def patch_mediapipe_mapping(mp_drawing):
    if hasattr(mp_drawing, "Mapping"):
        mp_drawing.Mapping = collections_abc.Mapping


def draw_text(frame, text, origin, scale=0.6, color=(255, 255, 255), thickness=1):
    cv2.putText(
        frame,
        text,
        origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        (0, 0, 0),
        thickness + 2,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        text,
        origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


def draw_panel(frame, x, y, width, height, alpha=0.64):
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + width, y + height), (18, 21, 24), -1)
    cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)
    cv2.rectangle(frame, (x, y), (x + width, y + height), (84, 216, 255), 1, cv2.LINE_AA)


def draw_bar(frame, x, y, width, height, ratio, color):
    ratio = clamp(ratio, 0.0, 1.0)
    cv2.rectangle(frame, (x, y), (x + width, y + height), (48, 52, 56), -1)
    cv2.rectangle(frame, (x, y), (x + int(width * ratio), y + height), color, -1)
    cv2.rectangle(frame, (x, y), (x + width, y + height), (180, 185, 190), 1)


def draw_corner_box(frame, bbox, color=(84, 216, 255), thickness=2):
    if not bbox:
        return
    x0, y0, x1, y1 = bbox
    width = x1 - x0
    height = y1 - y0
    corner = max(12, int(min(width, height) * 0.24))

    cv2.line(frame, (x0, y0), (x0 + corner, y0), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x0, y0), (x0, y0 + corner), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x1, y0), (x1 - corner, y0), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x1, y0), (x1, y0 + corner), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x0, y1), (x0 + corner, y1), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x0, y1), (x0, y1 - corner), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x1, y1), (x1 - corner, y1), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x1, y1), (x1, y1 - corner), color, thickness, cv2.LINE_AA)


def draw_label(frame, text, x, y, color=(84, 216, 255)):
    (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
    y = max(22, y)
    cv2.rectangle(frame, (x, y - text_h - 10), (x + text_w + 12, y + 4), color, -1)
    cv2.putText(frame, text, (x + 6, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (12, 16, 18), 1, cv2.LINE_AA)


def draw_status_panel(
    frame,
    fps,
    face_count,
    hand_count,
    stable_gesture,
    stable_confidence,
    progress,
    audio_enabled,
    recording,
    mirror_enabled,
    enhanced_enabled,
    privacy_enabled,
    trails_enabled,
    auto_snapshots,
    quality,
    stats,
):
    panel_w = min(520, frame.shape[1] - 20)
    draw_panel(frame, 10, 10, panel_w, 208)
    draw_text(frame, "AI Face + Hand Tracker MAX", (24, 38), 0.72, (84, 216, 255), 2)
    draw_text(
        frame,
        f"FPS {fps:5.1f} | Face {face_count} | Hand {hand_count} | Time {stats.runtime_label()}",
        (24, 66),
        0.52,
    )

    gesture_text = stable_gesture or "Mencari gesture stabil"
    gesture_color = (87, 255, 122) if stable_gesture else (210, 210, 210)
    draw_text(frame, f"Gesture: {gesture_text}", (24, 94), 0.58, gesture_color, 1)
    draw_bar(frame, 24, 108, min(470, panel_w - 48), 12, progress, (87, 255, 122) if stable_gesture else (84, 216, 255))
    draw_text(frame, f"Confidence {stable_confidence * 100:4.0f}% | Top {stats.top_gesture_label()}", (24, 142), 0.5)

    light_pct = clamp(quality.get("brightness", 0.0) / 255.0, 0.0, 1.0)
    health = quality.get("health", 0.0)
    draw_text(frame, "Camera health", (24, 168), 0.48, (230, 230, 230), 1)
    draw_bar(frame, 130, 156, min(130, panel_w - 155), 12, health, (255, 235, 150))
    draw_text(frame, f"Light {light_pct * 100:3.0f}% Sharp {quality.get('sharpness', 0):.0f}", (274, 168), 0.46)

    toggles = [
        "Audio ON" if audio_enabled else "Audio OFF",
        "REC" if recording else "Ready",
        "Mirror" if mirror_enabled else "No mirror",
        "Enhance" if enhanced_enabled else "Raw",
        "Blur" if privacy_enabled else "No blur",
        "Trail" if trails_enabled else "No trail",
        "AutoShot" if auto_snapshots else "ManualShot",
    ]
    draw_text(frame, " | ".join(toggles[:4]), (24, 196), 0.46, (255, 235, 150), 1)
    draw_text(frame, " | ".join(toggles[4:]), (278, 196), 0.46, (255, 235, 150), 1)

    if recording:
        cv2.circle(frame, (panel_w - 28, 31), 7, (0, 0, 255), -1, cv2.LINE_AA)


def draw_help(frame):
    height, width = frame.shape[:2]
    lines = [
        "Q/Esc keluar  M mirror  F face  H hand  D dense  A audio  E enhance",
        "B blur wajah  T trail  G auto-shot  P pause  S screenshot  R record",
    ]
    text_sizes = [cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.47, 1)[0] for line in lines]
    panel_w = min(width - 20, max(size[0] for size in text_sizes) + 20)
    panel_h = 54
    x = max(10, (width - panel_w) // 2)
    y = height - panel_h - 10
    draw_panel(frame, x, y, panel_w, panel_h, alpha=0.58)
    draw_text(frame, lines[0], (x + 10, y + 22), 0.47, (238, 238, 238), 1)
    draw_text(frame, lines[1], (x + 10, y + 44), 0.47, (238, 238, 238), 1)


def draw_face_overlay(frame, face_info, mp_drawing, mp_drawing_styles, mp_face_mesh, dense_face):
    face_points = face_info["points"]
    bbox = face_info["bbox"]
    face_landmark_list = points_to_landmark_list(face_points)

    if dense_face:
        mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=face_landmark_list,
            connections=mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style(),
        )

    mp_drawing.draw_landmarks(
        image=frame,
        landmark_list=face_landmark_list,
        connections=mp_face_mesh.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style(),
    )
    mp_drawing.draw_landmarks(
        image=frame,
        landmark_list=face_landmark_list,
        connections=mp_face_mesh.FACEMESH_IRISES,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_iris_connections_style(),
    )

    draw_corner_box(frame, bbox, (84, 216, 255), 2)
    pose = face_info.get("pose")
    if bbox and pose:
        pitch, yaw, roll, nose, nose_end = pose
        cv2.line(frame, nose, nose_end, (0, 255, 255), 2, cv2.LINE_AA)
        label = f"Face {face_info['index'] + 1}: {describe_pose(pitch, yaw)}  Y{yaw:+.0f} P{pitch:+.0f} R{roll:+.0f}"
        draw_label(frame, label, bbox[0], bbox[1], (84, 216, 255))


def draw_hand_overlay(frame, hand_info, mp_drawing, mp_drawing_styles, mp_hands):
    hand_points = hand_info["points"]
    hand_landmark_list = points_to_landmark_list(hand_points)
    mp_drawing.draw_landmarks(
        image=frame,
        landmark_list=hand_landmark_list,
        connections=mp_hands.HAND_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
        connection_drawing_spec=mp_drawing_styles.get_default_hand_connections_style(),
    )

    height, width = frame.shape[:2]
    bbox = normalized_bbox(hand_points, width, height, padding=16)
    draw_corner_box(frame, bbox, (87, 255, 122), 2)
    if bbox:
        display_name = GESTURE_LABELS.get(hand_info["category"], hand_info["category"])
        draw_label(
            frame,
            f"{hand_info['label']}: {display_name} {hand_info['score'] * 100:.0f}%",
            bbox[0],
            bbox[1],
            (87, 255, 122),
        )


def update_hand_trails(trails, hand_infos, width, height, max_points=32):
    active = set()
    for info in hand_infos:
        center = landmark_center(info["points"], width, height, index=0)
        if center is None:
            continue
        hand_idx = info["index"]
        active.add(hand_idx)
        if hand_idx not in trails:
            trails[hand_idx] = []
        trails[hand_idx].append(center)
        if len(trails[hand_idx]) > max_points:
            trails[hand_idx] = trails[hand_idx][-max_points:]

    for hand_idx in list(trails):
        if hand_idx not in active:
            trails.pop(hand_idx, None)


def draw_hand_trails(frame, trails):
    for points in trails.values():
        if len(points) < 2:
            continue
        for idx in range(1, len(points)):
            alpha = idx / max(1, len(points) - 1)
            color = (int(60 + 27 * alpha), int(120 + 135 * alpha), int(180 + 42 * alpha))
            thickness = max(1, int(1 + 4 * alpha))
            cv2.line(frame, points[idx - 1], points[idx], color, thickness, cv2.LINE_AA)


def draw_toast(frame, message):
    draw_panel(frame, 10, 228, 430, 46, alpha=0.7)
    draw_text(frame, message, (24, 258), 0.58, (255, 235, 150), 1)


def draw_pause(frame):
    draw_text(frame, "PAUSE", (24, 244), 1.0, (0, 220, 255), 2)


def draw_framing_guides(frame):
    height, width = frame.shape[:2]
    center = (width // 2, height // 2)
    radius = min(width, height) // 5
    cv2.circle(frame, center, radius, (72, 95, 110), 1, cv2.LINE_AA)
    cv2.line(frame, (center[0] - 18, center[1]), (center[0] + 18, center[1]), (72, 95, 110), 1, cv2.LINE_AA)
    cv2.line(frame, (center[0], center[1] - 18), (center[0], center[1] + 18), (72, 95, 110), 1, cv2.LINE_AA)


def fade_background(frame, amount=0.18):
    overlay = np.zeros_like(frame)
    cv2.addWeighted(overlay, amount, frame, 1.0 - amount, 0, frame)
